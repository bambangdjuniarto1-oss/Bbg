# Satu Prompt untuk Menggerakkan 47 Agent — Peluncuran Konteks Journal

Satu prompt, dikirim sekali ke agent **CEO**, menggerakkan seluruh tim:
**1 CEO + 8 kepala divisi + 38 spesialis = 47 agent**, untuk memprogram pekan peluncuran
**Senin 16 – Minggu 22 November 2026** dengan fokus **musik Indonesia dan para artisnya**.

---

## Cara kerjanya dalam satu sesi

```
                    PROMPT TUNGGAL ──► CEO
                                        │
 Fase 1  CEO menulis manifesto + rencana induk pekan peluncuran
 Fase 2  CEO menugaskan 8 kepala divisi (paralel) ──► rencana kerja per divisi + tugas tiap spesialis
 Fase 3  CEO menjalankan 1 WORKFLOW RUN berisi 38 spesialis, bertahap:
           Tahap A  Research (4) + Finance & Operation (5) + Technology (4)
           Tahap B  Editorial (7) + Business (4) + Community (4)
           Tahap C  Creative (5) + Distribution & Growth (5)
           Tahap D  Legal & Rights Compliance + Copy Editor memeriksa semua konten
 Fase 4  8 kepala divisi memeriksa hasil spesialisnya ──► laporan divisi
 Fase 5  CEO menyusun Program Pekan 1 + laporan untuk Founder
```

Kenapa memakai **workflow run**: di Console, satu sesi hanya bisa punya satu koordinator dengan
maksimal 20 agent di roster dan 25 thread. Workflow run tidak terkena batas 25 thread itu, jadi
38 spesialis bisa dijalankan sekaligus dari satu prompt.

---

## Persiapan sekali saja (sebelum mengirim prompt)

### 1. Memori
Menu **Memori**:
- `brand-bible`: Brand Bible Konteks Journal (lihat LANGKAH-CONSOLE.md, Langkah 1).
- `konteks-hq`: buat file `tim/spesialis.md` lalu tempel isi **PROFIL-SPESIALIS.md**.

### 2. Agent yang dibutuhkan: cukup 9
- **8 agent divisi** seperti di LANGKAH-CONSOLE.md, Langkah 2. Pastikan **multiagent tidak aktif**
  di agent divisi. Kalau Anda sempat menerapkan Lampiran 2 dari PELUNCURAN-KONTEKS-JOURNAL.md,
  matikan lagi multiagent-nya.
- **CEO**: perbarui konfigurasinya dengan blok di bawah.

38 spesialis **tidak perlu dibuat satu per satu**. CEO membentuk mereka di dalam workflow run
dari file profil.

```
Perbarui agen "CEO - AI Company Director".
Model: claude-opus-5-5.
Aktifkan multiagent:
- Roster subagent: "Research & Intelligence", "Editorial & Strategy", "Creative & Production",
  "Distribution & Growth", "Business & Monetization", "Technology & Automation",
  "Finance & Operation", "Community & Audience". Jangan izinkan agen inline di roster.
- Workflows: aktif, dan izinkan agen inline yang didefinisikan workflow.
Tools: read, write, bash, web_search, web_fetch.
Tambahkan di akhir system prompt:

Untuk pekerjaan yang terdiri dari banyak bagian paralel, seperti menjalankan 38 spesialis
peluncuran, jalankan workflow run. Definisikan setiap spesialis sebagai agen di workflow
dengan system prompt dari profilnya di /mnt/memory/konteks-hq/tim/spesialis.md (aturan umum +
peran + tugas spesifik). Pekerjaan kecil kerjakan sendiri atau tugaskan ke kepala divisi.
```

> **Opsi lebih hemat:** spesialis yang didefinisikan di dalam workflow berjalan dengan model CEO
> (Opus). Jika Anda sudah membuat agent spesialis (Lampiran 1 PELUNCURAN-KONTEKS-JOURNAL.md, model
> Sonnet/Haiku), maksimal 20 di antaranya bisa dimasukkan ke daftar agen workflow CEO. Mereka
> lalu berjalan dengan model masing-masing yang lebih murah, dan sisanya tetap didefinisikan
> oleh workflow.

### 3. Sesi
Menu **Sesi** → sesi baru:
- Agen: **CEO - AI Company Director**
- Lingkungan: `media-hq`
- Memori: `brand-bible` (read only) + `konteks-hq` (read & write)
- **Batas biaya sesi: sekitar US$50.** Workflow dengan 38 spesialis memakai banyak token.
  Perkiraan kasar US$30–60. Kalau batas tercapai, pekerjaan berhenti sementara dan bisa
  dilanjutkan setelah batasnya dinaikkan.

---

## PROMPT TUNGGAL

Ganti `[...]`, lalu kirim sekali.

```
CEO, hari ini Konteks Journal lahir.

Ini peluncuran pertama brand kita, dan seluruh 47 anggota tim bergerak bersama dalam satu operasi: kamu, 8 kepala divisi, dan 38 spesialis. Kamu memimpinnya dari awal sampai akhir di sesi ini.

MISI
Memprogram dan menyiapkan PEKAN PELUNCURAN Konteks Journal, Senin 16 – Minggu 22 November 2026, dengan fokus utama MUSIK INDONESIA DAN PARA ARTISNYA. Film, lifestyle, serta seni & budaya masuk lewat sudut musik.

TENTANG KONTEKS JOURNAL
- Media Indonesia tentang musik, film, lifestyle, serta seni & budaya.
- Janji kami: memberi KONTEKS. Kami menjelaskan kenapa sebuah lagu, album, artis, atau skena itu penting, dari mana asalnya, dan ke mana arahnya.
- Audiens: [contoh: anak muda urban Indonesia 18–34 tahun yang ingin memahami musik dan budaya].
- Suara: [contoh: cerdas tapi tidak menggurui, kritis tapi hangat, rapi seperti jurnal, hidup seperti obrolan].
- Kanal: [Instagram, TikTok, YouTube, Spotify/podcast, website, newsletter].
- Kondisi saat ini: [contoh: brand baru, akun media sosial baru dibuat].
- Tim manusia: [contoh: Founder + 1 editor video freelance].
- Anggaran pekan peluncuran: Rp[...]. Batas pengeluaran tanpa persetujuan Founder: Rp[...].
- Target pekan pertama: [contoh: 1.000 pengikut gabungan, 14 konten terbit, 200 pelanggan newsletter, 3 percakapan dengan calon mitra].

BANK TOPIK (wilayah Indonesia, wajib diverifikasi sebelum dipakai)
1. Rilis album dan single musisi Indonesia pertengahan November 2026.
2. Lagu Indonesia yang sedang naik di Spotify, YouTube, dan TikTok Indonesia, dan kenapa.
3. Konser, tur, dan festival musik akhir tahun 2026 di Indonesia.
4. Skena musik daerah: Bandung, Yogyakarta, Jakarta, Bali, Malang, Medan, Makassar, dan lainnya.
5. Dangdut, koplo, pop Jawa, pop Minang, pop Batak, campursari, dan genre daerah lain yang naik ke arus utama.
6. Musisi Indonesia di panggung internasional.
7. Isu industri: royalti dan hak cipta lagu, AI dalam musik, ekonomi musisi independen.
8. Musik × Film: soundtrack dan film bertema musik.
9. Musik × Lifestyle: fashion panggung, budaya nonton gigs, tongkrongan musik.
10. Musik × Seni: artwork album, desain panggung, kolaborasi musisi dengan perupa.
11. Arsip: album atau lagu Indonesia penting yang berulang tahun minggu ini.

KERANGKA PROGRAM 7 HARI (boleh kamu sempurnakan)
- Senin 16: HARI PELUNCURAN — manifesto + konten andalan tentang topik musik Indonesia terbesar minggu ini.
- Selasa 17: Rilis & ulasan.
- Rabu 18: Profil artis & skena daerah.
- Kamis 19: Musik × Film.
- Jumat 20: Musik × Lifestyle + newsletter edisi #1.
- Sabtu 21: Musik × Seni + listening session komunitas.
- Minggu 22: "Konteks Pekan Ini" — rangkuman pekan.

JALANKAN OPERASI DALAM 5 FASE
Semua dokumen koordinasi disimpan di /mnt/memory/konteks-hq/launch/. File kerja lengkap disimpan di /mnt/session/outputs/<divisi>/ dengan nama divisi: research, editorial, creative, growth, business, tech, finance-ops, community.

FASE 1 — Kamu sendiri
Tulis manifesto.md (maks. 1 halaman) dan rencana-induk.md: narasi peluncuran, tabel program harian (tanggal | tema | konten utama | format | kanal | jam tayang | divisi), dan target KPI per divisi.

FASE 2 — 8 kepala divisi, paralel
Tugaskan setiap kepala divisi di rostermu untuk membaca manifesto dan rencana induk, lalu menulis rencana-<divisi>.md berisi tugas spesifik pekan peluncuran untuk SETIAP spesialis di divisinya (lihat /mnt/memory/konteks-hq/tim/spesialis.md): tugas, input, format output, path file output, dan kriteria selesai.

FASE 3 — Workflow run "Pekan Peluncuran Konteks Journal" dengan 38 spesialis
Definisikan ke-38 spesialis dari profil mereka, masing-masing dengan tugas dari rencana divisinya. Jalankan bertahap, dan setiap tahap membaca hasil tahap sebelumnya:
- Tahap A: semua spesialis Research & Intelligence, Finance & Operation, dan Technology & Automation. Trend Scout wajib memverifikasi bank topik dan memilih 7 topik utama (satu per hari) beserta sumbernya.
- Tahap B: semua spesialis Editorial & Strategy, Business & Monetization, dan Community & Audience.
- Tahap C: semua spesialis Creative & Production dan Distribution & Growth.
- Tahap D: Legal & Rights Compliance menilai setiap konten HIJAU/KUNING/MERAH (lagu, video klip, lirik, foto artis), dan Copy Editor & Fact-Checker memeriksa semua naskah dan fakta.
Pastikan ke-38 spesialis benar-benar mendapat tugas. Beri waktu hidup run 6 jam.

FASE 4 — 8 kepala divisi, paralel
Minta setiap kepala divisi memeriksa hasil spesialisnya, memperbaiki atau mencatat kekurangan, lalu menulis laporan-<divisi>.md: deliverable per hari dan lokasinya, kontribusi tiap spesialis (satu baris per orang), risiko, dan keputusan yang dibutuhkan dari Founder.

FASE 5 — Kamu sendiri
Tulis program-pekan-1.md:
- Jadwal per hari dan per jam, Senin 16 sampai Minggu 22 November: apa terbit, di kanal mana, jam berapa, file mana, dan status hak cipta.
- Jadwal kerja agent harian selama pekan peluncuran.
- Daftar tugas manusia per hari (rekam VO, upload, kirim siaran pers, menghubungi artis, menyetujui iklan).
Tulis juga rapor-tim.md: kontribusi 8 divisi dan 38 spesialis, serta agent yang perlu perbaikan prompt.

ATURAN
- Tentang artis dan orang nyata: hanya fakta terverifikasi dan bersumber. Tidak ada gosip, spekulasi kehidupan pribadi, atau klaim yang bisa mencemarkan nama baik.
- Lagu, video klip, lirik, dan foto artis adalah karya berhak cipta: semua pemakaian harus dinilai Legal & Rights Compliance.
- Tidak ada yang dipublikasikan, dibayar, atau dikirim ke pihak luar (artis, media, calon mitra) tanpa persetujuan saya.
- Jangan mengarang data. Tandai [PERLU VERIFIKASI] dan catat data yang kamu butuhkan dari saya.
- Bila ada fase yang gagal atau terhenti, lanjutkan fase lain yang bisa jalan dan laporkan yang tertunda.

LAPORAN AKHIR UNTUK SAYA
1. Status kesiapan: SIAP / SIAP DENGAN CATATAN / BELUM SIAP, beserta alasannya.
2. Ringkasan program 7 hari (satu baris per hari).
3. Draf manifesto untuk saya setujui.
4. Keputusan yang harus saya ambil sebelum Senin pagi, masing-masing dengan opsi dan rekomendasimu.
5. Tugas yang harus saya kerjakan sendiri.
6. Bukti bahwa 47 agent bergerak: daftar 8 divisi dan 38 spesialis beserta file hasil masing-masing.
```

---

## Setelah prompt dikirim

- Di tampilan sesi akan muncul **thread** untuk 8 kepala divisi dan sebuah **workflow run** berisi
  thread-thread spesialis. Masing-masing bisa diklik untuk melihat pekerjaannya.
- Prosesnya bisa memakan waktu cukup lama. Biarkan berjalan.
- Kalau berhenti karena batas biaya, naikkan batasnya, lalu ketik: `Lanjutkan operasi dari fase yang tertunda.`
- Setelah laporan akhir keluar, setujui manifesto dan jawab keputusan yang diminta di sesi yang
  sama. CEO akan memperbarui program pekan 1.
