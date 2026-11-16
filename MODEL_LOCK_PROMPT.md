# Prompt Model Terkunci: Foto Produk Affiliate

Cara pakai: upload **Image 1 = foto model tetap**, **Image 2 = foto produk**. Copy MASTER PROMPT,
isi `{PRODUK}` dan `{STYLING}`, lalu tempel satu blok `{GAYA}` sesuai keyword.
Rekomendasi tools: Nano Banana Pro, GPT Image 2.6, atau Seedream 4.5 (mode edit dengan referensi), rasio 9:16 atau 3:4.

Tips: crop foto produk sampai hanya bajunya saja (buang teks promo, model lain, dan properti).
Hasilnya akan jauh lebih akurat.

---

## MASTER PROMPT

```
REFERENCES: Image 1 is the model, the only source for the person's identity and body. Ignore Image 1's clothing, background and lighting. Image 2 is the product, the only source for the garment. Ignore any text, logos, watermarks, other people, props and background in Image 2.

MODEL LOCK (must stay identical to Image 1, do not beautify or alter): Southeast Asian man in his late 20s, warm medium-tan skin with natural texture and visible pores, oval face with a defined jawline and slightly prominent cheekbones, thick straight dark eyebrows, dark brown almond-shaped eyes with a calm gaze, slightly rounded nose, medium lips, very light stubble on the upper lip and chin. Short black hair: tapered short sides, longer top neatly combed back and swept to the side with a side part and a soft wave. Athletic build, broad shoulders, defined arms and forearms, about 175 cm tall, same body proportions and hand shape as Image 1. No jewelry unless stated in STYLING. Same face in every angle; no age, weight, skin tone or hairstyle change.

PRODUCT (reproduce exactly from Image 2): {PRODUK}. Keep the exact color, fabric, thickness, fit, length, neckline, sleeve length, seams and details; true-to-life drape on his body with natural folds; no added logos, prints or text.

STYLING: {STYLING}

STYLE: {GAYA}

PHOTO QUALITY: photorealistic, real camera photo, natural skin texture, accurate fabric texture, correct hands with five fingers, realistic shadows that match the light source, sharp focus on the outfit, no text, no watermark, no frame, no collage.

AVOID: different face, different hairstyle, full beard, plastic or airbrushed skin, cartoon or CGI look, distorted hands or fingers, extra limbs, wrong garment color, changed garment design, logos or text on clothes, oversaturated colors, warped background.
```

---

## Blok PRODUK (contoh: FORMLOCK Oversized)

```
oversized heavyweight crew-neck T-shirt in off-white (very light warm grey), thick smooth structured cotton fabric that holds its boxy shape with minimal wrinkles, dropped shoulders, wide short sleeves ending just above the elbow, thick ribbed round neckline, straight hem ending at the hip, plain with no print or logo
```

## Aturan STYLING otomatis

| Produk | STYLING |
|---|---|
| Kaos oversized / boxy | black relaxed straight-leg trousers, clean white minimalist leather sneakers |
| Kaos fitted / long sleeve | dark indigo slim straight jeans, white sneakers |
| Kemeja / koko | black tapered ankle-length trousers, black leather loafers |
| Polo / knit | beige chino trousers, brown suede loafers |
| Jaket / outer | plain white crew-neck tee underneath, black straight jeans, white sneakers |
| Celana (produk = celana) | plain fitted crew-neck tee in a neutral color matching the pants, white sneakers |
| Sepatu (produk = sepatu) | plain black oversized tee, black relaxed trousers cropped at the ankle to show the shoes |

Keyword gaya boleh mengubah styling (lihat catatan di setiap blok GAYA).

---

## Keyword GAYA

**COKLAT** (seperti foto model)
```
warm terracotta-brown studio wall with classic wainscoting panel molding, fluffy white shag rug on the floor, soft bright frontal studio lighting with gentle shadows, clean commercial fashion catalog, framed from head to mid-thigh, standing slightly angled to the camera with hands loosely clasped in front of his waist, calm confident expression, 85mm lens, vertical 9:16
```

**STUDIO** (gelap, spotlight)
```
dark charcoal seamless studio backdrop with a soft warm circular spotlight glow behind him, moody editorial fashion catalog, full body from head to shoes, standing relaxed with hands in pockets and one leg crossed in front, low-key lighting with soft key light from the front-left, 85mm lens, vertical 9:16
```

**KATALOG** (e-commerce bersih)
```
clean light grey seamless studio background, bright soft even lighting with no harsh shadows, e-commerce product catalog photo, full body front view standing straight and relaxed, arms naturally at his sides, 50mm lens, vertical 3:4
```

**KAMAR** (try-on santai, gaya TikTok)
```
cozy lived-in bedroom with a wooden wardrobe, beige wall and a desk in the background, casual outfit try-on, shot on an iPhone on a tripod at chest height, framed from head to mid-thigh, he adjusts the hem of the garment and looks at the camera with a slight smile, warm indoor ambient light, slight phone grain, vertical 9:16
```

**STREET**
```
urban city sidewalk with modern shop fronts and soft background bokeh, golden hour sunlight from the side, streetwear lookbook, full body walking mid-stride toward the camera with a relaxed confident expression, 35mm lens at waist height, vertical 9:16
```

**CAFE**
```
minimalist coffee shop with light wood tables, concrete wall and large windows, soft natural window light, he stands leaning casually against the counter holding an iced coffee, lifestyle photo, framed from head to knees, 50mm lens, vertical 4:5
```

**MALL**
```
bright modern shopping mall corridor with glass storefronts and polished floor, soft overhead lighting, casual weekend OOTD, full body standing three-quarter to the camera with one hand in his pocket, 35mm lens, vertical 9:16
```

**MALAM** (night city)
```
city street at night with neon signs and warm street lamps, light reflections on wet asphalt, cinematic but realistic night photo, full body standing with hands in pockets looking slightly off camera, soft neon rim light, 35mm lens, vertical 9:16
```

**OUTDOOR** (taman, siang)
```
green city park with trees and a paved path, bright natural daylight with soft shadows, fresh casual lifestyle photo, full body walking slowly and glancing to the side with a natural smile, 50mm lens, vertical 9:16
```

**KANTOR** (smart casual). Styling: ganti sneakers dengan black leather loafers.
```
modern minimalist office with glass walls and plants, soft daylight, smart casual workwear look, standing beside a desk with one hand resting on it, confident friendly expression, framed from head to knees, 50mm lens, vertical 4:5
```

**LEBARAN** (untuk koko / busana muslim). Styling: black or matching trousers, leather sandals or loafers.
```
elegant home interior with warm wooden furniture, ketupat decorations and soft warm light, festive Eid al-Fitr atmosphere, full body standing with hands clasped in front and a warm smile, 50mm lens, vertical 9:16
```

---

## Keyword POSE (opsional, menggantikan pose di blok GAYA)

| Keyword | Kalimat pose |
|---|---|
| DEPAN | standing straight facing the camera, arms relaxed at his sides |
| SAKU | standing relaxed with both hands in his trouser pockets, weight on one leg |
| SAMPING | standing in side profile, head turned toward the camera |
| BELAKANG | back view showing the back of the garment, head turned slightly over the shoulder |
| JALAN | walking mid-stride toward the camera, natural arm swing |
| DUDUK | sitting on a stool, leaning forward slightly with forearms on his knees |
| DETAIL | close-up from chest to waist showing the fabric texture, neckline and stitching, hand lightly touching the fabric |
| TANGAN | arms crossed over the chest with a confident small smile |

## Format kirim ke editor (Claude)

```
[foto produk]
Gaya: STREET
Pose: JALAN, BELAKANG
```
Editor mengisi blok PRODUK dan STYLING secara otomatis, lalu mengirim prompt yang siap dipakai
(satu prompt per pose).

---

## Motion Control (gerakan sama persis dengan video referensi)

Upload: video referensi (sumber gerakan) + foto model yang sudah memakai produk (hasil prompt di atas).
Orientasi Karakter: **Video**. Batas prompt 500 karakter; prompt di bawah 435 karakter dan bisa
dipakai untuk produk apa pun.

```
Copy the reference video's body motion, gestures, hand positions, head turns, timing and camera movement exactly, frame by frame. Only the person, outfit and background change. Use the man from the image: same face, hair and body; never take the face or hair from the video. Outfit exactly as in the image. Background from the image. Real-time natural motion, realistic fabric folds, stable face, no morphing, no extra people, no text.
```

Agar hasil presisi, framing dan pose awal foto model harus mirip frame pertama video referensi
(jarak kamera, bagian badan yang terlihat, posisi tangan). Untuk itu, buat foto model dengan
tambahan baris POSE berikut di master prompt:
`framed exactly like the first frame of the reference video: {FRAMING}, {POSE_AWAL}`
