# Pipeline Video Explainer Isometrik Low-Poly (Blender, tanpa AI generator)

Video vertikal 9:16: diorama kota low-poly dibangun dengan script Blender (`bpy`),
dirender per adegan, lalu bubble keyword, label 3D, HUD angka, panel, subtitle
kuning, tombol FOLLOW, backsound orisinal, dan watermark ditempel lewat Python.

## Setup
```
pip install bpy pillow numpy scipy soundfile faster-whisper
```
Butuh `ffmpeg` (dengan filter `rubberband`) di PATH. Render pakai CPU (Cycles).

## Alur lengkap (contoh: video tahu kuning)
```
# 1) Audio: VO dipercepat 1.4x (pitch tetap) + backsound orisinal + mixing (VO lebih keras)
bash render/mix_audio.sh VO.wav out/tahu_audio 1.4 28.71 32.71 B 124
#    -> out/tahu_audio/mix.wav  (argumen: VO OUTDIR SPEED [BREAK_MULAI BREAK_SELESAI] VARIAN BPM)

# 2) Subtitle: timestamp per kata (lalu rapikan salah dengar di JSON)
python3 render/transcribe.py VO.wav render/scenes/tahu_words.json --speed 1.4

# 3) Render 3D semua adegan (frame PNG + anchors.json posisi label)
bash render/render_tahu.sh out/tahu_render 720x1280 4
#    satu adegan saja:  python3 render/scenes_tahu.py -- --scene T05 --out out/tahu_render/T05 --res 720x1280 --samples 4
#    cek posisi label tanpa render:  tambah --frames 1-0

# 4) Compositing + encode 1080x1920
python3 render/compose_full.py --render out/tahu_render --audio out/tahu_audio/mix.wav \
  --config render/scenes/tahu.json --words render/scenes/tahu_words.json \
  --comp out/tahu_comp --out out/video_tahu_kuning.mp4

# 5) Watermark Instagram + versi ringan
python3 render/watermark.py out/video_tahu_kuning.mp4 out/video_tahu_kuning_1080p_wm.mp4 --handle @juniart.ai
ffmpeg -i out/video_tahu_kuning_1080p_wm.mp4 -c:v libx264 -crf 24 -c:a aac -b:a 192k out/video_tahu_kuning_1080p_wm_ringan.mp4
```
Waktu render (CPU): ~4–5 detik/frame di 720x1280 samples 4, jadi ~3 jam untuk video 80 detik.
Hasil 720p di-upscale ke 1080x1920 saat compositing.

Video cuci sepatu memakai alur yang sama dengan `scenes.py` + `render_all.sh`
+ `scenes/full.json` + `scenes/words.json` (tempo 1.28, varian musik A).

## File
| File | Isi |
|---|---|
| `lowpoly.py` | palet warna, material, render setup, aset dasar (rumah, ruko, pohon, mobil, motor, jalan) |
| `world.py` | mesh builder `MB`, kota diorama, lampu/langit |
| `scenes.py` | adegan S01–S16 video cuci sepatu + helper kamera/studio |
| `world_tahu.py` | aset video tahu: tahu, bungkus plastik, tampah, penjual, pelanggan, motor+boks, pabrik, perumahan, rute |
| `scenes_tahu.py` | adegan T01–T20 video tahu (timeline mengikuti VO) |
| `render_all.sh`, `render_tahu.sh` | render semua adegan berurutan |
| `compose.py` | layer 2D: header, bubble, label, HUD, subtitle |
| `compose_full.py` | gabung semua adegan + panel (jadwal, tabel) + audio → mp4 |
| `music.py` | backsound orisinal disintesis (bebas hak cipta), varian A/B |
| `mix_audio.sh` | percepat VO, buat musik, mix dengan ducking |
| `transcribe.py` | timestamp kata dari VO (Whisper) |
| `watermark.py` | watermark akun IG di bawah bubble |
| `scenes/*.json` | teks bubble, label, HUD, panel per adegan + keyword kuning |
| `fonts/` | Plus Jakarta Sans (SIL OFL) |

## Bikin video topik baru
1. Salin `world_tahu.py`/`scenes_tahu.py` jadi file baru, ganti aset & adegan sesuai naskah.
2. Atur `_SRC` (detik mulai tiap adegan di VO asli) dan `SPEED`.
3. Buat `scenes/<topik>.json` (bubble, label, HUD, panel) dan `<topik>_words.json`.
4. Jalankan langkah 1–5 di atas.
