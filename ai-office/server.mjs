// Server: menyajikan kantor virtual, halaman Pengaturan, menerima brief, menyiarkan event agent lewat WebSocket,
// dan (opsional) menghubungkan bot Telegram. Secara bawaan hanya bisa diakses dari komputer ini (127.0.0.1).
import http from "node:http";
import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { WebSocketServer } from "ws";
import { bus, jalankanBrief, sedangSibuk, CLIENTS_DIR } from "./orchestrator.mjs";
import { jalankanDemo, demoSibuk } from "./demo.mjs";
import { ambil, simpan, untukBrowser, bersihkanTim, PROVIDER } from "./settings.mjs";
import { PRESET_TIM } from "./presets.mjs";
import { siap, daftarModel, tesKoneksi, statusLoginClaude, mulaiLoginClaude, dukungWebSearch, konfigurasi } from "./providers.mjs";
import { aturTelegram, tesTelegram } from "./telegram.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const PORT = Number(process.env.PORT || 3000);
const HOST = process.env.HOST || "127.0.0.1";

const modeDemo = () => process.env.DEMO === "1" || !siap().siap;
const sibuk = () => sedangSibuk() || demoSibuk();
const semuaAgent = () => {
  const t = ambil().tim;
  return [t.orchestrator, ...t.anggota];
};

// ---------- Riwayat event untuk penonton yang baru membuka halaman ----------
let riwayat = [];
let statusAgent = {};
const resetStatus = () => (statusAgent = Object.fromEntries(semuaAgent().map((a) => [a.id, { status: "idle", aktivitas: "" }])));
resetStatus();
bus.on("event", (ev) => {
  if (ev.type === "status") statusAgent[ev.agent] = { status: ev.status, aktivitas: ev.aktivitas };
  if (ev.type !== "status" && ev.type !== "usage") {
    riwayat.push(ev);
    if (riwayat.length > 300) riwayat.shift();
  }
});

// ---------- Helper HTTP ----------
const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".md": "text/plain; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".json": "application/json",
};

async function kirimFile(res, root, rel) {
  const target = path.resolve(root, "." + path.sep + rel);
  if (!target.startsWith(root + path.sep)) return kirim(res, 403, "Terlarang");
  try {
    const data = await fs.readFile(target);
    const headers = { "content-type": MIME[path.extname(target)] || "application/octet-stream" };
    // hasil kerja AI dibuka di sandbox supaya skripnya tidak bisa mengakses aplikasi ini
    if (root === CLIENTS_DIR) headers["content-security-policy"] = "sandbox allow-scripts allow-popups";
    res.writeHead(200, headers);
    res.end(data);
  } catch {
    kirim(res, 404, "Tidak ditemukan");
  }
}

function kirim(res, code, body, type = "text/plain; charset=utf-8") {
  res.writeHead(code, { "content-type": type });
  res.end(typeof body === "string" ? body : JSON.stringify(body));
}
const json = (res, body, code = 200) => kirim(res, code, body, "application/json");

async function bacaBody(req) {
  let data = "";
  for await (const chunk of req) {
    data += chunk;
    if (data.length > 200_000) throw new Error("Data terlalu besar");
  }
  return JSON.parse(data || "{}");
}

// Lindungi dari situs lain yang mencoba memerintah aplikasi lokal ini (CSRF / DNS rebinding)
const HOST_LOKAL = /^(localhost|127\.0\.0\.1|\[::1\])(:\d+)?$/;
function permintaanAman(req) {
  const host = req.headers.host ?? "";
  if (HOST === "127.0.0.1" && !HOST_LOKAL.test(host)) return false;
  if (req.method !== "GET") {
    const origin = req.headers.origin;
    if (!origin || origin !== `http://${host}`) return false;
  }
  return true;
}

export async function terimaBrief({ klien, brief }) {
  klien = String(klien || "").trim().slice(0, 80);
  brief = String(brief || "").trim().slice(0, 20_000);
  if (!klien || !brief) throw new Error("Nama klien dan brief wajib diisi.");
  if (sibuk()) throw new Error("Tim masih mengerjakan brief lain.");
  (modeDemo() ? jalankanDemo : jalankanBrief)({ klien, brief }).catch((err) => console.error("[brief]", err.message));
}

function wajibTidakSibuk() {
  if (sibuk()) throw new Error("Tim sedang bekerja. Tunggu sampai selesai sebelum mengubah pengaturan.");
}

// ---------- Login OpenRouter (OAuth PKCE, tanpa menyalin API key) ----------
const loginOpenRouter = new Map(); // state -> verifier
const b64url = (buf) => buf.toString("base64url");

// ---------- Router ----------
const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, "http://localhost");
  const p = decodeURIComponent(url.pathname);
  if (!permintaanAman(req)) return kirim(res, 403, "Permintaan ditolak");
  try {
    // --- Brief ---
    if (req.method === "POST" && p === "/api/brief") {
      await terimaBrief(await bacaBody(req));
      return json(res, { ok: true }, 202);
    }
    if (p === "/api/info") {
      return json(res, {
        demo: modeDemo(),
        provider: PROVIDER[ambil().koneksi.provider]?.label,
        agents: semuaAgent().map(({ instruksi, ...a }) => a),
      });
    }

    // --- Pengaturan ---
    if (req.method === "GET" && p === "/api/pengaturan") {
      return json(res, { ...untukBrowser(), status: siap(), webSearch: dukungWebSearch(), sibuk: sibuk() });
    }
    if (req.method === "POST" && p === "/api/pengaturan/koneksi") {
      wajibTidakSibuk();
      const b = await bacaBody(req);
      if (!PROVIDER[b.provider]) throw new Error("Provider tidak dikenal");
      const s = ambil();
      const slotKey = b.provider.startsWith("anthropic") ? "anthropic" : b.provider;
      if (typeof b.apiKey === "string" && b.apiKey.trim()) s.koneksi.apiKey[slotKey] = b.apiKey.trim();
      if (b.hapusKey) delete s.koneksi.apiKey[slotKey];
      s.koneksi.provider = b.provider;
      s.koneksi.baseUrl = String(b.baseUrl ?? "").trim().slice(0, 300);
      s.koneksi.model = String(b.model ?? "").trim().slice(0, 120);
      s.koneksi.modelTim = String(b.modelTim ?? "").trim().slice(0, 120);
      simpan(s);
      siarkan({ type: "pengaturan-berubah" });
      return json(res, { ok: true, status: siap() });
    }
    if (req.method === "POST" && p === "/api/pengaturan/tim") {
      wajibTidakSibuk();
      const b = await bacaBody(req);
      const s = ambil();
      s.tim = b.preset ? structuredClone(PRESET_TIM[b.preset]?.tim ?? (() => { throw new Error("Template tidak dikenal"); })()) : bersihkanTim(b.tim);
      simpan(s);
      resetStatus();
      riwayat = [];
      siarkan({ type: "tim-berubah" });
      return json(res, { ok: true });
    }
    if (req.method === "POST" && p === "/api/pengaturan/telegram") {
      const b = await bacaBody(req);
      const s = ambil();
      if (typeof b.token === "string" && b.token.trim()) s.telegram.token = b.token.trim();
      if (b.hapusToken) s.telegram.token = "";
      s.telegram.chatId = String(b.chatId ?? "").trim().slice(0, 40);
      s.telegram.aktif = Boolean(b.aktif);
      simpan(s);
      aturTelegram({ terimaBrief, bus });
      return json(res, { ok: true });
    }
    if (req.method === "POST" && p === "/api/tes-koneksi") {
      return json(res, { ok: true, jawaban: await tesKoneksi(), model: konfigurasi().modelBos });
    }
    if (req.method === "POST" && p === "/api/tes-telegram") {
      const t = ambil().telegram;
      if (!t.token || !t.chatId) throw new Error("Simpan token bot dan chat ID dulu.");
      return json(res, { ok: true, pesan: await tesTelegram(t) });
    }
    if (req.method === "GET" && p === "/api/model") {
      return json(res, { ok: true, model: await daftarModel() });
    }

    // --- Login akun Claude Console (Anthropic CLI) ---
    if (req.method === "GET" && p === "/api/claude-login") {
      return json(res, { ok: true, ...(await statusLoginClaude()), berjalan: Boolean(loginClaude) });
    }
    if (req.method === "POST" && p === "/api/claude-login") {
      if (!loginClaude) {
        const proses = mulaiLoginClaude();
        if (proses.selesai) {
          loginClaude = proses;
          proses.selesai.then((hasil) => {
            loginClaude = null;
            hasilLoginClaude = hasil;
          });
        }
      }
      return json(res, { ok: true });
    }
    if (req.method === "GET" && p === "/api/claude-login/hasil") {
      return json(res, { ok: true, berjalan: Boolean(loginClaude), hasil: hasilLoginClaude, log: loginClaude?.ambilLog() ?? "" });
    }

    // --- Login OpenRouter ---
    if (p === "/auth/openrouter/mulai") {
      const verifier = b64url(crypto.randomBytes(32));
      const challenge = b64url(crypto.createHash("sha256").update(verifier).digest());
      const state = b64url(crypto.randomBytes(12));
      loginOpenRouter.set(state, verifier);
      setTimeout(() => loginOpenRouter.delete(state), 10 * 60_000);
      const kembali = `http://${req.headers.host}/auth/openrouter/kembali?state=${state}`;
      const tujuan = `https://openrouter.ai/auth?callback_url=${encodeURIComponent(kembali)}&code_challenge=${challenge}&code_challenge_method=S256`;
      res.writeHead(302, { location: tujuan });
      return res.end();
    }
    if (p === "/auth/openrouter/kembali") {
      const verifier = loginOpenRouter.get(url.searchParams.get("state") ?? "");
      const code = url.searchParams.get("code");
      if (!verifier || !code) throw new Error("Login OpenRouter kedaluwarsa atau dibatalkan. Ulangi dari Pengaturan.");
      loginOpenRouter.delete(url.searchParams.get("state"));
      const r = await fetch("https://openrouter.ai/api/v1/auth/keys", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ code, code_verifier: verifier, code_challenge_method: "S256" }),
      });
      const data = await r.json().catch(() => ({}));
      if (!r.ok || !data.key) throw new Error(`OpenRouter menolak login: ${data.error?.message ?? r.status}`);
      const s = ambil();
      s.koneksi.apiKey.openrouter = data.key;
      s.koneksi.provider = "openrouter";
      simpan(s);
      res.writeHead(302, { location: "/?pengaturan=koneksi&login=openrouter" });
      return res.end();
    }

    // --- File ---
    if (p.startsWith("/files/")) return kirimFile(res, CLIENTS_DIR, p.slice("/files/".length));
    if (p.startsWith("/vendor/three/")) return kirimFile(res, path.join(here, "node_modules", "three"), p.slice("/vendor/three/".length));
    return kirimFile(res, path.join(here, "public"), p === "/" ? "index.html" : p.slice(1));
  } catch (err) {
    if (p.startsWith("/auth/")) return kirim(res, 400, `Gagal: ${err.message}\n\nKembali ke http://${req.headers.host}/`);
    return json(res, { ok: false, error: String(err.message ?? err) }, 400);
  }
});

let loginClaude = null;
let hasilLoginClaude = null;

// ---------- WebSocket ----------
const wss = new WebSocketServer({
  server,
  path: "/ws",
  verifyClient: ({ req }) => !req.headers.origin || req.headers.origin === `http://${req.headers.host}`,
});
wss.on("connection", (ws) => {
  ws.send(JSON.stringify({ type: "init", demo: modeDemo(), riwayat, statusAgent }));
});
function siarkan(ev) {
  const msg = JSON.stringify(ev);
  for (const ws of wss.clients) if (ws.readyState === 1) ws.send(msg);
}
bus.on("event", siarkan);

server.listen(PORT, HOST, () => {
  const alamat = `http://${HOST === "127.0.0.1" ? "localhost" : HOST}:${PORT}`;
  console.log(`\n🏢 Kantor Virtual AI siap di ${alamat}`);
  console.log(modeDemo()
    ? "   Belum ada koneksi AI → mode DEMO. Buka aplikasi lalu klik ⚙️ Pengaturan untuk menghubungkan AI."
    : `   Koneksi: ${PROVIDER[ambil().koneksi.provider].label}, model ${konfigurasi().modelBos}`);
  aturTelegram({ terimaBrief, bus });
});
