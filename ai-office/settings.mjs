// Penyimpanan pengaturan aplikasi (koneksi AI, tim & persona, Telegram).
// Disimpan otomatis ke data/settings.json oleh aplikasi; pengguna mengubahnya lewat halaman Pengaturan.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { PRESET_TIM } from "./presets.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const DATA_DIR = path.join(here, "data");
const FILE = path.join(DATA_DIR, "settings.json");

export const MAKS_ANGGOTA = 12;

export const PROVIDER = {
  demo: { label: "Demo (simulasi, tanpa AI)" },
  anthropic: { label: "Claude (API key)", butuhKey: true },
  "anthropic-login": { label: "Claude (login akun Claude Console)" },
  openrouter: { label: "OpenRouter (login atau API key)", butuhKey: true, baseUrl: "https://openrouter.ai/api/v1" },
  openai: { label: "OpenAI (API key)", butuhKey: true, baseUrl: "https://api.openai.com/v1" },
  gemini: { label: "Google Gemini (API key)", butuhKey: true, baseUrl: "https://generativelanguage.googleapis.com/v1beta/openai" },
  ollama: { label: "Ollama (lokal, tanpa key)", baseUrl: "http://localhost:11434/v1" },
  custom: { label: "Kustom (OpenAI-compatible)", butuhKey: false },
};

function bawaan() {
  const envKey = process.env.ANTHROPIC_API_KEY;
  return {
    koneksi: {
      provider: envKey ? "anthropic" : "demo",
      apiKey: {}, // per provider: { anthropic: "...", openai: "..." }
      baseUrl: "",
      model: envKey ? process.env.MODEL || "claude-opus-5-5" : "",
      modelTim: process.env.MODEL_TIM || "",
    },
    tim: structuredClone(PRESET_TIM.marketing.tim),
    telegram: {
      aktif: Boolean(process.env.TELEGRAM_BOT_TOKEN && process.env.TELEGRAM_CHAT_ID),
      token: process.env.TELEGRAM_BOT_TOKEN || "",
      chatId: process.env.TELEGRAM_CHAT_ID || "",
    },
  };
}

let cache;
export function ambil() {
  if (cache) return cache;
  try {
    const isi = JSON.parse(fs.readFileSync(FILE, "utf8"));
    const def = bawaan();
    cache = {
      koneksi: { ...def.koneksi, ...isi.koneksi, apiKey: { ...(isi.koneksi?.apiKey ?? {}) } },
      tim: isi.tim ?? def.tim,
      telegram: { ...def.telegram, ...isi.telegram },
    };
  } catch {
    cache = bawaan();
  }
  // API key dari environment tetap dipakai bila belum ada yang disimpan lewat aplikasi
  if (process.env.ANTHROPIC_API_KEY && !cache.koneksi.apiKey.anthropic) {
    cache.koneksi.apiKey.anthropic = process.env.ANTHROPIC_API_KEY;
  }
  return cache;
}

export function simpan(baru) {
  cache = baru;
  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.writeFileSync(FILE, JSON.stringify(baru, null, 2), { encoding: "utf8", mode: 0o600 });
  try {
    fs.chmodSync(FILE, 0o600); // hanya pemilik komputer yang bisa membaca key
  } catch {}
}

const sensor = (k) => (k ? `${k.slice(0, 6)}…${k.slice(-4)}` : "");

// Versi aman untuk dikirim ke browser: API key/token tidak pernah dikirim utuh.
export function untukBrowser() {
  const s = ambil();
  return {
    koneksi: {
      provider: s.koneksi.provider,
      baseUrl: s.koneksi.baseUrl,
      model: s.koneksi.model,
      modelTim: s.koneksi.modelTim,
      keyTersimpan: Object.fromEntries(Object.entries(s.koneksi.apiKey).filter(([, v]) => v).map(([p, v]) => [p, sensor(v)])),
    },
    tim: s.tim,
    telegram: { aktif: s.telegram.aktif, chatId: s.telegram.chatId, tokenTersimpan: sensor(s.telegram.token) },
    provider: PROVIDER,
    preset: Object.fromEntries(Object.entries(PRESET_TIM).map(([id, p]) => [id, { nama: p.nama, deskripsi: p.deskripsi }])),
    maksAnggota: MAKS_ANGGOTA,
  };
}

export const slug = (s) =>
  String(s).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 24) || "agent";

const WARNA_OK = /^#[0-9a-f]{6}$/i;
const teks = (v, maks) => String(v ?? "").trim().slice(0, maks);

// Validasi tim yang dikirim dari halaman Pengaturan
export function bersihkanTim(tim) {
  const o = tim?.orchestrator ?? {};
  const orchestrator = {
    id: "bos",
    nama: teks(o.nama, 30) || "NOVA",
    jabatan: teks(o.jabatan, 40) || "Orchestrator",
    warna: WARNA_OK.test(o.warna) ? o.warna : "#f5b041",
    instruksi: teks(o.instruksi, 8000),
  };
  const dipakai = new Set(["bos"]);
  const anggota = (Array.isArray(tim?.anggota) ? tim.anggota : []).slice(0, MAKS_ANGGOTA).map((a, i) => {
    let id = slug(a.id || a.nama || `agent-${i + 1}`);
    while (dipakai.has(id)) id += "-2";
    dipakai.add(id);
    return {
      id,
      nama: teks(a.nama, 30) || `Agent ${i + 1}`,
      jabatan: teks(a.jabatan, 40) || "Spesialis",
      warna: WARNA_OK.test(a.warna) ? a.warna : "#5dade2",
      instruksi: teks(a.instruksi, 8000),
      webSearch: Boolean(a.webSearch),
    };
  });
  if (anggota.length === 0) throw new Error("Tim minimal punya 1 anggota selain orchestrator.");
  return { orchestrator, anggota };
}
