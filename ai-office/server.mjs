// Server: menyajikan kantor virtual, menerima brief, menyiarkan event agent lewat WebSocket,
// dan (opsional) menghubungkan bot Telegram.
import http from "node:http";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { WebSocketServer } from "ws";
import { bus, jalankanBrief, sedangSibuk, CLIENTS_DIR } from "./orchestrator.mjs";
import { jalankanDemo, demoSibuk } from "./demo.mjs";
import { SEMUA_AGENT } from "./agents.mjs";
import { mulaiTelegram } from "./telegram.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const PORT = Number(process.env.PORT || 3000);
const DEMO = process.env.DEMO === "1" || !(process.env.ANTHROPIC_API_KEY || process.env.ANTHROPIC_AUTH_TOKEN);

const jalankan = DEMO ? jalankanDemo : jalankanBrief;
const sibuk = () => (DEMO ? demoSibuk() : sedangSibuk());

// ---------- Riwayat event untuk penonton yang baru membuka halaman ----------
const riwayat = [];
const statusAgent = Object.fromEntries(SEMUA_AGENT.map((a) => [a.id, { status: "idle", aktivitas: "" }]));
bus.on("event", (ev) => {
  if (ev.type === "status") statusAgent[ev.agent] = { status: ev.status, aktivitas: ev.aktivitas };
  if (ev.type !== "status" && ev.type !== "usage") {
    riwayat.push(ev);
    if (riwayat.length > 300) riwayat.shift();
  }
});

// ---------- HTTP ----------
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
  if (!target.startsWith(root + path.sep) && target !== root) return kirim(res, 403, "Terlarang");
  try {
    const data = await fs.readFile(target);
    res.writeHead(200, { "content-type": MIME[path.extname(target)] || "application/octet-stream" });
    res.end(data);
  } catch {
    kirim(res, 404, "Tidak ditemukan");
  }
}

function kirim(res, code, body, type = "text/plain; charset=utf-8") {
  res.writeHead(code, { "content-type": type });
  res.end(typeof body === "string" ? body : JSON.stringify(body));
}

async function bacaBody(req) {
  let data = "";
  for await (const chunk of req) {
    data += chunk;
    if (data.length > 100_000) throw new Error("Brief terlalu panjang");
  }
  return JSON.parse(data || "{}");
}

export async function terimaBrief({ klien, brief }) {
  klien = String(klien || "").trim().slice(0, 80);
  brief = String(brief || "").trim().slice(0, 20_000);
  if (!klien || !brief) throw new Error("Nama klien dan brief wajib diisi.");
  if (sibuk()) throw new Error("Tim masih mengerjakan brief lain.");
  jalankan({ klien, brief }).catch((err) => console.error("[brief]", err));
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, "http://localhost");
  const p = decodeURIComponent(url.pathname);
  try {
    if (req.method === "POST" && p === "/api/brief") {
      await terimaBrief(await bacaBody(req));
      return kirim(res, 202, { ok: true }, "application/json");
    }
    if (p === "/api/info") {
      return kirim(res, 200, { demo: DEMO, agents: SEMUA_AGENT.map(({ system, ...a }) => a) }, "application/json");
    }
    if (p.startsWith("/files/")) return kirimFile(res, CLIENTS_DIR, p.slice("/files/".length));
    if (p.startsWith("/vendor/three/")) {
      return kirimFile(res, path.join(here, "node_modules", "three"), p.slice("/vendor/three/".length));
    }
    return kirimFile(res, path.join(here, "public"), p === "/" ? "index.html" : p.slice(1));
  } catch (err) {
    return kirim(res, 400, { ok: false, error: String(err.message ?? err) }, "application/json");
  }
});

// ---------- WebSocket ----------
const wss = new WebSocketServer({ server, path: "/ws" });
wss.on("connection", (ws) => {
  ws.send(JSON.stringify({ type: "init", demo: DEMO, riwayat, statusAgent }));
});
bus.on("event", (ev) => {
  const msg = JSON.stringify(ev);
  for (const ws of wss.clients) if (ws.readyState === 1) ws.send(msg);
});

server.listen(PORT, () => {
  console.log(`\n🏢 Kantor virtual AI siap di http://localhost:${PORT}`);
  console.log(DEMO
    ? "   Mode: DEMO (simulasi, tanpa API). Isi ANTHROPIC_API_KEY lalu jalankan npm start untuk tim asli."
    : `   Mode: LIVE dengan model ${process.env.MODEL || "claude-opus-5-5"}`);
  mulaiTelegram({ terimaBrief, bus, agents: SEMUA_AGENT });
});
