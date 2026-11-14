// Mode demo: mensimulasikan alur kerja tim (sesuai tim di Pengaturan) tanpa memanggil AI.
import fs from "node:fs/promises";
import path from "node:path";
import { emit, slugify, CLIENTS_DIR } from "./orchestrator.mjs";
import { ambil } from "./settings.mjs";

const tunggu = (ms) => new Promise((r) => setTimeout(r, ms));
const JALAN = 9000; // waktu karakter berjalan dari lounge ke meja

let sibuk = false;
export const demoSibuk = () => sibuk;

export async function jalankanDemo({ klien, brief }) {
  if (sibuk) throw new Error("Demo masih berjalan.");
  sibuk = true;
  const tim = structuredClone(ambil().tim);
  const bos = tim.orchestrator;
  const slug = slugify(klien);
  const root = path.join(CLIENTS_DIR, slug);
  const st = (agent, status, aktivitas = "") => emit({ type: "status", agent, status, aktivitas });
  const chat = (from, text, extra = {}) => emit({ type: "chat", from, text, ...extra });
  const tulis = async (agent, p, isi) => {
    st(agent, "working", `menulis ${p}`);
    await fs.mkdir(path.dirname(path.join(root, p)), { recursive: true });
    await fs.writeFile(path.join(root, p), isi, "utf8");
    emit({ type: "file", agent, klien: slug, path: p, url: `/files/${slug}/${p}` });
  };

  async function kerja(a) {
    emit({ type: "delegasi", from: "bos", to: a.id, tugas: `Kerjakan bagian ${a.jabatan} untuk ${klien}` });
    st(a.id, "working", "menerima tugas");
    chat(a.id, `Siap, otw kerjain bagian ${a.jabatan} untuk ${klien} 🚀`);
    await tunggu(JALAN);
    st(a.id, "working", "menyusun hasil");
    await tunggu(2500);
    const file = `output/${a.id}.md`;
    await tulis(a.id, file, `# ${a.jabatan}: ${klien}\n\n(DEMO) Ini contoh hasil dari ${a.nama}. Hubungkan AI di Pengaturan untuk hasil asli.\n\nBrief:\n${brief}\n`);
    await tunggu(800);
    chat(a.id, `Selesai ✅\n• Bagian ${a.jabatan} beres (contoh demo)\n📄 ${file}`, { klien: slug });
    st(a.id, "idle");
  }

  try {
    emit({ type: "brief", klien, slug, brief });
    st("bos", "working", "menyusun rencana");
    await tunggu(1500);
    const [pertama, ...sisa] = tim.anggota;
    chat("bos", `Oke, brief ${klien} gue terima. ${pertama.nama} mulai duluan${sisa.length ? `, lalu ${sisa.map((a) => a.nama).join(", ")} jalan paralel` : ""}.`);

    st("bos", "review", `menunggu ${pertama.nama}`);
    await kerja(pertama);
    if (sisa.length) {
      st("bos", "working", `memeriksa hasil ${pertama.nama}`);
      await tunggu(1200);
      st("bos", "review", "menunggu tim");
      // sisanya paralel, bergelombang 3 orang supaya animasinya enak dilihat
      for (let i = 0; i < sisa.length; i += 3) {
        await Promise.all(sisa.slice(i, i + 3).map((a, j) => tunggu(j * 600).then(() => kerja(a))));
      }
    }

    st("bos", "working", "menyusun laporan");
    await tunggu(1500);
    chat(
      "bos",
      `Laporan: semua tugas ${klien} beres ✅\n\n${tim.anggota.map((a) => `• ${a.jabatan} → output/${a.id}.md`).join("\n")}\n\nIni mode DEMO: isinya contoh. Buka ⚙️ Pengaturan → Koneksi AI untuk menghubungkan AI asli.`,
      { final: true, klien: slug },
    );
    emit({ type: "selesai", klien: slug, usage: { input: 0, output: 0 } });
  } finally {
    for (const a of [bos, ...tim.anggota]) st(a.id, "idle");
    sibuk = false;
  }
}
