// Lapisan provider AI. Setiap provider menyediakan "sesi percakapan" dengan antarmuka yang sama:
//   const sesi = buatSesi({ system, tools, webSearch, peran }); const r = await sesi.kirim(isi);
//   r = { teks, toolCalls: [{ id, name, input }], selesai }
// Claude memakai Anthropic SDK resmi; OpenRouter/OpenAI/Gemini/Ollama/kustom memakai format
// chat completions yang kompatibel dengan OpenAI.
import Anthropic from "@anthropic-ai/sdk";
import { spawn, execFile } from "node:child_process";
import { ambil, PROVIDER } from "./settings.mjs";

export const MODEL_CLAUDE_BAWAAN = "claude-opus-5-5";

// ---------- Konfigurasi aktif ----------
export function konfigurasi() {
  const k = ambil().koneksi;
  const p = k.provider;
  const baseUrl = p === "custom" ? k.baseUrl : k.baseUrl && p === "ollama" ? k.baseUrl : PROVIDER[p]?.baseUrl;
  const modelBos = k.model || (p.startsWith("anthropic") ? MODEL_CLAUDE_BAWAAN : "");
  return { provider: p, apiKey: k.apiKey[p.startsWith("anthropic") ? "anthropic" : p] || "", baseUrl, modelBos, modelTim: k.modelTim || modelBos };
}

export function siap() {
  const c = konfigurasi();
  if (c.provider === "demo") return { siap: false, alasan: "Mode demo aktif" };
  if (!c.modelBos) return { siap: false, alasan: "Model belum dipilih" };
  if (PROVIDER[c.provider]?.butuhKey && !c.apiKey) return { siap: false, alasan: "API key belum diisi" };
  if (c.provider === "custom" && !c.baseUrl) return { siap: false, alasan: "Base URL belum diisi" };
  return { siap: true };
}

// ---------- Claude ----------
function klienClaude(c) {
  if (c.provider === "anthropic-login") {
    // Mode login: tanpa apiKey, SDK otomatis memakai profil hasil "ant auth login".
    // Variabel API key di environment dibuang karena akan mengalahkan profil login.
    // (Key dari environment sudah disalin ke pengaturan saat aplikasi dimulai.)
    delete process.env.ANTHROPIC_API_KEY;
    delete process.env.ANTHROPIC_AUTH_TOKEN;
    return new Anthropic();
  }
  return new Anthropic({ apiKey: c.apiKey });
}

// Fitur yang hanya dikenali model Claude tertentu
const dukungEffort = (m) => /^claude-(fable|mythos|opus-5|sonnet-5|haiku-5|opus-4-[6-9]|sonnet-4-6)/.test(m);
const dukungFallback = (m) => /^claude-(fable-5-[12]|opus-5-5|opus-5$|sonnet-5-5)/.test(m);
const webSearchBaru = (m) => /^claude-(fable|mythos|opus-5|sonnet-5|opus-4-[6-9]|sonnet-4-6)/.test(m);

function sesiClaude({ system, tools, webSearch, model, effort }, c) {
  const client = klienClaude(c);
  const daftarTool = tools.map((t) => ({ name: t.name, description: t.description, strict: true, input_schema: t.parameters }));
  if (webSearch) {
    daftarTool.push({ type: webSearchBaru(model) ? "web_search_20260209" : "web_search_20250305", name: "web_search", max_uses: 6 });
  }
  const messages = [];
  return {
    async kirim(isi) {
      // isi: string (pesan user) atau array hasil tool [{ id, hasil, error }]
      messages.push({
        role: "user",
        content: typeof isi === "string"
          ? isi
          : isi.map((h) => ({ type: "tool_result", tool_use_id: h.id, content: h.hasil, ...(h.error ? { is_error: true } : {}) })),
      });
      for (;;) {
        const params = {
          model,
          max_tokens: 32000,
          system: [{ type: "text", text: system, cache_control: { type: "ephemeral" } }],
          tools: daftarTool,
          messages,
        };
        if (dukungEffort(model)) params.output_config = { effort };
        if (dukungFallback(model)) {
          params.betas = ["server-side-fallback-2026-07-01"];
          params.fallbacks = "default";
        }
        const res = await client.beta.messages.stream(params).finalMessage();
        if (res.stop_reason === "refusal") {
          throw new Error(`model menolak permintaan ini (${res.stop_details?.category ?? "tanpa kategori"})`);
        }
        messages.push({ role: "assistant", content: res.content });
        if (res.stop_reason === "pause_turn") continue; // web search panjang: lanjutkan giliran
        const toolCalls = res.content.filter((b) => b.type === "tool_use").map((b) => ({ id: b.id, name: b.name, input: b.input }));
        if (res.stop_reason === "max_tokens") throw new Error("jawaban terpotong (batas token)");
        return {
          teks: res.content.filter((b) => b.type === "text").map((b) => b.text).join("\n"),
          toolCalls,
          mencari: res.content.some((b) => b.type === "server_tool_use"),
          usage: {
            input: res.usage.input_tokens + (res.usage.cache_read_input_tokens ?? 0) + (res.usage.cache_creation_input_tokens ?? 0),
            output: res.usage.output_tokens,
          },
        };
      }
    },
  };
}

// ---------- OpenAI-compatible (OpenRouter, OpenAI, Gemini, Ollama, kustom) ----------
async function panggilOpenAI(c, path, body) {
  const headers = { "content-type": "application/json" };
  if (c.apiKey) headers.authorization = `Bearer ${c.apiKey}`;
  if (c.provider === "openrouter") {
    headers["HTTP-Referer"] = "http://localhost";
    headers["X-Title"] = "Kantor Virtual AI";
  }
  const res = await fetch(`${c.baseUrl.replace(/\/$/, "")}${path}`, {
    method: body ? "POST" : "GET",
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  const teks = await res.text();
  let data;
  try {
    data = JSON.parse(teks);
  } catch {
    throw new Error(`respons tidak valid dari ${c.baseUrl} (HTTP ${res.status})`);
  }
  if (!res.ok || data.error) {
    const pesan = data.error?.message || data.error || teks.slice(0, 200);
    if (res.status === 401 || res.status === 403) throw new Error(`API key ditolak: ${pesan}`);
    if (res.status === 429) throw new Error(`kena batas pemakaian (rate limit): ${pesan}`);
    throw new Error(`HTTP ${res.status}: ${pesan}`);
  }
  return data;
}

function sesiOpenAI({ system, tools, model }, c) {
  const messages = [{ role: "system", content: system }];
  const daftarTool = tools.map((t) => ({ type: "function", function: { name: t.name, description: t.description, parameters: t.parameters } }));
  return {
    async kirim(isi) {
      if (typeof isi === "string") messages.push({ role: "user", content: isi });
      else for (const h of isi) messages.push({ role: "tool", tool_call_id: h.id, content: h.error ? `ERROR: ${h.hasil}` : h.hasil });
      const data = await panggilOpenAI(c, "/chat/completions", { model, messages, tools: daftarTool, tool_choice: "auto" });
      const pilihan = data.choices?.[0];
      if (!pilihan) throw new Error("model tidak mengembalikan jawaban");
      const m = pilihan.message;
      messages.push({ role: "assistant", content: m.content ?? "", ...(m.tool_calls?.length ? { tool_calls: m.tool_calls } : {}) });
      if (pilihan.finish_reason === "length") throw new Error("jawaban terpotong (batas token)");
      const toolCalls = (m.tool_calls ?? []).map((tc) => {
        let input;
        try {
          input = JSON.parse(tc.function.arguments || "{}");
        } catch {
          input = { __rusak: tc.function.arguments };
        }
        return { id: tc.id, name: tc.function.name, input };
      });
      return {
        teks: typeof m.content === "string" ? m.content : "",
        toolCalls,
        mencari: false,
        usage: { input: data.usage?.prompt_tokens ?? 0, output: data.usage?.completion_tokens ?? 0 },
      };
    },
  };
}

// ---------- API publik ----------
export function buatSesi({ system, tools, webSearch = false, peran = "tim", effort = "medium" }) {
  const c = konfigurasi();
  const model = peran === "bos" ? c.modelBos : c.modelTim;
  if (c.provider.startsWith("anthropic")) return sesiClaude({ system, tools, webSearch, model, effort }, c);
  return sesiOpenAI({ system, tools, model }, c);
}

export const dukungWebSearch = () => konfigurasi().provider.startsWith("anthropic");

export async function daftarModel() {
  const c = konfigurasi();
  if (c.provider === "demo") return [];
  if (c.provider.startsWith("anthropic")) {
    const hasil = [];
    for await (const m of klienClaude(c).models.list()) hasil.push({ id: m.id, nama: m.display_name });
    return hasil;
  }
  const data = await panggilOpenAI(c, "/models");
  return (data.data ?? []).map((m) => ({ id: m.id, nama: m.name || m.id })).sort((a, b) => a.id.localeCompare(b.id));
}

export async function tesKoneksi() {
  const s = siap();
  if (!s.siap) throw new Error(s.alasan);
  const sesi = buatSesi({ system: "Jawab sesingkat mungkin.", tools: [], peran: "bos", effort: "low" });
  const r = await sesi.kirim("Balas dengan satu kata: OK");
  return r.teks.trim().slice(0, 100) || "(jawaban kosong)";
}

// ---------- Login akun Claude Console via Anthropic CLI ("ant") ----------
const jalankan = (cmd, args) =>
  new Promise((resolve) => {
    execFile(cmd, args, { timeout: 15000 }, (err, stdout, stderr) => resolve({ err, out: `${stdout}${stderr}` }));
  });

export async function statusLoginClaude() {
  const { err, out } = await jalankan("ant", ["auth", "status"]);
  if (err?.code === "ENOENT") return { terpasang: false, masuk: false, info: "" };
  const masuk = !/not logged in|no credential|no active|tidak/i.test(out) && /profile|oauth|logged in|workspace|organization/i.test(out);
  return { terpasang: true, masuk, info: out.trim().slice(0, 600) };
}

let prosesLogin = null;
export function mulaiLoginClaude() {
  if (prosesLogin) return { sudahBerjalan: true };
  // "ant auth login" membuka browser di komputer ini untuk login, lalu menyimpan profil.
  // Variabel API key dibuang supaya tidak menimpa profil hasil login.
  const env = { ...process.env };
  delete env.ANTHROPIC_API_KEY;
  delete env.ANTHROPIC_AUTH_TOKEN;
  prosesLogin = spawn("ant", ["auth", "login"], { env, stdio: ["ignore", "pipe", "pipe"] });
  let log = "";
  prosesLogin.stdout.on("data", (d) => (log += d));
  prosesLogin.stderr.on("data", (d) => (log += d));
  const selesai = new Promise((resolve) => {
    prosesLogin.on("error", (e) => {
      prosesLogin = null;
      resolve({ ok: false, pesan: e.code === "ENOENT" ? "Anthropic CLI (ant) belum terpasang." : e.message });
    });
    prosesLogin.on("exit", (code) => {
      prosesLogin = null;
      resolve({ ok: code === 0, pesan: log.trim().slice(-500) });
    });
  });
  return { selesai, ambilLog: () => log };
}
