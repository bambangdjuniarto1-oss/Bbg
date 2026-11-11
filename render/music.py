"""Backsound orisinal (disintesis, bebas hak cipta): upbeat explainer ~128 BPM, kunci G mayor.

Nuansanya dibuat mirip video referensi (ringan, ceria, pluck + pad + beat tipis) tapi komposisinya
sendiri: progresi G-D-Em-C, arpeggio pluck 16-an, pad dengan efek pump, bass offbeat, motif marimba.
Ada breakdown (drum hilang) saat adegan "cuma nunggu" dan chord penutup di akhir.

  python3 render/music.py OUT.wav DURASI_DETIK [--bpm 128] [--break 20.6 24.4]
"""
import argparse

import numpy as np
from scipy.signal import butter, sosfilt

SR = 44100
RNG = np.random.default_rng(7)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def lp(x, fc, order=2):
    return sosfilt(butter(order, fc, "low", fs=SR, output="sos"), x)


def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, "high", fs=SR, output="sos"), x)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "band", fs=SR, output="sos"), x)


def add(buf, start, sig, gain=1.0, pan=0.0):
    i = int(start * SR)
    if i >= buf.shape[1] or i < 0:
        return
    sig = sig[: buf.shape[1] - i]
    lg, rg = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[0, i:i + len(sig)] += sig * gain * lg * 1.414
    buf[1, i:i + len(sig)] += sig * gain * rg * 1.414


# ------------------------------------------------------------------ instrumen
def kick():
    t = np.arange(int(.35 * SR)) / SR
    f = 48 + 110 * np.exp(-t * 32)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 7.5)
    s[:220] += RNG.standard_normal(220) * .25 * np.linspace(1, 0, 220)
    return s


def clap():
    t = np.arange(int(.25 * SR)) / SR
    n = bp(RNG.standard_normal(len(t)), 900, 3200)
    env = np.exp(-t * 16)
    for d in (.0, .011, .022):
        env += np.where(t >= d, np.exp(-(t - d) * 120), 0) * .6
    return n * env * .5


def hat(open_=False):
    t = np.arange(int((.22 if open_ else .06) * SR)) / SR
    n = hp(RNG.standard_normal(len(t)), 7500)
    return n * np.exp(-t * (14 if open_ else 70)) * .35


def harm_tone(f, dur, decay_base, decay_h, nh=10, bright=1.0):
    t = np.arange(int(dur * SR)) / SR
    s = np.zeros_like(t)
    for h in range(1, nh + 1):
        if f * h > 16000:
            break
        s += np.sin(2 * np.pi * f * h * t) / h ** (1.3 / bright) * np.exp(-t * (decay_base + decay_h * h))
    att = np.minimum(1, t / .003)
    return s * att


def pluck(note, dur=.4):
    return harm_tone(midi(note), dur, 7, 2.2, nh=8) * .5


def marimba(note, dur=.6):
    f = midi(note)
    t = np.arange(int(dur * SR)) / SR
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 6) + .35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 22)
    s += .15 * np.sin(2 * np.pi * f * 10 * t) * np.exp(-t * 60)
    return s * np.minimum(1, t / .002) * .55


def saw_pad(note, dur, detune=(-.08, 0, .08)):
    t = np.arange(int(dur * SR)) / SR
    s = np.zeros_like(t)
    for d in detune:
        f = midi(note + d)
        for h in range(1, 13):
            if f * h > 9000:
                break
            s += np.sin(2 * np.pi * f * h * t + RNG.uniform(0, 6.28)) / h
    env = np.minimum(1, t / .25) * np.minimum(1, (dur - t) / .2)
    return lp(s, 2200) * env * .06


def bass_note(note, dur):
    f = midi(note)
    t = np.arange(int(dur * SR)) / SR
    s = np.sin(2 * np.pi * f * t) + .45 * np.sin(2 * np.pi * 2 * f * t) + .2 * np.sin(2 * np.pi * 3 * f * t)
    env = np.minimum(1, t / .005) * np.exp(-t * 3.5) * np.minimum(1, (dur - t) / .02)
    return lp(s, 900) * env * .5


def swell(dur):
    t = np.arange(int(dur * SR)) / SR
    n = RNG.standard_normal(len(t))
    out = np.zeros_like(n)
    steps = 24
    seg = len(n) // steps
    for k in range(steps):
        fc = 600 + 7000 * (k / steps) ** 2
        out[k * seg:(k + 1) * seg] = bp(n[k * seg:(k + 1) * seg], fc * .6, min(fc * 1.6, 18000))
    return out * (t / dur) ** 2 * .18


# ------------------------------------------------------------------ aransemen
# G - D - Em - C (root MIDI di oktaf 3) + nada chord
CHORDS = [
    (43, [55, 59, 62, 67]),   # G
    (38, [54, 57, 62, 66]),   # D
    (40, [55, 59, 64, 67]),   # Em
    (36, [55, 60, 64, 67]),   # C
]
ARP = [0, 1, 2, 3, 2, 1, 2, 3, 0, 2, 1, 3, 2, 1, 0, 1]
MOTIF = [(0, 79), (.75, 78), (1.5, 74), (2.5, 71), (3, 74),            # bar ganjil
         (4, 76), (4.75, 74), (5.5, 71), (6.5, 72), (7, 71)]          # bar genap


# variasi B (video tahu): kunci C mayor, progresi C-G-Am-F, motif lain
CHORDS_B = [
    (36, [55, 60, 64, 67]),   # C
    (43, [55, 59, 62, 67]),   # G
    (45, [57, 60, 64, 69]),   # Am
    (41, [57, 60, 65, 69]),   # F
]
MOTIF_B = [(0, 76), (.5, 79), (1.5, 76), (2, 74), (3, 72),
           (4, 74), (4.5, 76), (5.5, 72), (6.5, 69), (7, 72)]
# variasi C (video hotel): kunci F mayor, progresi F-C-Dm-Bb, motif lebih tenang
CHORDS_C = [
    (41, [57, 60, 65, 69]),   # F
    (36, [55, 60, 64, 67]),   # C
    (38, [57, 62, 65, 69]),   # Dm
    (46, [58, 62, 65, 70]),   # Bb
]
MOTIF_C = [(0, 77), (1, 76), (1.5, 72), (2.5, 69), (3, 72),
           (4, 74), (5, 72), (5.5, 70), (6.5, 69), (7, 65)]
# variasi D (video laundry koin): kunci D mayor, progresi D-Bm-G-A, motif lincah
CHORDS_D = [
    (38, [54, 57, 62, 66]),   # D
    (47, [54, 59, 62, 66]),   # Bm
    (43, [55, 59, 62, 67]),   # G
    (45, [57, 61, 64, 69]),   # A
]
MOTIF_D = [(0, 78), (.5, 81), (1, 78), (1.5, 76), (2.5, 74), (3, 76),
           (4, 74), (4.5, 76), (5, 74), (5.5, 71), (6.5, 73), (7, 69)]
VARIANTS = {"A": None, "B": (CHORDS_B, MOTIF_B), "C": (CHORDS_C, MOTIF_C), "D": (CHORDS_D, MOTIF_D)}


def render(dur, bpm=128.0, brk=(20.6, 24.4)):
    beat = 60.0 / bpm
    bar = 4 * beat
    n_bars = int(np.ceil(dur / bar)) + 1
    buf = np.zeros((2, int((dur + 3) * SR)))
    pad_bus = np.zeros_like(buf)
    K, C, H, HO = kick(), clap(), hat(), hat(True)
    end_bar = int((dur - 2.2) // bar)          # bar terakhir sebelum chord penutup
    b0, b1 = int(round(brk[0] / bar)), int(round(brk[1] / bar))

    for b in range(n_bars):
        t0 = b * bar
        if b > end_bar:
            break
        root, notes = CHORDS[b % 4]
        intro = b < 2
        breakdown = b0 <= b < b1
        # pad
        for nt in notes[:3]:
            add(pad_bus, t0, saw_pad(nt - 12, bar + .2), .9, RNG.uniform(-.4, .4))
        # arpeggio pluck 16-an (+ delay ping-pong)
        if not breakdown or b == b1 - 1:
            for i, idx in enumerate(ARP):
                nt = notes[idx] + (12 if (i // 4) % 2 else 0)
                g = .55 if i % 4 == 0 else .38
                add(buf, t0 + i * beat / 4, pluck(nt), g * (.6 if intro else 1), .25 if i % 2 else -.25)
                add(buf, t0 + i * beat / 4 + .75 * beat, pluck(nt), g * .22, -.6 if i % 2 else .6)
        if intro or breakdown:
            if breakdown:      # breakdown: pluck tipis tiap ketukan, pad saja
                for k in range(4):
                    add(buf, t0 + k * beat, marimba(notes[(k + 1) % 4]), .35, .3 * (-1) ** k)
            if b == b1 - 1 or b == 1:
                add(buf, t0 + bar - 2 * beat, swell(2 * beat), 1.0)
            continue
        # drum
        for k in range(4):
            add(buf, t0 + k * beat, K, .95)
            if k in (1, 3):
                add(buf, t0 + k * beat, C, .55, .1)
            for e in range(2):
                hh = HO if e == 1 else H
                add(buf, t0 + k * beat + e * beat / 2, hh, .5 if e else .32, .35)
            add(buf, t0 + k * beat + .75 * beat, H, .18, -.35)
        # bass offbeat
        for k in range(4):
            add(buf, t0 + k * beat + beat / 2, bass_note(root, beat * .45), .75)
        add(buf, t0, bass_note(root, beat * .4), .6)
        # motif marimba di bagian setelah breakdown
        if b >= b1 and (b - b1) % 4 < 2:
            off = 0 if (b - b1) % 2 == 0 else 4
            for bt, nt in MOTIF:
                if off <= bt < off + 4:
                    add(buf, t0 + (bt - off) * beat, marimba(nt), .5, .2)
        if b % 8 == 7 and b + 1 <= end_bar:
            add(buf, t0 + bar - beat, swell(beat), 1.0)

    # efek pump pada pad (seperti sidechain kick), kecuali saat intro/breakdown
    tt = np.arange(pad_bus.shape[1]) / SR
    phase = (tt % beat) / beat
    pump = 1 - .55 * np.exp(-phase * 7)
    nodrum = (tt < 2 * bar) | ((tt >= b0 * bar) & (tt < b1 * bar))
    pump[nodrum] = 1
    buf += pad_bus * pump

    # chord penutup
    tend = (end_bar + 1) * bar
    root, notes = CHORDS[0]
    add(buf, tend, K, 1.0)
    for nt in notes:
        add(buf, tend, marimba(nt + 12, 2.5), .45, RNG.uniform(-.3, .3))
        add(buf, tend, harm_tone(midi(nt), 2.8, 1.6, .5, nh=8), .35, RNG.uniform(-.5, .5))
    add(buf, tend, bass_note(root, 2.5), .8)

    buf = buf[:, : int(dur * SR)]
    fade = int(.4 * SR)
    buf[:, -fade:] *= np.linspace(1, 0, fade)
    buf = np.tanh(buf * 1.2) / np.tanh(1.2)
    buf /= np.abs(buf).max() / .89
    return buf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("dur", type=float)
    ap.add_argument("--bpm", type=float, default=128.0)
    ap.add_argument("--break", dest="brk", type=float, nargs=2, default=[20.6, 24.4])
    ap.add_argument("--variant", default="A", choices=sorted(VARIANTS))
    a = ap.parse_args()
    import soundfile as sf
    global CHORDS, MOTIF
    if VARIANTS[a.variant]:
        CHORDS, MOTIF = VARIANTS[a.variant]
    sf.write(a.out, render(a.dur, a.bpm, tuple(a.brk)).T, SR, subtype="PCM_16")
    print("wrote", a.out)


if __name__ == "__main__":
    main()
