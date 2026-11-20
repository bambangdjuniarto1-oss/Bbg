# Video POV: Claude Code x Tim Analis Sosmed

`pov-claude-code-tim-sosmed.mp4`: 1080×1920 (9:16), 24 detik, 30 fps, dengan musik latar.

Adegan 3D (laptop di meja, kamera seperti dipegang tangan) dirender dari
`ai-office/public/video-pov-sosmed.html`, frame demi frame. Isi layar adalah simulasi:
Claude Code membagi tugas ke Taufik, Umar, Yoga, dan Nadia, lalu dashboard sosmed terisi.
Angka di dashboard adalah data contoh, bukan data akun sungguhan.

Musik: `render/music.py` (sintesis orisinal, varian A, 24 detik).

Cara render ulang:
1. `cd ai-office && PORT=3100 npm start`
2. Buka `http://localhost:3100/video-pov-sosmed.html?t=10` untuk melihat satu frame (detik ke-10).
3. Ambil frame 0–24 detik pada 30 fps (memanggil `window.gambar(t)`), lalu gabungkan dengan ffmpeg.
