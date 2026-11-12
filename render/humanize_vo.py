"""Bikin VO hasil TTS terdengar lebih natural (kurang "suara AI") + percepat dengan tempo bervariasi.

  python3 render/humanize_vo.py VO.wav WORDS_RAW.json OUTDIR --plan render/scenes/NAMA_vo.json

WORDS_RAW.json = hasil transcribe.py dengan --speed 1.0 (timestamp di VO asli).
Langkah:
 1. Intonasi (Praat PSOLA): register tiap kalimat yang "loncat" (mis. 236 Hz lalu 130 Hz) ditarik
    mendekati register tengah, kalimat yang datar/monoton diberi rentang nada lebih lebar, nada turun
    pelan di akhir kalimat (deklinasi), dan pertanyaan di akhir naik.
 2. Jeda: jeda seragam khas TTS diganti jeda natural (koma pendek, titik sedang, ganti bagian lebih
    panjang).
 3. Tempo per bagian (angka lebih pelan supaya kebaca), dipotong di jeda supaya tanpa artefak.
 4. Warna suara: sedikit hangat, desis dikurangi, ruang kecil yang sangat tipis.
Hasil: OUTDIR/vo_human.wav + OUTDIR/words.json (timestamp di timeline baru).
"""
import argparse
import json
import subprocess

import numpy as np
import parselmouth
import soundfile as sf
from parselmouth.praat import call


def sentences(words):
    out, cur = [], []
    for i, (a, b, t) in enumerate(words):
        cur.append(i)
        if t.endswith((".", "?", "!")):
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def st(x):
    return 12 * np.log2(x)


def intonation(wav, words, plan, out_wav):
    snd = parselmouth.Sound(wav)
    pitch = snd.to_pitch_ac(time_step=0.01, pitch_floor=75, pitch_ceiling=500)
    f = pitch.selected_array["frequency"]
    tt = pitch.xs()
    gmed = np.median(f[f > 0])
    man = call(snd, "To Manipulation", 0.01, 75, 500)
    tier = call(man, "Extract pitch tier")
    n = call(tier, "Get number of points")
    pts = [(call(tier, "Get time from index", i), call(tier, "Get value at index", i)) for i in range(1, n + 1)]
    sents = sentences(words)
    rng = []
    for s in sents:
        a, b = words[s[0]][0] - 0.05, words[s[-1]][1] + 0.05
        v = f[(tt >= a) & (tt <= b) & (f > 0)]
        med = np.median(v)
        r = st(np.percentile(v, 90)) - st(np.percentile(v, 10))
        keep = plan.get("register_keep", 0.35)
        tgt = gmed * (med / gmed) ** keep
        k = float(np.clip((plan.get("target_range", 9.5) / max(r, 1)) ** 0.6, 0.85, 1.5))
        rng.append((a, b, med, tgt, k))
        print(f"  kalimat {a:6.1f}s  {med:4.0f}Hz -> {tgt:4.0f}Hz  rentang {r:4.1f}st x{k:.2f}")
    q_last = plan.get("question_end", True)
    t_end = words[-1][1]
    call(tier, "Remove points between", 0, snd.duration)
    for t, v in pts:
        cur = None
        for (a, b, med, tgt, k) in rng:
            if a <= t <= b:
                cur = (a, b, med, tgt, k)
                break
        if cur is None:
            call(tier, "Add point", t, v)
            continue
        a, b, med, tgt, k = cur
        nv = tgt * (v / med) ** k
        x = (t - a) / max(b - a, .3)
        nv *= 2 ** ((0.8 - 1.6 * x) / 12)  # deklinasi ±0.8 st
        if q_last and t > t_end - 0.75:
            nv *= 2 ** (3.0 * (t - (t_end - 0.75)) / 0.75 / 12)
        call(tier, "Add point", t, float(np.clip(nv, 70, 420)))
    call([tier, man], "Replace pitch tier")
    res = call(man, "Get resynthesis (overlap-add)")
    res.save(out_wav, "WAV")


def reshape(y, sr, words, plan):
    """Ganti jeda; kembalikan audio baru + peta waktu (list (t_lama, t_baru))."""
    sec = set(plan.get("section_starts", []))
    keep_parts, tmap = [], [(0.0, 0.0)]
    pos_old, pos_new = 0.0, 0.0
    rms_thr = 10 ** (-42 / 20)
    for i in range(len(words) - 1):
        e, s = words[i][1], words[i + 1][0]
        g = s - e
        tw = words[i][2]
        if round(s, 1) in sec:
            ng = plan.get("pause_section", 0.62)
        elif tw.endswith((".", "?", "!")):
            ng = plan.get("pause_sentence", 0.42)
        elif tw.endswith(","):
            ng = plan.get("pause_comma", 0.22)
        else:
            ng = min(g, 0.2)
        if g - ng < 0.06:
            continue
        c0, c1 = e + ng / 2, s - ng / 2
        seg = y[int(c0 * sr):int(c1 * sr)]
        if len(seg) == 0 or np.sqrt(np.mean(seg ** 2)) > rms_thr * 3:
            continue
        keep_parts.append(y[int(pos_old * sr):int(c0 * sr)])
        pos_new += c0 - pos_old
        tmap.append((c0, pos_new))
        tmap.append((c1, pos_new))
        pos_old = c1
    keep_parts.append(y[int(pos_old * sr):])
    pos_new += len(y) / sr - pos_old
    tmap.append((len(y) / sr, pos_new))
    xf = int(0.015 * sr)
    out = keep_parts[0]
    for p in keep_parts[1:]:
        if len(out) > xf and len(p) > xf:
            r = np.linspace(0, 1, xf)
            mid = out[-xf:] * (1 - r) + p[:xf] * r
            out = np.concatenate([out[:-xf], mid, p[xf:]])
        else:
            out = np.concatenate([out, p])
    return out, tmap


def remap(t, tmap):
    old = np.array([a for a, _ in tmap])
    new = np.array([b for _, b in tmap])
    return float(np.interp(t, old, new))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vo")
    ap.add_argument("words")
    ap.add_argument("out")
    ap.add_argument("--plan", required=True)
    ap.add_argument("--pad", type=float, default=1.2)
    a = ap.parse_args()
    plan = json.load(open(a.plan))
    words = json.load(open(a.words))
    subprocess.run(["mkdir", "-p", a.out], check=True)
    src = f"{a.out}/vo_44k.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.vo, "-ac", "1", "-ar", "44100", src], check=True)
    print("1) intonasi")
    intonation(src, words, plan, f"{a.out}/vo_into.wav")
    y, sr = sf.read(f"{a.out}/vo_into.wav")
    print("2) jeda")
    y, tmap = reshape(y, sr, words, plan)
    w2 = [[remap(s, tmap), remap(e, tmap), t] for s, e, t in words]
    # 3) tempo per bagian: potong di tengah jeda sebelum kata awal bagian
    segs = plan["tempo"]  # [[t_mulai_asli, tempo], ...]
    cuts = []
    for t0, tp in segs:
        idx = min(range(len(words)), key=lambda i: abs(words[i][0] - t0))
        c = 0.0 if idx == 0 else (w2[idx - 1][1] + w2[idx][0]) / 2
        cuts.append((c, tp))
    cuts.append((len(y) / sr, None))
    parts, w3, t_out = [], [], 0.0
    for k in range(len(cuts) - 1):
        c0, tp = cuts[k]
        c1 = cuts[k + 1][0]
        seg = y[int(c0 * sr):int(c1 * sr)]
        sf.write(f"{a.out}/_p.wav", seg, sr)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{a.out}/_p.wav", "-af",
                        f"rubberband=tempo={tp}:pitchq=quality:formant=preserved", f"{a.out}/_q.wav"], check=True)
        q, _ = sf.read(f"{a.out}/_q.wav")
        parts.append(q)
        for s, e, t in w2:
            if c0 <= s < c1:
                w3.append([round(t_out + (s - c0) / tp, 3), round(t_out + (e - c0) / tp, 3), t])
        t_out += len(q) / sr
        print(f"3) bagian {c0:6.1f}s tempo {tp}")
    y = np.concatenate(parts + [np.zeros(int(a.pad * sr))])
    sf.write(f"{a.out}/vo_tempo.wav", y, sr)
    print("4) warna suara")
    af = ("highpass=f=75,equalizer=f=220:t=q:w=1.0:g=1.8,equalizer=f=3200:t=q:w=1.4:g=-1.2,"
          "equalizer=f=7500:t=q:w=1.0:g=-2.0,deesser=i=0.35,"
          "aecho=0.9:0.9:23|37:0.05|0.03,"
          "acompressor=threshold=-22dB:ratio=2.5:attack=8:release=120:makeup=2")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{a.out}/vo_tempo.wav", "-af", af,
                    "-ar", "44100", f"{a.out}/vo_human.wav"], check=True)
    json.dump(w3, open(f"{a.out}/words.json", "w"), ensure_ascii=False)
    print(f"durasi {len(y) / sr:.2f}s -> {a.out}/vo_human.wav, {len(w3)} kata")


if __name__ == "__main__":
    main()
