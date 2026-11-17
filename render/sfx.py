"""Efek suara (SFX) sintetis orisinal untuk video: whoosh transisi, impact, tick hitungan, pop, ding, glitch,
cap (stamp), sirine, notifikasi, pemindai (scan), pita/stiker.

  python3 render/sfx.py EVENTS.json DURASI OUT.wav

EVENTS.json = [[detik, jenis, gain(opsional), arg(opsional)], ...]
jenis: whoosh, whoosh_low, swoosh, impact, boom, riser (berakhir di detik), tick, ticks (arg = lama detik),
pop, ding, coin, glitch, stamp, siren (arg = lama), notif, scan (arg = lama), sticker, type (arg = jumlah huruf)
"""
import json
import sys

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

SR = 44100
RNG = np.random.default_rng(11)


def _f(x, lo=None, hi=None, order=2):
    if lo and hi:
        sos = butter(order, [lo, hi], "bandpass", fs=SR, output="sos")
    elif lo:
        sos = butter(order, lo, "highpass", fs=SR, output="sos")
    else:
        sos = butter(order, hi, "lowpass", fs=SR, output="sos")
    return sosfilt(sos, x)


def tt(d):
    return np.arange(int(d * SR)) / SR


def sweep_noise(d, f0, f1, q=.6, env=None):
    t = tt(d)
    n = RNG.standard_normal(len(t))
    out = np.zeros_like(n)
    steps = 32
    seg = max(1, len(n) // steps)
    for k in range(steps):
        u = k / (steps - 1)
        fc = f0 * (f1 / f0) ** u
        a, b = k * seg, min(len(n), (k + 1) * seg + 256)
        out[a:b] += _f(n[a:b], max(30, fc * (1 - q)), min(19000, fc * (1 + q)))[: b - a] * (1 if b - a == seg else .5)
    if env is None:
        env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.5
    return out * env


def whoosh(d=.55, up=True):
    s = sweep_noise(d, 300 if up else 4000, 4500 if up else 250, .7)
    return s / (np.abs(s).max() + 1e-9) * .8


def whoosh_low(d=.7):
    t = tt(d)
    s = sweep_noise(d, 120, 1400, .8, np.sin(np.pi * t / d) ** 2)
    return s / (np.abs(s).max() + 1e-9) * .8


def impact(d=1.6):
    t = tt(d)
    boom = np.sin(2 * np.pi * np.cumsum(42 + 90 * np.exp(-t * 14)) / SR) * np.exp(-t * 3.0)
    crack = _f(RNG.standard_normal(len(t)), 800, 7000) * np.exp(-t * 30) * .7
    tail = _f(RNG.standard_normal(len(t)), None, 1800) * np.exp(-t * 4) * .25
    return np.tanh((boom + crack + tail) * 1.4) * .9


def boom(d=2.2):
    t = tt(d)
    s = np.sin(2 * np.pi * np.cumsum(34 + 45 * np.exp(-t * 6)) / SR) * np.exp(-t * 1.6)
    return np.tanh(s * 1.8) * .9


def riser(d=1.6):
    t = tt(d)
    s = sweep_noise(d, 400, 9000, .5, (t / d) ** 2.2)
    tone = np.sin(2 * np.pi * np.cumsum(200 * (8 ** (t / d))) / SR) * (t / d) ** 2 * .25
    s = s / (np.abs(s).max() + 1e-9) * .7 + tone
    return s


def tick():
    t = tt(.04)
    return (np.sin(2 * np.pi * 2400 * t) * .6 + _f(RNG.standard_normal(len(t)), 3000, None)) * np.exp(-t * 160) * .5


def ticks(d=1.5, rate=14):
    out = np.zeros(int((d + .1) * SR))
    k = 0
    while k / rate < d:
        tk = tick()
        i = int(k / rate * SR)
        out[i:i + len(tk)] += tk * (.7 + .3 * (k % 2))
        k += 1
    return out


def pop():
    t = tt(.12)
    f = 300 + 900 * np.exp(-t * 40)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 35) * .7


def ding(f=1568.0, d=1.0):
    t = tt(d)
    s = sum(np.sin(2 * np.pi * f * h * t) * np.exp(-t * (3 + h * 2)) / h for h in (1, 2.76, 5.4))
    return s * np.minimum(1, t / .002) * .45


def coin():
    a = ding(1975, .5)
    b = ding(2637, .8)
    out = np.zeros(len(b) + int(.07 * SR))
    out[:len(a)] += a
    out[int(.07 * SR):int(.07 * SR) + len(b)] += b
    return out * .8


def glitch(d=.35):
    t = tt(d)
    n = RNG.standard_normal(len(t))
    hold = 220
    n = np.repeat(n[::hold], hold)[: len(t)]
    sq = np.sign(np.sin(2 * np.pi * RNG.choice([180, 360, 720, 1440]) * t))
    gate = (np.sin(2 * np.pi * 28 * t) > -.2).astype(float)
    s = (n * .6 + sq * .35) * gate
    s = np.round(s * 6) / 6
    return _f(s, 150, 9000) * np.exp(-t * 4) * .6


def stamp():
    t = tt(.5)
    thud = np.sin(2 * np.pi * np.cumsum(90 + 140 * np.exp(-t * 40)) / SR) * np.exp(-t * 18)
    slap = _f(RNG.standard_normal(len(t)), 400, 5000) * np.exp(-t * 45) * .8
    return np.tanh((thud + slap) * 1.6) * .85


def siren(d=1.6):
    t = tt(d)
    f = 700 + 350 * np.sin(2 * np.pi * 2.2 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sign(np.sin(ph)) * .3 + np.sin(ph) * .5
    s = _f(s, 300, 4000)
    env = np.minimum(1, t / .05) * np.minimum(1, (d - t) / .25)
    return s * env * .45


def notif():
    a = ding(1318, .4)
    b = ding(1975, .7)
    out = np.zeros(len(b) + int(.09 * SR))
    out[:len(a)] += a
    out[int(.09 * SR):int(.09 * SR) + len(b)] += b
    p = pop()
    out[:len(p)] += p * .6
    return out * .8


def scan(d=1.4):
    t = tt(d)
    f = 900 + 500 * np.sin(2 * np.pi * 1.5 * t)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * .3 + _f(RNG.standard_normal(len(t)), 3000, 8000) * .15
    env = np.minimum(1, t / .05) * np.minimum(1, (d - t) / .1)
    trem = .6 + .4 * np.sin(2 * np.pi * 18 * t)
    return s * env * trem * .7


def sticker():
    t = tt(.32)
    rip = _f(RNG.standard_normal(len(t)), 1500, 9000) * (np.abs(np.sin(2 * np.pi * 60 * t)) ** 3) * np.exp(-t * 6)
    p = np.zeros_like(t)
    tap = stamp()[: int(.12 * SR)] * .5
    p[int(.2 * SR):int(.2 * SR) + len(tap)] += tap
    return rip * .6 + p


def typing(n=6):
    out = np.zeros(int((n * .085 + .2) * SR))
    for k in range(n):
        t = tt(.05)
        c = _f(RNG.standard_normal(len(t)), 1800, 7000) * np.exp(-t * 120) * .5
        i = int(k * (.07 + RNG.uniform(0, .03)) * SR)
        out[i:i + len(c)] += c
    return out


GEN = {"whoosh": lambda a: whoosh(a or .55), "whoosh_rev": lambda a: whoosh(a or .55, False),
       "whoosh_low": lambda a: whoosh_low(a or .7), "swoosh": lambda a: whoosh(a or .3) * .7,
       "impact": lambda a: impact(), "boom": lambda a: boom(), "riser": lambda a: riser(a or 1.6),
       "tick": lambda a: tick(), "ticks": lambda a: ticks(a or 1.5), "pop": lambda a: pop(), "ding": lambda a: ding(),
       "coin": lambda a: coin(), "glitch": lambda a: glitch(a or .35), "stamp": lambda a: stamp(),
       "siren": lambda a: siren(a or 1.6), "notif": lambda a: notif(), "scan": lambda a: scan(a or 1.4),
       "sticker": lambda a: sticker(), "type": lambda a: typing(int(a or 6))}
PAN = {"whoosh": .25, "whoosh_rev": -.25, "swoosh": -.2, "tick": .15, "ticks": .15, "pop": 0, "coin": .2}


def main():
    ev, dur, out = json.load(open(sys.argv[1])), float(sys.argv[2]), sys.argv[3]
    buf = np.zeros((2, int((dur + 3) * SR)))
    for e in ev:
        t, kind = float(e[0]), e[1]
        g = e[2] if len(e) > 2 else 1.0
        arg = e[3] if len(e) > 3 else None
        s = GEN[kind](arg)
        if kind == "riser":
            t -= len(s) / SR
        i = max(0, int(t * SR))
        s = s[: buf.shape[1] - i]
        p = PAN.get(kind, 0.0)
        lg, rg = np.cos((p + 1) * np.pi / 4), np.sin((p + 1) * np.pi / 4)
        buf[0, i:i + len(s)] += s * g * lg * 1.414
        buf[1, i:i + len(s)] += s * g * rg * 1.414
    buf = buf[:, : int(dur * SR)]
    pk = np.abs(buf).max()
    if pk > .95:
        buf *= .95 / pk
    sf.write(out, buf.T, SR, subtype="PCM_16")
    print("sfx", len(ev), "->", out)


if __name__ == "__main__":
    main()
