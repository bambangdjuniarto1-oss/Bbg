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

Video hotel (Rp40 miliar) memakai alur yang sama dengan `world_hotel.py` + `scenes_hotel.py` +
`render_hotel.sh` + `scenes/hotel.json` + `scenes/hotel_words.json`. VO-nya berisi 2 take, yang dipakai take
pertama: `ffmpeg -i VO.wav -af "atrim=0:101.45,afade=t=out:st=101.38:d=0.07,apad=pad_dur=2.24" vo_take1.wav`,
lalu `bash render/mix_audio.sh vo_take1.wav out/hotel_audio 1.4 47.0 50.6 C 120`.
Cek aset: `python3 render/preview_hotel.py -- out/prev 540x960 6`.

Video laundry koin memakai `world_laundry.py` + `scenes_laundry.py` + `render_laundry.sh` +
`scenes/laundry.json` + `scenes/laundry_words.json` (tempo 1.35, musik varian D):
`ffmpeg -i VO.wav -af apad=pad_dur=1.2 vo_pad.wav` lalu `bash render/mix_audio.sh vo_pad.wav out/laundry_audio 1.35 28.4 30.0 D 124`.
Karakter generasi baru (`L.character`) punya lengan/kaki terpisah: `L.walk_to(...)` untuk berjalan, `L.pose(...)` untuk pose.
Cek aset: `python3 render/preview_laundry.py -- out/prev 540x960 6`.

Video AMDK memakai `world_amdk.py` + `scenes_amdk.py` + `render_amdk.sh` + `scenes/amdk.json` +
`scenes/amdk_words.json` (musik varian E). VO TTS dibuat lebih natural dulu dengan `humanize_vo.py`
(register nada antarkalimat diratakan, kalimat datar diberi rentang nada, jeda natural, tempo per bagian,
warna suara lebih hangat), lalu musik di-mix tanpa percepatan tambahan:
`python3 render/transcribe.py VO.wav words_raw.json --speed 1.0` →
`python3 render/humanize_vo.py VO.wav words_raw.json out/amdk_vo --plan render/scenes/amdk_vo.json` →
`bash render/mix_audio.sh out/amdk_vo/vo_human.wav out/amdk_audio 1.0 55.6 58.2 E 122`.
Cek aset: `python3 render/preview_amdk.py -- out/prev 540x960 6`.

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
| `world_hotel.py` | aset video hotel: hotel 30 kamar (+versi potongan), kamar, lobi, restoran/meeting/ballroom, minimarket generik, kantor, uang, kalkulator |
| `scenes_hotel.py` | adegan H01–H20 video hotel |
| `world_laundry.py` | aset video laundry koin: karakter baru (bisa jalan/pose), mesin cuci + drum berputar, pengering, kios QRIS/koin, gedung laundry koin, interior, laundry konvensional, kos, apartemen, kampus |
| `scenes_laundry.py` | adegan L01–L20 video laundry koin |
| `world_amdk.py` | aset video AMDK: air gelas/botol/galon (plastik bening + air), karton, palet, karyawan pabrik (helm, rompi, jas lab, masker), tronton, forklift, pabrik AMDK, lini produksi berjalan, gudang distributor, peta Indonesia + pin |
| `scenes_amdk.py` | adegan A01–A22 video AMDK |
| `humanize_vo.py` | olah VO TTS supaya kurang "suara AI": intonasi (Praat PSOLA), jeda, tempo per bagian, EQ |
| `render_*.sh` | render semua adegan berurutan |
| `compose.py` | layer 2D: header, bubble, label, HUD, subtitle |
| `compose_full.py` | gabung semua adegan + panel (jadwal, tabel, grafik batang) + audio → mp4 |
| `music.py` | backsound orisinal disintesis (bebas hak cipta), varian A/B/C/D/E |
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
