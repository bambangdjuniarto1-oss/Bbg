# Kantor Virtual AI

Tim agent AI berbasis Claude dengan tampilan kantor 3D. Kamu cukup kirim **satu brief**. Orchestrator (NOVA) membagi tugas ke tim, lalu setiap agent bekerja dan melapor. Tampilannya berupa gedung isometrik 3 lantai (18 kubikel per lantai, total 54 kursi) dengan Ruang CEO, Studio Produksi, Ruang Server, ruang rapat, lounge, dan pantry. Setiap divisi duduk berdekatan. Karakter berjalan dari lounge ke kubikelnya saat bekerja dan kembali santai setelah selesai. Tombol di bawah layar memilih tampilan seluruh gedung atau satu lantai.

| Agent | Peran | Hasil |
|---|---|---|
| **NOVA** | Orchestrator / bos | Membagi tugas, memeriksa hasil, laporan akhir ke CEO |
| **Raka** | Riset (pakai web search) | `output/riset.md` |
| **Sasa** | Copywriter | `output/copy.md` |
| **Bima** | Builder | `output/site/index.html` (landing page) |
| **Citra** | Content | `output/images/slide-*.svg` (carousel IG) |

Semua hasil tersimpan di `clients/<nama-klien>/` dan bisa dibuka langsung dari chat.

## Cara clone dari GitHub

Butuh **Git** dan **Node.js 20+** (unduh di git-scm.com dan nodejs.org).

```bash
# 1. Clone repo (publik, tidak perlu login)
git clone https://github.com/bambangdjuniarto1-oss/Bbg.git
cd Bbg

# 2. Pindah ke branch yang berisi proyek ini
git checkout claude/awesome-rubin-rxca7e

# 3. Masuk ke folder proyek
cd ai-office
```

Kalau ingin mengunduh **hanya branch ini** (lebih cepat):

```bash
git clone --branch claude/awesome-rubin-rxca7e --single-branch https://github.com/bambangdjuniarto1-oss/Bbg.git
cd Bbg/ai-office
```

Tanpa Git: buka https://github.com/bambangdjuniarto1-oss/Bbg/tree/claude/awesome-rubin-rxca7e, klik **Code → Download ZIP**, lalu ekstrak.

Untuk mengambil pembaruan terbaru di kemudian hari:

```bash
git pull
```

## Cara menjalankan

```bash
cd ai-office
npm install
npm start
```

Buka **http://localhost:3000**. Tanpa pengaturan apa pun, aplikasi berjalan dalam **mode demo** supaya kamu bisa melihat cara kerjanya.

## Menghubungkan AI (tanpa edit file)

Klik **⚙️ Pengaturan → Koneksi AI**, pilih salah satu, lalu klik **Simpan** dan **Tes koneksi**:

| Pilihan | Yang dibutuhkan |
|---|---|
| **Claude (API key)** | API key dari platform.claude.com → API Keys |
| **Claude (login akun Claude Console)** | Tanpa API key. Klik *Login dengan akun Claude*, lalu login di browser. Butuh Anthropic CLI (`ant`) terpasang. Tagihan masuk ke akun Console, bukan langganan Claude Pro/Max |
| **OpenRouter** | Klik *Login dengan OpenRouter* (tanpa menyalin key), atau tempel API key. Satu akun untuk Claude, GPT, Gemini, Llama, dll |
| **OpenAI** | API key dari platform.openai.com |
| **Google Gemini** | API key dari Google AI Studio |
| **Ollama** | Gratis, berjalan di komputer sendiri, tanpa key. Pasang dari ollama.com lalu unduh model yang mendukung *tool calling* |
| **Kustom** | Layanan lain berformat OpenAI (Groq, DeepSeek, LM Studio, dll): isi base URL dan key |

- Klik **Muat daftar model** untuk memilih model. Model untuk anggota tim bisa dibuat lebih murah daripada model bos.
- API key disimpan di komputer ini saja (`data/settings.json`, hanya bisa dibaca pemilik akun komputer) dan tidak pernah ditampilkan utuh lagi di layar.
- Pencarian internet untuk agent hanya tersedia dengan koneksi Claude.

## Mengatur tim & persona (tanpa edit file)

Klik **⚙️ Pengaturan → Tim & Persona**:

- **Pakai template:** *Agensi Digital Marketing* (5 agent), *Perusahaan Media* (CEO ARKA + 8 kepala divisi), atau *Perusahaan Media: struktur lengkap* (47 agent: CEO + 8 kepala divisi + 38 spesialis, 3 lantai).
- Ubah nama, jabatan, warna baju, dan instruksi setiap agent. Tambah atau hapus anggota (maksimal 50).
- Atur **Atasan** setiap anggota: kepala divisi melapor ke bos, spesialis melapor ke kepala divisinya. Bos mendelegasikan ke kepala divisi, lalu kepala divisi mendelegasikan ke spesialisnya.
- Centang *Boleh mencari di internet* untuk agent riset.
- Klik **Simpan tim**. Kantor dimuat ulang dengan tim baru.

Aturan kerja dasar (menyimpan file, melapor, tidak mengarang data) ditambahkan otomatis, jadi instruksi cukup berisi peran dan hasil yang diharapkan.

## Perintah lewat Telegram (opsional)

Klik **⚙️ Pengaturan → Telegram**, ikuti 3 langkah di sana, isi token bot dan chat ID, centang *Aktifkan*, lalu klik **Kirim pesan tes**. Setelah itu kirim brief di grup dengan format `Nama Klien: isi brief`.

## Pengaturan lanjutan (opsional)

| Variabel | Default | Fungsi |
|---|---|---|
| `PORT` | `3000` | Port web |
| `HOST` | `127.0.0.1` | Secara bawaan aplikasi hanya bisa dibuka dari komputer ini. Ubah hanya bila paham risikonya |
| `ANTHROPIC_API_KEY` | – | Bila diisi, dipakai sebagai key Claude awal |

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

- `presets.mjs`: template tim bawaan.
- `settings.mjs`: penyimpanan pengaturan dari halaman Pengaturan.
- `providers.mjs`: koneksi ke Claude, OpenRouter, OpenAI, Gemini, Ollama, dan layanan kustom.
- `orchestrator.mjs`: loop agent Claude (Messages API + tool use). Akses file dikunci ke folder klien.
- `server.mjs`: server web, WebSocket, dan API `/api/brief`.
- `telegram.mjs`: jembatan ke Telegram.
- `public/app.js`: kantor isometrik, karakter voxel, animasi, dan panel chat.
- `public/pengaturan.js`: halaman Pengaturan.
- `demo.mjs`: simulasi tanpa API.

## Hal yang perlu diperhatikan

- **Biaya:** satu brief memicu puluhan panggilan model. Angka token tampil di pojok kanan atas. Pilih model anggota tim yang lebih murah di Pengaturan kalau perlu.
- **Periksa sebelum dikirim ke klien.** Agent diminta menulis `[PERLU DIISI]` untuk data yang tidak diketahui (harga, kontak, testimoni). Cari tanda itu sebelum hasil dipakai.
- **Gambar** dibuat sebagai SVG (desain grafis berbasis teks dan bentuk). Untuk foto produk realistis, tambahkan API generator gambar terpisah ke agent Content.
- **Deploy website** belum otomatis. Hasilnya berupa file HTML yang bisa kamu unggah ke Netlify, Vercel, atau Cloudflare Pages.
