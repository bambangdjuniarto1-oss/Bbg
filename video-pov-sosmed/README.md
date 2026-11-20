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

## Versi KnowByHours

`pov-claude-code-knowbyhours.mp4`: versi bermerek @knowbyhours (kuning–hitam, logo K, caption berstabilo).
Sumber: `ai-office/public/video-pov-knowbyhours.html`. Jumlah pengikut (3.458) dan postingan (20)
diambil dari profil; reach, engagement, disimpan, dan sentimen adalah angka ilustrasi
(ditandai "*data ilustrasi" di video). Ganti dengan angka dari Instagram Insights sebelum dipublikasikan.
