# Prompt Instruksi Pertama — Menjalankan Bisnis

Ada dua cara memakai prompt di file ini:

- **Cara A (disarankan):** kirim **Prompt Utama** ke agent **CEO**. CEO akan membagi tugas ke 8 divisi
  dalam satu sesi.
- **Cara B:** jalankan sesi **langsung ke agent divisi**, misalnya untuk menguji satu divisi atau saat
  CEO belum siap. Pakai prompt per divisi di bagian 2.

Sebelum mengirim, ganti semua `[...]`. Bagian yang tidak Anda ketahui boleh dikosongkan; agent
diminta mencatatnya sebagai "data yang dibutuhkan dari Founder".

---

## 1. PROMPT UTAMA — untuk CEO / AI Company Director

Kirim di **Sesi** baru (agen: CEO, lingkungan: `media-hq`, memori: `brand-bible`).

```
Halo CEO. Ini instruksi pertama dari Founder. Hari ini kita resmi mulai menjalankan perusahaan dengan tim AI.

PROFIL PERUSAHAAN
- Nama: [NAMA PERUSAHAAN]
- Bidang: media musik, film, lifestyle, seni & budaya (Indonesia)
- Kondisi saat ini: [contoh: baru mulai / sudah punya akun IG 5.000 followers dan channel YouTube 1.000 subscriber]
- Kanal aktif: [Instagram, TikTok, YouTube, Spotify, website, newsletter]
- Tim manusia: [contoh: Founder + 1 editor video freelance]
- Anggaran operasional bulanan: Rp[...]
- Target 90 hari: [contoh: 10.000 followers baru, 3 seri konten tetap, 1 sponsor pertama]

TUGASMU: susun "RENCANA PELUNCURAN 30 HARI" dengan melibatkan semua divisi.

Tahap 1 (paralel):
1. Research & Intelligence: peta tren 30 hari ke depan (rilis musik, film tayang, festival, pameran, tren lifestyle), 3 persona audiens, dan 5 media kompetitor beserta celah yang bisa kita isi.
2. Finance & Operation: kerangka anggaran bulanan per divisi berdasarkan anggaran di atas, SOP alur produksi konten (ide → terbit), dan checklist hak cipta (musik, cuplikan film, foto).
3. Technology & Automation: daftar pekerjaan berulang yang bisa diotomasi minggu ini dan alat yang dibutuhkan.

Tahap 2 (setelah hasil Research tersedia):
4. Editorial & Strategy: 4 pilar konten, 3 seri/program tetap (nama, format, frekuensi), dan kalender editorial 30 hari.
5. Community & Audience: konsep komunitas, rencana newsletter mingguan, dan panduan komunitas.
6. Business & Monetization: 3 model pendapatan paling realistis untuk 90 hari pertama, 10 calon brand/sponsor yang cocok beserta alasannya, dan draf media kit.

Tahap 3 (setelah kalender editorial tersedia):
7. Creative & Production: konsep kreatif dan naskah untuk 3 konten pertama dari kalender, plus panduan visual sederhana.
8. Distribution & Growth: rencana distribusi per platform (frekuensi, jam tayang, format), caption dan judul SEO untuk 3 konten pertama, dan target pertumbuhan per kanal.
9. Finance & Operation: cek hak cipta untuk 3 konten pertama (HIJAU/KUNING/MERAH).

ATURAN
- Setiap divisi menyimpan hasilnya di /mnt/session/outputs/<nama-divisi>/.
- Jangan mengarang data. Tandai [PERLU VERIFIKASI] untuk yang belum pasti, dan catat data apa yang kamu butuhkan dari saya.
- Tidak ada yang dipublikasikan, dibayar, atau dikirim ke pihak luar tanpa persetujuan saya.

YANG SAYA TERIMA DI AKHIR
1. Ringkasan eksekutif (maks. 1 halaman).
2. Rencana Peluncuran 30 Hari: per minggu, siapa mengerjakan apa.
3. Daftar keputusan yang harus saya ambil, masing-masing dengan opsi dan rekomendasimu.
4. Daftar data/akses yang kamu butuhkan dari saya.
5. Daftar semua file hasil kerja divisi.
```

---

## 2. PROMPT PER DIVISI — instruksi pertama (Cara B)

Pakai bila menjalankan sesi langsung ke agent divisi. Isi `[KONTEKS]` dengan blok PROFIL
PERUSAHAAN dari Prompt Utama di atas.

### Research & Intelligence
```
[KONTEKS]
Instruksi pertama: buat "Intelligence Brief #1" untuk perusahaan kita.
1. Kalender 30 hari ke depan: rilis musik penting, film tayang di bioskop & streaming, festival, konser, pameran seni, momen lifestyle (hari besar, musim).
2. 10 tren yang sedang naik di musik, film, lifestyle, seni (Indonesia), masing-masing dengan bukti dan sumber.
3. 3 persona audiens: usia, kebiasaan konsumsi media, platform favorit, apa yang mereka cari.
4. 5 media kompetitor/sejenis: kekuatan, kelemahan, dan celah yang bisa kita isi.
5. 10 ide konten yang paling berpeluang, diurutkan berdasarkan potensi.
Bedakan FAKTA, DUGAAN, dan TIDAK DIKETAHUI. Simpan ke /mnt/session/outputs/research/brief-01.md.
```

### Editorial & Strategy
```
[KONTEKS]
Instruksi pertama: bangun fondasi editorial.
1. Pernyataan misi editorial (1 paragraf) dan 5 prinsip suara brand, dengan contoh "begini / bukan begini".
2. 4 pilar konten (musik, film, lifestyle, seni & budaya) beserta porsinya.
3. 3 seri/program tetap: nama, format, durasi, frekuensi, dan contoh 4 episode pertama.
4. Kalender editorial 30 hari dalam tabel: tanggal | pilar | topik | angle | format | kanal utama.
5. Style guide singkat: ejaan, penulisan nama/judul karya, aturan kutipan, label konten bersponsor.
Simpan ke /mnt/session/outputs/editorial/.
```

### Creative & Production
```
[KONTEKS]
Instruksi pertama: siapkan identitas kreatif dan template produksi.
1. Panduan visual sederhana: palet warna, tipografi, gaya foto/video, gaya thumbnail.
2. Template naskah video dalam tabel: No | Durasi | Voice-over | Visual | Teks layar | Musik/SFX.
3. Tiga template format: video pendek 30–60 detik (Reels/TikTok), video YouTube 5–8 menit, dan carousel 7 slide.
4. Naskah lengkap untuk 1 contoh video 60 detik dengan topik [TOPIK atau "ulasan film lokal yang sedang tayang"].
5. Daftar kebutuhan aset dan sumber legal untuk musik, footage, dan font.
Simpan ke /mnt/session/outputs/creative/.
```

### Distribution & Growth
```
[KONTEKS]
Instruksi pertama: buat strategi distribusi dan pertumbuhan 90 hari.
1. Peran tiap kanal (mis. TikTok untuk jangkauan, YouTube untuk kedalaman, newsletter untuk loyalitas).
2. Frekuensi posting dan jam tayang yang disarankan per kanal, dengan alasannya.
3. Sistem repurposing: dari 1 konten utama menjadi berapa turunan, untuk kanal apa saja.
4. Panduan caption, hashtag, dan judul SEO, dengan 5 contoh.
5. Target per kanal untuk hari ke-30, ke-60, dan ke-90, serta 3 eksperimen pertumbuhan pertama.
6. Usulan iklan berbayar (opsional): tujuan, target, anggaran, KPI. Ini hanya usulan.
Simpan ke /mnt/session/outputs/growth/.
```

### Business & Monetization
```
[KONTEKS]
Instruksi pertama: petakan jalur pendapatan.
1. Daftar semua model pendapatan yang mungkin (branded content, sponsorship seri, event, lisensi, merchandise, membership, ad revenue), lalu nilai masing-masing: potensi, waktu sampai menghasilkan, usaha, dan risiko.
2. Rekomendasi 3 model prioritas untuk 90 hari pertama.
3. 10 calon brand/sponsor yang cocok dengan audiens kita, beserta alasan dan ide kolaborasinya.
4. Draf media kit: profil, audiens, kanal, paket kerja sama (harga ditandai [PERLU PERSETUJUAN FOUNDER]).
5. Daftar 15 musisi, sineas, atau seniman potensial untuk kolaborasi atau wawancara.
Jangan mengirim apa pun ke pihak luar. Simpan ke /mnt/session/outputs/business/.
```

### Technology & Automation
```
[KONTEKS]
Instruksi pertama: rancang "mesin" operasional.
1. Petakan alur kerja dari ide sampai terbit, lalu tandai langkah yang bisa diotomasi.
2. Daftar alat yang dibutuhkan (penjadwal posting, penyimpanan aset, dashboard data, CMS), dengan opsi gratis dan berbayar.
3. Rencana jadwal otomatis agent (harian, mingguan, bulanan) beserta prompt-nya.
4. Struktur folder dan aturan penamaan file untuk semua divisi.
5. Checklist keamanan: pengelolaan kunci API di Brankas kredensial, data pribadi audiens (UU PDP), dan siapa yang menyetujui apa.
Simpan ke /mnt/session/outputs/tech/.
```

### Finance & Operation
```
[KONTEKS]
Instruksi pertama: siapkan fondasi keuangan, operasi, dan hukum.
1. Kerangka anggaran bulanan per divisi berdasarkan anggaran Rp[...], termasuk perkiraan biaya API Claude, alat, dan freelancer.
2. Template pelacakan biaya dan ROI per program/sponsor.
3. SOP produksi: tahapan, penanggung jawab, waktu standar, dan titik persetujuan Founder.
4. Checklist hak cipta & risiko: musik, cuplikan film, foto, logo, kutipan, wajah orang, konten bersponsor, dengan sistem HIJAU/KUNING/MERAH (rujukan: UU 28/2014 Hak Cipta, UU ITE, UU PDP, aturan platform).
5. Template brief dan draf perjanjian kerja freelancer (tandai: wajib ditinjau pengacara).
Simpan ke /mnt/session/outputs/finance-ops/.
```

### Community & Audience
```
[KONTEKS]
Instruksi pertama: rancang komunitas.
1. Konsep komunitas: nama, identitas, nilai, dan platform utama (Discord / Telegram / WA Channel), dengan alasannya.
2. Program rutin 30 hari pertama (diskusi, listening session, nonton bareng, tantangan UGC).
3. Konsep newsletter mingguan: nama, struktur rubrik, dan contoh edisi pertama.
4. Konsep membership berjenjang (gratis dan berbayar) beserta benefitnya.
5. Panduan komunitas dan 10 template balasan moderasi.
Simpan ke /mnt/session/outputs/community/.
```

---

## 3. PROMPT RUTIN — setelah peluncuran

Pasang di menu **Penerapan** (jadwal otomatis) atau kirim manual.

| Kapan | Agen | Prompt |
|---|---|---|
| Setiap hari 08.00 WIB | Research & Intelligence | `Buat ringkasan tren hari ini (musik, film, lifestyle, seni) dan 3 ide konten cepat. Simpan ke /mnt/session/outputs/research/harian-<tanggal>.md.` |
| Senin 07.00 WIB | CEO | `Susun rencana kerja minggu ini: minta Intelligence Brief terbaru dari Research, perbarui kalender bersama Editorial, siapkan produksi bersama Creative, rencana distribusi bersama Growth, dan cek hak cipta bersama Finance & Operation. Berikan daftar tugas per divisi dan keputusan yang saya perlukan.` |
| Rabu 13.00 WIB | Business & Monetization | `Perbarui pipeline sponsor & kolaborasi: status tiap calon mitra, 3 peluang baru, dan langkah berikutnya. Jangan mengirim apa pun ke pihak luar.` |
| Jumat 16.00 WIB | CEO | `Buat laporan mingguan untuk Founder: apa yang terbit, performa (minta Research mengolah data yang saya unggah), pengeluaran, masalah, keputusan yang dibutuhkan, dan prioritas minggu depan.` |
| Tanggal 1 setiap bulan | CEO | `Buat evaluasi bulanan: capaian vs target 90 hari, divisi yang perlu diperbaiki, usulan perubahan prompt atau model untuk agent, dan rencana bulan depan.` |
