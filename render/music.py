"""Backsound orisinal (disintesis, bebas hak cipta): upbeat explainer ~128 BPM, kunci G mayor.

Nuansanya dibuat mirip video referensi (ringan, ceria, pluck + pad + beat tipis) tapi komposisinya
sendiri: progresi G-D-Em-C, arpeggio pluck 16-an, pad dengan efek pump, bass offbeat, motif marimba.
Ada breakdown (drum hilang) saat adegan "cuma nunggu" dan chord penutup di akhir.

  python3 render/music.py OUT.wav DURASI_DETIK [--bpm 128] [--break 20.6 24.4]
"""
import argparse
import os

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
# variasi E (video AMDK): kunci A mayor, progresi F#m-D-A-E (vi-IV-I-V), motif lebar & optimis
CHORDS_E = [
    (42, [57, 61, 64, 66]),   # F#m
    (38, [57, 62, 66, 69]),   # D
    (45, [57, 61, 64, 69]),   # A
    (40, [56, 59, 64, 68]),   # E
]
MOTIF_E = [(0, 73), (.5, 76), (1, 78), (2, 76), (2.5, 73), (3, 71),
           (4, 69), (4.5, 71), (5, 73), (6, 76), (6.5, 73), (7, 71)]
# variasi F (video sawit): kunci D minor, progresi Dm-Bb-F-C (i-VI-III-VII), hangat & sedikit reflektif
CHORDS_F = [
    (38, [57, 62, 65, 69]),   # Dm
    (46, [58, 62, 65, 70]),   # Bb
    (41, [57, 60, 65, 69]),   # F
    (36, [55, 60, 64, 67]),   # C
]
MOTIF_F = [(0, 74), (.5, 77), (1, 81), (2, 79), (2.5, 77), (3, 76),
           (4, 74), (4.5, 72), (5, 74), (6, 77), (6.5, 76), (7, 72)]
# variasi G (video bisnis media): gaya beda total, groove hip-hop/business ~94 BPM, lihat render_biz()
VARIANTS = {"M": "doc", "L": "sakura", "K": "vice", "J": "neon", "I": "street", "H": "fest", "G": "biz", "A": None, "B": (CHORDS_B, MOTIF_B), "C": (CHORDS_C, MOTIF_C), "D": (CHORDS_D, MOTIF_D),
            "E": (CHORDS_E, MOTIF_E), "F": (CHORDS_F, MOTIF_F)}


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


# ================================================================== gaya "biz" (varian G)
# Groove hip-hop modern untuk konten bisnis/finansial: electric piano (FM) chord minor 9,
# sub-bass 808 dengan glide, kick-snare tegas, hi-hat 16-an + roll, bell motif, riser & impact.
# Progresi C minor: Cm9 - Abmaj7 - Fm9 - G7sus/G7 (i - VI - iv - V), terdengar percaya diri & serius.
BIZ_CHORDS = [
    (36, [51, 55, 58, 62]),        # Cm9  (Eb G Bb D)
    (44, [51, 55, 60, 63]),        # Abmaj7 (Eb G C Eb)
    (41, [51, 56, 60, 63]),        # Fm9-ish (Eb Ab C Eb) + G di atas
    (43, [53, 55, 59, 62]),        # G7 (F G B D)
]
BIZ_BELL = [(0, 75), (.5, 74), (1, 72), (2, 67), (3, 70),
            (4, 72), (4.5, 70), (5, 68), (6, 67), (7, 74)]
KICK16 = [0, 7, 10]
SNARE16 = [4, 12]


def epiano(note, dur, vel=1.0):
    f = midi(note)
    t = np.arange(int(dur * SR)) / SR
    idx = 1.8 * vel * np.exp(-t * 5) + .25
    mod = np.sin(2 * np.pi * f * t) * idx
    s = np.sin(2 * np.pi * f * t + mod)
    s += .22 * np.sin(2 * np.pi * f * 2 * t + mod * .5) * np.exp(-t * 2.5)
    s += .08 * np.sin(2 * np.pi * f * 14 * t) * np.exp(-t * 40) * vel       # "tine"
    env = np.minimum(1, t / .004) * np.exp(-t * 1.1) * np.minimum(1, (dur - t) / .08)
    return s * env * .22


def bell(note, dur=1.6):
    f = midi(note)
    t = np.arange(int(dur * SR)) / SR
    mod = np.sin(2 * np.pi * f * 3.5 * t) * 1.6 * np.exp(-t * 4)
    s = np.sin(2 * np.pi * f * t + mod) * np.exp(-t * 2.6)
    return s * np.minimum(1, t / .002) * .3


def sub808(note, dur):
    f = midi(note)
    t = np.arange(int(dur * SR)) / SR
    fr = f * (1 + .9 * np.exp(-t * 45))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    s = np.sin(ph) + .18 * np.sin(2 * ph)
    env = np.minimum(1, t / .003) * np.exp(-t * .9) * np.minimum(1, (dur - t) / .03)
    return np.tanh(s * env * 1.6) * .55


def snare():
    t = np.arange(int(.3 * SR)) / SR
    n = bp(RNG.standard_normal(len(t)), 1400, 7000) * np.exp(-t * 17)
    body = np.sin(2 * np.pi * 185 * t) * np.exp(-t * 28)
    return (n * .55 + body * .5) * .8


def rim():
    t = np.arange(int(.08 * SR)) / SR
    return (np.sin(2 * np.pi * 1700 * t) * .6 + bp(RNG.standard_normal(len(t)), 2000, 6000) * .4) * np.exp(-t * 70) * .3


def impact(dur=2.4):
    t = np.arange(int(dur * SR)) / SR
    boom = np.sin(2 * np.pi * (38 + 40 * np.exp(-t * 8)) * t) * np.exp(-t * 2.2)
    n = lp(RNG.standard_normal(len(t)), 3000) * np.exp(-t * 3.5) * .35
    return (boom + n) * .8


def reverb(x, secs=1.8, mix=.22):
    from scipy.signal import fftconvolve
    t = np.arange(int(secs * SR)) / SR
    out = np.zeros_like(x)
    for ch in range(2):
        ir = RNG.standard_normal(len(t)) * np.exp(-t * 3.2)
        ir = lp(ir, 5200)
        ir[: int(.02 * SR)] = 0
        ir /= np.sqrt(np.sum(ir ** 2))
        out[ch] = fftconvolve(x[ch], ir)[: x.shape[1]]
    return x + out * mix


def render_biz(dur, bpm=94.0, brk=(40.0, 45.0)):
    beat = 60.0 / bpm
    bar = 4 * beat
    s16 = beat / 4
    n_bars = int(np.ceil(dur / bar)) + 1
    L = int((dur + 4) * SR)
    dry = np.zeros((2, L))
    keys = np.zeros((2, L))
    end_bar = int((dur - 2.6) // bar)
    b0, b1 = int(round(brk[0] / bar)), int(round(brk[1] / bar))
    K, SN, CL, H, HO = kick(), snare(), clap(), hat(), hat(True)
    for b in range(n_bars):
        if b > end_bar:
            break
        t0 = b * bar
        root, notes = BIZ_CHORDS[b % 4]
        intro = b < 2
        breakdown = b0 <= b < b1
        # electric piano: chord ketukan 1, ulang sinkop di "&" ketukan 2
        for k, (st_, vel, ln) in enumerate(((0, 1.0, 1.9), (1.5 * beat, .7, 1.2), (3.5 * beat, .55, .6))):
            if (intro or breakdown) and k == 2:
                continue
            for i, nt in enumerate(notes):
                add(keys, t0 + st_ + i * .012, epiano(nt, ln * beat + .3, vel), .9, -.35 + .23 * i)
        if b % 4 == 2:
            add(keys, t0, epiano(notes[-1] + 5, 2 * beat), .5, .3)
        if intro or breakdown:
            for bt, nt in BIZ_BELL:
                off = 0 if b % 2 == 0 else 4
                if off <= bt < off + 4 and breakdown:
                    add(keys, t0 + (bt - off) * beat, bell(nt), .55, .25)
            if b == 1 or b == b1 - 1:
                add(dry, t0 + bar - 2 * beat, swell(2 * beat), 1.1)
                for r in range(8):          # snare roll naik
                    add(dry, t0 + bar - 2 * beat + r * beat / 4, SN, .12 + .05 * r, .05)
            continue
        if b == 2 or b == b1:
            add(dry, t0, impact(), .9)
        # drum
        roll = b % 4 == 3
        for i in range(16):
            tt_ = t0 + i * s16
            if i in KICK16 or (b % 2 and i == 13):
                add(dry, tt_, K, 1.0)
            if i in SNARE16:
                add(dry, tt_, SN, .75, .05)
                add(dry, tt_ + .008, CL, .35, -.1)
            if roll and i >= 12:
                for r in range(3):
                    add(dry, tt_ + r * s16 / 3, H, .26, .3)
            else:
                add(dry, tt_, HO if i == 14 else H, (.42, .18, .3, .18)[i % 4] * (1.4 if i == 14 else 1), .3)
            if i in (6, 11) and b % 2 == 0:
                add(dry, tt_, rim(), .7, -.4)
        # 808 mengikuti kick, nada ke-5 di langkah 10
        for i, n_ in ((0, root - 12), (7, root - 12), (10, root - 5 if b % 2 else root - 12)):
            ln = {0: 7, 7: 3, 10: 6}[i] * s16
            add(dry, t0 + i * s16, sub808(n_, ln), .95)
        # bell motif di bagian setelah intro/breakdown (2 dari 4 bar)
        if (b - (b1 if b >= b1 else 2)) % 8 < 2:
            off = 0 if b % 2 == 0 else 4
            for bt, nt in BIZ_BELL:
                if off <= bt < off + 4:
                    add(keys, t0 + (bt - off) * beat, bell(nt), .42, .25)
        if b % 8 == 7 and b + 1 <= end_bar:
            add(dry, t0 + bar - beat, swell(beat), .9)
    # intro: keys di-lowpass (efek "muffled") lalu terbuka saat drum masuk
    ni = int(2 * bar * SR)
    for ch in range(2):
        keys[ch, :ni] = lp(keys[ch, :ni], 900)
    buf = dry + reverb(keys, 2.0, .3)
    tend = (end_bar + 1) * bar
    root, notes = BIZ_CHORDS[0]
    add(buf, tend, impact(3.0), .9)
    add(buf, tend, sub808(root - 12, 2.8), .9)
    for i, nt in enumerate(notes):
        add(buf, tend + i * .03, epiano(nt, 3.0), .9, -.3 + .2 * i)
        add(buf, tend + .4 + i * .09, bell(nt + 12, 2.4), .35, .3 - .2 * i)
    buf = buf[:, : int(dur * SR)]
    fade = int(.5 * SR)
    buf[:, -fade:] *= np.linspace(1, 0, fade)
    buf = np.tanh(buf * 1.1) / np.tanh(1.1)
    buf /= np.abs(buf).max() / .89
    return buf


# ------------------------------------------------------------------ varian H "fest": festival house 124 BPM
# Am - F - C - G (anthem festival), supersaw stab dipompa sidechain, bass offbeat, pluck arp,
# build-up snare + riser sebelum drop, sorak penonton tipis di tiap drop.
FEST_CHORDS = [
    (45, [57, 60, 64, 69]),
    (41, [57, 60, 65, 69]),
    (48, [55, 60, 64, 67]),
    (43, [55, 59, 62, 67]),
]
FEST_ARP = [0, 2, 1, 3, 2, 1, 3, 2]
FEST_LEAD = [(0, 76), (.75, 76), (1.5, 74), (2, 72), (3, 71), (3.5, 72),
             (4, 72), (4.75, 72), (5.5, 71), (6, 69), (7, 67), (7.5, 69)]


def supersaw(note, dur, n=7, spread=.18):
    t = np.arange(int(dur * SR)) / SR
    s = np.zeros_like(t)
    for k in range(n):
        f = midi(note + (k - (n - 1) / 2) * spread / ((n - 1) / 2))
        ph = (f * t + RNG.uniform(0, 1)) % 1.0
        s += 2 * ph - 1
    env = np.minimum(1, t / .006) * np.exp(-t * 2.2) * np.minimum(1, (dur - t) / .03)
    return lp(s / n, 3800) * env * .32


def fest_bass(note, dur):
    f = midi(note)
    t = np.arange(int(dur * SR)) / SR
    ph = (f * t) % 1.0
    s = .6 * np.sin(2 * np.pi * f * t) + .4 * lp(2 * ph - 1, 600)
    env = np.minimum(1, t / .004) * np.exp(-t * 6) * np.minimum(1, (dur - t) / .015)
    return s * env * .55


def crowd(dur):
    """sorak penonton sintetis: banyak 'vokal' noise berformant acak + napas lebar."""
    t = np.arange(int(dur * SR)) / SR
    out = np.zeros_like(t)
    for _ in range(60):
        st_ = RNG.uniform(0, dur * .4)
        ln = RNG.uniform(.6, dur - st_)
        i0, n = int(st_ * SR), int(ln * SR)
        fc = RNG.uniform(500, 1600)
        v = bp(RNG.standard_normal(n), fc * .8, fc * 1.25)
        tt = np.arange(n) / SR
        v *= np.minimum(1, tt / .15) * np.minimum(1, (ln - tt) / .4) * (1 + .3 * np.sin(2 * np.pi * RNG.uniform(3, 7) * tt))
        out[i0:i0 + n] += v * RNG.uniform(.3, 1)
    out += bp(RNG.standard_normal(len(t)), 300, 5000) * .5
    env = np.minimum(1, t / .3) * np.minimum(1, (dur - t) / (dur * .6))
    return out * env * .05


def render_fest(dur, bpm=124.0, brk=(46.4, 54.2)):
    beat = 60.0 / bpm
    bar = 4 * beat
    s16 = beat / 4
    n_bars = int(np.ceil(dur / bar)) + 1
    L = int((dur + 4) * SR)
    dry = np.zeros((2, L))
    syn = np.zeros((2, L))
    end_bar = int((dur - 2.6) // bar)
    b0, b1 = int(round(brk[0] / bar)), int(round(brk[1] / bar))
    K, SN, CL, H, HO = kick(), snare(), clap(), hat(), hat(True)
    kick_times = []
    for b in range(n_bars):
        if b > end_bar:
            break
        t0 = b * bar
        root, notes = FEST_CHORDS[b % 4]
        intro = b < 2
        breakdown = b0 <= b < b1
        # pad (selalu), lebih tipis saat full
        for i, nt in enumerate(notes):
            add(syn, t0, saw_pad(nt, bar + .1), 1.0 if (intro or breakdown) else .55, -.4 + .27 * i)
        # pluck arp 8-an
        for k in range(8):
            nt = notes[FEST_ARP[k]] + 12
            add(syn, t0 + k * beat / 2, pluck(nt, .35), .55 if not intro else .4, .35 if k % 2 else -.35)
        if intro or breakdown:
            if b == 1 or b == b1 - 1:          # build-up: snare roll makin rapat + riser
                add(dry, t0, swell(bar), 1.4)
                for r in range(16):
                    add(dry, t0 + r * s16, SN, .08 + .035 * r, .05)
            if breakdown and b < b1 - 1:
                add(dry, t0, K, .55)            # detak jantung pelan
            continue
        if b == 2 or b == b1:
            add(dry, t0, impact(), .8)
            add(dry, t0, crowd(3.5), 1.0)
        # drum four-on-the-floor
        for i in range(16):
            tt_ = t0 + i * s16
            if i % 4 == 0:
                add(dry, tt_, K, 1.0)
                kick_times.append(tt_)
            if i in (4, 12):
                add(dry, tt_, CL, .9, -.05)
                add(dry, tt_, SN, .35, .05)
            if i % 4 == 2:
                add(dry, tt_, HO, .36, .25)
            elif i % 2 == 1:
                add(dry, tt_, H, .18, -.25)
        # bass offbeat
        for k in range(4):
            add(dry, t0 + k * beat + beat / 2, fest_bass(root - 12 if k != 3 or b % 2 == 0 else root - 5, beat * .45), .9)
        # supersaw stab offbeat (dipompa)
        for k in range(4):
            for i, nt in enumerate(notes):
                add(syn, t0 + k * beat + beat / 2, supersaw(nt, beat * .48), .5, -.5 + .33 * i)
        # lead hook: 2 bar setiap 4 bar, setelah drop
        rel = b - (b1 if b >= b1 else 2)
        if rel % 8 < 4:
            off = 0 if rel % 2 == 0 else 4
            for bt, nt in FEST_LEAD:
                if off <= bt < off + 4:
                    add(syn, t0 + (bt - off) * beat, pluck(nt, .5), .6, .15)
                    add(syn, t0 + (bt - off) * beat, bell(nt + 12, .8), .14, -.2)
        if b % 8 == 7 and b + 1 <= end_bar and b + 1 != b0:
            add(dry, t0 + bar - beat, swell(beat), .9)
    # sidechain pumping pada synth
    pump = np.ones(L)
    rel_n = int(beat * .8 * SR)
    curve = 1 - .7 * np.exp(-np.arange(rel_n) / (rel_n * .25))
    for kt in kick_times:
        i = int(kt * SR)
        n = min(rel_n, L - i)
        pump[i:i + n] = np.minimum(pump[i:i + n], curve[:n])
    syn *= pump
    ni = int(2 * bar * SR)
    for ch in range(2):
        syn[ch, :ni] = lp(syn[ch, :ni], 1100)
    buf = dry + reverb(syn, 1.6, .25)
    tend = (end_bar + 1) * bar
    root, notes = FEST_CHORDS[0]
    add(buf, tend, impact(3.0), .9)
    add(buf, tend, crowd(3.0), 1.0)
    for i, nt in enumerate(notes):
        add(buf, tend + i * .02, supersaw(nt, 3.0), .6, -.4 + .27 * i)
    buf = buf[:, : int(dur * SR)]
    fade = int(.5 * SR)
    buf[:, -fade:] *= np.linspace(1, 0, fade)
    buf = np.tanh(buf * 1.1) / np.tanh(1.1)
    buf /= np.abs(buf).max() / .89
    return buf

# ------------------------------------------------------------------ varian I "street": funk jalanan ~96 BPM
# Groove boom-bap swing yang jenaka untuk cerita "jalanan": clavinet stab, bass jari bergerak,
# shaker, motif PELUIT (suara siulan sintetis), peluit parkir "prit-prit-priiit" di awal.
# Progresi F mayor jazzy: Dm9 - G13 - Cmaj9 - A7(b9) (ii - V - I - VI).
# Breakdown (bagian "uangnya ke mana"): drum setengah-tempo & teredam, keys minor, lalu drop
# saat "Pelajarannya".
STREET_CHORDS = [
    (38, [53, 57, 60, 64]),        # Dm9  (F A C E)
    (43, [53, 59, 64, 65]),        # G13  (F B E F)
    (36, [52, 55, 59, 62]),        # Cmaj9 (E G B D)
    (33, [55, 58, 61, 64]),        # A7b9 (G Bb C# E)
]
STREET_DARK = [
    (38, [53, 57, 60, 65]),        # Dm
    (34, [53, 58, 62, 65]),        # Bb
    (36, [52, 55, 60, 64]),        # C
    (33, [52, 57, 61, 64]),        # A
]
STREET_WHISTLE = [(0, 81), (.5, 84), (1, 86), (1.75, 84), (2.5, 81), (3, 79),
                  (4, 81), (4.5, 84), (5, 88), (5.75, 86), (6.5, 84), (7, 81)]
STREET_BASS = [(0, 0, .7), (.75, 0, .2), (1.5, 7, .4), (2, 12, .3), (2.5, 10, .3), (3, 7, .4), (3.5, 5, .4)]


def whistle(note, dur, vib=6.0):
    f = midi(note)
    t = np.arange(int(dur * SR)) / SR
    fr = f * (1 + .012 * np.sin(2 * np.pi * vib * t) * np.minimum(1, t / .12)) * (1 - .03 * np.exp(-t * 40))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    s = np.sin(ph) + .06 * np.sin(2 * ph)
    breath = bp(RNG.standard_normal(len(t)), f * .9, f * 1.15) * .25
    env = np.minimum(1, t / .025) * np.minimum(1, (dur - t) / .05) * (.85 + .15 * np.exp(-t * 3))
    return (s + breath) * env * .22


def parking_whistle():
    """peluit parkir: prit - prit - priiit (bola di dalam peluit = getaran frekuensi cepat)."""
    out = []
    for ln, gap in ((.12, .08), (.12, .1), (.55, 0)):
        t = np.arange(int(ln * SR)) / SR
        f = 2900 * (1 + .04 * np.sign(np.sin(2 * np.pi * 38 * t)))
        ph = 2 * np.pi * np.cumsum(f) / SR
        s = np.sin(ph) + .3 * bp(RNG.standard_normal(len(t)), 2500, 3400)
        env = np.minimum(1, t / .008) * np.minimum(1, (ln - t) / .03)
        out += [s * env * .3, np.zeros(int(gap * SR))]
    return np.concatenate(out)


def clav(note, dur, vel=1.0):
    f = midi(note)
    t = np.arange(int(dur * SR)) / SR
    ph = (f * t) % 1.0
    s = np.where(ph < .25, 1.0, -.33) + .4 * np.sin(2 * np.pi * f * t)
    s = bp(s, 300, 3200 * (.6 + .4 * vel))
    env = np.minimum(1, t / .002) * np.exp(-t * 9) * np.minimum(1, (dur - t) / .01)
    return s * env * .14 * vel


def finger_bass(note, dur):
    f = midi(note)
    t = np.arange(int(dur * SR)) / SR
    s = np.sin(2 * np.pi * f * t) + .35 * np.sin(4 * np.pi * f * t) * np.exp(-t * 8) + .12 * np.sin(6 * np.pi * f * t) * np.exp(-t * 14)
    env = np.minimum(1, t / .004) * np.exp(-t * 3) * np.minimum(1, (dur - t) / .02)
    return np.tanh(s * env * 1.3) * .5


def shaker():
    t = np.arange(int(.09 * SR)) / SR
    return hp(RNG.standard_normal(len(t)), 5500) * np.minimum(1, t / .012) * np.exp(-t * 45) * .25


def render_street(dur, bpm=96.0, brk=(21.8, 41.3)):
    beat = 60.0 / bpm
    bar = 4 * beat
    sw = beat / 4 * 1.18                       # 16-an swing: ketukan genap mundur sedikit
    def s16(i):
        return (i // 2) * beat / 2 + (i % 2) * sw
    n_bars = int(np.ceil(dur / bar)) + 1
    L = int((dur + 4) * SR)
    dry = np.zeros((2, L))
    keys = np.zeros((2, L))
    end_bar = int((dur - 2.6) // bar)
    b0, b1 = int(round(brk[0] / bar)), int(round(brk[1] / bar))
    K, SN, H, HO = kick(), snare(), hat(), hat(True)
    add(dry, .05, parking_whistle(), .55, .15)
    for b in range(n_bars):
        if b > end_bar:
            break
        t0 = b * bar
        intro = b < 1
        breakdown = b0 <= b < b1
        root, notes = (STREET_DARK if breakdown else STREET_CHORDS)[b % 4]
        # clavinet: stab sinkop funky
        stabs = ((0, 1.0), (6, .7), (10, .8), (14, .6)) if not breakdown else ((0, .8), (10, .5))
        for i, vel in stabs:
            for j, nt in enumerate(notes):
                add(keys, t0 + s16(i) + j * .006, clav(nt, beat * .45, vel), 1.0, -.3 + .2 * j)
        add(keys, t0, epiano(notes[0] - 12, bar * .9, .5), .5, 0)
        if breakdown:
            for k in (0, 2):
                add(keys, t0 + k * beat, bell(notes[(k + 2) % 4] + 12, 1.4), .3, .3)
        if intro:
            for k in range(8):
                add(dry, t0 + k * beat / 2, shaker(), .8, .3)
            add(dry, t0 + bar - beat, swell(beat), .8)
            continue
        if b == 1 or b == b1:
            add(dry, t0, impact(), .75)
        if breakdown:
            # setengah tempo, teredam
            add(dry, t0, K, .7)
            add(dry, t0 + 2 * beat, SN, .35, .05)
            for k in range(4):
                add(dry, t0 + k * beat, H, .12, .3)
            add(dry, t0, finger_bass(root - 12, bar * .9), .55)
            if b == b1 - 1:
                add(dry, t0 + bar - 2 * beat, swell(2 * beat), 1.0)
                for r in range(8):
                    add(dry, t0 + bar - 2 * beat + r * beat / 4, SN, .1 + .05 * r, .05)
            continue
        # drum boom-bap swing
        for i in range(16):
            tt_ = t0 + s16(i)
            if i in (0, 7, 10) or (b % 2 and i == 15):
                add(dry, tt_, K, .95)
            if i in (4, 12):
                add(dry, tt_, SN, .8, .05)
            if i % 2 == 0:
                add(dry, tt_, HO if i == 14 and b % 2 else H, .34 if i % 4 == 0 else .22, .3)
            add(dry, tt_, shaker(), .36 if i % 2 else .22, -.35)
            if i in (3, 13) and b % 2 == 0:
                add(dry, tt_, rim(), .5, -.4)
        # bass jari bergerak
        for bt, iv, ln in STREET_BASS:
            add(dry, t0 + bt * beat, finger_bass(root + iv - 12 + (0 if iv < 12 else 0), ln * beat + .05), .8)
        # motif peluit: 2 dari tiap 4 bar (setelah intro & setelah drop)
        ref = b1 if b >= b1 else 1
        if (b - ref) % 4 < 2:
            off = 0 if (b - ref) % 2 == 0 else 4
            for bt, nt in STREET_WHISTLE:
                if off <= bt < off + 4:
                    nxt = [x for x, _ in STREET_WHISTLE if x > bt]
                    ln = min(((nxt[0] if nxt else 8) - bt) * beat * .9, .6)
                    add(keys, t0 + (bt - off) * beat, whistle(nt, ln), .55, .2)
        if b % 8 == 7 and b + 1 <= end_bar:
            add(dry, t0 + bar - beat, swell(beat), .8)
    # breakdown: keys sedikit teredam
    i0, i1 = int(b0 * bar * SR), int(b1 * bar * SR)
    for ch in range(2):
        keys[ch, i0:i1] = lp(keys[ch, i0:i1], 1400)
        dry[ch, i0:i1] = lp(dry[ch, i0:i1], 2500)
    buf = dry + reverb(keys, 1.6, .25)
    tend = (end_bar + 1) * bar
    root, notes = STREET_CHORDS[2]
    add(buf, tend, impact(2.6), .7)
    add(buf, tend, finger_bass(root - 12, 2.6), .9)
    for i, nt in enumerate(notes):
        add(buf, tend + i * .02, epiano(nt, 2.8), .9, -.3 + .2 * i)
    add(buf, tend + .3, parking_whistle(), .45, .15)
    buf = buf[:, : int(dur * SR)]
    fade = int(.5 * SR)
    buf[:, -fade:] *= np.linspace(1, 0, fade)
    buf = np.tanh(buf * 1.1) / np.tanh(1.1)
    buf /= np.abs(buf).max() / .89
    return buf


NEON_CHORDS = [  # F minor: Fm - Db - Ab - Eb (root bass, nada pad)
    (41, [65, 68, 72, 75]), (37, [61, 65, 68, 72]), (44, [63, 68, 72, 75]), (39, [62, 67, 70, 75])]
NEON_ARP = [0, 2, 1, 3, 2, 1, 3, 2]
NEON_LEAD = [(0, 77), (.75, 80), (1.5, 79), (2, 75), (3, 77), (4, 72), (4.75, 75), (5.5, 77), (6, 80), (7, 79)]


def gated_snare():
    """snare 80-an: badan + derau panjang yang dipotong (gated reverb)."""
    t = np.arange(int(.42 * SR)) / SR
    n = bp(RNG.standard_normal(len(t)), 900, 8000)
    gate = np.where(t < .26, 1.0, np.exp(-(t - .26) * 60))
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 26)
    return (n * .5 * np.exp(-t * 4) * gate + body * .55) * .75


def pulse_bass(note, dur, cutoff=1100):
    f = midi(note)
    t = np.arange(int(dur * SR)) / SR
    s = np.zeros_like(t)
    for d in (-.06, .06):
        ph = (f * (2 ** (d / 12)) * t) % 1.0
        s += 2 * ph - 1
    env = np.minimum(1, t / .004) * np.exp(-t * 5) * np.minimum(1, (dur - t) / .01)
    return lp(s * .5, cutoff) * env * .55


def tick_clock():
    t = np.arange(int(.03 * SR)) / SR
    return hp(RNG.standard_normal(len(t)), 4000) * np.exp(-t * 220) * .5


def render_neon(dur, bpm=100.0, marks=(8.85, 24.47, 29.38, 46.70, 51.26, 64.40)):
    """synthwave gelap. marks = drop1, break1, drop2, break2, drop3, outro(CTA).
    Ketukan dijangkar ulang di tiap awal bagian, jadi drop jatuh pas di kata kuncinya."""
    beat = 60.0 / bpm
    L = int((dur + 4) * SR)
    dry = np.zeros((2, L))
    syn = np.zeros((2, L))
    d1, b1, d2, b2, d3, oc = marks
    end = dur
    secs = [(0.0, d1, "intro"), (d1, b1, "main"), (b1, d2, "break"), (d2, b2, "main2"), (b2, d3, "break2"),
            (d3, oc, "main3"), (oc, end, "outro")]
    K, SN, H, HO = kick(), gated_snare(), hat(), hat(True)
    for s0, s1, kind in secs:
        nb = int(np.ceil((s1 - s0) / beat))
        for bt in range(nb):
            t0 = s0 + bt * beat
            if t0 >= s1 - .02:
                break
            ci = (bt // 4) % 4
            root, notes = NEON_CHORDS[ci]
            if bt % 4 == 0:
                bar_len = min(4 * beat, s1 - t0)
                pad = sum(saw_pad(n_, bar_len + .3) for n_ in notes)
                add(syn, t0, pad, .9 if kind not in ("break", "break2") else 1.1, 0)
            if kind == "intro":
                for k in range(2):
                    add(dry, t0 + k * beat / 2, pulse_bass(root, beat / 2 * .9, 500 + 1400 * (t0 / s1)), .7)
                for k in range(4):
                    add(dry, t0 + k * beat / 4, tick_clock(), .5 if k == 0 else .25, .4)
                if bt % 2 == 0:
                    add(dry, t0, K, .45)
                continue
            if kind in ("break", "break2"):
                if bt == 0:
                    add(dry, t0, impact(2.8), .9)
                    add(dry, t0, sub808(root - 12, 2.5), .8)
                for k in range(2):
                    add(dry, t0 + k * beat / 2, tick_clock(), .35, -.3)
                arp = notes[NEON_ARP[bt % 8]] + 12
                add(syn, t0, bell(arp, 1.2), .25, .3)
                continue
            outro = kind == "outro"
            # drum
            add(dry, t0, K, .95 if not outro else .7)
            if bt % 2 == 1:
                add(dry, t0, SN, .8 if not outro else .55, .05)
            for k in range(4):
                add(dry, t0 + k * beat / 4, HO if k == 2 else H, .28 if k == 2 else .2, .3)
            # bass oktaf 8-an
            for k in range(2):
                add(dry, t0 + k * beat / 2, pulse_bass(root + (12 if k else 0), beat / 2 * .85), .85)
            # arpeggio 16-an
            if not outro or bt % 2 == 0:
                for k in range(4):
                    nt = notes[NEON_ARP[(bt * 4 + k) % 8] % 4] + 12
                    add(syn, t0 + k * beat / 4, pluck(nt, beat * .5), .32, -.35 + .7 * (k % 2))
            # lead di main2 & main3 (2 bar dari tiap 4)
            if kind in ("main2", "main3") and (bt // 8) % 2 == 0:
                for lt, ln in NEON_LEAD:
                    if bt % 8 <= lt < bt % 8 + 1:
                        nxt = [x for x, _ in NEON_LEAD if x > lt]
                        L_ = ((nxt[0] if nxt else 8) - lt) * beat * .95
                        add(syn, t0 + (lt - bt % 8) * beat, supersaw(ln, L_), .55, .1)
        # transisi: riser + snare roll menjelang drop
        if kind in ("intro", "break", "break2"):
            rl = min(2.0, s1 - s0 - .2)
            add(dry, s1 - rl, swell(rl), 1.1)
            if kind != "intro":
                for r in range(8):
                    add(dry, s1 - 2 * beat + r * beat / 4, SN, .12 + .06 * r, .05)
        if kind in ("main", "main2", "main3"):
            add(dry, s0, impact(2.4), .8)
            add(dry, s0, sub808(NEON_CHORDS[0][0] - 12, 1.6), .7)
    # bagian break & intro: synth diredam
    for s0, s1, kind in secs:
        if kind in ("intro", "break", "break2"):
            i0, i1 = int(s0 * SR), int(s1 * SR)
            for ch in range(2):
                syn[ch, i0:i1] = lp(syn[ch, i0:i1], 900 if kind != "intro" else 1400)
    buf = dry + reverb(syn, 2.2, .3)
    root, notes = NEON_CHORDS[0]
    tend = end - 2.2
    add(buf, tend, impact(2.4), .6)
    buf = buf[:, : int(dur * SR)]
    fade = int(1.2 * SR)
    buf[:, -fade:] *= np.linspace(1, 0, fade)
    buf = np.tanh(buf * 1.1) / np.tanh(1.1)
    buf /= np.abs(buf).max() / .89
    return buf



# ================================================================== VICE (nuansa GTA VI / Leonida, orisinal)
VICE_CHORDS = [  # F# minor: F#m9 - Dmaj7 - Bm9 - C#7  (bass root, voicing Rhodes)
    (42, [57, 61, 64, 68]), (38, [54, 57, 61, 66]), (35, [54, 57, 62, 66]), (37, [53, 56, 59, 65])]
VICE_HOOK = [(0, 73), (.5, 76), (1, 78), (1.75, 76), (2.5, 73), (3, 71), (4, 69), (4.5, 71), (5, 73), (6, 76),
             (6.75, 78), (7.25, 80)]


def sax(note, dur, vib=5.2):
    """lead mirip saksofon 80-an: gergaji ber-vibrato + filter + napas."""
    f = midi(note)
    t = np.arange(int(dur * SR)) / SR
    fv = f * (1 + .006 * np.sin(2 * np.pi * vib * t) * np.minimum(1, t / .25))
    ph = 2 * np.pi * np.cumsum(fv) / SR
    s = sum(np.sin(k * ph) / k ** 1.15 for k in range(1, 12))
    s = lp(s, 2600)
    br = bp(RNG.standard_normal(len(t)), 1200, 4000) * .06
    env = np.minimum(1, t / .05) * np.minimum(1, (dur - t) / .08)
    return (s * .22 + br) * env


def brass_stab(notes, dur=.42):
    """stab brass synth (tiupan pendek, filter membuka cepat)."""
    t = np.arange(int(dur * SR)) / SR
    out = np.zeros_like(t)
    for n_ in notes:
        for dt in (-.06, .06):
            f = midi(n_) * (1 + dt / 12)
            out += 2 * ((t * f) % 1) - 1
    out = lp(out, 2400) * np.exp(-t * 5) * np.minimum(1, t / .008)
    return out * .09


def glide808(n0, n1, dur):
    """808 meluncur dari n0 ke n1 (khas trap)."""
    t = np.arange(int(dur * SR)) / SR
    f = midi(n0) + (midi(n1) - midi(n0)) * np.minimum(1, t / .12)
    ph = 2 * np.pi * np.cumsum(f) / SR
    env = np.minimum(1, t / .003) * np.exp(-t * .8) * np.minimum(1, (dur - t) / .03)
    return np.tanh((np.sin(ph) + .2 * np.sin(2 * ph)) * env * 1.8) * .55


def render_vice(dur, bpm=92.0, marks=(8.85, 24.47, 29.38, 46.70, 51.26, 64.40)):
    """backsound orisinal nuansa GTA VI: Rhodes + bass 808 + drum hip-hop (snare gated 80-an) + stab brass +
    lead saksofon synth. marks = drop1, break1, drop2, break2, drop3, outro (dijangkar ke kata kunci)."""
    beat = 60.0 / bpm
    L = int((dur + 4) * SR)
    dry = np.zeros((2, L))
    syn = np.zeros((2, L))
    d1, b1, d2, b2, d3, oc = marks
    secs = [(0.0, d1, "intro"), (d1, b1, "main"), (b1, d2, "break"), (d2, b2, "main2"), (b2, d3, "break2"),
            (d3, oc, "main3"), (oc, dur, "outro")]
    K, SN, CL, H, HO = kick(), gated_snare(), clap(), hat(), hat(True)
    for s0, s1, kind in secs:
        nb = int(np.ceil((s1 - s0) / beat))
        for bt in range(nb):
            t0 = s0 + bt * beat
            if t0 >= s1 - .02:
                break
            ci = (bt // 4) % 4
            root, notes = VICE_CHORDS[ci]
            brk = kind in ("break", "break2")
            if bt % 4 == 0:
                bl = min(4 * beat, s1 - t0)
                for j, n_ in enumerate(notes):                    # Rhodes sedikit digeser (strum)
                    add(syn, t0 + .012 * j, epiano(n_, bl + .2, .9), .85 if not brk else 1.0, -.25 + .17 * j)
                if kind in ("main", "main2", "main3") and bt % 8 == 0:
                    add(syn, t0, brass_stab([n_ + 12 for n_ in notes[:3]]), .9, .1)
                    add(syn, t0 + beat * 1.5, brass_stab([n_ + 12 for n_ in notes[1:4]], .3), .6, -.1)
            if kind == "intro":
                if bt % 2 == 0:
                    add(dry, t0, K, .4)
                for k in range(2):
                    add(dry, t0 + k * beat / 2, H, .14, .35)
                if bt % 4 == 0:
                    add(dry, t0, sub808(root - 12, beat * 3.6), .45)
                continue
            if brk:
                if bt == 0:
                    add(dry, t0, impact(2.8), .85)
                    add(dry, t0, sub808(root - 12, 2.6), .8)
                if bt % 2 == 0:
                    add(dry, t0, K, .3)
                add(dry, t0 + beat / 2, rim(), .35, .2)
                continue
            outro = kind == "outro"
            bar_b = bt % 4
            # kick hip-hop: 1, (1&), 3-and-a-bit; snare gated + clap di 2 & 4
            if bar_b in (0, 2):
                add(dry, t0, K, .95 if not outro else .7)
            if bar_b == 0:
                add(dry, t0 + beat * .75, K, .55)
            if bar_b == 2 and (bt // 4) % 2 == 1:
                add(dry, t0 + beat * .5, K, .5)
            if bar_b in (1, 3):
                add(dry, t0, SN, .7 if not outro else .5, .05)
                add(dry, t0, CL, .45, -.05)
            # hat 8-an + roll 16-an/32-an di akhir tiap 2 bar
            roll = (bt % 8 == 7) and not outro
            n_h = 8 if roll else 2
            for k in range(n_h):
                add(dry, t0 + k * beat / n_h, H, .2 if k % 2 == 0 else .13, .3)
            if bar_b == 3 and not roll:
                add(dry, t0 + beat * .5, HO, .18, .3)
            # 808 mengikuti akar, meluncur ke akar berikut di ketuk 4
            if bar_b == 0:
                add(dry, t0, sub808(root - 12, beat * 2.9), .8)
            if bar_b == 3:
                nroot = VICE_CHORDS[((bt + 1) // 4) % 4][0]
                add(dry, t0 + beat * .5, glide808(root - 12, nroot - 12, beat * .55), .55)
            # lead saksofon di main2 & main3 (2 bar dari tiap 4)
            if kind in ("main2", "main3") and (bt // 8) % 2 == 0:
                for lt, ln in VICE_HOOK:
                    if bt % 8 <= lt < bt % 8 + 1:
                        nxt = [x for x, _ in VICE_HOOK if x > lt]
                        L_ = ((nxt[0] if nxt else 8) - lt) * beat * .92
                        add(syn, t0 + (lt - bt % 8) * beat, sax(ln, L_), .9, .15)
            # pluck tipis (gitar chorus) di main
            if kind == "main" and bt % 2 == 1:
                add(syn, t0 + beat / 2, pluck(notes[(bt // 2) % 4] + 12, beat * .6), .22, .4)
        if kind in ("intro", "break", "break2"):
            rl = min(2.0, s1 - s0 - .2)
            add(dry, s1 - rl, swell(rl), 1.0)
            if kind != "intro":
                for r in range(8):
                    add(dry, s1 - 2 * beat + r * beat / 4, SN, .1 + .05 * r, .05)
        if kind in ("main", "main2", "main3"):
            add(dry, s0, impact(2.4), .75)
    for s0, s1, kind in secs:
        if kind in ("intro", "break", "break2"):
            i0, i1 = int(s0 * SR), int(s1 * SR)
            for ch in range(2):
                syn[ch, i0:i1] = lp(syn[ch, i0:i1], 1100 if kind != "intro" else 1800)
    buf = dry + reverb(syn, 2.0, .28)
    add(buf, dur - 2.2, impact(2.4), .55)
    buf = buf[:, : int(dur * SR)]
    fade = int(1.4 * SR)
    buf[:, -fade:] *= np.linspace(1, 0, fade)
    buf = np.tanh(buf * 1.1) / np.tanh(1.1)
    buf /= np.abs(buf).max() / .89
    return buf

# ================================================================== SAKURA (berita tegang -> pop Jepang -> tenang)
SK_DARK = [(40, [52, 55, 59, 64]), (36, [52, 55, 60, 64]), (33, [52, 57, 60, 64]), (35, [51, 54, 59, 63])]  # Em C Am B
SK_POP = [(43, [55, 59, 62, 66]), (38, [54, 57, 62, 66]), (40, [55, 59, 62, 64]), (36, [55, 60, 64, 67])]  # G D Em C
SK_RES = [(40, [55, 59, 64, 66]), (36, [55, 60, 64, 67]), (43, [55, 59, 62, 67]), (38, [54, 57, 62, 66])]  # Em9 C G D
KOTO = [79, 78, 76, 74, 76, 71, 74, 76, 79, 81, 79, 76, 74, 71, 74, 76]   # pentatonik G (nuansa Jepang)


def koto(note, dur=.7):
    """petikan mirip koto: harmonik terang, peluruhan cepat, sedikit 'tekuk' nada di awal."""
    f = midi(note)
    t = np.arange(int(dur * SR)) / SR
    fb = f * (1 + .012 * np.exp(-t * 30))
    ph = 2 * np.pi * np.cumsum(fb) / SR
    s = sum(np.sin(k * ph) * np.exp(-t * (4 + 2.2 * k)) / k ** .8 for k in range(1, 9))
    return s * np.minimum(1, t / .002) * .32


def news_sting(dur=1.6):
    """sting 'breaking news': dua nada sinus bertumpuk + noise sapuan."""
    t = np.arange(int(dur * SR)) / SR
    s = (np.sin(2 * np.pi * midi(76) * t) + .7 * np.sin(2 * np.pi * midi(83) * t)) * np.exp(-t * 2.5)
    return s * .25 * np.minimum(1, t / .004)


def chord_wobble(notes, dur, rate):
    """chord future-bass: supersaw dengan volume 'wobble' (sidechain) tiap rate detik."""
    s = sum(supersaw(n_, dur) for n_ in notes)
    t = np.arange(len(s)) / SR
    g = .35 + .65 * np.minimum(1, ((t % rate) / rate) * 3)
    return lp(s * g, 4200) * .55


def render_sakura(dur, bpm=96.0, marks=(6.3, 18.68, 20.55, 30.68, 34.64, 43.67, 60.62)):
    """intro tegang (jam berdetak) -> trap gelap (fatwa) -> jeda (siapa kena?) -> trap gelap (PHK) -> riser ->
    pop Jepang terang (campaign pink sakura: koto + future bass) -> tegas-tenang (respons krisis) -> outro lembut."""
    beat = 60.0 / bpm
    L = int((dur + 4) * SR)
    dry = np.zeros((2, L))
    syn = np.zeros((2, L))
    m = list(marks)
    kinds = ["intro", "dark", "brk", "dark2", "rise", "pop", "res", "outro"]
    bounds = [0.0] + m + [dur]
    secs = [(bounds[i], bounds[i + 1], kinds[i]) for i in range(len(kinds))]
    K, SN, CL, H, HO = kick(), gated_snare(), clap(), hat(), hat(True)
    for s0, s1, kind in secs:
        prog = SK_POP if kind == "pop" else SK_RES if kind in ("res", "outro") else SK_DARK
        nb = int(np.ceil((s1 - s0) / beat))
        for bt in range(nb):
            t0 = s0 + bt * beat
            if t0 >= s1 - .02:
                break
            root, notes = prog[(bt // 4) % 4]
            bb = bt % 4
            if bb == 0:
                bl = min(4 * beat, s1 - t0) + .25
                if kind == "pop":
                    add(syn, t0, chord_wobble([n_ + 12 for n_ in notes], bl, beat / 2), .8)
                elif kind in ("res", "outro"):
                    for j, n_ in enumerate(notes):
                        add(syn, t0 + .015 * j, epiano(n_, bl, .85), .9, -.3 + .2 * j)
                    add(syn, t0, sum(saw_pad(n_, bl) for n_ in notes[:3]), .35)
                else:
                    add(syn, t0, sum(saw_pad(n_, bl) for n_ in notes), .55 if kind != "intro" else .4)
            if kind == "intro":
                add(dry, t0, tick_clock(), .55, .3)
                add(dry, t0 + beat / 2, tick_clock(), .3, -.3)
                if bb == 0:
                    add(dry, t0, K, .55)                                   # detak jantung
                    add(dry, t0 + .22, K, .35)
                    add(dry, t0, sub808(root - 12, beat * 3.5), .5)
                if bt == 0:
                    add(dry, t0, news_sting(), .8)
                continue
            if kind in ("brk", "rise"):
                if bt == 0:
                    add(dry, t0, impact(2.6), .85)
                    add(dry, t0, sub808(root - 12, 2.4), .75)
                add(dry, t0, tick_clock(), .35, .2)
                add(syn, t0, bell(notes[bt % 4] + 12, 1.0), .2, .3)
                continue
            if kind in ("dark", "dark2"):
                # trap setengah-tempo: kick 1 & 2-and, snare 3, hat 8-an/16-an bergulir
                if bb == 0:
                    add(dry, t0, K, .95)
                    add(dry, t0, sub808(root - 12, beat * 1.8), .85)
                if bb == 1:
                    add(dry, t0 + beat / 2, K, .6)
                    add(dry, t0 + beat / 2, sub808(root - 12, beat * 1.2), .6)
                if bb == 2:
                    add(dry, t0, SN, .8, .05)
                    add(dry, t0, CL, .4, -.05)
                n_h = 4 if (bt % 8 in (6, 7)) else 2
                for k in range(n_h):
                    add(dry, t0 + k * beat / n_h, H, .2 if k % 2 == 0 else .12, .3)
                if bt % 2 == 1:
                    add(syn, t0, pluck(notes[(bt // 2) % 4] + 12, beat * .8), .2, -.4)
                continue
            if kind == "pop":
                # four-on-the-floor ringan + clap, koto pentatonik 8-an, bass oktaf
                add(dry, t0, K, .85)
                if bb in (1, 3):
                    add(dry, t0, CL, .6, .05)
                    add(dry, t0, SN, .35)
                for k in range(2):
                    add(dry, t0 + k * beat / 2 + (beat / 4 if k else 0) * 0, HO if k else H, .16, .3)
                    add(syn, t0 + k * beat / 2, koto(KOTO[(bt * 2 + k) % 16], .6), .75, -.35 + .7 * k)
                    add(dry, t0 + k * beat / 2, pulse_bass(root + (12 if k else 0), beat / 2 * .8, 900), .7)
                continue
            outro = kind == "outro"
            # 'res': hip-hop mantap, tenang
            if bb in (0, 2):
                add(dry, t0, K, .85 if not outro else .5)
            if bb == 0 and not outro:
                add(dry, t0 + beat * .75, K, .45)
            if bb in (1, 3):
                add(dry, t0, SN, .55 if not outro else .3, .05)
            for k in range(2):
                add(dry, t0 + k * beat / 2, H, .15 if not outro else .09, .3)
            if bb == 0:
                add(dry, t0, sub808(root - 12, beat * 3.2), .7 if not outro else .45)
            if not outro and bt % 2 == 0:
                add(syn, t0 + beat / 2, koto(notes[(bt // 2) % 4] + 12, .8), .35, .4)
        if kind in ("intro", "brk", "rise"):
            rl = min(2.2 if kind == "rise" else 1.4, s1 - s0 - .2)
            add(dry, s1 - rl, swell(rl), 1.15 if kind == "rise" else .8)
            if kind != "intro":
                for r in range(8):
                    add(dry, s1 - 2 * beat + r * beat / 4, SN, .1 + .06 * r, .05)
        if kind in ("dark", "dark2", "pop", "res"):
            add(dry, s0, impact(2.4), .8)
    for s0, s1, kind in secs:
        if kind in ("intro", "brk", "rise"):
            i0, i1 = int(s0 * SR), int(s1 * SR)
            for ch in range(2):
                syn[ch, i0:i1] = lp(syn[ch, i0:i1], 1300)
    buf = dry + reverb(syn, 2.2, .3)
    add(buf, dur - 2.4, impact(2.4), .5)
    buf = buf[:, : int(dur * SR)]
    fade = int(1.6 * SR)
    buf[:, -fade:] *= np.linspace(1, 0, fade)
    buf = np.tanh(buf * 1.1) / np.tanh(1.1)
    buf /= np.abs(buf).max() / .89
    return buf


# ---------------------------------------------------------------- dokumenter (Persib)
DOC_EPIC = [(38, [50, 53, 57, 62]), (34, [50, 53, 58, 62]), (41, [48, 53, 57, 60]), (36, [48, 52, 55, 60])]   # Dm Bb F C
DOC_BIZ = [(41, [53, 57, 60, 64]), (38, [53, 57, 62, 65]), (34, [53, 58, 62, 65]), (36, [52, 55, 60, 64])]   # Fmaj7 Dm7 Bbmaj7 C
DOC_RISE = [(34, [53, 58, 62, 65]), (36, [52, 55, 60, 64]), (38, [53, 57, 62, 65]), (41, [53, 57, 60, 65])]  # Bb C Dm F
DOC_MOTIF = [74, 77, 76, 72, 74, 69, 72, 74]


def taiko(big=1.0):
    t = np.arange(int(1.2 * SR)) / SR
    f = 52 + 60 * np.exp(-t * 18)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5)
    skin = bp(RNG.standard_normal(len(t)), 120, 1800) * np.exp(-t * 22) * .5
    return np.tanh((body + skin) * 1.4 * big) * .8


def string_ens(note, dur, bright=1300):
    s = saw_pad(note, dur) + .6 * saw_pad(note + 12, dur, (-.06, .05))
    t = np.arange(len(s)) / SR
    env = np.minimum(1, t / .5) * np.minimum(1, (dur - t) / .6)
    return lp(s * env, bright) * .9


def piano(note, dur=1.8, vel=1.0):
    return harm_tone(midi(note), dur, 2.2, 5.0, nh=8, bright=.8) * .5 * vel + epiano(note, dur, vel) * .6


def render_doc(dur, bpm=100.0, marks=(7.05, 20.31, 24.65, 46.53, 60.52, 68.31), kinds=None):
    """dokumenter sepak bola: intro malam stadion -> anthem epik (taiko+strings) -> hening (rahasia?) ->
    bed bisnis berdenyut (ostinato) -> mimpi IPO naik -> ujian terberat (drum perang) -> resolusi hangat."""
    beat = 60.0 / bpm
    L = int((dur + 4) * SR)
    dry = np.zeros((2, L))
    syn = np.zeros((2, L))
    kinds = list(kinds or ["intro", "epic", "brk", "biz", "rise", "war", "res"])
    assert len(kinds) == len(marks) + 1, "jumlah DOC_KINDS harus = jumlah DOC_MARKS + 1"
    bounds = [0.0] + list(marks) + [dur]
    secs = [(bounds[i], bounds[i + 1], kinds[i]) for i in range(len(kinds))]
    K, SN, H = kick(), snare(), hat()
    for s0, s1, kind in secs:
        prog = DOC_BIZ if kind in ("biz", "res") else DOC_RISE if kind == "rise" else DOC_EPIC
        nb = int(np.ceil((s1 - s0) / beat))
        for bt in range(nb):
            t0 = s0 + bt * beat
            if t0 >= s1 - .02:
                break
            root, notes = prog[(bt // 4) % 4]
            bb = bt % 4
            if bb == 0:
                bl = min(4 * beat, s1 - t0) + .4
                lvl = {"intro": .35, "brk": .3, "biz": .32, "res": .42}.get(kind, .55)
                add(syn, t0, sum(string_ens(n_, bl, 900 if kind in ("intro", "brk") else 1600) for n_ in notes), lvl)
                add(dry, t0, bass_note(root, bl * .9), .5 if kind not in ("intro", "brk") else .3)
            if kind == "intro":
                if bb == 0:
                    add(dry, t0, taiko(.7), .6)
                if bt % 2 == 0:
                    add(syn, t0, piano(DOC_MOTIF[(bt // 2) % 8] - 12, 2.0, .7), .45, .2)
                continue
            if kind == "brk":
                if bt == 0:
                    add(dry, t0, impact(2.6), .8)
                add(syn, t0, bell(notes[bt % 4] + 12, 1.2), .18, .3)
                continue
            if kind in ("epic", "war"):
                war = kind == "war"
                # pola taiko mars: 1 . 3 & 4
                if bb in (0, 2):
                    add(dry, t0, taiko(1.0), .9 if war else .75, -.15)
                if bb == 3 or (war and bb == 1):
                    add(dry, t0 + beat / 2, taiko(.8), .6, .15)
                if war:
                    add(dry, t0, K, .7)
                    for k in range(4):
                        add(dry, t0 + k * beat / 4, H, .1, .3)
                    if bb in (1, 3):
                        add(dry, t0, SN, .5)
                add(syn, t0, pluck(notes[bt % 4] + 12, beat * .9), .3, -.4 + .8 * (bt % 2))
                add(syn, t0 + beat / 2, pluck(notes[(bt + 2) % 4] + 12, beat * .9), .22, .4)
                if bt % 2 == 0:
                    add(syn, t0, piano(DOC_MOTIF[(bt // 2) % 8], 1.6), .5, .1)
                if war and bb == 0:
                    add(syn, t0, brass_stab([n_ for n_ in notes], .5), .5)
                continue
            if kind in ("biz", "rise"):
                # ostinato 8-an bersih + kick lembut 4/4 + rim, bel di 'rise'
                if bb in (0, 2):
                    add(dry, t0, K, .55 if kind == "biz" else .7)
                if bb in (1, 3):
                    add(dry, t0, rim(), .5)
                for k in range(2):
                    add(syn, t0 + k * beat / 2, pluck(notes[(bt * 2 + k) % 4] + 12, beat * .45), .32, -.3 + .6 * k)
                    add(dry, t0 + k * beat / 2, H, .08, .35)
                if kind == "rise" and bt % 2 == 0:
                    add(syn, t0, bell(notes[(bt // 2) % 4] + 24, 1.4), .2, .2)
                continue
            # resolusi hangat
            if bb == 0:
                add(dry, t0, taiko(.6), .45)
            if bt % 2 == 0:
                add(syn, t0, piano(DOC_MOTIF[(bt // 2) % 8], 2.0, .9), .5, .1)
            add(syn, t0, epiano(notes[bt % 4] + 12, beat * 1.5, .6), .25, -.2)
        if kind in ("intro", "brk", "rise"):
            rl = min(2.2 if kind == "rise" else 1.5, s1 - s0 - .2)
            add(dry, s1 - rl, swell(rl), 1.1 if kind == "rise" else .8)
        if kind in ("epic", "biz", "war", "res"):
            add(dry, s0, impact(2.4), .8)
    buf = dry + reverb(syn, 2.6, .38)
    add(buf, dur - 2.6, impact(2.4), .5)
    buf = buf[:, : int(dur * SR)]
    fade = int(1.8 * SR)
    buf[:, -fade:] *= np.linspace(1, 0, fade)
    buf = np.tanh(buf * 1.1) / np.tanh(1.1)
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
    if VARIANTS[a.variant] == "doc":
        mk = tuple(float(x) for x in os.environ.get("DOC_MARKS", "7.05,20.31,24.65,46.53,60.52,68.31").split(","))
        kd = os.environ.get("DOC_KINDS")
        sf.write(a.out, render_doc(a.dur, a.bpm, mk, kd.split(",") if kd else None).T, SR, subtype="PCM_16")
        print("wrote", a.out)
        return
    if VARIANTS[a.variant] == "sakura":
        mk = tuple(float(x) for x in os.environ.get("SAKURA_MARKS", "6.3,18.68,20.55,30.68,34.64,43.67,60.62").split(","))
        sf.write(a.out, render_sakura(a.dur, a.bpm, mk).T, SR, subtype="PCM_16")
        print("wrote", a.out)
        return
    if VARIANTS[a.variant] == "vice":
        mk = tuple(float(x) for x in os.environ.get("NEON_MARKS", "8.85,24.47,29.38,46.70,51.26,64.40").split(","))
        sf.write(a.out, render_vice(a.dur, a.bpm, mk).T, SR, subtype="PCM_16")
        print("wrote", a.out)
        return
    if VARIANTS[a.variant] == "neon":
        mk = tuple(float(x) for x in os.environ.get("NEON_MARKS", "8.85,24.47,29.38,46.70,51.26,64.40").split(","))
        sf.write(a.out, render_neon(a.dur, a.bpm, mk).T, SR, subtype="PCM_16")
        print("wrote", a.out)
        return
    if VARIANTS[a.variant] == "street":
        sf.write(a.out, render_street(a.dur, a.bpm, tuple(a.brk)).T, SR, subtype="PCM_16")
        print("wrote", a.out)
        return
    if VARIANTS[a.variant] == "fest":
        sf.write(a.out, render_fest(a.dur, a.bpm, tuple(a.brk)).T, SR, subtype="PCM_16")
        print("wrote", a.out)
        return
    if VARIANTS[a.variant] == "biz":
        sf.write(a.out, render_biz(a.dur, a.bpm, tuple(a.brk)).T, SR, subtype="PCM_16")
        print("wrote", a.out)
        return
    if VARIANTS[a.variant]:
        CHORDS, MOTIF = VARIANTS[a.variant]
    sf.write(a.out, render(a.dur, a.bpm, tuple(a.brk)).T, SR, subtype="PCM_16")
    print("wrote", a.out)


if __name__ == "__main__":
    main()
