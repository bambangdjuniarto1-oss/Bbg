// Mesin agent: orchestrator NOVA mendelegasikan tugas ke tim lewat tool "delegasikan".
// Setiap agent adalah loop tool-use Claude dengan akses file terbatas pada folder klien.
import Anthropic from "@anthropic-ai/sdk";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { EventEmitter } from "node:events";
import { ORCHESTRATOR, TIM } from "./agents.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
export const CLIENTS_DIR = path.join(here, "clients");
export const bus = new EventEmitter();

const MODEL = process.env.MODEL || "claude-opus-5-5";
const MODEL_TIM = process.env.MODEL_TIM || MODEL;
const MAKS_LANGKAH = 30;

let client;
const getClient = () => (client ??= new Anthropic());

export const emit = (ev) => bus.emit("event", { ...ev, t: Date.now() });
export const slugify = (s) =>
  s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 40) || "klien";

// ---------- Tool file (dibatasi ke folder klien) ----------

function amankanPath(root, p) {
  const target = path.resolve(root, p);
  const rel = path.relative(root, target);
  if (rel === "" || rel.startsWith("..") || path.isAbsolute(rel)) {
    throw new Error(`path "${p}" keluar dari folder klien`);
  }
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

const objek = (properties) => ({
  type: "object",
  properties,
  required: Object.keys(properties),
  additionalProperties: false,
});

const TOOLS_FILE = [
  {
    name: "daftar_file",
    description: "Lihat semua file yang ada di folder klien.",
    strict: true,
    input_schema: objek({}),
  },
  {
    name: "baca_file",
    description: "Baca isi file di folder klien. Path relatif, contoh: output/riset.md",
    strict: true,
    input_schema: objek({ path: { type: "string" } }),
  },
  {
    name: "tulis_file",
    description: "Tulis (atau timpa) file di folder klien. Path relatif, contoh: output/copy.md",
    strict: true,
    input_schema: objek({ path: { type: "string" }, isi: { type: "string" } }),
  },
];

const WEB_SEARCH = { type: "web_search_20260209", name: "web_search", max_uses: 6 };

async function jalankanToolFile(nama, input, ctx, agent) {
  const root = ctx.root;
  if (nama === "daftar_file") {
    const files = await daftarFile(root);
    return files.length ? files.join("\n") : "(folder kosong)";
  }
  if (nama === "baca_file") {
    status(agent, "working", `membaca ${input.path}`);
    return await fs.readFile(amankanPath(root, input.path), "utf8");
  }
  if (nama === "tulis_file") {
    const target = amankanPath(root, input.path);
    status(agent, "working", `menulis ${input.path}`);
    await fs.mkdir(path.dirname(target), { recursive: true });
    await fs.writeFile(target, input.isi, "utf8");
    emit({ type: "file", agent: agent.id, klien: ctx.slug, path: input.path, url: `/files/${ctx.slug}/${input.path}` });
    return `Tersimpan: ${input.path} (${input.isi.length} karakter)`;
  }
  throw new Error(`tool tidak dikenal: ${nama}`);
}

function status(agent, s, aktivitas = "") {
  emit({ type: "status", agent: agent.id, status: s, aktivitas });
}

function chat(agent, text, extra = {}) {
  if (text?.trim()) emit({ type: "chat", from: agent.id, text: text.trim(), ...extra });
}

// ---------- Loop agent generik ----------

async function loopAgent({ agent, system, tools, messages, effort, model, ctx, jalankanTool }) {
  for (let langkah = 0; langkah < MAKS_LANGKAH; langkah++) {
    const res = await getClient()
      .beta.messages.stream({
        model,
        max_tokens: 32000,
        system: [{ type: "text", text: system, cache_control: { type: "ephemeral" } }],
        tools,
        messages,
        output_config: { effort },
        betas: ["server-side-fallback-2026-07-01"],
        fallbacks: "default",
      })
      .finalMessage();

    ctx.usage.input += res.usage.input_tokens + (res.usage.cache_read_input_tokens ?? 0);
    ctx.usage.output += res.usage.output_tokens;
    emit({ type: "usage", ...ctx.usage });

    if (res.stop_reason === "refusal") {
      throw new Error(`${agent.nama} menolak tugas ini (${res.stop_details?.category ?? "tanpa kategori"})`);
    }
    messages.push({ role: "assistant", content: res.content });

    if (res.stop_reason === "pause_turn") continue;

    const teks = res.content.filter((b) => b.type === "text").map((b) => b.text).join("\n");
    const toolCalls = res.content.filter((b) => b.type === "tool_use");

    if (res.content.some((b) => b.type === "server_tool_use")) {
      status(agent, "working", "mencari di internet");
    }

    if (toolCalls.length === 0) {
      if (res.stop_reason === "max_tokens") throw new Error(`${agent.nama} kehabisan token`);
      return teks;
    }
    if (res.stop_reason === "max_tokens") throw new Error(`input tool ${agent.nama} terpotong (max_tokens)`);

    // Teks di sela pemanggilan tool = catatan progres; tampilkan di chat.
    if (teks.trim() && agent.id === ORCHESTRATOR.id) chat(agent, teks);

    // Semua tool di satu giliran dijalankan paralel, hasilnya dikirim dalam satu pesan.
    const hasil = await Promise.all(
      toolCalls.map(async (tc) => {
        try {
          const out = await jalankanTool(tc.name, tc.input);
          return { type: "tool_result", tool_use_id: tc.id, content: String(out) };
        } catch (err) {
          return { type: "tool_result", tool_use_id: tc.id, is_error: true, content: String(err.message ?? err) };
        }
      }),
    );
    messages.push({ role: "user", content: hasil });
  }
  throw new Error(`${agent.nama} melewati batas ${MAKS_LANGKAH} langkah`);
}

// ---------- Agent spesialis ----------

async function jalankanTim(agent, tugas, ctx) {
  status(agent, "working", "menerima tugas");
  chat(agent, `Siap bos, otw kerjain bagian ${agent.jabatan.toLowerCase()} untuk ${ctx.klien} 🚀`);
  try {
    const laporan = await loopAgent({
      agent,
      system: agent.system,
      tools: agent.pakaiWebSearch ? [...TOOLS_FILE, WEB_SEARCH] : TOOLS_FILE,
      messages: [{ role: "user", content: `Klien: ${ctx.klien}\n\nTugas dari ${ORCHESTRATOR.nama}:\n${tugas}` }],
      effort: "medium",
      model: MODEL_TIM,
      ctx,
      jalankanTool: (nama, input) => jalankanToolFile(nama, input, ctx, agent),
    });
    chat(agent, laporan);
    return laporan;
  } finally {
    status(agent, "idle");
  }
}

// ---------- Orchestrator ----------

const TOOL_DELEGASI = {
  name: "delegasikan",
  description:
    "Berikan tugas ke satu anggota tim dan tunggu laporannya. Panggil beberapa kali dalam satu giliran untuk kerja paralel.",
  strict: true,
  input_schema: objek({
    agent: { type: "string", enum: TIM.map((a) => a.id), description: "riset | copywriter | builder | content" },
    tugas: { type: "string", description: "Instruksi lengkap: tujuan, file input, file output." },
  }),
};

let sibuk = false;
export const sedangSibuk = () => sibuk;

export async function jalankanBrief({ klien, brief }) {
  if (sibuk) throw new Error("Tim masih mengerjakan brief lain. Tunggu sampai selesai.");
  sibuk = true;
  const slug = slugify(klien);
  const ctx = { klien, slug, root: path.join(CLIENTS_DIR, slug), usage: { input: 0, output: 0 } };
  await fs.mkdir(ctx.root, { recursive: true });
  await fs.writeFile(path.join(ctx.root, "brief.md"), `# Brief: ${klien}\n\n${brief}\n`, "utf8");

  const bos = ORCHESTRATOR;
  emit({ type: "brief", klien, slug, brief });
  status(bos, "working", "menyusun rencana");
  try {
    const laporan = await loopAgent({
      agent: bos,
      system: bos.system,
      tools: [TOOL_DELEGASI],
      messages: [
        {
          role: "user",
          content: `Brief dari CEO untuk klien "${klien}" (sudah disimpan di brief.md di folder klien):\n\n${brief}`,
        },
      ],
      effort: "high",
      model: MODEL,
      ctx,
      jalankanTool: async (nama, input) => {
        if (nama !== "delegasikan") throw new Error(`tool tidak dikenal: ${nama}`);
        const agent = TIM.find((a) => a.id === input.agent);
        if (!agent) throw new Error(`agent "${input.agent}" tidak ada`);
        emit({ type: "delegasi", from: bos.id, to: agent.id, tugas: input.tugas });
        status(bos, "review", `menunggu ${agent.nama}`);
        const hasil = await jalankanTim(agent, input.tugas, ctx);
        status(bos, "working", `memeriksa hasil ${agent.nama}`);
        return hasil;
      },
    });
    chat(bos, laporan, { final: true, klien: slug });
    emit({ type: "selesai", klien: slug, usage: ctx.usage });
    return laporan;
  } catch (err) {
    const pesan = err instanceof Anthropic.AuthenticationError
      ? "API key Claude tidak valid. Cek ANTHROPIC_API_KEY."
      : err instanceof Anthropic.RateLimitError
        ? "Kena rate limit Claude API. Coba lagi sebentar lagi."
        : `Gagal: ${err.message ?? err}`;
    chat(bos, `⚠️ ${pesan}`, { error: true });
    emit({ type: "selesai", klien: slug, usage: ctx.usage, error: true });
    throw err;
  } finally {
    for (const a of [bos, ...TIM]) status(a, "idle");
    sibuk = false;
  }
}
