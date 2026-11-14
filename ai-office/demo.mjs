// Mode demo: mensimulasikan alur kerja tim tanpa memanggil Claude API.
// Berguna untuk mencoba tampilan kantor virtual sebelum memasang API key.
import fs from "node:fs/promises";
import path from "node:path";
import { emit, slugify, CLIENTS_DIR } from "./orchestrator.mjs";

const tunggu = (ms) => new Promise((r) => setTimeout(r, ms));
let sibuk = false;
export const demoSibuk = () => sibuk;

const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

export async function jalankanDemo({ klien, brief }) {
  if (sibuk) throw new Error("Demo masih berjalan.");
  sibuk = true;
  const k = esc(klien);
  const slug = slugify(klien);
  const root = path.join(CLIENTS_DIR, slug);
  const tulis = async (agent, p, isi) => {
    emit({ type: "status", agent, status: "working", aktivitas: `menulis ${p}` });
    await fs.mkdir(path.dirname(path.join(root, p)), { recursive: true });
    await fs.writeFile(path.join(root, p), isi, "utf8");
    emit({ type: "file", agent, klien: slug, path: p, url: `/files/${slug}/${p}` });
  };
  const st = (agent, status, aktivitas = "") => emit({ type: "status", agent, status, aktivitas });
  const chat = (from, text, extra = {}) => emit({ type: "chat", from, text, ...extra });

  try {
    emit({ type: "brief", klien, slug, brief });
    st("bos", "working", "menyusun rencana");
    await tunggu(1500);
    chat("bos", `Oke CEO, brief ${klien} gue terima. Urutannya: Raka riset dulu, lalu Sasa tulis copy, terakhir Bima (website) dan Citra (visual) jalan barengan.`);
    st("bos", "review", "menunggu Raka");

    emit({ type: "delegasi", from: "bos", to: "riset", tugas: "Riset tren & kompetitor" });
    st("riset", "working", "menerima tugas");
    chat("riset", `Siap bos, otw riset untuk ${klien} 🔎`);
    await tunggu(11000); // waktu berjalan dari pantry ke meja
    st("riset", "working", "mencari di internet");
    await tunggu(2500);
    await tulis("riset", "output/riset.md", `# Riset ${klien}\n\n(DEMO) Data contoh, bukan hasil riset sungguhan.\n\n## Angle Terkuat\n"Satu paket, langsung beres."\n`);
    await tunggu(800);
    chat("riset", "Riset selesai ✅\n• Tren: pelanggan suka paket praktis sekali pesan\n• Celah: kompetitor belum bundling\n• Angle: \"Satu paket, langsung beres\"\n📄 output/riset.md");
    st("riset", "idle");

    st("bos", "working", "memeriksa hasil Raka");
    await tunggu(1000);
    st("bos", "review", "menunggu Sasa");
    emit({ type: "delegasi", from: "bos", to: "copywriter", tugas: "Tulis copy iklan" });
    st("copywriter", "working", "membaca output/riset.md");
    chat("copywriter", `Siap bos, otw copywriter untuk ${klien} ✍️`);
    await tunggu(11000); // waktu berjalan dari pantry ke meja
    await tulis("copywriter", "output/copy.md", `# Copy ${klien}\n\n(DEMO)\n\n**Headline:** Satu Paket, Langsung Beres!\n**CTA:** Pesan Sekarang\n`);
    await tunggu(700);
    chat("copywriter", "Copy selesai ✅\n• 3 copy iklan + 1 caption IG\n• Hook: \"Satu Paket, Langsung Beres\"\n📄 output/copy.md");
    st("copywriter", "idle");

    st("bos", "working", "memeriksa hasil Sasa");
    await tunggu(1000);
    st("bos", "review", "menunggu Bima & Citra");
    emit({ type: "delegasi", from: "bos", to: "builder", tugas: "Buat landing page" });
    emit({ type: "delegasi", from: "bos", to: "content", tugas: "Buat carousel" });
    chat("builder", `Siap bos, otw bikin website ${klien} 💻`);
    chat("content", `Siap bos, otw bikin visual carousel 🎨`);
    st("builder", "working", "membaca output/copy.md");
    st("content", "working", "membaca output/copy.md");
    await tunggu(11000); // waktu berjalan dari pantry ke meja
    await tulis("builder", "output/site/index.html", `<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${k}</title><style>body{margin:0;font-family:system-ui,sans-serif;background:#fff7ef;color:#2b1d14;text-align:center}header{padding:64px 20px;background:linear-gradient(135deg,#ffb88c,#ff6f91);color:#fff}h1{font-size:2.4rem;margin:0 0 12px}a.cta{display:inline-block;margin-top:20px;background:#fff;color:#ff4d6d;padding:14px 28px;border-radius:999px;font-weight:700;text-decoration:none}section{padding:40px 20px;max-width:640px;margin:auto}</style></head><body><header><h1>Satu Paket, Langsung Beres!</h1><p>${k}: halaman contoh dari mode DEMO.</p><a class="cta" href="#">Pesan Sekarang</a></header><section><h2>Kenapa pilih kami?</h2><p>Isi ini dibuat oleh mode demo. Pasang API key untuk hasil asli dari tim Claude.</p></section></body></html>`);
    for (let i = 1; i <= 3; i++) {
      const teks = ["Satu Paket,", "Pesta Beres", "Pesan Sekarang"][i - 1];
      await tulis("content", `output/images/slide-${i}.svg`, `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1080"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffb88c"/><stop offset="1" stop-color="#ff6f91"/></linearGradient></defs><rect width="1080" height="1080" fill="url(#g)"/><circle cx="880" cy="200" r="140" fill="#fff" opacity=".25"/><text x="540" y="520" font-family="sans-serif" font-size="110" font-weight="800" fill="#fff" text-anchor="middle">${teks}</text><text x="540" y="640" font-family="sans-serif" font-size="44" fill="#fff" text-anchor="middle">${k} · ${i}/3</text></svg>`);
      await tunggu(500);
    }
    chat("content", "Visual selesai ✅\n• 3 slide carousel 1080×1080\n📄 output/images/", {
      images: [1, 2, 3].map((i) => `/files/${slug}/output/images/slide-${i}.svg`),
    });
    st("content", "idle");
    await tunggu(800);
    chat("builder", `Website selesai ✅\n• Landing page responsif + tombol CTA\n🔗 /files/${slug}/output/site/index.html`);
    st("builder", "idle");

    st("bos", "working", "menyusun laporan");
    await tunggu(1500);
    chat("bos", `Laporan untuk CEO: semua tugas ${klien} beres ✅\n\n• Riset → output/riset.md\n• Copy → output/copy.md\n• Website → output/site/index.html\n• Carousel → output/images/\n\nIni mode DEMO: isinya contoh. Pasang ANTHROPIC_API_KEY dan jalankan "npm start" untuk hasil asli.`, { final: true, klien: slug });
    emit({ type: "selesai", klien: slug, usage: { input: 0, output: 0 } });
  } finally {
    for (const a of ["bos", "riset", "copywriter", "builder", "content"]) st(a, "idle");
    sibuk = false;
  }
}
