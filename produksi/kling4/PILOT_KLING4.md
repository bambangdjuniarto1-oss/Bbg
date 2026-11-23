# Pilot Episode: KLING 4.0 (gaya AI filmmaker, host AI "NARA")

Status: **pra-produksi selesai**. Naskah, karakter, daftar shot, prompt, SFX, grafis, dan animatic sudah siap.
Yang belum: generate visual + suara di Higgsfield (saldo sekarang 0 kredit) dan hasil tes Kling 4.0 asli.

- Durasi: ±58 detik, 9:16, 13 shot (ganti shot tiap 3–7 detik, potongan cepat di dalam shot panjang via grafis)
- Animatic (timing + grafis + SFX, background placeholder): `out/kling4_animatic.mp4`
- Config grafis: `render/scenes/byte_kling4.json` · SFX: `render/scenes/byte_kling4_sfx.json`

---

## 1. Karakter host: NARA

Karakter fiktif, **tidak meniru orang nyata** dan tidak meniru host dstudio (tidak pakai kacamata hitam, tidak pakai outfit krem).

**Wajah & tubuh (tetap sama di SEMUA episode):**
- Perempuan Indonesia, ±27 tahun, kulit sawo matang hangat
- Rambut hitam bob bergelombang sebahu, belahan samping, beberapa helai jatuh di dahi
- Alis tebal natural, mata cokelat tua, **tahi lalat kecil di bawah mata kiri** (penanda konsistensi)
- Makeup minimal, bibir nude kecokelatan
- **Ear cuff emas tipis di telinga kanan**, **lanyard crew hijau lime** (warna brand Byteinsight) di setiap episode

**Yang berganti per topik:** outfit, set, properti.

| Episode | Outfit | Set |
|---|---|---|
| Kling 4.0 (pilot) | Jumpsuit utility abu arang, lengan digulung | Soundstage gelap: dinding storyboard polaroid, monitor edit, lampu film |
| Seedance | Kemeja satin hitam | Studio tari / panggung, lampu sorot |
| Iklan AI / budget | Blazer oversized hitam | Ruang meeting agensi, layar presentasi |

**Prompt master karakter** (pakai untuk character sheet, lalu jadikan referensi di semua shot):

```
Photorealistic portrait of NARA, a 27-year-old Indonesian woman with warm tan skin, shoulder-length wavy black
bob with side part and loose strands over the forehead, thick natural eyebrows, dark brown eyes, a small beauty
mark under her left eye, minimal makeup with a nude-brown lip, a thin gold ear cuff on her right ear, wearing a
charcoal utility jumpsuit with sleeves rolled up and a lime-green film crew lanyard. Confident, friendly,
slightly playful expression. Shot on 35mm, soft key light, cinematic film studio background, shallow depth of
field, natural skin texture, no retouching, vertical 9:16.
```

Character sheet: depan, 3/4 kiri, 3/4 kanan, badan penuh. Simpan 1 gambar terbaik sebagai **NARA_REF**.

---

## 2. Naskah + daftar shot

Gaya bicara: **gue/kalian**, cepat, yakin, sedikit bercanda. Fakta Kling 4.0 diambil dari materi resmi Kling dan ulasan pihak ketiga (lihat bagian 6).

| # | Waktu | Voice-over (NARA) | Visual | Grafis di layar | Jenis shot |
|---|---|---|---|---|---|
| S01 | 0.0–3.0 | "Tiga puluh detik. Satu prompt." | Nara jalan ke kamera di soundstage gelap, bawa clapperboard | kicker `KLING 4.0 · TES JUJUR`, counter `0 → 30 DTK` | B-roll (tanpa lip-sync) |
| S02 | 3.0–6.2 | "Kling 4.0 sekarang bisa bikin video tiga puluh detik, sekali generate." | Close-up Nara ngomong ke kamera, lampu film di belakang | judul `30 DETIK` + `sekali generate` | **Talking** |
| S03 | 6.2–9.6 | "Dulu? Gue harus nyambung enam klip lima detik." | Nara di meja edit, monitor penuh potongan klip | grid 6 klip `TAKE`, dicoret X | **Talking** |
| S04 | 9.6–12.6 | "Dan tiap sambungan, mukanya berubah." | Nara angkat 2 foto print, wajahnya beda | caption `tiap sambungan, [muka berubah]` | **Talking** |
| S05 | 12.6–16.4 | "Sekarang kalian bisa kasih sampai sepuluh keyframe…" | Nara menempel polaroid di dinding storyboard | struk `STORYBOARD · KLING 4.0` (KF 01–05…) | **Talking** |
| S06 | 16.4–19.6 | "…plus referensi karakter, biar wajahnya nggak lari." | Nara memegang kartu referensi wajah di depan kamera | tag `OMNI REFERENCE` | **Talking** |
| S07 | 19.6–22.6 | "Suaranya juga langsung jadi." | Nara pakai headphone di depan mixer | tag `AUDIO` + `stereo, langsung dari model` | B-roll |
| S08 | 22.6–26.0 | "Jadi gue tes. Satu prompt, film pendek." | Nara mengetik di laptop, cahaya layar di wajah | judul `GUE TES` | B-roll |
| S09 | 26.0–33.0 | *(musik naik, tanpa VO)* | **Hasil tes Kling 4.0 asli** (potongan terbaik) | kartu besar `hasil 1× generate` | Hasil tes |
| S10 | 33.0–40.0 | "[ISI SETELAH TES: penilaian jujur. Misalnya: gerakannya halus, tapi tangan masih aneh di detik 18.]" | Nara menonton monitor, reaksi | caption pendapat (isi setelah tes) | **Talking** |
| S11 | 40.0–48.0 | "Tips biar kredit nggak kebakar: draft dulu di mode Flash 720p, kunci adegan pakai keyframe, baru render final." | Nara jalan sambil menunjuk 3 polaroid | judul `HEMAT KREDIT` + caption `draft dulu di [Flash 720p]` | **Talking** |
| S12 | 48.0–54.8 | "Mau prompt lengkap film pendek tadi? Komen KLING." | Close-up Nara mendekat ke kamera, senyum | kotak komentar `KLING` | **Talking** |
| S13 | 54.8–58.0 | *(logo)* | End card | `BYTE INSIGHT · @ai.byteinsight` | Grafis |

**Caption Instagram:**
```
Video AI 30 detik. Sekali generate. 🎬

Dulu bikin film pendek AI = nyambung 6 klip 5 detik, dan wajah karakternya berubah tiap sambungan.
Kling 4.0 bisa langsung 30 detik, sampai 10 keyframe, plus referensi karakter.

Gue tes jujur pakai 1 prompt. Hasilnya ada di video.

Mau prompt lengkapnya?
Komen "KLING", gue kirim ke DM kalian.

#kling #klingai #aivideo #aifilmmaking #byteinsight
```

---

## 3. Prompt per shot

Semua shot: tambahkan **NARA_REF** sebagai referensi karakter, rasio 9:16. Akhiran gaya umum:
`cinematic, shot on 35mm film, teal shadows and warm highlights, soft haze, practical film lights, shallow depth of field, natural skin texture`

| # | Prompt gambar (start frame) | Prompt gerak (video) |
|---|---|---|
| S01 | Nara walking toward camera through a dark film soundstage, holding a black clapperboard, rows of film lights and C-stands behind her, haze in light beams | She walks confidently toward the camera and raises the clapperboard, slow dolly back, light beams flicker |
| S02 | Medium close-up of Nara facing camera, film lights and blurred crew behind her | Talking to camera with natural hand gestures, subtle push-in |
| S03 | Nara seated at an editing desk with two monitors full of short video clip thumbnails, timeline glowing | Talking to camera, then gestures at the monitors, slight handheld |
| S04 | Nara holding two printed photos of a woman whose faces look slightly different, frowning playfully | Talking, lifts both photos toward camera, slow push-in |
| S05 | Nara pinning instant photos onto a storyboard wall covered with ten polaroid keyframes and red string | Talking while pinning a photo, camera tracks sideways along the wall |
| S06 | Nara holding a face reference card close to the lens, studio behind softly blurred | Talking, rotates the card toward camera, rack focus from card to her face |
| S07 | Nara wearing studio headphones at a mixing console with glowing meters | She nods to the beat, smiling, slow orbit around her |
| S08 | Nara typing on a laptop in a dark studio, screen light on her face | Typing then pressing enter, light from screen pulses, slow push-in |
| S10 | Nara watching a monitor with an honest, thinking reaction, monitor light on her face | Talking with a thoughtful expression, small head shake then smile |
| S11 | Nara walking past three hanging polaroids, pointing at them one by one | Talking while walking, camera tracks with her |
| S12 | Close-up of Nara leaning toward camera, playful smile | Leans in and talks to camera, ends with a wink |

**Prompt tes Kling 4.0 (S09)**: ini konten intinya, jadi di-generate di Kling 4.0 sendiri (kling.ai atau Genjutsu Lite di Higgsfield):
```
A 30-second cinematic short film. Jakarta at night in the rain. A young courier on a motorbike weaves through
neon-lit traffic, stops under a flyover, and opens a glowing package that lights up her face.
Keyframes: 1) wide aerial of Jakarta skyline in rain, 2) courier riding past neon signs, 3) close-up of rain on
her helmet visor, 4) she stops under the flyover, 5) package glows, 6) her surprised face lit in gold.
Anamorphic lens, teal and orange grade, realistic motion, ambient city sound and rain.
```

---

## 4. Audio

- **Voice-over:** 1 suara perempuan Indonesia yang sama untuk semua episode (TTS Higgsfield, `language: id`, instruksi "santai, percaya diri, sedikit playful"). Satu file per baris naskah.
- **Musik** (ElevenLabs Music, 60 detik, instrumental):
  `modern cinematic tech pulse, dark synth bass, ticking percussion, tension build to a lift at 26 seconds, clean ending at 55 seconds, no vocals`
- **SFX** (gratis, `render/sfx.py`): whoosh tiap potongan, tick saat counter, glitch saat X merah, impact saat judul muncul, riser sebelum hasil tes, typing di kotak komentar. Sudah ada di `byte_kling4_sfx.json`.
- Mix: VO -14 LUFS, musik di-duck -10 dB saat VO, SFX -6 dB di bawah VO.

---

## 5. Rencana generate & anggaran kredit (quote Higgsfield 23 Nov 2026)

| Langkah | Model | Jumlah | Kredit |
|---|---|---|---|
| Character sheet NARA | GPT Image (0,75/gambar) | 4 | 3 |
| Start frame per shot (×2 percobaan) | GPT Image | 22 | ±17 |
| Voice-over per baris | Seed Audio (±1,1/baris) | 10 | ±11 |
| Shot talking + lip-sync (S02–S06, S10–S12) | Grok Video 1.5 720p 5 dtk (22,5) atau Intone | 8 × 1,5 take | ±270 |
| Shot B-roll tanpa lip-sync (S01, S07, S08) | Kling 3.0 Turbo 720p 5 dtk (7,5) | 3 × 1,5 take | ±34 |
| Musik 60 detik | ElevenLabs Music v2.5 | 1 | ±9 |
| **Total pilot** | | | **±345 kredit** |

Tes Kling 4.0 (S09) di luar hitungan ini, karena Kling 4.0 belum ada sebagai model sendiri di Higgsfield.

**Cara hemat:** shot talking diganti start frame + animasi kamera dari kode untuk 3 shot (S04, S06, S10) → hemat ±100 kredit.

---

## 6. Fakta Kling 4.0 yang dipakai (wajib dicek ulang sebelum posting)

| Klaim di video | Status |
|---|---|
| Video 30 detik sekali generate | Ada di halaman fitur resmi Kling |
| Sampai 10 keyframe | Ada di beberapa ulasan + materi Kling |
| Referensi karakter (omni reference, sampai 15 aset) | Ada di beberapa ulasan |
| Audio stereo langsung dari model | Ada di ulasan pihak ketiga |
| Mode Flash 720p untuk draft | Ada di ulasan pihak ketiga |
| 4K / HDR 10-bit | **Tidak dipakai**: sumber saling bertentangan |

Sumber: [kling.ai: Kling 4.0](https://kling.ai/feature/kling-4-ai-video-generation) · [kling.ai: Kling 4.0 vs 3.0](https://kling.ai/blog/kling-4-vs-3) · [Miraflow](https://miraflow.ai/blog/kling-4-0-explained-30-second-10-keyframe-video-model-2026) · [aiidelist](https://aiidelist.com/blog/kling-4)

Tes sendiri tetap wajib: penilaian di S10 harus dari hasil asli, bukan ditebak.
