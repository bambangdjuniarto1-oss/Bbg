# Kantor Virtual AI

Tim agent AI berbasis Claude dengan tampilan kantor 3D. Kamu cukup kirim **satu brief**. Orchestrator (NOVA) membagi tugas ke tim, lalu setiap agent bekerja dan melapor. Tampilannya berupa kantor isometrik satu lantai (Ruang CEO, Ruang Rapat, Workspace kubikel, Lounge & Pantry). Karakter berjalan dari lounge ke kubikelnya saat bekerja dan kembali santai setelah selesai.

| Agent | Peran | Hasil |
|---|---|---|
| **NOVA** | Orchestrator / bos | Membagi tugas, memeriksa hasil, laporan akhir ke CEO |
| **Raka** | Riset (pakai web search) | `output/riset.md` |
| **Sasa** | Copywriter | `output/copy.md` |
| **Bima** | Builder | `output/site/index.html` (landing page) |
| **Citra** | Content | `output/images/slide-*.svg` (carousel IG) |

Semua hasil tersimpan di `clients/<nama-klien>/` dan bisa dibuka langsung dari chat.

## Cara menjalankan

Butuh Node.js 20 atau lebih baru.

```bash
cd ai-office
npm install

# 1) Coba tampilannya dulu tanpa API (simulasi)
npm run demo

# 2) Tim asli dengan Claude
export ANTHROPIC_API_KEY=sk-ant-...      # buat di platform.claude.com
npm start
```

Buka http://localhost:3000, isi nama klien dan brief, lalu klik **Kirim ke Bos**.

Contoh brief:
> Klien toko kue, minta promo Party Bundle (kue + 25 cakesicles). Siapkan riset kompetitor di Jakarta, copy iklan, landing page dengan tombol WhatsApp 62812xxxx, dan carousel IG 3 slide.

## Pengaturan (environment variable)

| Variabel | Default | Fungsi |
|---|---|---|
| `ANTHROPIC_API_KEY` | – | Wajib untuk mode LIVE. Tanpa ini server otomatis masuk mode demo |
| `MODEL` | `claude-opus-5-5` | Model untuk orchestrator |
| `MODEL_TIM` | sama dengan `MODEL` | Model untuk 4 agent. Isi `claude-sonnet-5-5` atau `claude-haiku-5-5` untuk menekan biaya |
| `PORT` | `3000` | Port web |
| `TELEGRAM_BOT_TOKEN` | – | Token bot dari @BotFather (opsional) |
| `TELEGRAM_CHAT_ID` | – | ID chat/grup yang boleh memberi perintah (opsional) |

## Perintah lewat Telegram (opsional)

1. Buat bot di **@BotFather** dan simpan tokennya.
2. Masukkan bot ke grup, lalu matikan *Group Privacy* bot di BotFather supaya bot bisa membaca pesan grup.
3. Cari ID grup: kirim pesan ke grup, lalu buka `https://api.telegram.org/bot<TOKEN>/getUpdates` dan lihat `chat.id`.
4. Jalankan dengan `TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=... npm start`.
5. Kirim brief di grup dengan format `Nama Klien: isi brief`.

Semua laporan agent akan muncul di grup itu, sekaligus di kantor virtual. Bot hanya melayani chat dengan ID yang kamu tentukan.

## Cara kerjanya

```
Brief (web / Telegram)
   │
   ▼
NOVA (orchestrator) ── tool "delegasikan" ──► Raka ─► Sasa ─► Bima ∥ Citra
   │                                            (tiap agent: loop Claude + tool baca/tulis file)
   ▼
Event status/chat/file ──WebSocket──► Kantor virtual 3D (Three.js)
```

- `agents.mjs`: nama, warna, dan **system prompt** setiap agent. Ubah di sini untuk menambah peran atau mengganti gaya kerja.
- `orchestrator.mjs`: loop agent Claude (Messages API + tool use). Akses file dikunci ke folder klien.
- `server.mjs`: server web, WebSocket, dan API `/api/brief`.
- `telegram.mjs`: jembatan ke Telegram.
- `public/app.js`: kantor isometrik, karakter voxel, animasi, dan panel chat.
- `demo.mjs`: simulasi tanpa API.

## Hal yang perlu diperhatikan

- **Biaya:** satu brief memicu puluhan panggilan model. Angka token tampil di pojok kanan atas. Pakai `MODEL_TIM` yang lebih murah kalau perlu.
- **Periksa sebelum dikirim ke klien.** Agent diminta menulis `[PERLU DIISI]` untuk data yang tidak diketahui (harga, kontak, testimoni). Cari tanda itu sebelum hasil dipakai.
- **Gambar** dibuat sebagai SVG (desain grafis berbasis teks dan bentuk). Untuk foto produk realistis, tambahkan API generator gambar terpisah ke agent Content.
- **Deploy website** belum otomatis. Hasilnya berupa file HTML yang bisa kamu unggah ke Netlify, Vercel, atau Cloudflare Pages.
