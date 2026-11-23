# Pilot KLING 4.0: film pendek "SATU TAKE"

Format: **iklan sinematik / film pendek**, bukan tutorial. Fitur Kling 4.0 tidak dijelaskan pakai teks, tapi
**dibuktikan lewat cerita**: klimaks film adalah satu shot 30 detik tanpa potongan yang memang di-generate
sekali di Kling 4.0. Info teknis dan CTA ada di caption, bukan di layar.

- Durasi ±61 detik, 9:16
- Teks di layar dibatasi: slug lokasi/waktu, subtitle dialog, timecode REC, title card, end card
- Animatic (timing + suara, gambar placeholder): `out/kling4_animatic.mp4`
- Config: `render/scenes/byte_kling4.json` · SFX & scoring sementara: `render/scenes/byte_kling4_sfx.json`

---

## 1. Logline

Jam 3 pagi, budget produksi habis. Sutradara muda **NARA** cuma punya **satu take** untuk menyelamatkan filmnya.
Dia teriak "Action", dan kamera bergerak 30 detik tanpa putus: dari set studio ke jalanan Jakarta yang hujan,
naik ke atap gedung, menembus ke gurun saat matahari terbit, lalu kembali ke studio. "Cut." Krunya terdiam.
"Itu… beneran satu take?" Nara senyum: "Satu prompt."

**KLING 4.0: 30 detik. Satu take.**

---

## 2. Karakter

**NARA** (pemeran utama, karakter tetap Byteinsight di semua episode; outfit & set berganti per topik)
- Perempuan Indonesia ±27 tahun, kulit sawo matang hangat, rambut hitam bob bergelombang sebahu dengan
  helai di dahi, alis tebal natural, mata cokelat tua, **tahi lalat kecil di bawah mata kiri**,
  **ear cuff emas tipis di telinga kanan**, makeup minimal
- Episode ini: jaket kerja hitam di atas kaus abu, **lanyard crew hijau lime**, headset di leher
- Karakter fiktif: tidak meniru orang nyata dan tidak meniru host dstudio

**DIMAS** (asisten sutradara, karakter pendukung)
- Laki-laki Indonesia ±30 tahun, kumis tipis, beanie abu, hoodie hitam, headset, membawa tablet & clapperboard

**Prompt master** (bikin character sheet dulu, lalu dipakai sebagai referensi di semua shot):
```
NARA: Photorealistic 27-year-old Indonesian woman, warm tan skin, shoulder-length wavy black bob with loose
strands over the forehead, thick natural eyebrows, dark brown eyes, small beauty mark under her left eye, thin
gold ear cuff on her right ear, minimal makeup. Black work jacket over a grey t-shirt, lime-green film crew
lanyard, headset around her neck. Film director at 3 AM: tired but focused. 35mm film look, natural skin texture.

DIMAS: Photorealistic 30-year-old Indonesian man, thin mustache, grey beanie, black hoodie, production headset,
holding a tablet. Assistant director, exhausted, loyal. 35mm film look, natural skin texture.
```

---

## 3. Naskah & daftar shot

Gaya visual seluruh film: `cinematic 35mm film, anamorphic, teal shadows and warm practical lights, haze,
rain, shallow depth of field, natural skin texture, vertical 9:16`

| # | Waktu | Gambar | Suara | Teks di layar | Shot |
|---|---|---|---|---|---|
| S01 | 0.0–3.5 | Hitam → ECU mata Nara, pantulan cahaya monitor bergerak di matanya | Hujan deras di atap seng, dengung lampu | slug `STUDIO 7 · 03.12 WIB` | B-roll |
| S02 | 3.5–7.5 | Wide: soundstage hampir kosong, set fasad ruko palsu, mesin hujan, 2 kru tertidur di apple box, Nara di kursi sutradara | Hujan, drone scoring pelan masuk | – | B-roll |
| S03 | 7.5–11.5 | Dimas masuk, berhenti di samping Nara, ragu | **DIMAS:** "Mbak… budget-nya habis. Kita cuma punya satu take." | subtitle | **Dialog** |
| S04 | 11.5–14.5 | CU Nara, diam sebentar, lalu menatap set | **NARA:** "Satu cukup." | subtitle | **Dialog** |
| S05 | 14.5–17.5 | Lampu studio menyala satu per satu (bang, bang, bang), kru bangun, kamera crane bergerak | Klunk lampu ×3 | – | B-roll |
| S06 | 17.5–19.0 | ECU clapperboard `SC 1 · TAKE 1` dipukul Dimas | Klap slate, **NARA (OS):** "Action." | subtitle | B-roll |
| **S07** | **19.0–49.0** | **SATU TAKE 30 DETIK, di-generate SEKALI di Kling 4.0.** Lihat bagian 4 | Musik naik penuh, hujan, kota | `REC` + timecode 00:00 → 00:30, bingkai kamera | **Kling 4.0** |
| S08 | 49.0–51.5 | Kembali ke studio. Nara menurunkan headset | **NARA:** "Cut." Lalu **hening total** (hujan berhenti) | subtitle | B-roll (VO) |
| S09 | 51.5–55.0 | Dimas menatap monitor, lalu Nara. Nara berdiri, senyum tipis | **DIMAS:** "Itu… beneran satu take?" **NARA:** "Satu prompt." | subtitle | **Dialog** (2 karakter) |
| S10 | 55.0–58.5 | Hitam | Boom rendah | title card **KLING 4.0** + *30 detik. Satu take.* | Grafis |
| S11 | 58.5–61.0 | End card | Ekor reverb | **BYTE INSIGHT** · @ai.byteinsight | Grafis |

---

## 4. Shot utama S07: prompt Kling 4.0 (satu generate, 30 detik, keyframe)

Ini yang jadi "bukti". **Wajib benar-benar 1× generate di Kling 4.0, tanpa potongan.** Kalau gagal dan harus
disambung, judulnya jangan "satu take" (ganti konsep, jangan bohong ke audiens).

```
One continuous 30-second shot, no cuts. Vertical 9:16, cinematic 35mm anamorphic look.
The camera starts behind a young Indonesian female director (NARA reference) in a dark film soundstage at night,
pushes past her shoulder toward a fake Jakarta shophouse set with a rain machine. As the camera passes through
the set, the rain becomes real and the set becomes a real rainy Jakarta street at night: neon signs, motorbikes,
reflections on wet asphalt. A woman in a yellow raincoat runs past; the camera follows her up a narrow
staircase to a rooftop overlooking the city skyline, lightning in the distance. She leaps off the edge, and the
camera dives with her through the clouds into a golden desert at sunrise, sand blowing. The camera pulls back
and back, revealing the desert is playing on a monitor in the soundstage, crew silhouettes watching.
Ambient rain, city, wind, then studio silence.
```

Keyframe (kalau mode keyframe dipakai; satu gambar per titik, semuanya dari prompt gaya yang sama):
1. Bahu Nara + set ruko palsu (detik 0) · 2. Jalan Jakarta hujan, neon (5) · 3. Perempuan jas hujan kuning di tangga (11)
4. Atap gedung, skyline + kilat (16) · 5. Menembus awan (21) · 6. Gurun matahari terbit (25) · 7. Monitor di studio, siluet kru (30)

Generate 2–3 kali, pilih yang paling mulus. Simpan **screen recording proses generate** sebagai bahan konten
lanjutan ("behind the scene satu take").

---

## 5. Prompt shot pendukung (start frame + gerak)

Semua pakai referensi NARA / DIMAS + gaya visual umum di atas.

| # | Start frame | Gerak |
|---|---|---|
| S01 | Extreme close-up of NARA's eyes in darkness, reflection of a glowing editing monitor in her pupils, rain streaks on a window behind | Very slow push-in, monitor light flickers across her eyes, she blinks once |
| S02 | Wide shot of a dark film soundstage at 3 AM: fake Jakarta shophouse set with a rain machine, two crew asleep on apple boxes, NARA alone in a director's chair, single work light | Slow crane down toward NARA, haze drifting through the work light |
| S03 | DIMAS standing beside NARA's chair holding a tablet, hesitant, soundstage behind | He speaks to her quietly, glancing at the tablet (lip-sync) |
| S04 | Close-up of NARA, lit by the monitor, rain machine blurred behind | Pause, then she looks up at the set and speaks (lip-sync) |
| S05 | Wide soundstage, giant film lights switching on one by one from back to front, crew waking up | Lights bang on in sequence, camera slowly rises on a crane |
| S06 | Extreme close-up of a clapperboard reading "SC 1 TAKE 1" in DIMAS's hands, set lights behind | The clapper snaps shut, slight camera shake |
| S08 | Close-up of NARA lowering her headset from her ears, monitor glow fading | She exhales and lowers the headset, everything goes still |
| S09 | Two-shot: DIMAS staring at the monitor, NARA standing up beside him | He turns to her and asks; she answers with a small smile (lip-sync, 2 characters) |

---

## 6. Desain suara

| Waktu | Suara |
|---|---|
| 0–19 | Hujan deras di atap (terus-menerus), dengung lampu, drone scoring gelap pelan |
| 14.5–17 | 3× klunk lampu studio menyala (berat, bergema) |
| 17.5 | Klap slate kering, lalu "Action." |
| 19–49 | **Musik naik penuh** (pulse sinematik), suara kota, petir di detik ±35, angin gurun di ±44 |
| 49 | "Cut." → **hening total 1 detik** (momen paling penting) |
| 55 | Boom rendah di title card |

Musik final (ElevenLabs Music via Higgsfield, 61 detik, instrumental):
`slow dark cinematic drone that builds into a soaring orchestral-electronic pulse from 19 to 49 seconds, abrupt stop at 49, soft low boom at 55, no vocals`

Di animatic sekarang: hujan, klunk lampu, slate, drone, dan boom dari `render/sfx.py` (gratis). Musik dan dialog asli menyusul.

---

## 7. Caption Instagram (info & CTA ada di sini, bukan di video)

```
Satu take. 30 detik. Satu prompt. 🎬

Semua yang terjadi setelah "Action" itu SATU kali generate di Kling 4.0:
tanpa potongan, tanpa sambungan.

Yang bikin ini mungkin:
• video sampai 30 detik sekali generate
• sampai 10 keyframe buat ngunci alur adegan
• referensi karakter biar wajah konsisten

Mau prompt lengkap + keyframe-nya?
Komen "TAKE", gue kirim ke DM.

#kling #klingai #aifilm #aifilmmaking #byteinsight
```

---

## 8. Anggaran kredit Higgsfield (quote 23 Nov 2026)

| Langkah | Model | Kredit |
|---|---|---|
| Character sheet NARA + DIMAS (8 gambar) | GPT Image (0,75) | 6 |
| Start frame + keyframe S07 (±20 gambar) | GPT Image | 15 |
| Dialog TTS (5 baris, 2 suara) | Seed Audio (±1,1) | 6 |
| Shot dialog lip-sync S03, S04, S09 (×1,5 take) | Grok Video 1.5 / Intone (22,5 per 5 dtk) | ±100 |
| Shot B-roll S01, S02, S05, S06, S08 (×1,5 take) | Kling 3.0 Turbo (7,5 per 5 dtk) | ±56 |
| Musik 61 detik | ElevenLabs Music v2.5 | ±9 |
| **Total di Higgsfield** | | **±190** |
| **S07 satu take 30 dtk** | **Kling 4.0** (kling.ai; belum ada sebagai model sendiri di Higgsfield) | biaya terpisah |

---

## 9. Fakta Kling 4.0 (dipakai di caption, wajib cek ulang sebelum posting)

| Klaim | Status |
|---|---|
| Video 30 detik sekali generate | Halaman fitur resmi Kling |
| Sampai 10 keyframe | Materi Kling + beberapa ulasan |
| Referensi karakter / omni reference | Beberapa ulasan |
| 4K / HDR 10-bit | **Tidak dipakai**: sumber bertentangan |

Sumber: [kling.ai: Kling 4.0](https://kling.ai/feature/kling-4-ai-video-generation) · [kling.ai: Kling 4.0 vs 3.0](https://kling.ai/blog/kling-4-vs-3) · [Miraflow](https://miraflow.ai/blog/kling-4-0-explained-30-second-10-keyframe-video-model-2026) · [aiidelist](https://aiidelist.com/blog/kling-4)
