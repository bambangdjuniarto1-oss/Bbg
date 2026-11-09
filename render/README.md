# Render Pipeline (Cara A — Blender, tanpa AI generator)

Kota low-poly dibangun pakai script Blender (`bpy`), dirender per adegan, lalu
header, host cutout, speech bubble, label 3D, HUD, dan subtitle ditempel oleh
`compose.py` dan digabung dengan narasi mp3.

## Setup
```
pip install bpy pillow        # Blender 5.x sebagai modul Python (CPU / Cycles)
```
Butuh `ffmpeg` di PATH.

## Render satu adegan (contoh S12)
```
# 1) render 3D (frame PNG + anchors.json posisi label)
python3 render/s12_mitra.py -- --out out/s12 --res 1080x1920 --frames 1-147 --samples 12

# 2) compositing + audio
python3 render/compose.py --scene render/scenes/s12.json --frames out/s12/frames \
  --anchors out/s12/anchors.json --audio narasi.mp3 --words render/scenes/words.json \
  --out out/S12.mp4 [--host host_cutout.png]
```
Preview cepat: `--res 540x960 --samples 8`.

## File
- `lowpoly.py` — palet warna + bangun rumah, ruko, pohon, mobil, motor, jalan, kota prosedural.
- `s12_mitra.py` — adegan S12 (aerial laundry mitra → toko cuci sepatu).
- `compose.py` — layer 2D bergaya video referensi.
- `scenes/*.json` — teks bubble, label, HUD, subtitle per adegan.
- `scenes/words.json` — timestamp per kata dari narasi (Whisper).
- `fonts/` — Plus Jakarta Sans (SIL OFL).
