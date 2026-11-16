# Toples Produksi: Video Try-On Affiliate Rizlan

Template harian. Rizlan cukup kirim **foto produk pakaian**, lalu editor (Claude) menjalankan
alur di bawah ini tanpa perlu tanya ulang.

---

## 1. Aset tetap (sudah diupload ke Higgsfield)

| Aset | Keterangan | media_id Higgsfield |
|---|---|---|
| Rizlan A | Depan, tangan di saku (identitas utama) | `cef6e45a-ce12-41d9-9ffa-eb6c61a554e9` |
| Rizlan B | Depan, sudut kamera sedikit rendah | `3068ad92-4d97-4d51-983f-6a35b652b18a` |
| Rizlan C | Tampak belakang | `48877c9a-56a2-47ee-bcac-86c1678d12d6` |
| Rizlan D | Tampak samping kiri | `849c8e67-4d65-40ee-b8cb-46643c232a14` |
| Rizlan E | 3/4 badan, jam tangan terlihat | `33f0ecda-cda6-4756-ad02-27473106af35` |
| Produk #1 | Kemeja koko jacquard taupe, kerah shanghai | `bc7523d6-d68e-48eb-9a8f-dd64a0fb78b5` |

**Ciri tubuh yang dikunci (tidak boleh berubah):** pria muda Asia Tenggara, kulit sawo matang,
rambut hitam pendek disisir ke samping, kumis tipis dan janggut tipis di dagu, badan ramping
dan tinggi, smartwatch hitam di pergelangan **kiri**.

**Set lokasi (dari foto Rizlan):** dinding semen abu bertekstur, dua lampu dinding industrial
berkerangkeng yang menyala, pipa conduit hitam horizontal, tanaman philodendron besar di kanan,
lantai semen, ujung kursi besi putih di kanan bawah. Pencahayaan malam yang hangat dari lampu dinding.

> Catatan: foto "kamar" dan video Rizlan berjaket coklat belum diterima. Video yang terkirim
> identik dengan video contoh (kemeja putih). Jika foto kamar dikirim, ganti blok SET di prompt.

---

## 2. Aturan mix and match otomatis

| Jenis produk | Celana | Alas kaki | Inner | Aksesori |
|---|---|---|---|---|
| Kemeja koko / kerah shanghai (formal-santai) | Slacks hitam tapered, panjang semata kaki | Loafers kulit hitam | Tidak terlihat (kancing tertutup) | Smartwatch hitam |
| Kemeja casual / linen | Chino krem atau hitam | Sneakers putih minimalis | Kaos putih polos (jika kancing dibuka) | Smartwatch hitam |
| Kaos / polo | Celana kargo atau jogger netral | Sneakers putih atau slide hitam | — | Smartwatch hitam |
| Jaket / outer | Jeans biru gelap lurus | Sneakers putih atau boots coklat | Kaos polos senada | Smartwatch hitam |
| Celana (produk = celana) | — | Sesuai gaya celana | Kaos polos netral di atas | Smartwatch hitam |

Prinsip: warna pendamping netral (hitam, putih, krem, abu) supaya produk tetap jadi pusat perhatian.

---

## 3. Alur produksi (video 30 detik, rasio 9:16)

1. **Keyframe** (`gpt_image_2_6`, 9:16): Rizlan memakai produk di set lokasi. Buat 2 keyframe:
   K1 tampak depan dan K2 pose 3/4. Referensi: Rizlan A, C, D, E, lalu foto produk.
2. **Video** (`seedance_2_5`, `mode: omni_reference`, 720p, `generate_audio: false`):
   2 klip × 15 detik. Klip 1 memakai `start_image` K1, Klip 2 memakai `start_image` K2.
   `image_references`: Rizlan A, C, D dan foto produk.
3. **Gabung** dengan ffmpeg (hard cut, gaya try-on TikTok), output 30 detik dalam 1080×1920.
4. **Sound**: tambahkan sound trending langsung di aplikasi TikTok. Ini lebih baik untuk jangkauan
   dan aman dari masalah hak cipta.
5. **Label**: aktifkan "AI-generated content" saat posting.

**Biaya per video (cek 16 Nov 2026):** keyframe 0,25 kredit/gambar; klip Seedance 15 detik
720p = 105 kredit (1080p = 240). **Total per video 30 detik ≈ 211 kredit (720p).**

---

## 4. Bank gerakan (acak per video, jangan pakai kombinasi yang sama 2 kali)

Pilih 5 gerakan per klip. Setiap gerakan berdurasi sekitar 3 detik.

1. Menarik ujung bawah kemeja agar rapi sambil memindahkan berat badan ke satu kaki
2. Merapikan kerah dengan kedua tangan, melirik ke bawah, lalu kembali ke kamera
3. Mengusap placket kancing dari atas ke bawah dan menyentuh saku dada (tekstur kain tersorot lampu)
4. Badan berputar 3/4 ke kiri, tangan kiri masuk saku, menoleh ke kamera lewat bahu
5. Berputar 180° pelan untuk memperlihatkan punggung, jeda sebentar, lalu kembali ke depan
6. Membuka dan mengancingkan manset kiri sambil melihat smartwatch
7. Melangkah satu langkah ke kamera, mencubit kain di dada untuk memperlihatkan ketebalan
8. Kedua tangan di saku celana, pose santai dengan berat badan bergeser
9. Menyilangkan tangan di dada sambil tersenyum tipis percaya diri
10. Menggulung lengan kemeja sampai siku, lalu menurunkannya lagi
11. Merapikan rambut dengan satu tangan sambil melihat ke samping
12. Mengangguk kecil ke kamera dan menurunkan tangan ke sisi badan

Kunci agar gerakan tidak terlihat robot: sebut "real-time natural human motion, no slow motion",
ada jeda kecil dan pergeseran berat badan, napas natural, dan kain yang terlipat secara realistis.

---

## 5. Template prompt

### Keyframe (gpt_image_2_6)

```
Photorealistic smartphone photo, vertical 9:16. Use the man from reference images 1-4 exactly:
same face, same warm tan skin, same short black side-swept hair, same thin moustache and light
chin beard, same slim tall build, black smartwatch on his left wrist. He is wearing the garment
from the last reference image exactly: {DESKRIPSI_PRODUK}. Styled with {CELANA}, {ALAS_KAKI}.
{POSE}. SET: textured grey cement wall with two glowing caged industrial wall lamps, black
conduit pipe running along the wall, large philodendron plant on the right, cement floor, edge of
a white metal chair bottom right. Shot on iPhone on a tripod at chest height, warm night lighting
from the wall lamps, natural shadows, slight sensor noise, unedited, realistic skin texture.
No text, no mirror.
```

### Klip video (seedance_2_5)

```
Static iPhone on a tripod, vertical video, real-time natural human motion, no slow motion.
The man from the start frame records a casual TikTok outfit try-on of his {PRODUK_SINGKAT}.
0-3s: {GERAKAN_1}. 3-6s: {GERAKAN_2}. 6-9s: {GERAKAN_3}. 9-12s: {GERAKAN_4}. 12-15s: {GERAKAN_5}.
Small natural pauses, weight shifts and breathing between moves. Keep his face, hair, beard,
body proportions, smartwatch, shirt color, pattern and collar identical to the references the
whole time. Fabric creases and moves realistically under the warm wall-lamp light.
Same location throughout. No text, no captions, no mirror, no other people.
```

---

## 6. Prompt gaya video referensi (kemeja putih, 1 take, kamera diam)

Ciri video referensi: satu take tanpa cut, HP di tripod setinggi dada, framing kepala sampai
paha dengan sedikit plafon terlihat, cahaya ruangan apa adanya, gerakan santai sesuai beat musik,
lalu ditutup dengan tangan menyilang dan senyum.

### 6a. Keyframe (GPT Image 2.6 / Nano Banana Pro)
Referensi berurutan: Rizlan A, C, D, E, lalu foto produk.

```
Vertical 9:16 candid iPhone video frame, not a photoshoot. The man in reference images 1-4,
exactly the same person: same face shape, eyes, nose, lips, warm tan skin, short black side-swept
hair, thin moustache and light chin beard, same slim tall body, black smartwatch on his left
wrist. He wears the shirt from the last reference image exactly: {DESKRIPSI_PRODUK}, untucked,
slightly wrinkled like a real worn shirt. {CELANA}, {ALAS_KAKI}.
Framing: phone on a tripod at chest height, about 2 meters away, slightly wide lens, framed from
the top of his head to mid-thigh with a little ceiling visible above him. He stands relaxed facing
the camera, arms loose at his sides, calm expression with a hint of a smile.
SET: {SET}
Lighting: existing room light only, soft and uneven, no studio light, no rim light. Slight sensor
noise, mild phone sharpening, realistic skin texture with pores. No text, no watermark, no mirror.
```

SET A (lokasi Rizlan): `textured grey cement wall, two glowing caged industrial wall lamps, black conduit pipe along the wall, large philodendron plant on the right, cement floor.`
SET B (seperti referensi): `small lived-in apartment bedroom: tall dark-wood wardrobe on the left, beige wall, recessed ceiling downlight, cluttered desk on the right with a tablet, small items and an orange bag hanging on the wall.`

### 6b. Klip 1, detik 0-15 (meniru koreografi referensi)
Seedance 2.5: `omni_reference`, start_image = keyframe, image_references = Rizlan A, C, D +
produk, 9:16, 15 detik, `generate_audio: false`.

```
Vertical 9:16 TikTok outfit try-on, one continuous take, static phone on a tripod at chest
height, no camera movement, no cuts. Real-time natural human motion at normal speed, no slow
motion, no smooth gliding; small natural imperfections, weight shifts and breathing. The man from
the start frame casually shows off his shirt, relaxed and slightly shy-confident, like a real
creator who just pressed record.
0-1.5s: he is leaning in close toward the camera looking into the lens, then straightens up and
steps back into place.
1.5-3s: lets his arms settle, loosely clasps his hands in front of his waist and rubs them once.
3-5s: drops his hands, shifts his weight onto one leg, slides his left hand into his trouser
pocket with a slight turn of the torso.
5-7s: brings his right hand up and lightly touches the chest pocket and the button placket,
glancing down at the shirt.
7-9s: lifts both hands to the collar and adjusts it, then smooths the front of the shirt down.
9-11s: turns slowly to his right into side profile, hands loosely together in front, and keeps
turning until his back faces the camera, pausing so the back of the shirt is visible.
11-13s: turns back around toward the camera through a 3/4 angle.
13-15s: crosses his arms over his chest and gives a small confident smile, holding the pose.
Identity lock: face, hair, beard, body proportions, smartwatch on left wrist, shirt color,
pattern, collar and pocket identical to the references in every frame, including during the
turn. Fabric creases, folds and sways realistically. Same location and lighting throughout.
No text, no captions, no mirror, no other people, no morphing.
```

### 6c. Klip 2, detik 15-30 (lanjutan, gerakan berbeda)
Start_image = frame terakhir klip 1 (tangan menyilang), supaya sambungannya mulus.

```
Vertical 9:16 TikTok outfit try-on, one continuous take, same static tripod framing, location
and lighting as the start frame, no camera movement, no cuts. Real-time natural human motion at
normal speed, no slow motion; natural pauses, weight shifts and breathing.
0-3s: he uncrosses his arms, unbuttons his left cuff, glances at his smartwatch and buttons the
cuff again.
3-6s: takes one step closer to the camera, pinches the fabric at his chest and rubs it between
his fingers to show the texture, looking down at it.
6-9s: steps back to his spot, rolls his shoulders and tugs the hem of the shirt down to
straighten it.
9-12s: turns 3/4 to his left, puts his right hand in his trouser pocket and looks back at the
camera over his shoulder.
12-15s: turns to face the camera, both hands in his pockets, small nod and relaxed smile,
holding the final pose.
Identity lock: face, hair, beard, body proportions, smartwatch on left wrist, shirt color,
pattern, collar and pocket identical to the references in every frame. Fabric moves
realistically. No text, no captions, no mirror, no other people, no morphing.
```

### 6d. Negative prompt (untuk tools yang mendukung)
```
slow motion, robotic movement, stiff posture, floating or gliding, sudden jumps, morphing face,
changing hairstyle, changing shirt pattern or color, extra fingers, warped hands, plastic skin,
beauty filter, cinematic lighting, bokeh, camera movement, zoom, text, watermark, mirror
```

### 6e. Finishing agar mirip referensi
Gabung klip 1 + 2 tanpa transisi, potong tepat di beat musik. Export 720×1280 30 fps, tambah
grain tipis (sekitar 3%), tanpa color grading berlebihan. Sound trending ditambahkan di TikTok.

---

## 7. Collart Fashion (AI Fashion Video, motion transfer)

Alur: Step 1 Reference Video (sumber gerakan) → Step 2 Model (foto Rizlan) → Step 3 Clothing
(foto produk) → Step 4 Output Settings. Gerakan diambil dari video referensi, jadi prompt hanya
untuk fine-tuning: identitas, styling, kain, dan look kamera. Jangan menulis dialog atau ucapan.
Biaya sekitar 140 kredit per generate.

Prompt (Step 4):
```
Follow the reference video's body motion and timing exactly, real-time natural human movement, no slow motion, no stiff or robotic poses. Keep the model identical to the uploaded photo: same face, warm tan skin, short black side-swept hair, thin moustache and light chin beard, slim tall build, black smartwatch on his left wrist. He wears the uploaded garment exactly: {DESKRIPSI_PRODUK}, untucked. Styled with {CELANA} and {ALAS_KAKI}. Garment color, pattern and collar stay consistent in every frame, including the back view during the turn; fabric wrinkles and moves naturally. Static phone on a tripod at chest height, casual TikTok try-on look, natural indoor lighting, slight phone grain. No text, no mirror, no extra people, no distorted face or hands.
```

Custom Scene: upload foto lokasi kosong (tanpa orang) atau tulis:
```
Textured grey cement wall with two glowing caged industrial wall lamps, black conduit pipe along the wall, large philodendron plant on the right, cement floor, warm evening light from the lamps.
```

Settings: Background Music OFF (sound trending ditambahkan di TikTok), resolusi tertinggi.
Durasi mengikuti video referensi, jadi untuk 30 detik buat 2 generate dengan 2 video referensi
berbeda (≥15 detik), lalu gabung di CapCut.

---

## 8. Log produksi

| # | Tanggal | Produk | Gerakan klip 1 | Gerakan klip 2 | Status |
|---|---|---|---|---|---|
| 1 | 16-11-2026 | Kemeja koko jacquard taupe | 1, 2, 3, 4, 12 | 6, 5, 7, 8, 9 | Menunggu kredit Higgsfield |
