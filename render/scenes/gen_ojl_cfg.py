"""buat render/scenes/ojl.json + render/scenes/ojl_sfx.json — "Ojol Rp15.500, GoTo untung Rp441 miliar".
Rumus 3K: KORBAN (penumpang bayar Rp15.500, driver bawa Rp11.040) -> KEJUTAN 1 (GoTo untung Rp441 M / 3 bulan) ->
KAIL (driver 92%, tapi potongan dihitung sebelum komisi) -> KEJUTAN 2 (untungnya ada di HP kamu: GoPay Rp550 M,
pinjaman +59%) -> CTA (driver: naik/sama/turun; penumpang: tag teman).
Tiap KEJUTAN diberi bom efek: flash + chroma + punch + SFX boom (jatuh sedikit sebelum kata kunci).

  python3 render/scenes/gen_ojl_cfg.py WORDS.json
"""
import json
import re
import sys

WORDS = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "render/scenes/ojl_words.json"))
src = open("render/scenes_ojl.py").read()
TL = [(a, float(b)) for a, b in re.findall(r'\("(O\d\d)", ([\d.]+)\)', src)]
T0 = dict(TL)
CITY = set(re.search(r"CITY = \{([^}]*)\}", src).group(1).replace('"', "").replace(" ", "").split(","))

# (jumlah token VO, teks subtitle dengan **kata kunci**)
CUES = [
    (7, "Setiap kali kamu bayar ojol **Rp15.500**,"),
    (7, "driver kamu cuma bawa pulang **Rp11.040**,"),
    (7, "padahal potongannya katanya sudah turun jadi **8%**."),
    (5, "Dan di saat yang sama,"),
    (4, "**GoTo**, induk perusahaan Gojek,"),
    (11, "justru cetak untung **Rp441 miliar** cuma dalam **3 bulan**."),
    (8, "Kedengarannya kayak uang driver **pindah ke kantong perusahaan**,"),
    (6, "tapi ceritanya ternyata **nggak sesederhana itu**."),
    (8, "Dari sisi Gojek, driver **GoRide** sekarang dapat"),
    (5, "**92%** dari tarif perjalanan,"),
    (5, "harga buat penumpang **nggak dinaikkan**,"),
    (5, "dan **insentif driver** malah diperluas."),
    (8, "Gojek bahkan ngaku untung bisnis ojek dan antar makanannya"),
    (3, "cuma tumbuh **3%**."),
    (8, "Potongan yang masih **terasa besar** buat driver itu"),
    (6, "datang dari **biaya aplikasi** dan **asuransi**,"),
    (4, "yang dihitung **sebelum komisi**."),
    (7, "Nah, kalau bisnis ojeknya cuma tumbuh **3%**,"),
    (9, "berarti untung **ratusan miliar** itu datang dari tempat lain,"),
    (7, "dan tempat itu ada di **HP kamu**."),
    (7, "Di kuartal yang sama, **GoPay** menghasilkan untung"),
    (4, "**Rp550 miliar**,"),
    (8, "**lebih besar** dari seluruh bisnis ojek dan antar makanan."),
    (6, "Dan pendapatan dari **pinjaman** naik **59%**."),
    (9, "Jadi sekarang, aplikasi ojek itu lebih mirip **pintu masuk**,"),
    (7, "karena uangnya ada di **dompet digital** kamu."),
    (7, "Kalau kamu **driver**, tulis di komentar pendapatanmu"),
    (6, "sejak **Juli**: **naik**, **sama**, atau **turun**?"),
    (9, "Kalau kamu **penumpang**, **tag teman** kamu yang narik ojol,"),
    (9, "biar dia tahu ke mana sebenarnya **uang ini mengalir**."),
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
    ("O01", "Bayar ojol **Rp15.500**", [lb("FC", "SIMULASI 1 ORDER", 1.6, "cyan", "contoh rincian versi SPAI", 50, 2.9)]),
    ("O02", "Driver bawa **Rp11.040**", [lb("APP", "APLIKASI DRIVER", 3.4, "cyan", "ilustrasi rincian pendapatan", 50, 7.5)]),
    ("O03", "**GoTo**, induk Gojek", [lb("LOGO", "GOTO GOJEK TOKOPEDIA", 10.7, "green", "emiten BEI: GOTO", 50)]),
    ("O04", "Untung **Rp441 M** / 3 bulan", [lb("LK", "LAPORAN KEUANGAN INTERIM", 15.9, "cyan", "30 Sep 2026 • disampaikan ke BEI", 50),
                                          lb("AD", "DETIKFINANCE", 16.7, "purple", "GoTo cetak laba Rp441 miliar", 50)]),
    ("O05", "Uang driver **pindah**?", []),
    ("O06", "Driver dapat **92%**", [lb("AJ", "JAWAPOS", 24.6, "purple", "potongan 8% berlaku 1 Juli 2026", 50)]),
    ("O07", "Tarif tetap, **insentif +**", [lb("AK", "KATADATA", 28.8, "purple", "insentif driver diperluas", 50)]),
    ("O08", "Ojek & makanan cuma **+3%**", []),
    ("O09", "Dipotong **sebelum komisi**", [lb("PH", "RINCIAN PENDAPATAN", 37.0, "cyan", "ilustrasi • contoh SPAI", 50, 39.6),
                                         lb("AH", "DETIKFINANCE", 37.7, "purple", "hitungan potongan ojol 8%", 50)]),
    ("O10", "Untungnya di **HP kamu**", [lb("GP", "DOMPET DIGITAL", 50.5, "cyan", "", 50)]),
    ("O11", "GoPay **Rp550 M**", [lb("SL", "PRESENTASI GOTO Q3 2026", 52.9, "cyan", "EBITDA disesuaikan fintech +304%", 50),
                               lb("AG", "KATADATA", 55.8, "purple", "GoPay salip Gojek", 50)]),
    ("O12", "Pinjaman **+59%**", [lb("LR", "CATATAN 25 • LK INTERIM", 59.95, "gold", "pendapatan pinjaman 9 bulan 2026", 50)]),
    ("O13", "Aplikasi = **pintu masuk**", []),
    ("O14", "Driver: **naik / sama / turun**?", []),
    ("O15", "**Tag** teman ojolmu", []),
]

HERO = [
    hero(1.42, 2.95, "**Rp15.500**", "dibayar penumpang", style="cyan", size=112),
    hero(4.50, 5.70, "**Rp11.040**", "dibawa pulang driver", style="pink", size=112),
    hero(7.70, 8.85, "potongan **8%**", "Perpres 27/2026 • berlaku 1 Juli 2026", style="gold", size=100),
    hero(14.16, 18.55, "Rp**441** miliar", "laba GoTo • Q3 2026 (Jul–Sep)", dict(t0=14.16, t1=14.95, frm=0, to=441, fmt="{}"),
         style="red", size=116),
    hero(25.75, 28.2, "**92%**", "tarif perjalanan untuk driver GoRide", style="green", size=130),
    hero(36.03, 36.75, "cuma **+3%**", "laba ojek & antar makanan (EBITDA disesuaikan)", style="cyan", size=104),
    hero(39.75, 42.5, "-Rp2.500  -Rp1.000", "biaya aplikasi & asuransi (contoh SPAI)", style="pink", size=88),
    hero(42.53, 43.55, "baru **8%**", "komisi dihitung dari sisa Rp12.000", style="gold", size=100),
    hero(50.22, 51.3, "di **HP kamu**", "", style="cyan", size=116),
    hero(53.84, 56.0, "Rp**550** miliar", "EBITDA disesuaikan GoPay • Q3 2026", dict(t0=53.84, t1=54.6, frm=0, to=550, fmt="{}"),
         style="red", size=116),
    hero(56.0, 58.4, "> Rp**347** miliar", "ojek + antar makanan (on-demand) • Q3 2026", style="green", size=96),
    hero(59.97, 61.5, "**+59%**", "pendapatan pinjaman 9 bln 2026: Rp4,25 T vs Rp2,68 T", style="gold", size=124),
    hero(63.93, 65.0, "**PINTU MASUK**", "", style="green", size=104),
]

COMMENTS = [dict(t=69.0, text="TURUN. Order makin jarang, bonus susah", y=1400),
            dict(t=70.2, text="SAMA aja, potongannya pindah tempat", y=1550),
            dict(t=73.3, text="@temen_narik baca ini bro", y=1700)]

PUNCH = [(0.05, .6), (1.48, .6), (4.56, .7), (7.78, .5), (10.56, .5), (14.16, 1.3), (18.77, .4), (22.32, .5),
         (25.81, .9), (27.39, .3), (29.69, .4), (30.53, .5), (36.09, .7), (39.81, .6), (40.79, .6), (42.59, .8),
         (45.78, .5), (47.23, .4), (50.28, 1.2), (52.58, .6), (53.90, 1.3), (55.53, .5), (59.31, .5), (60.03, 1.0),
         (63.99, .9), (65.75, .5), (68.59, .4), (70.16, .6), (70.66, .6), (71.31, .6), (73.30, .5), (76.69, .5),
         (69.0, .4), (70.2, .4)]
FLASH = [(14.16, .26, "r"), (25.81, .14, "w"), (50.28, .22, "w"), (53.90, .26, "r"), (60.03, .18, "w")]
CHROMA = [(14.16, .4), (42.59, .25), (50.28, .3), (53.90, .4), (60.03, .25)]
PALE = [0, 0, "NONE"]

scenes = []
for sid, bub, labels in S:
    t0 = T0[sid]
    for l_ in labels:
        l_["t"] = round(l_["t"] - t0, 3)
        if "until" in l_:
            l_["until"] = round(l_["until"] - t0, 3)
    scenes.append(dict(id=sid, bubble=bub, labels=labels, tilt=0, theme="city" if sid in CITY else "neon"))

cfg = dict(scenes=scenes, hero=HERO, comments=COMMENTS, comment_scene="O14", bisubs=SUBS, sub_y=1190,
           sub_style=dict(en_size=60, id_size=34, max_w=860),
           fx=dict(punch=PUNCH, flash=FLASH, chroma=CHROMA, pale=PALE), keywords=[])
json.dump(cfg, open("render/scenes/ojl.json", "w"), ensure_ascii=False, indent=1)

# ---------------------------------------------------------------- SFX: suara jalanan (motor lewat, klakson),
# notif HP, uang/koin; bom kejutan sedikit sebelum kata kunci; semua diredam di bawah VO saat mixing.
ev = []
for sid, t in TL[1:]:
    ev.append([t - .25, "whoosh_low", .18, .55])
ev += [
    # KORBAN: kota, ojol berhenti, bayar
    [0.0, "whoosh", .3, .9], [.55, "motor", .32, 1.6], [1.25, "horn", .14], [1.45, "cash", .22], [1.7, "pop", .2],
    [3.0, "notif", .32], [3.4, "pop", .18], [4.5, "coin", .22], [7.6, "stamp", .26],
    # GoTo tower
    [9.2, "riser", .22, 1.2], [10.5, "motor", .18, 1.4], [11.0, "sparkle", .2],
    # BOM Rp441 M
    [13.3, "riser", .3, .8], [14.02, "boom", .3], [14.2, "coins_pour", .2, 1.6], [15.8, "paper", .22, .45],
    [16.4, "notif", .22],
    # koin melayang ke menara
    [19.4, "coins_pour", .16, 2.0], [21.6, "pop", .26], [22.2, "motor", .2, 1.4],
    # KAIL: 92%, tarif tetap, insentif
    [23.7, "pop", .22], [25.7, "impact", .26], [26.4, "swoosh", .2], [28.3, "stamp", .24], [30.4, "pop", .22],
    [30.9, "coins_pour", .16, .9],
    # food street +3%
    [32.8, "motor", .3, 1.5], [33.9, "horn", .12], [34.6, "motor", .24, 1.3], [36.0, "ding", .22],
    # potongan sebelum komisi
    [37.0, "notif", .26], [39.7, "stamp", .22], [40.7, "stamp", .22], [42.1, "pop", .2], [42.5, "clank", .24],
    # KEJUTAN 2: HP kamu
    [44.0, "motor", .2, 1.6], [46.2, "motor", .16, 1.4], [48.6, "riser", .28, 1.6], [50.14, "boom", .26],
    [50.3, "notif", .3],
    # GoPay Rp550 M
    [51.5, "whoosh", .2, .5], [53.1, "riser", .26, .7], [53.76, "boom", .28], [53.9, "cash", .22],
    [55.6, "paper", .2, .45], [56.3, "pop", .2],
    # pinjaman +59%
    [58.5, "whoosh", .22, .5], [59.6, "riser", .22, .5], [60.0, "impact", .26], [60.2, "sparkle", .2],
    # pintu masuk
    [61.6, "motor", .26, 1.5], [62.3, "motor", .2, 1.5], [63.95, "ding", .24], [64.9, "coins_pour", .2, 1.5],
    [65.75, "notif", .24],
    # CTA
    [67.4, "motor", .16, 1.6], [69.0, "notif", .26], [70.16, "pop", .26], [70.66, "pop", .26], [71.31, "pop", .26],
    [70.2, "notif", .24], [73.3, "notif", .26], [74.5, "whoosh", .22, .9],
]
ev.sort(key=lambda e: e[0])
json.dump(ev, open("render/scenes/ojl_sfx.json", "w"), indent=0)
print(len(SUBS), "subtitle,", len(ev), "SFX")
