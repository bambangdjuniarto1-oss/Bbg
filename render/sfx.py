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


# ------------------------------------------------------------------ efek tambahan (seri GTA / kota)
def _norm(s, pk=.8):
    return s / (np.abs(s).max() + 1e-9) * pk


def cash():
    """mesin kasir: denting bel + laci logam meluncur + koin."""
    t = tt(.9)
    bell_ = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, d in ((2637, 5), (3951, 7), (5274, 9)))
    drawer = np.zeros_like(t)
    i = int(.18 * SR)
    sl = _f(RNG.standard_normal(int(.22 * SR)), 600, 4000) * np.linspace(1, .2, int(.22 * SR)) * .5
    drawer[i:i + len(sl)] += sl
    out = _norm(bell_ * .7 + drawer)
    c = coin()
    j = int(.42 * SR)
    out[j:j + len(c)] += c[: len(out) - j] * .6
    return out


def crowd(d=2.0):
    """riuh orang banyak (gumaman) - noise band 300-2500 dengan modulasi suku kata acak."""
    t = tt(d)
    n = _f(RNG.standard_normal(len(t)), 300, 2500)
    mod = np.zeros_like(t)
    for k in range(14):
        f = RNG.uniform(2.5, 6.0)
        mod += np.abs(np.sin(2 * np.pi * f * t + RNG.uniform(0, 6)))
    env = np.minimum(1, t / .3) * np.minimum(1, (d - t) / .4)
    return _norm(n * mod / 14 * env, .55)


def cheer(d=1.8):
    """sorak penonton: noise terang naik-turun + siulan pendek."""
    t = tt(d)
    n = _f(RNG.standard_normal(len(t)), 700, 6000)
    env = np.minimum(1, t / .12) * np.exp(-np.maximum(0, t - .5) * 1.6)
    wh = np.sin(2 * np.pi * np.cumsum(1800 + 900 * np.minimum(1, t / .35)) / SR) * np.exp(-t * 3) * .25
    return _norm(n * env + wh * (t < .6), .75)


def chain(d=.7):
    """rantai logam bergemerincing."""
    out = np.zeros(int(d * SR))
    for k in range(10):
        tk = tt(.08)
        f = RNG.uniform(2500, 5200)
        c = (np.sin(2 * np.pi * f * tk) + .5 * np.sin(2 * np.pi * f * 1.48 * tk)) * np.exp(-tk * 60)
        i = int(RNG.uniform(0, d - .09) * SR)
        out[i:i + len(c)] += c * RNG.uniform(.4, 1)
    return _norm(out, .7)


def clank():
    """gembok terkunci: hantaman logam + klik."""
    t = tt(.6)
    body = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, d in ((420, 9), (1130, 14), (2210, 22)))
    hit = _f(RNG.standard_normal(len(t)), 800, 6000) * np.exp(-t * 70)
    return _norm(body * .6 + hit)


def ping(f=1760.0):
    """blip sonar/peta (pin menyala)."""
    t = tt(.45)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 9) + .3 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t * 16)
    return _norm(s, .6)


def heart():
    """detak jantung (lub-dub)."""
    out = np.zeros(int(.8 * SR))
    for off, g in ((0, 1.0), (.22, .7)):
        t = tt(.18)
        s = np.sin(2 * np.pi * (60 - 80 * t) * t) * np.exp(-t * 22) * g
        i = int(off * SR)
        out[i:i + len(s)] += s
    return _norm(out, .9)


def car(d=1.6):
    """mobil lewat (doppler): mesin harmonik + ban, keras di tengah."""
    t = tt(d)
    u = t / d
    f = 95 * (1.18 - .36 * u)
    ph = 2 * np.cumsum(f) * np.pi / SR
    eng = sum(np.sin(k * ph) / k for k in range(1, 7))
    tyre = _f(RNG.standard_normal(len(t)), 200, 1800) * .4
    env = 1 / (1 + ((u - .5) * 6) ** 2)
    return _norm((eng + tyre) * env, .7)


def heli(d=2.4):
    """rotor helikopter (denyut 'thup-thup')."""
    t = tt(d)
    pulse = (np.sin(2 * np.pi * 11 * t) > .6).astype(float)
    pulse = _f(pulse, hi=200)
    n = _f(RNG.standard_normal(len(t)), 60, 600)
    env = np.minimum(1, t / .5) * np.minimum(1, (d - t) / .6)
    return _norm(n * (.3 + pulse) * env, .65)


def shutter():
    t = tt(.2)
    s = _f(RNG.standard_normal(len(t)), 1500, 9000) * (np.exp(-t * 90) + .6 * np.exp(-np.maximum(0, t - .07) * 90) * (t > .07))
    return _norm(s, .7)


def star():
    """bintang 'wanted' (orisinal): dua nada synth naik + kilau."""
    out = np.zeros(int(.7 * SR))
    for off, f in ((0, 987.8), (.09, 1318.5)):
        t = tt(.5)
        s = (np.sign(np.sin(2 * np.pi * f * t)) * .25 + np.sin(2 * np.pi * f * t)) * np.exp(-t * 7)
        i = int(off * SR)
        out[i:i + len(s)] += s
    return _norm(out, .55)


def bass_drop(d=1.4):
    """sub turun (808 drop) untuk angka besar."""
    t = tt(d)
    f = 110 * np.exp(-t * 2.2) + 32
    s = np.tanh(2.2 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-t * 1.6)
    return _norm(s, .9)


def sparkle(d=.9):
    """kilau (logo/kartu muncul): butiran nada tinggi acak."""
    out = np.zeros(int(d * SR))
    for k in range(18):
        tk = tt(.12)
        f = RNG.uniform(3000, 7500)
        c = np.sin(2 * np.pi * f * tk) * np.exp(-tk * 40)
        i = int(RNG.uniform(0, d - .13) * SR)
        out[i:i + len(c)] += c * (1 - i / len(out))
    return _norm(out, .5)


def coins_pour(d=1.6):
    """hujan koin/uang mengalir."""
    out = np.zeros(int(d * SR))
    c = coin()
    for k in range(int(d * 16)):
        i = int(RNG.uniform(0, d - .3) * SR)
        seg = c[: min(len(c), len(out) - i)] * RNG.uniform(.2, .6)
        out[i:i + len(seg)] += seg
    return _norm(out, .7)


def flutter(d=.6):
    """kartu/kertas berkibar (deretan swoosh pendek)."""
    out = np.zeros(int(d * SR))
    for k in range(6):
        s = whoosh(.12) * RNG.uniform(.4, .9)
        i = int(k * d / 7 * SR)
        out[i:i + len(s)] += s[: len(out) - i]
    return _norm(out, .6)


GEN_X = {"cash": lambda a: cash(), "crowd": lambda a: crowd(a or 2.0), "cheer": lambda a: cheer(a or 1.8),
         "chain": lambda a: chain(a or .7), "clank": lambda a: clank(), "ping": lambda a: ping(a or 1760.0),
         "heart": lambda a: heart(), "car": lambda a: car(a or 1.6), "heli": lambda a: heli(a or 2.4),
         "shutter": lambda a: shutter(), "star": lambda a: star(), "bass_drop": lambda a: bass_drop(a or 1.4),
         "sparkle": lambda a: sparkle(a or .9), "coins_pour": lambda a: coins_pour(a or 1.6),
         "flutter": lambda a: flutter(a or .6)}


def gavel():
    """ketukan palu (fatwa/keputusan): kayu padat + gema ruangan."""
    t = tt(1.4)
    knock = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, d in ((180, 18), (420, 26), (910, 40)))
    click = _f(RNG.standard_normal(len(t)), 1500, 6000) * np.exp(-t * 90) * .8
    body = np.sin(2 * np.pi * np.cumsum(60 + 50 * np.exp(-t * 20)) / SR) * np.exp(-t * 6) * .8
    s = knock + click + body
    rev = np.convolve(s, _f(RNG.standard_normal(int(.5 * SR)), 200, 3000) * np.exp(-tt(.5) * 9) * .04)[: len(t)]
    return _norm(np.tanh((s + rev) * 1.5), .9)


def news_alert():
    """sting 'BREAKING NEWS': dua nada sinus naik + denting + sapuan."""
    t = tt(1.5)
    out = np.zeros_like(t)
    for k, (f, t0) in enumerate(((880, 0), (1320, .12), (1760, .24))):
        i = int(t0 * SR)
        u = t[: len(t) - i]
        out[i:] += np.sin(2 * np.pi * f * u) * np.exp(-u * (3 + k)) * .5
    sw = sweep_noise(1.5, 6000, 900, .5, np.exp(-t * 2.5)) * .25
    return _norm(out + sw, .8)


def paper(d=.45):
    """kertas/halaman meluncur (artikel muncul)."""
    t = tt(d)
    n = _f(RNG.standard_normal(len(t)), 1200, 9000)
    am = np.abs(np.sin(np.pi * t / d)) ** .7 * (1 + .5 * np.sin(2 * np.pi * 37 * t))
    return _norm(n * am, .6)


def glass(d=1.2):
    """kaca retak/pecah (krisis): retakan tinggi + serpihan dentingan acak."""
    t = tt(d)
    crack = _f(RNG.standard_normal(len(t)), 2500, 12000) * np.exp(-t * 25)
    out = crack.copy()
    for _ in range(26):
        t0 = RNG.uniform(.02, d * .7)
        f = RNG.uniform(3000, 9000)
        i = int(t0 * SR)
        u = t[: len(t) - i]
        out[i:] += np.sin(2 * np.pi * f * u) * np.exp(-u * RNG.uniform(18, 40)) * RNG.uniform(.1, .3)
    thud = np.sin(2 * np.pi * np.cumsum(70 + 80 * np.exp(-t * 18)) / SR) * np.exp(-t * 9) * .7
    return _norm(out + thud, .85)


def shutter_door(d=1.1):
    """rolling door toko ditarik turun: gerinda logam berderit lalu benturan."""
    t = tt(d)
    rat = _f(RNG.standard_normal(len(t)), 300, 2400) * (1 + .8 * np.sign(np.sin(2 * np.pi * 34 * t))) * .35
    rat *= np.minimum(1, t / .05) * (t < d * .8)
    i = int(d * .8 * SR)
    u = t[: len(t) - i]
    hit = np.zeros_like(t)
    hit[i:] = (np.sin(2 * np.pi * 95 * u) * np.exp(-u * 12) + _f(RNG.standard_normal(len(u)), 400, 3000)
               * np.exp(-u * 30) * .6)
    return _norm(rat + hit, .85)


def kawaii(d=.8):
    """chime manis (pink sakura / pop Jepang): arpeggio lonceng pentatonik naik."""
    t = tt(d)
    out = np.zeros_like(t)
    for k, f in enumerate((1568, 1976, 2349, 2637, 3136)):
        i = int(k * .06 * SR)
        u = t[: len(t) - i]
        out[i:] += (np.sin(2 * np.pi * f * u) + .3 * np.sin(4 * np.pi * f * u)) * np.exp(-u * 6) * .3
    return _norm(out, .7)


def flash():
    """lampu kilat kamera: klik + dengung isi ulang naik."""
    t = tt(.6)
    clk = _f(RNG.standard_normal(len(t)), 2000, 9000) * np.exp(-t * 120)
    whine = np.sin(2 * np.pi * np.cumsum(2500 + 5000 * t / .6) / SR) * np.exp(-t * 5) * .12 * (t > .05)
    return _norm(clk + whine, .7)


GEN_X.update({"gavel": lambda a: gavel(), "news": lambda a: news_alert(), "paper": lambda a: paper(a or .45),
              "glass": lambda a: glass(a or 1.2), "door": lambda a: shutter_door(a or 1.1),
              "kawaii": lambda a: kawaii(a or .8), "flash": lambda a: flash()})


# ---------------------------------------------------------------- stadion (bobotoh)
VOWEL = {"a": (750, 1200, 2600), "e": (480, 1900, 2600), "i": (320, 2300, 3000), "o": (500, 850, 2500),
         "u": (350, 700, 2400)}


def _stadium_verb(x, secs=2.4, mix=.55):
    from scipy.signal import fftconvolve
    t = tt(secs)
    ir = _f(RNG.standard_normal(len(t)), 150, 6000) * np.exp(-t * 2.4)
    ir[: int(.03 * SR)] = 0
    ir /= np.sqrt(np.sum(ir ** 2))
    return x + fftconvolve(x, ir)[: len(x)] * mix


def _voices(d, n=36, vowel="a", lo=110, hi=260, env=None):
    """massa suara penonton: n sumber glotal (pitch acak + vibrato + jitter) disaring formant vokal."""
    t = tt(d)
    g = np.zeros_like(t)
    for k in range(n):
        f0 = RNG.uniform(lo, hi) * (1 + .02 * np.sin(2 * np.pi * RNG.uniform(4, 7) * t + RNG.uniform(0, 6)))
        ph = np.cumsum(f0) / SR + RNG.uniform(0, 1)
        saw = 2 * (ph % 1) - 1
        a = np.clip(.6 + .4 * np.sin(2 * np.pi * RNG.uniform(.2, .9) * t + RNG.uniform(0, 6)), 0, 1)
        g += saw * a * RNG.uniform(.5, 1)
    f1, f2, f3 = VOWEL[vowel]
    out = _f(g, f1 * .8, f1 * 1.25) + .7 * _f(g, f2 * .85, f2 * 1.15) + .3 * _f(g, f3 * .9, f3 * 1.1)
    if env is not None:
        out *= env
    return out / n


def stadium_roar(d=3.0):
    """gemuruh stadion: massa vokal 'aaah' + desis riuh, naik cepat, tahan, surut - dengan gema stadion."""
    t = tt(d)
    env = np.minimum(1, t / .35) * np.minimum(1, (d - t) / (d * .45))
    v = _voices(d, 40, "a", 120, 300, env) + .6 * _voices(d, 24, "o", 95, 180, env)
    n = _f(RNG.standard_normal(len(t)), 500, 5000) * env * .25
    return _norm(_stadium_verb(v * 3 + n), .8)


def goal_roar(d=3.6):
    """ledakan sorak gol: serangan seketika, puncak tinggi, ekor panjang."""
    t = tt(d)
    env = np.minimum(1, t / .08) * np.exp(-np.maximum(0, t - .9) * .9)
    v = _voices(d, 44, "a", 160, 360, env) + .5 * _voices(d, 24, "e", 200, 420, env)
    n = _f(RNG.standard_normal(len(t)), 900, 7000) * env * .35
    return _norm(_stadium_verb(v * 3 + n, 2.6, .6), .85)


def _crowd_clap(d=.25, n=60):
    out = np.zeros(int(d * SR))
    for k in range(n):
        c = _f(RNG.standard_normal(int(.03 * SR)), 900, 5000) * np.exp(-tt(.03) * 140)
        i = int(abs(RNG.normal(0, .018)) * SR)
        out[i:i + len(c)] += c[: len(out) - i] * RNG.uniform(.4, 1)
    return out / 10


def chant(d=4.0, bpm=118.0):
    """yel suporter generik: tepuk-tepuk-tepuk + teriakan dua suku kata serempak, berulang, bergema."""
    beat = 60 / bpm
    out = np.zeros(int((d + .5) * SR))
    bar = 0
    while bar * 4 * beat < d:
        b0 = bar * 4 * beat
        for k in range(3):
            i = int((b0 + k * beat) * SR)
            if i >= len(out):
                continue
            c = _crowd_clap()
            out[i:i + len(c)] += c[: len(out) - i] * 1.3
        for j, (vw, off, L) in enumerate((("e", 3.0, .32), ("i", 3.5, .42))):
            i = int((b0 + off * beat) * SR)
            if i >= len(out):
                continue
            tl = tt(L)
            env = np.minimum(1, tl / .03) * np.exp(-tl * 4) * (1.0 if j else .9)
            v = _voices(L, 30, vw, 150 + 40 * j, 300 + 60 * j, env) * 4
            out[i:i + len(v)] += v[: len(out) - i]
        bar += 1
    out = out[: int(d * SR)]
    t = tt(d)
    out *= np.minimum(1, t / .2) * np.minimum(1, (d - t) / .5)
    return _norm(_stadium_verb(out, 2.2, .5), .75)


def sup_drum(d=2.4, bpm=118.0):
    """bass drum suporter di tribun: dum . dum-dum ., bergema."""
    beat = 60 / bpm
    out = np.zeros(int((d + .5) * SR))
    k = 0
    while k * beat < d:
        for off, g in ((0, 1.0), (.5, .0), (1, .8), (1.5, .7)):
            if g == 0 or (k + off) * beat >= d:
                continue
            tk = tt(.5)
            hit = np.sin(2 * np.pi * np.cumsum(70 + 50 * np.exp(-tk * 30)) / SR) * np.exp(-tk * 7)
            hit += _f(RNG.standard_normal(len(tk)), 200, 2000) * np.exp(-tk * 40) * .3
            i = int((k + off) * beat * SR)
            if i >= len(out):
                continue
            out[i:i + len(hit)] += hit[: len(out) - i] * g
        k += 2
    out = out[: int(d * SR)]
    return _norm(_stadium_verb(out, 2.0, .45), .8)


def ref_whistle(d=.7):
    """peluit wasit: nada ~2,9 kHz dengan getar bola (trill)."""
    t = tt(d)
    f = 2900 + 40 * np.sin(2 * np.pi * 6 * t)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * (.65 + .35 * np.sin(2 * np.pi * 34 * t))
    s += _f(RNG.standard_normal(len(t)), 2500, 6000) * .08
    env = np.minimum(1, t / .02) * np.minimum(1, (d - t) / .05)
    return _norm(_stadium_verb(s * env, 1.4, .3), .6)


def stadium_bed(d=6.0):
    """riuh dasar tribun (gumaman ribuan orang) untuk latar panjang."""
    t = tt(d)
    env = np.minimum(1, t / 1.0) * np.minimum(1, (d - t) / 1.2)
    v = _voices(d, 30, "o", 100, 220, env * (.7 + .3 * np.sin(2 * np.pi * .23 * t)))
    n = _f(RNG.standard_normal(len(t)), 300, 2500) * env * .12
    return _norm(_stadium_verb(v * 2 + n, 2.4, .6), .5)


GEN_X.update({"roar": lambda a: stadium_roar(a or 3.0), "goal": lambda a: goal_roar(a or 3.6),
              "chant": lambda a: chant(a or 4.0), "drum": lambda a: sup_drum(a or 2.4),
              "whistle": lambda a: ref_whistle(a or .7), "bed": lambda a: stadium_bed(a or 6.0)})


_SMP = {}


def sample(arg):
    """potongan rekaman: arg = [path, mulai_detik, lama_detik, fade_in, fade_out] (mono, dinormalisasi RMS)."""
    path, st, d = arg[0], float(arg[1]), float(arg[2])
    fi = float(arg[3]) if len(arg) > 3 else .4
    fo = float(arg[4]) if len(arg) > 4 else .8
    if path not in _SMP:
        x, sr = sf.read(path, always_2d=True)
        x = x.mean(1)
        if sr != SR:
            from scipy.signal import resample_poly
            x = resample_poly(x, SR, sr)
        _SMP[path] = x
    x = _SMP[path][int(st * SR): int((st + d) * SR)].copy()
    t = np.arange(len(x)) / SR
    x *= np.minimum(1, t / max(fi, 1e-3)) * np.minimum(1, (d - t) / max(fo, 1e-3))
    rms = np.sqrt(np.mean(x ** 2)) + 1e-9
    return x * (.12 / rms)


GEN_X["smp"] = sample


GEN = {"whoosh": lambda a: whoosh(a or .55), "whoosh_rev": lambda a: whoosh(a or .55, False),
       "whoosh_low": lambda a: whoosh_low(a or .7), "swoosh": lambda a: whoosh(a or .3) * .7,
       "impact": lambda a: impact(), "boom": lambda a: boom(), "riser": lambda a: riser(a or 1.6),
       "tick": lambda a: tick(), "ticks": lambda a: ticks(a or 1.5), "pop": lambda a: pop(), "ding": lambda a: ding(),
       "coin": lambda a: coin(), "glitch": lambda a: glitch(a or .35), "stamp": lambda a: stamp(),
       "siren": lambda a: siren(a or 1.6), "notif": lambda a: notif(), "scan": lambda a: scan(a or 1.4),
       "sticker": lambda a: sticker(), "type": lambda a: typing(int(a or 6))}
GEN.update(GEN_X)
PAN = {"whoosh": .25, "whoosh_rev": -.25, "swoosh": -.2, "tick": .15, "ticks": .15, "pop": 0, "coin": .2,
       "car": -.3, "heli": .35, "ping": .15, "cash": .15, "flutter": -.2}


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
