"""buat render/scenes/kpr.json + render/scenes/kpr_sfx.json — "KPR naik Rp83 rb, BI Rate 6%".
Rumus 3K: KORBAN (tagihan +Rp83 rb, santai) -> KEJUTAN 1 (ternyata dicicil sejak Mei, total Rp98 jt) ->
KAIL (deposito cuma +Rp17 rb, siapa yang kena) -> KEJUTAN 2 (rupiah rekor terlemah) -> CTA (FIXED/FLOATING).
Tiap KEJUTAN diberi bom efek: flash merah + chroma + punch + SFX boom/bass drop.

  python3 render/scenes/gen_kpr_cfg.py WORDS.json
"""
import json
import re
import sys

sys.path.insert(0, "render")
from kpr_time import tm  # noqa: E402   (semua waktu di bawah ditulis pada timeline v1 lalu dipetakan ke VO v2)

WORDS = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "render/scenes/kpr_words.json"))
src = open("render/scenes_kpr.py").read()
TL = [(a, round(tm(float(b)), 3)) for a, b in re.findall(r'\("(K\d\d)", ([\d.]+)\)', src)]
END = round(tm(82.6), 2)
T0 = dict(TL)
CITY = set(re.search(r"CITY = \{([^}]*)\}", src).group(1).replace('"', "").replace(" ", "").split(","))

# (jumlah token VO, teks subtitle dengan **kata kunci**)
CUES = [
    (7, "**Rp83.000** sebulan, segitu tambahan **cicilan KPR**"),
    (8, "yang lagi ditagih bank ke banyak orang **minggu ini**,"),
    (4, "dan kebanyakan **santai aja**,"),
    (9, "karena kalau dibagi per hari, **nggak sampai Rp3.000**."),
    (7, "Tambahan itu muncul setelah **Bank Indonesia** naikin"),
    (6, "suku bunga acuan jadi **6%**."),
    (10, "Tapi coba kamu buka lagi **riwayat cicilan** dari awal tahun,"),
    (9, "dan kamu bakal sadar, kenaikannya **ternyata juga dicicil**,"),
    (5, "sedikit-sedikit **sejak bulan Mei**,"),
    (7, "waktu bunga acuan masih **4,75%**."),
    (9, "KPR **Rp500 juta** yang dulu cicilannya **Rp4,5 juta**,"),
    (5, "sekarang hampir **Rp4,9 juta**."),
    (10, "Artinya ada **Rp410 ribu** lebih banyak yang keluar tiap bulan,"),
    (6, "dan kalau ditotal sampai lunas,"),
    (4, "jumlahnya hampir **Rp98 juta**."),
    (9, "Mungkin kamu mikir, ya udah, setidaknya **tabungan ikut naik**."),
    (4, "Tapi **deposito Rp100 juta**,"),
    (8, "setelah dipotong pajak, tambahannya **cuma Rp17.000** sebulan,"),
    (7, "karena kata para ekonom, bunga kredit itu"),
    (5, "**cepat naiknya**, tapi **lambat turunnya**."),
    (10, "Kalau KPR kamu masih **bunga tetap**, atau lagi nyicil **motor**,"),
    (5, "tenang aja, cicilannya **nggak berubah**."),
    (7, "Yang kena itu yang pakai **bunga floating**,"),
    (7, "yang **masa bunga tetapnya** sebentar lagi habis,"),
    (5, "dan yang **baru mau akad**."),
    (7, "Dan yang bikin banyak orang **garuk kepala**,"),
    (7, "semua kenaikan ini katanya buat **jaga rupiah**,"),
    (11, "padahal Jumat kemarin rupiah justru ditutup di **Rp18.270** per dolar,"),
    (4, "**paling lemah** sepanjang sejarah."),
    (8, "Kalau kamu sendiri, KPR-nya pakai **bunga apa**?"),
    (6, "Tulis **FIXED** atau **FLOATING** di komentar,"),
    (7, "nanti saya bantu hitungin **skenario cicilan** kamu."),
]
assert sum(c[0] for c in CUES) == len(WORDS), (sum(c[0] for c in CUES), len(WORDS))
SUBS = []
i = 0
for k, (nw, txt) in enumerate(CUES):
    ws = WORDS[i:i + nw]
    i += nw
    t0 = ws[0][0] - .06
    end = ws[-1][1] + .4
    if k + 1 < len(CUES):
        nxt = WORDS[i][0] - .06
        end = nxt if nxt - ws[-1][1] < .7 else ws[-1][1] + .45
    SUBS.append([round(max(0, t0), 3), round(end, 3), txt, ""])


def lb(anchor, title, t, color="cyan", sub="", lift=60, until=None):
    d = dict(anchor=anchor, title=title, sub=sub, color=color, t=t, lift=lift)
    if until is not None:
        d["until"] = until
    return d


def hero(t0, t1, text, sub="", count=None, style="pink", size=104, y=1480):
    d = dict(t0=t0, t1=t1, text=text, sub=sub, style=style, size=size, y=y)
    if count:
        d["count"] = count
    return d


S = [
    ("K01", "Cicilan KPR **+Rp83 rb**", [lb("NT", "M-BANKING", .9, "cyan", "ilustrasi notifikasi tagihan", 50, 4.8)]),
    ("K02", "Per hari **< Rp3 rb**", []),
    ("K03", "BI Rate naik ke **6%**", [lb("AK", "KATADATA", 12.6, "purple", "18 Nov 2026", 50),
                                    lb("AI", "INDONESIA BUSINESS POST", 13.1, "purple", "media berbahasa Inggris", 50)]),
    ("K04", "Ternyata **dicicil**", [lb("PH", "RIWAYAT CICILAN", 15.0, "cyan", "simulasi KPR Rp500 jt • 20 th", 50, 19.4)]),
    ("K05", "Sejak Mei, dari **4,75%**", []),
    ("K06", "KPR **Rp500 juta**", []),
    ("K07", "Sampai lunas **Rp98 juta**", []),
    ("K08", "Deposito cuma **+Rp17 rb**", [lb("AA", "AKURAT", 42.4, "purple", "pejuang KPR diintai cicilan membengkak", 50,
                                            46.6)]),
    ("K09", "Cepat naik, **lambat turun**", [lb("AE", "KONTAN", 49.5, "purple", "kata ekonom", 50)]),
    ("K10", "Fixed & motor: **aman**", []),
    ("K11", "Yang **kena**", []),
    ("K12", "Katanya **jaga rupiah**", []),
    ("K13", "Rupiah **rekor terlemah**", [lb("A1", "KONTAN", 68.2, "red", "ditutup Rp18.268, 16 Nov", 50),
                                        lb("A2", "AFU.ID", 70.6, "red", "rekor terlemah 2x sepekan", 50)]),
    ("K14", "Kamu **FIXED** atau **FLOATING**?", []),
]

HERO = [
    hero(.25, 2.9, "**+Rp83.000**/bulan", "tambahan cicilan KPR (simulasi Rp500 jt)", style="pink", size=100),
    hero(13.56, 14.4, "BI Rate **6%**", "RDG BI 17–18 Nov 2026", style="gold", size=112),
    hero(19.65, 21.2, "ternyata **DICICIL**", "naik bertahap sejak Mei", style="red", size=104),
    hero(24.11, 25.3, "masih **4,75%**", "BI Rate sebelum Mei 2026", style="cyan"),
    hero(28.17, 29.8, "**Rp4,50 jt**", "cicilan awal • bunga 9%", style="cyan"),
    hero(29.89, 32.4, "**Rp4,91 jt**", "sekarang • bunga 10,25% (simulasi)", style="pink"),
    hero(32.59, 35.3, "**+Rp410 rb**/bulan", "", style="red", size=100),
    hero(38.15, 40.4, "Rp**98** juta", "tambahan sampai lunas (20 tahun)", dict(t0=38.15, t1=38.9, frm=0, to=98, fmt="{}"),
         style="red", size=116),
    hero(47.42, 48.6, "cuma **+Rp17 rb**", "deposito Rp100 jt, bunga +0,25%, setelah pajak 20%", style="cyan", size=96),
    hero(55.3, 56.95, "**AMAN**", "bunga tetap • cicilan motor", style="green", size=116),
    hero(69.17, 71.6, "**Rp18.268**/US$", "penutupan terlemah: Senin 16 Nov 2026", style="red", size=104),
    hero(71.72, 73.6, "**REKOR** terlemah", "sepanjang sejarah", style="red", size=100),
]

COMMENTS = [dict(t=77.2, text="FLOATING, baru kerasa naik 2x tahun ini", y=1400),
            dict(t=78.4, text="FIXED, tapi 2027 udah habis masa fix-nya", y=1550)]

PUNCH = [(0.25, .7), (2.89, .4), (8.85, .5), (11.31, .4), (13.56, .9), (16.09, .4), (19.65, 1.2), (20.49, .6),
         (22.76, .5), (24.11, .6), (26.39, .5), (28.17, .5), (29.89, .6), (32.59, .8), (36.99, .4), (38.64, 1.2),
         (43.36, .4), (44.30, .4), (47.42, .8), (50.79, .6), (51.72, .4), (53.77, .5), (55.30, .6), (58.84, .6),
         (61.38, .6), (63.01, .6), (64.52, .5), (66.41, .5), (66.98, .6), (69.17, 1.3), (71.72, 1.0), (76.94, .6),
         (77.57, .6), (77.2, .4), (78.4, .4)]
FLASH = [(13.56, .14, "w"), (19.65, .24, "r"), (38.64, .24, "r"), (69.17, .26, "r"), (71.72, .18, "r")]
CHROMA = [(19.65, .35), (38.64, .35), (66.98, .2), (69.17, .4), (71.72, .3)]
PALE = [0, 0, "NONE"]

for h in HERO:
    h["t0"], h["t1"] = round(tm(h["t0"]), 3), round(tm(h["t1"]), 3)
    if h.get("count"):
        h["count"]["t0"], h["count"]["t1"] = round(tm(h["count"]["t0"]), 3), round(tm(h["count"]["t1"]), 3)
for c in COMMENTS:
    c["t"] = round(tm(c["t"]), 3)
PUNCH = [(round(tm(t), 3), a) for t, a in PUNCH]
FLASH = [(round(tm(t), 3), a, c) for t, a, c in FLASH]
CHROMA = [(round(tm(t), 3), a) for t, a in CHROMA]
for _, _, labels in S:
    for l_ in labels:
        l_["t"] = tm(l_["t"])
        if "until" in l_:
            l_["until"] = tm(l_["until"])

scenes = []
for sid, bub, labels in S:
    t0 = T0[sid]
    for l_ in labels:
        l_["t"] = round(l_["t"] - t0, 3)
        if "until" in l_:
            l_["until"] = round(l_["until"] - t0, 3)
    scenes.append(dict(id=sid, bubble=bub, labels=labels, tilt=0, theme="city" if sid in CITY else "neon"))

cfg = dict(scenes=scenes, hero=HERO, comments=COMMENTS, comment_scene="K14", bisubs=SUBS, sub_y=1190,
           sub_style=dict(en_size=60, id_size=34, max_w=860),
           fx=dict(punch=PUNCH, flash=FLASH, chroma=CHROMA, pale=PALE), keywords=[])
json.dump(cfg, open("render/scenes/kpr.json", "w"), ensure_ascii=False, indent=1)

# ---------------------------------------------------------------- SFX (v2: lebih sedikit, halus, diredam di bawah VO)
# bom kejutan jatuh SEDIKIT SEBELUM kata kunci (kata tetap terdengar jelas), tanpa glitch/sirene/bass drop.
ev = []
for sid, t in TL[1:]:
    ev.append([t - .25, "whoosh_low", .18, .55])
EV1 = [
    # KORBAN
    [.55, "notif", .4], [5.6, "pop", .22], [7.72, "paper", .22, .45], [8.85, "coin", .2],
    # BI Rate 6%
    [13.35, "riser", .25, .3], [13.5, "impact", .3],
    # KEJUTAN 1: dicicil (bom)
    [14.6, "notif", .25], [16.1, "swoosh", .2], [19.0, "riser", .3, .6], [19.5, "boom", .26],
    [21.45, "pop", .16], [22.05, "pop", .16], [22.45, "pop", .18], [24.0, "ding", .22],
    # KPR Rp500 jt
    [26.3, "pop", .25], [28.1, "cash", .22], [29.8, "cash", .25], [32.5, "coins_pour", .22, 1.6],
    # BOM Rp98 jt
    [37.3, "riser", .3, 1.1], [38.45, "boom", .3], [38.6, "coins_pour", .18, 1.2],
    # KAIL: deposito, ekonom
    [41.2, "coins_pour", .14, .5], [47.35, "coin", .25], [47.7, "clank", .25],
    [50.7, "whoosh", .25, .5], [51.72, "tick", .14], [52.07, "tick", .14], [52.42, "tick", .14],
    # aman / kena
    [53.7, "sparkle", .25], [54.8, "pop", .22], [58.8, "stamp", .25], [61.35, "stamp", .27], [62.98, "stamp", .27],
    # KEJUTAN 2: rupiah (bom)
    [64.5, "pop", .2], [66.4, "sparkle", .2], [67.6, "riser", .3, 1.4], [69.0, "boom", .3], [71.6, "stamp", .26],
    # CTA
    [74.0, "whoosh", .25, .7], [76.9, "pop", .3], [77.5, "pop", .3], [77.2, "notif", .3], [78.4, "notif", .3],
]
for e in EV1:
    e[0] = round(tm(e[0]), 3)
    ev.append(e)
ev.sort(key=lambda e: e[0])
json.dump(ev, open("render/scenes/kpr_sfx.json", "w"), indent=0)
print(len(SUBS), "subtitle,", len(ev), "SFX")
