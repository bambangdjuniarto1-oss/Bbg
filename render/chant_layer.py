"""Lapisan chant bobotoh asli (rekaman tribun kiriman user) di bawah backsound.

  python3 render/chant_layer.py MUSIC.wav CHANT_SRC.wav OUT.wav DUR --env "t:db,t:db,..." [--rel -9]

Rekaman di-EQ (highpass 120 Hz, redam 1,5-4 kHz supaya tidak menabrak VO), dinormalisasi ke RMS musik, diulang
(crossfade 1,5 s) sepanjang video, lalu dikali amplop volume (dB relatif terhadap musik, interpolasi linear).
Hasil = musik + chant (stereo), siap masuk mix_final.sh sebagai MUSIC.
"""
import argparse
import subprocess

import numpy as np
import soundfile as sf

SR = 44100


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-af",
                          "highpass=f=120,equalizer=f=2600:t=q:w=1.0:g=-4,lowpass=f=9000",
                          "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).T.copy()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("music")
    ap.add_argument("chant")
    ap.add_argument("out")
    ap.add_argument("dur", type=float)
    ap.add_argument("--env", required=True)
    ap.add_argument("--rel", type=float, default=0.0, help="geser semua amplop (dB)")
    ap.add_argument("--start", type=float, default=0.0, help="mulai potongan rekaman (detik)")
    a = ap.parse_args()
    mus, sr = sf.read(a.music, always_2d=True)
    mus = mus.T
    n = int(a.dur * SR)
    mus = np.pad(mus, ((0, 0), (0, max(0, n - mus.shape[1]))))[:, :n]
    src = load(a.chant)[:, int(a.start * SR):]
    xf = int(1.5 * SR)
    out = np.zeros((2, n + src.shape[1]))
    pos = 0
    ramp = np.linspace(0, 1, xf)
    while pos < n:
        seg = src.copy()
        if pos > 0:
            seg[:, :xf] *= ramp
            out[:, pos:pos + xf] *= 1 - ramp
        out[:, pos:pos + seg.shape[1]] += seg
        pos += seg.shape[1] - xf
    ch = out[:, :n]
    rms = lambda x: np.sqrt(np.mean(x ** 2)) + 1e-9
    ch *= rms(mus) / rms(ch)
    pts = sorted((float(t), float(d)) for t, d in (p.split(":") for p in a.env.split(",")))
    t = np.arange(n) / SR
    env_db = np.interp(t, [p[0] for p in pts], [p[1] for p in pts]) + a.rel
    ch *= 10 ** (env_db / 20)
    mix = mus + ch
    mix /= max(1.0, np.abs(mix).max() / .95)
    sf.write(a.out, mix.T, SR, subtype="PCM_16")
    print("wrote", a.out)


if __name__ == "__main__":
    main()
