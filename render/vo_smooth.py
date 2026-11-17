"""Rapikan VO TTS tanpa membuatnya "patah":
 - jeda panjang dipendekkan HANYA di dalam bagian hening (dideteksi dari energi audio, bukan dari
   timestamp whisper), sambungan pakai crossfade equal-power sehingga suara ruang tetap menyambung;
   suara pembicara tidak pernah dipotong;
 - satu tempo seragam (rubberband, formant dijaga) untuk seluruh VO, tanpa ganti tempo per bagian;
 - tanpa manipulasi intonasi (PSOLA).
Timestamp kata ikut dipetakan ke timeline baru.

  python3 render/vo_smooth.py VO.wav WORDS_RAW.json OUTDIR --tempo 1.18 \
      --sections "Kita,Terus,Ke pemilik,Tapi tunggu,Jawabannya,Follow,Jujur,Ini simulasi"
Hasil: OUTDIR/vo.wav (44,1 kHz) + OUTDIR/words.json
"""
import argparse
import json
import os
import subprocess

import numpy as np
import soundfile as sf

HOP = 0.005


def load(path, sr=44100):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy(), sr


def silences(x, sr, thr_db=-40.0, min_len=.14):
    h = int(HOP * sr)
    win = int(.02 * sr)
    n = len(x) // h
    rms = np.array([np.sqrt(np.mean(x[i * h:i * h + win] ** 2) + 1e-12) for i in range(n)])
    db = 20 * np.log10(rms / (rms.max() + 1e-12))
    quiet = db < thr_db
    out, i = [], 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            if (j - i) * HOP >= min_len and i > 0 and j < n:
                out.append([i * HOP, j * HOP])
            i = j
        else:
            i += 1
    return out


def classify(sil, words, sect_starts):
    """target lama jeda berdasar kata sebelum/sesudah jeda."""
    mid = (sil[0] + sil[1]) / 2
    prev = None
    for k, (a, b, t) in enumerate(words):
        if a <= mid:
            prev = k
    if prev is None or prev + 1 >= len(words):
        return None
    nxt = prev + 1
    # jeda harus berada di antara dua kata (bukan di dalam kata)
    if words[nxt][0] < sil[0] - .25 or words[prev][1] > sil[1] + .25:
        return None
    t = words[prev][2]
    if nxt in sect_starts:
        return .58
    if t.endswith(("?", "!")):
        return .42
    if t.endswith("."):
        return .36
    if t.endswith((",", ":", ";")):
        return .2
    return .14


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vo")
    ap.add_argument("words")
    ap.add_argument("outdir")
    ap.add_argument("--tempo", type=float, default=1.18)
    ap.add_argument("--sections", default="")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    x, sr = load(a.vo)
    words = json.load(open(a.words))
    heads = [s.strip().lower().split() for s in a.sections.split(",") if s.strip()]
    sect = set()
    for h in heads:
        for k in range(len(words) - len(h) + 1):
            if all(words[k + i][2].lower().strip(",.?!") == h[i] for i in range(len(h))):
                sect.add(k)
                break
    sil = silences(x, sr)
    xf = int(.02 * sr)
    pieces, cur = [], 0
    tmap = [(0.0, 0.0)]                      # (detik lama, detik baru)
    new_t = 0.0
    saved = 0.0
    for s0, s1 in sil:
        tgt = classify((s0, s1), words, sect)
        L = s1 - s0
        if tgt is None or L <= tgt + .03:
            continue
        keep = tgt / 2
        c0 = int((s0 + keep) * sr)          # potong bagian tengah jeda
        c1 = int((s1 - keep) * sr)
        seg = x[cur:c0 + xf]
        pieces.append(seg)
        new_t += (c0 - cur) / sr
        tmap.append((c0 / sr, new_t))
        tmap.append((c1 / sr, new_t))
        cur = c1
        saved += (c1 - c0) / sr
    pieces.append(x[cur:])
    # sambung dengan crossfade equal-power (hanya terjadi di dalam hening)
    out = pieces[0]
    fade = np.linspace(0, np.pi / 2, xf)
    for p in pieces[1:]:
        tail = out[-xf:] * np.cos(fade)
        head = p[:xf] * np.sin(fade)
        out = np.concatenate([out[:-xf], tail + head, p[xf:]])
    tmap.append((len(x) / sr, len(out) / sr))
    tmp = os.path.join(a.outdir, "_gap.wav")
    sf.write(tmp, out, sr, subtype="FLOAT")
    dst = os.path.join(a.outdir, "vo.wav")
    af = (f"rubberband=tempo={a.tempo}:transients=mixed:phase=laminar:window=standard:formant=preserved:"
          f"pitchq=quality:channels=together,highpass=f=70,"
          f"equalizer=f=6500:t=q:w=1.2:g=-2")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", af, "-ar", "44100", "-c:a", "pcm_s16le", dst],
                   check=True)
    os.remove(tmp)
    olds = np.array([p[0] for p in tmap])
    news = np.array([p[1] for p in tmap])

    def m(t):
        return float(np.interp(t, olds, news)) / a.tempo
    nw = [[round(m(w0), 3), round(m(w1), 3), t] for w0, w1, t in words]
    json.dump(nw, open(os.path.join(a.outdir, "words.json"), "w"), ensure_ascii=False)
    dur = len(out) / sr / a.tempo
    print(f"jeda dipangkas {saved:.2f}s dari {len(sil)} hening; durasi akhir {dur:.2f}s; seksi {sorted(sect)}")


if __name__ == "__main__":
    main()
