// Mesin agent: orchestrator mendelegasikan tugas ke anggota tim lewat tool "delegasikan".
// Tim, persona, dan provider AI dibaca dari Pengaturan (settings.mjs), jadi bisa diubah dari aplikasi.
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { EventEmitter } from "node:events";
import { ambil } from "./settings.mjs";
import { buatSesi, dukungWebSearch } from "./providers.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
export const CLIENTS_DIR = path.join(here, "clients");
export const bus = new EventEmitter();
const MAKS_LANGKAH = 30;

export const emit = (ev) => bus.emit("event", { ...ev, t: Date.now() });
export const slugify = (s) =>
  s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 40) || "klien";

// ---------- Aturan yang selalu ditambahkan (tidak bisa dihapus dari Pengaturan) ----------
const ATURAN_TIM = `

Aturan kerja (dari sistem):
- Semua file ada di folder klien. Pakai path relatif seperti "output/hasil.md".
- Baca file input yang disebut di tugas sebelum mulai (tool baca_file / daftar_file).
- Simpan hasil kerja dengan tool tulis_file.
- Jangan mengarang data, harga, testimoni, atau kontak. Kalau tidak tahu, tulis [PERLU DIISI].
- Akhiri dengan laporan singkat (maks 6 poin) untuk atasanmu: apa yang dikerjakan dan file apa yang ditulis.
- Bahasa Indonesia, kecuali diminta lain.`;

const bawahan = (tim, id) => tim.anggota.filter((a) => (a.atasan || "") === id);
const deskripsiAnggota = (tim, a) => {
  const anak = bawahan(tim, a.id);
  return `- ${a.id}: ${a.nama} (${a.jabatan}).${anak.length ? ` Memimpin ${anak.length} spesialis.` : ""} ${a.instruksi.split("\n")[0].slice(0, 220)}`;
};
const toolDelegasi = (daftar) => ({
  name: "delegasikan",
  description: "Berikan tugas ke satu anggota tim dan tunggu laporannya. Panggil beberapa kali dalam satu giliran untuk kerja paralel.",
  parameters: objek({
    agent: { type: "string", enum: daftar.map((a) => a.id), description: "ID anggota tim" },
    tugas: { type: "string", description: "Instruksi lengkap: tujuan, file input, file output." },
  }),
});

function systemBos(tim) {
  const daftar = bawahan(tim, "").map((a) => deskripsiAnggota(tim, a)).join("\n");
  return `${tim.orchestrator.instruksi || `Kamu ${tim.orchestrator.nama}, pemimpin tim agent AI.`}

Anggota tim kamu:
${daftar}

Cara kerja (dari sistem):
1. Pecah brief jadi tugas untuk anggota tim yang relevan. Delegasikan lewat tool "delegasikan".
2. Tugas yang bergantung pada hasil anggota lain dikerjakan berurutan. Tugas yang saling lepas boleh paralel: panggil "delegasikan" beberapa kali dalam satu giliran.
3. Tulis instruksi yang spesifik: nama klien, tujuan, file input yang harus dibaca, dan file output yang harus ditulis.
4. Periksa laporan setiap anggota. Kalau kurang, delegasikan revisi sekali ke anggota yang sama.
5. Setelah semua beres, tulis laporan akhir untuk CEO: ringkasan, daftar file, dan hal yang perlu dicek manusia.
Jangan mengerjakan sendiri pekerjaan anggota tim. Jangan mengarang hasil yang tidak dilaporkan.`;
}

// ---------- Tool file (dibatasi ke folder klien) ----------
function amankanPath(root, p) {
  const target = path.resolve(root, String(p));
  const rel = path.relative(root, target);
  if (rel === "" || rel.startsWith("..") || path.isAbsolute(rel)) throw new Error(`path "${p}" keluar dari folder klien`);
  return target;
}

async function daftarFile(dir, root = dir) {
  const hasil = [];
  for (const e of await fs.readdir(dir, { withFileTypes: true }).catch(() => [])) {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) hasil.push(...(await daftarFile(full, root)));
    else hasil.push(path.relative(root, full));
  }
  return hasil;
}

const objek = (properties) => ({ type: "object", properties, required: Object.keys(properties), additionalProperties: false });

const TOOLS_FILE = [
  { name: "daftar_file", description: "Lihat semua file yang ada di folder klien.", parameters: objek({}) },
  {
    name: "baca_file",
    description: "Baca isi file di folder klien. Path relatif, contoh: output/riset.md",
    parameters: objek({ path: { type: "string" } }),
  },
  {
    name: "tulis_file",
    description: "Tulis (atau timpa) file di folder klien. Path relatif, contoh: output/copy.md",
    parameters: objek({ path: { type: "string" }, isi: { type: "string" } }),
  },
];

async function jalankanToolFile(nama, input, ctx, agent) {
  if (input?.__rusak !== undefined) throw new Error("argumen tool bukan JSON yang valid, coba lagi");
  if (nama === "daftar_file") {
    const files = await daftarFile(ctx.root);
    return files.length ? files.join("\n") : "(folder kosong)";
  }
  if (nama === "baca_file") {
    status(agent, "working", `membaca ${input.path}`);
    return await fs.readFile(amankanPath(ctx.root, input.path), "utf8");
  }
  if (nama === "tulis_file") {
    if (typeof input.isi !== "string") throw new Error("isi file wajib berupa teks");
    const target = amankanPath(ctx.root, input.path);
    status(agent, "working", `menulis ${input.path}`);
    await fs.mkdir(path.dirname(target), { recursive: true });
    await fs.writeFile(target, input.isi, "utf8");
    const rel = path.relative(ctx.root, target).split(path.sep).join("/");
    emit({ type: "file", agent: agent.id, klien: ctx.slug, path: rel, url: `/files/${ctx.slug}/${rel}` });
    return `Tersimpan: ${rel} (${input.isi.length} karakter)`;
  }
  throw new Error(`tool tidak dikenal: ${nama}`);
}

const status = (agent, s, aktivitas = "") => emit({ type: "status", agent: agent.id, status: s, aktivitas });
const chat = (agent, text, extra = {}) => text?.trim() && emit({ type: "chat", from: agent.id, text: text.trim(), ...extra });

// ---------- Loop agent generik ----------
async function loopAgent({ agent, sesi, pesanAwal, ctx, jalankanTool, tampilkanCatatan = false }) {
  let isi = pesanAwal;
  for (let langkah = 0; langkah < MAKS_LANGKAH; langkah++) {
    const r = await sesi.kirim(isi);
    ctx.usage.input += r.usage.input;
    ctx.usage.output += r.usage.output;
    emit({ type: "usage", ...ctx.usage });
    if (r.mencari) status(agent, "working", "mencari di internet");
    if (r.toolCalls.length === 0) return r.teks;
    if (tampilkanCatatan) chat(agent, r.teks); // catatan progres di sela pemanggilan tool

    // Semua tool di satu giliran dijalankan paralel
    isi = await Promise.all(
      r.toolCalls.map(async (tc) => {
        try {
          return { id: tc.id, hasil: String(await jalankanTool(tc.name, tc.input)) };
        } catch (err) {
          return { id: tc.id, hasil: String(err.message ?? err), error: true };
        }
      }),
    );
  }
  throw new Error(`${agent.nama} melewati batas ${MAKS_LANGKAH} langkah`);
}

// ---------- Anggota tim ----------
async function jalankanAnggota(agent, tugas, ctx) {
  status(agent, "working", "menerima tugas");
  chat(agent, `Siap, otw kerjain bagian ${agent.jabatan} untuk ${ctx.klien} 🚀`);
  try {
    const pakaiWeb = agent.webSearch && dukungWebSearch();
    const catatanWeb = agent.webSearch && !pakaiWeb
      ? "\n- Pencarian internet tidak tersedia di koneksi AI ini. Pakai pengetahuanmu dan tandai data yang perlu diverifikasi dengan [PERLU DICEK]."
      : "";
    const anak = bawahan(ctx.tim, agent.id);
    const aturanTim = anak.length
      ? `\n\nTim spesialismu:\n${anak.map((a) => deskripsiAnggota(ctx.tim, a)).join("\n")}
- Delegasikan lewat tool "delegasikan" hanya ke spesialis yang relevan; yang saling lepas boleh paralel.
- Beri instruksi spesifik (file input dan output), periksa laporannya, lalu gabungkan.`
      : "";
    const sesi = buatSesi({
      system: agent.instruksi + aturanTim + ATURAN_TIM + catatanWeb,
      tools: anak.length ? [...TOOLS_FILE, toolDelegasi(anak)] : TOOLS_FILE,
      webSearch: pakaiWeb,
      peran: "tim",
      effort: "medium",
    });
    const atasan = ctx.tim.anggota.find((a) => a.id === agent.atasan) ?? ctx.tim.orchestrator;
    const laporan = await loopAgent({
      agent,
      sesi,
      pesanAwal: `Klien: ${ctx.klien}\n\nTugas dari ${atasan.nama}:\n${tugas}`,
      ctx,
      jalankanTool: (nama, input) =>
        nama === "delegasikan" ? delegasikan(agent, anak, input, ctx) : jalankanToolFile(nama, input, ctx, agent),
    });
    chat(agent, laporan || "(selesai tanpa laporan)");
    return laporan;
  } finally {
    status(agent, "idle");
  }
}

async function delegasikan(dari, daftar, input, ctx) {
  const agent = daftar.find((a) => a.id === input.agent);
  if (!agent) throw new Error(`anggota "${input.agent}" tidak ada. Pilihan: ${daftar.map((a) => a.id).join(", ")}`);
  const tugas = String(input.tugas ?? "");
  emit({ type: "delegasi", from: dari.id, to: agent.id, tugas });
  status(dari, "review", `menunggu ${agent.nama}`);
  const hasil = await jalankanAnggota(agent, tugas, ctx);
  status(dari, "working", `memeriksa hasil ${agent.nama}`);
  return hasil;
}

// ---------- Orchestrator ----------
let sibuk = false;
export const sedangSibuk = () => sibuk;

export async function jalankanBrief({ klien, brief }) {
  if (sibuk) throw new Error("Tim masih mengerjakan brief lain. Tunggu sampai selesai.");
  sibuk = true;
  const tim = structuredClone(ambil().tim);
  const bos = tim.orchestrator;
  const slug = slugify(klien);
  const ctx = { klien, slug, tim, root: path.join(CLIENTS_DIR, slug), usage: { input: 0, output: 0 } };


  try {
    await fs.mkdir(ctx.root, { recursive: true });
    await fs.writeFile(path.join(ctx.root, "brief.md"), `# Brief: ${klien}\n\n${brief}\n`, "utf8");
    emit({ type: "brief", klien, slug, brief });
    status(bos, "working", "menyusun rencana");

    const laporan = await loopAgent({
      agent: bos,
      sesi: buatSesi({ system: systemBos(tim), tools: [toolDelegasi(bawahan(tim, ""))], peran: "bos", effort: "high" }),
      pesanAwal: `Brief dari CEO untuk klien "${klien}" (sudah disimpan di brief.md di folder klien):\n\n${brief}`,
      ctx,
      tampilkanCatatan: true,
      jalankanTool: async (nama, input) => {
        if (nama !== "delegasikan") throw new Error(`tool tidak dikenal: ${nama}`);
        return delegasikan(bos, bawahan(tim, ""), input, ctx);
      },
    });
    chat(bos, laporan, { final: true, klien: slug });
    emit({ type: "selesai", klien: slug, usage: ctx.usage });
    return laporan;
  } catch (err) {
    chat(bos, `⚠️ Gagal: ${err.message ?? err}\n\nCek Pengaturan → Koneksi AI, lalu klik "Tes koneksi".`, { error: true });
    emit({ type: "selesai", klien: slug, usage: ctx.usage, error: true });
    throw err;
  } finally {
    for (const a of [bos, ...tim.anggota]) status(a, "idle");
    sibuk = false;
  }
}
