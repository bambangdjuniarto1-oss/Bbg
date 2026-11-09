# Prompt Produksi — Video Explainer "Omzet 50 Juta dari Cuci Sepatu"

Gaya: **hybrid motion graphic** = animasi 3D isometric / low-poly + talking head cutout.
Format: **vertikal 9:16 (1080×1920), 30 fps, durasi ±74 detik** (ngikutin durasi narasi mp3).

---

## 0. Bedah Gaya Video Referensi (wajib dibaca sebelum generate)

Hasil analisa frame-by-frame dari video referensi (lihat `referensi/sheet_01-03.jpg` dan `referensi/frame_detail.jpg`):

| Elemen | Detail |
|---|---|
| **Layout layar** | 25% atas = header polos abu-biru muda (`#E2ECEE`). 75% bawah = adegan 3D. Batas keduanya **di-fade halus** (scene 3D memudar ke warna header, bukan garis tegas). |
| **Talking head** | Foto asli host, **dipotong sebatas bahu (cutout, background dihapus)**, posisi kiri atas, ukuran kecil (±18% lebar layar). Nama host di bawahnya, font bold hitam kecil. Ekspresi berganti tiap kalimat (senyum, kaget, menjelaskan). |
| **Speech bubble** | Bubble putih rounded, outline hitam tipis, ekor mengarah ke host, **drop-shadow keras ke kanan-bawah**. Isi 2–3 kata kunci: teks hitam bold + **1 kata merah** (`#D7262E`). Contoh: "Jalan ada **kelasnya**". |
| **Gaya 3D** | Low-poly, **flat shading tanpa tekstur**, warna solid, pencahayaan siang lembut, bayangan tipis. Mirip "maket kota" / game mobile simulasi. |
| **Palet scene** | Atap merah bata `#C4442F` & biru baja `#4F7FA8`, rumput hijau `#4FA23E`, aspal abu `#585D61`, trotoar krem `#D8D5CE`, tembok pastel (krem, mint, pink salem), mobil warna primer (merah, kuning, biru, putih). |
| **Konteks lokal** | Jalanan Indonesia: ruko, warung, spanduk "PULSA / TOKEN", motor bebek, tiang listrik, pohon bulat low-poly. |
| **Kamera** | 3 jenis shot yang selalu diulang: **(1) drone/aerial miring 45°** yang melayang pelan, **(2) POV pengendara motor** (stang + speedometer kelihatan), **(3) street-level tracking** di depan bangunan. Gerakan kamera selalu halus, konstan, tidak ada cut kasar. |
| **Label 3D** | Pill tag warna solid (hijau / oranye / merah / ungu / biru) dengan judul KAPITAL bold + sub-judul kecil, ada garis penunjuk + titik bulat ke objek. Contoh: "PRIMER · JALAN BESAR". |
| **HUD / info panel** | Kotak gelap semi-transparan, rounded, teks putih kecil + angka kuning besar + progress bar. Contoh: "WAKTU MENOLEH 2,9 detik". |
| **Subtitle** | Tengah layar (±55% dari atas), font sans bold putih, **outline/shadow hitam**, 2–4 kata per baris, **kata kunci kuning** `#FFD43B`. Muncul per kata (word-by-word). |
| **Font** | Sans-serif geometris bold, mirip **Plus Jakarta Sans ExtraBold / Poppins Bold / Inter Bold**. |

> **Prinsip penting:** AI image/video generator lemah di teks & UI. Jadi **generate adegan 3D-nya BERSIH (tanpa teks, tanpa UI)**, lalu header, host cutout, bubble, label, HUD, dan subtitle **ditempel di editor** (CapCut / After Effects / Premiere). Begitu cara video referensi dibuat juga.

---

## 1. Naskah Narasi + Pembagian Adegan

Transkrip dari mp3 (diambil otomatis, cek ulang kata yang ditandai `*`):

| # | Waktu | Narasi | Bubble host | Kata kunci kuning (subtitle) |
|---|---|---|---|---|
| S01 | 0.0–6.4 | Omzet 50 juta sebulan dari cuci sepatu, bisa. Tapi pertanyaannya, | Omzet **50 juta**? | 50 juta, bisa |
| S02 | 6.4–11.0 | *ribuan pasang sepatu itu datangnya dari mana? | Datang dari **mana**? | dari mana |
| S03 | 11.0–15.5 | Kita hitung bareng ya, harga cuci satu pasang 30 ribu rupiah, | Hitung **bareng** | 30 ribu |
| S04 | 15.5–21.7 | biar tembus 50 juta kamu harus cuci sekitar 1.667 pasang sebulan. | **1.667** pasang | 1.667 pasang |
| S05 | 21.7–26.0 | Artinya sehari kamu butuh 55 pasang. | **55** sehari | 55 pasang |
| S06 | 26.5–31.3 | Kalau cuma nunggu orang datang ke satu toko, yaa, berat. | Cuma **nunggu**? | nunggu, berat |
| S07 | 31.3–35.0 | Nah, solusinya, gandeng laundry. | Gandeng **laundry** | gandeng laundry |
| S08 | 35.0–39.8 | Kenapa? Karena orang-orang yang males nyuci sepatu itu sebenernya sudah ada di sana, | Customer **sudah ada** | males, sudah ada |
| S09 | 39.8–43.4 | laundry sudah punya customer, kamu tinggal bikin sistem kerja samanya. | Bikin **sistem** | sistem kerja sama |
| S10 | 43.4–49.0 | Kasih harga khusus buat laundry mitra, mereka untung dari selisih harga, | Harga **mitra** | harga khusus, selisih |
| S11 | 49.0–53.2 | kamu dapat tambahan order, tanpa harus nunggu orang datang ke toko. | **Order** ngalir | tambahan order |
| S12 | 53.7–58.4 | Bayangin, kalau ada beberapa laundry mitra yang kirim sepatu setiap hari, | Mitra **tiap hari** | setiap hari |
| S13 | 58.4–61.5 | target 55 pasang itu jadi masuk akal. | Jadi **masuk akal** | masuk akal |
| S14 | 61.5–65.2 | Jadi, jangan cuma mikirin gimana dapetin customer, | Bukan cuma **customer** | dapetin customer |
| S15 | 65.2–68.8 | pikirin juga gimana bangun sistem yang bikin customer datang terus. | Bangun **sistem** | datang terus |
| S16 | 68.8–74.2 | Follow buat insight bisnis lainnya, dengan hitungan yang nyata. | **Follow** ya! | follow, nyata |

---

## 2. MASTER STYLE PROMPT (dipakai di SEMUA prompt)

Copy blok ini dan tempel di awal/akhir setiap prompt gambar & video supaya gayanya konsisten.

```
STYLE LOCK: low-poly 3D isometric diorama of an Indonesian neighborhood, flat shading,
no textures, solid matte colors, clean simple geometry like a mobile city-builder game,
soft bright midday lighting, gentle ambient occlusion, very soft short shadows,
pale blue-grey sky (#E2ECEE), red-brick (#C4442F) and steel-blue (#4F7FA8) hip roofs,
bright green grass (#4FA23E), grey asphalt roads (#585D61) with white dashed lines,
cream sidewalks, pastel walls (cream, mint, salmon pink), rounded low-poly trees,
small blocky cars in primary colors, Indonesian shophouses (ruko), warung, motorbikes,
power poles. Clean, friendly, educational explainer look. Vertical 9:16 composition,
top 25% of frame kept as empty pale sky / soft fade for UI overlay.
```

**Negative prompt** (untuk tool yang mendukung):

```
photorealistic, realistic textures, film grain, noise, dark moody lighting, night,
heavy shadows, bloom, lens flare, depth of field blur, cartoon outlines, cel-shading lines,
anime, clay, plastic gloss, text, letters, watermark, logo, subtitles, UI, distorted
geometry, warped buildings, extra wheels, melting objects, fisheye, shaky camera
```

---

## TAHAP 1 — MOODBOARD (GAMBAR)

**Tool rekomendasi:** Midjourney v7 / Nano Banana (Gemini) / GPT-Image / Flux.
**Wajib:** upload `referensi/sheet_01.jpg` + `referensi/frame_detail.jpg` sebagai **style reference** (Midjourney: `--sref`; Nano Banana/GPT: lampirkan gambar + tulis "match the visual style of the attached reference exactly").
Rasio: `--ar 9:16` (kecuali moodboard sheet).

### 1A. Moodboard Board Utama (1 gambar ringkasan gaya)

```
A professional motion design moodboard sheet on a clean light-grey background,
arranged as a neat grid of 9 vertical 9:16 thumbnails plus a color palette strip and
a typography sample. Thumbnails show: (1) aerial 45-degree drone view of a low-poly
Indonesian neighborhood with a small shoe-cleaning shop, (2) street-level view of the
shoe-cleaning shop front with sneaker racks, (3) POV from a motorbike rider with
handlebar and round speedometer visible on a low-poly street, (4) a laundry shop next
door with customers dropping bags, (5) aerial view with glowing route lines connecting
several laundries to one shoe shop, (6) close-up of a stack of colorful sneakers,
(7) delivery scooters carrying shoe bags on a road, (8) a shop owner waiting alone at
an empty counter, (9) wide establishing shot of the whole town at noon.
Color palette chips: #E2ECEE, #C4442F, #4F7FA8, #4FA23E, #585D61, #D8D5CE, #FFD43B, #D7262E.
[STYLE LOCK]
--ar 16:9 --sref [link referensi] --stylize 100
```

### 1B. Character Sheet Host (talking head cutout)

> Talking head **pakai foto asli host lo**, bukan AI. Rekam video host (dada ke atas, background polos, lighting rata) sambil lip-sync narasi, lalu hapus background (CapCut "Remove Background" / Runway "Remove Background"). Kalau mau stok ekspresi dari foto, pakai prompt edit ini di Nano Banana / GPT-Image dengan foto host sebagai input:

```
Using the attached photo of this person, create a character expression sheet:
6 head-and-shoulders cutouts of the SAME person, identical face, hair and outfit,
on a pure white background, soft even studio light, slight 3/4 angle facing right.
Expressions: friendly smile, curious raised eyebrow, surprised "wow", explaining with
open mouth, confident nod, pointing gesture near face. Clean edges, no background
objects, no text. Keep the face 100% faithful to the photo.
```

### 1C. UI Kit Sheet (bubble, label, HUD, subtitle)

> Untuk referensi desain doang — versi final tetap dibikin di editor biar teksnya rapi.

```
Flat UI kit sheet for a vertical explainer video, on pale blue-grey background #E2ECEE:
(a) white rounded-rectangle speech bubble with thin black outline, small tail pointing
left, hard black drop shadow offset bottom-right, bold black sans-serif text with one
word in red #D7262E; (b) pill-shaped 3D map labels in solid green, orange, purple, blue
and red, bold white uppercase title with small subtitle and a thin pointer line ending
in a white circle; (c) dark semi-transparent rounded HUD panel with small white caption,
big yellow number and a yellow progress bar; (d) bold white subtitle text with black
outline, one keyword in yellow #FFD43B. Font style: Plus Jakarta Sans ExtraBold.
Clean vector, crisp, centered layout.
--ar 16:9
```

### 1D. Key Frame per Adegan (16 gambar, 9:16)

Format tiap prompt: `[deskripsi adegan] + [STYLE LOCK] --ar 9:16 --sref [referensi]`

| # | Prompt key frame |
|---|---|
| **S01** | Street-level view of a small modern shoe-cleaning shop (Indonesian ruko) with a bright red awning, glass front, wall racks full of colorful clean sneakers, a cleaning counter with brushes and spray bottles, a low-poly shop owner in apron, a motorbike parked in front, slight low angle making the shop look promising. |
| **S02** | High aerial 45-degree drone view pulling back from the same shoe-cleaning shop, revealing a dense low-poly neighborhood grid of red and blue roofs, roads and tiny cars; the shop is small in the center; several empty map-pin markers floating above random houses. |
| **S03** | Close-up of one pair of white sneakers on a wooden cleaning counter, half dirty half sparkling clean, cleaning brush and foam beside it, empty floating price-tag shape above (no text), shop interior softly in background. |
| **S04** | Huge stack of hundreds of colorful sneakers piling up like a small mountain in front of the shoe shop, stacked boxes and pairs filling the street, camera slightly above, sense of overwhelming quantity. |
| **S05** | Interior of the shoe shop: one long shelf wall exactly filled with neat rows of sneaker pairs (around 55 pairs), a wall calendar showing one day highlighted, morning light. |
| **S06** | Lonely shop owner sitting behind the counter of the shoe shop, chin on hand, empty street outside, a wall clock, a few leaves blowing, muted calm mood but same bright palette, wide static shot. |
| **S07** | Street-level shot: the shoe shop next to a busy laundry shop (blue awning, washing machines visible through glass), two low-poly shop owners shaking hands in front between both shops. |
| **S08** | Inside view of the laundry shop: many low-poly customers dropping off bags of clothes, some bags with sneakers poking out, washing machines, folding table, queue at counter. |
| **S09** | Aerial 45-degree view of a neighborhood showing one laundry shop and the shoe shop a few blocks apart, a thick glowing yellow dashed route line drawn on the road connecting them. |
| **S10** | Laundry counter close-up with a stack of shoe bags labeled with blank tags, a low-poly laundry owner smiling holding a small stack of cash, two blank floating price panels hovering (no text). |
| **S11** | POV from a delivery motorbike rider: handlebar and round speedometer visible in foreground, a bag of sneakers strapped on the front, riding on a low-poly street toward the shoe shop ahead. |
| **S12** | High aerial view of the whole town: 4–5 laundry shops highlighted with colored pins, small delivery scooters riding along roads, glowing route lines from each laundry converging into the central shoe shop. |
| **S13** | Shoe shop at full capacity: shelves completely full of clean sneakers, owner happily packing pairs into bags, a green checkmark-shaped light floating above, bright cheerful. |
| **S14** | Street-level: shoe shop owner standing at the door looking left and right at the street, waiting for walk-in customers, a few pedestrians passing by. |
| **S15** | Wide aerial golden-midday timelapse feeling: continuous loop of scooters arriving and leaving the shoe shop from multiple laundries, route lines pulsing, busy but organized. |
| **S16** | Final establishing shot: slow pull-back high above the entire low-poly town, shoe shop and partner laundries visible with small pins, lots of empty pale sky at top for the call-to-action overlay. |

**Checklist lolos Tahap 1** sebelum lanjut ke video:
- [ ] Semua key frame warna & tingkat low-poly-nya seragam (jejerin 16 gambar, cek tidak ada yang "realistis" sendiri).
- [ ] 25% atas tiap frame cukup kosong buat header + host.
- [ ] Bangunan toko cuci sepatu & laundry **desainnya sama** di semua adegan (pakai gambar S01 & S07 sebagai referensi tambahan untuk adegan lain).

---

## TAHAP 2 — RENDERING VIDEO

**Tool rekomendasi:** Kling 2.x / Veo 3 / Hailuo (MiniMax) / Runway Gen-4 — mode **image-to-video**.
**Input:** key frame dari Tahap 1D sebagai *first frame*. Durasi klip 5 detik (potong/perpanjang di editor). **Matikan audio bawaan generator** (narasi pakai mp3 final).

### 2A. Template prompt video

```
[GERAKAN KAMERA]. [AKSI DI DALAM ADEGAN]. Smooth, steady, constant-speed camera
motion, no cuts, no shake. Keep the low-poly flat-shaded style, colors and geometry
exactly as the first frame. Objects stay solid and do not morph. No text, no UI.
Vertical 9:16.
```

### 2B. Prompt per adegan

| # | Durasi | Prompt video (image-to-video) |
|---|---|---|
| **S01** | 6.4 dtk | Slow dolly-in toward the shoe shop front. The shop owner brushes a sneaker on the counter, a motorbike passes in the foreground left to right. |
| **S02** | 4.6 dtk | Camera rises and pulls back from the shop into a high 45-degree aerial view, revealing the whole neighborhood; tiny cars drive along the roads; map pins gently bob up and down. |
| **S03** | 4.5 dtk | Slow orbit 20 degrees around the sneaker on the counter; the brush sweeps once and the dirty half turns clean with a small sparkle. |
| **S04** | 6.2 dtk | Camera tilts up slowly while sneakers keep dropping from above and stacking into a growing pile until it towers over the shop. |
| **S05** | 4.3 dtk | Smooth lateral tracking shot along the shelf as sneaker pairs pop into place one by one, filling every slot. |
| **S06** | 4.8 dtk | Almost static shot with very slow push-in; the clock hand moves fast, the owner sighs and taps the counter, leaves drift across the empty street. |
| **S07** | 3.7 dtk | Fast but smooth whip-pan from the shoe shop to the laundry next door, then settle on the two owners shaking hands. |
| **S08** | 4.8 dtk | Slow dolly through the laundry; customers walk in and drop bags on the counter, washing machines spin. |
| **S09** | 3.6 dtk | Slow aerial glide; a yellow dashed route line draws itself along the road from the laundry to the shoe shop. |
| **S10** | 5.6 dtk | Gentle push-in on the laundry owner; the owner counts the cash and smiles, two floating panels slide in from the sides. |
| **S11** | 4.2 dtk | First-person motorbike ride forward along the street at steady speed, handlebar slightly swaying, speedometer needle rising, shoe shop approaching. |
| **S12** | 4.7 dtk | High aerial slow rotation clockwise; scooters ride from every laundry along glowing route lines into the central shoe shop. |
| **S13** | 3.1 dtk | Quick smooth push-in; the last empty shelf slot fills, the owner raises both hands happily, green light pulse. |
| **S14** | 3.7 dtk | Static street-level shot; owner looks left and right at the door, pedestrians walk past without entering. |
| **S15** | 3.6 dtk | Aerial slow crane-up; continuous stream of scooters coming and going, route lines pulsing in a loop. |
| **S16** | 5.4 dtk | Slow, long pull-back high above the town until it becomes a small diorama in the lower 70% of the frame, pale sky fills the top. |

> Gerakan khas referensi yang **wajib ada**: minimal 4 shot aerial drone (S02, S09, S12, S15/S16), minimal 1 shot POV motor (S11), sisanya street-level tracking.

### 2C. Compositing di Editor (CapCut / After Effects)

Urutan layer dari bawah ke atas:

1. **Klip 3D** (S01–S16) — sambung dengan cut biasa atau *cross-dissolve 6 frame*. Sinkronkan ke timestamp tabel di bagian 1.
2. **Gradient fade** — persegi `#E2ECEE` menutup 25% atas, bagian bawahnya gradient ke transparan (tinggi gradient ±8% layar).
3. **Host cutout** — kiri atas, x≈12%, y≈11%, lebar ±18%. Ganti ekspresi/klip tiap adegan. Nama host di bawahnya (bold 28px, hitam).
4. **Speech bubble** — di kanan host, teks dari kolom "Bubble host". Animasi masuk: *scale 80%→100% + bounce*, 8 frame.
5. **Label 3D & HUD panel** — tempel di atas objek (pakai *motion tracking* kalau kamera bergerak). Isi yang disarankan:
   - S01: HUD "OMZET / BULAN — **Rp 50 jt**"
   - S03: label oranye "HARGA CUCI · **Rp 30.000 / pasang**"
   - S04: HUD counter animasi 0 → **1.667 pasang / bulan**
   - S05: HUD "TARGET HARIAN — **55 pasang**" + progress bar
   - S07: label hijau "LAUNDRY · MITRA" & label merah "TOKO CUCI SEPATU"
   - S10: dua panel "HARGA MITRA" / "HARGA PASAR" + label "SELISIH = UNTUNG MITRA" (isi angka sesuai harga riil lo)
   - S12: label pill di tiap laundry: "MITRA 1 … MITRA 5"
   - S13: HUD progress bar penuh "**55 / 55** ✔" (hijau)
   - S16: bubble "**Follow** ya!" + tombol follow animasi
6. **Subtitle** — tengah (y≈55%), Plus Jakarta Sans ExtraBold 64–72px, putih, stroke hitam 6px, kata kunci kuning `#FFD43B`, animasi muncul per kata (CapCut: Auto Caption → style "word highlight").
7. **Audio** — narasi mp3 final (volume 100%) + musik latar lo-fi/upbeat ringan (−22 dB) + SFX kecil: *pop* saat bubble/label muncul, *whoosh* saat kamera pindah, *ding* di S13.

### 2D. Export

- 1080×1920, 30 fps, H.264, bitrate 12–16 Mbps, audio AAC 320 kbps.
- Cek *safe zone* TikTok/Reels: jangan taruh subtitle/teks penting di 15% paling bawah & 8% paling kanan.

---

## 3. Tips Biar Hasilnya Mirip Referensi

1. **Konsistensi > kerumitan.** Selalu pakai *STYLE LOCK* + gambar referensi yang sama di setiap generate.
2. **Kunci bangunan utama.** Setelah dapat desain toko cuci sepatu & laundry yang pas, jadikan gambar itu referensi untuk semua adegan berikutnya.
3. **Jangan minta teks ke AI.** Semua teks di layar dibuat di editor.
4. **Generate 3–4 variasi per adegan**, ambil yang geometrinya paling stabil (tidak meleleh/berubah bentuk).
5. **Kamera pelan.** Gerakan cepat bikin model video merusak low-poly-nya; di video referensi semua gerakan kamera lambat & konstan.
6. Alternatif kalau mau 100% konsisten: bangun kotanya sekali di **Blender** pakai asset low-poly (mis. Kenney City Kit / Synty Polygon City), lalu animasikan kamera sendiri — ini cara paling mungkin dipakai video referensi aslinya.
