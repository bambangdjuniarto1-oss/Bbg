"""buat render/scenes/kpr.json + render/scenes/kpr_sfx.json — "KPR naik Rp83 rb, BI Rate 6%".
Rumus 3K: KORBAN (tagihan +Rp83 rb, santai) -> KEJUTAN 1 (ternyata dicicil sejak Mei, total Rp98 jt) ->
KAIL (deposito cuma +Rp17 rb, siapa yang kena) -> KEJUTAN 2 (rupiah rekor terlemah) -> CTA (FIXED/FLOATING).
Tiap KEJUTAN diberi bom efek: flash merah + chroma + punch + SFX boom/bass drop.

  python3 render/scenes/gen_kpr_cfg.py WORDS.json
"""
import json
import re
import sys

WORDS = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "render/scenes/kpr_words.json"))
src = open("render/scenes_kpr.py").read()
TL = [(a, float(b)) for a, b in re.findall(r'\("(K\d\d)", ([\d.]+)\)', src)]
END = float(re.search(r"END_T = ([\d.]+)", src).group(1))
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

# ---------------------------------------------------------------- SFX
ev = []
for sid, t in TL[1:]:
    ev.append([t - .22, "whoosh_low", .26, .55])
ev += [
    # KORBAN: notifikasi tagihan, santai
    [0.0, "boom", .3], [.6, "notif", .55], [.85, "ding", .3], [2.89, "pop", .3], [5.6, "pop", .3],
    [7.4, "paper", .35, .45], [7.72, "flutter", .3, .8], [8.85, "coin", .3], [8.95, "coin", .25], [9.05, "coin", .22],
    # BI Rate 6%
    [11.12, "clank", .35], [11.31, "pop", .3], [12.4, "paper", .3, .45], [12.9, "paper", .3, .45],
    [13.3, "riser", .4, .3], [13.56, "impact", .55], [13.56, "news", .35],
    # KEJUTAN 1: riwayat dicicil -> BOM
    [14.6, "notif", .4], [15.0, "type", .25, 1.5], [16.1, "swoosh", .3], [18.6, "riser", .45, 1.0],
    [19.65, "boom", .75], [19.65, "bass_drop", .55], [19.65, "stamp", .55], [20.49, "glitch", .35, .3],
    [21.45, "tick", .25], [21.65, "tick", .25], [21.85, "tick", .25], [22.05, "tick", .25], [22.25, "pop", .3],
    [22.45, "pop", .3], [22.76, "impact", .35], [23.4, "pop", .25], [24.11, "ding", .35],
    # KPR 500 jt: uang bertambah, koin keluar tiap bulan
    [26.39, "pop", .4], [28.17, "cash", .35], [29.89, "cash", .4], [29.89, "impact", .3],
    [32.59, "coins_pour", .4, 1.8], [32.59, "impact", .4],
    # BOM 98 juta
    [35.6, "whoosh", .35, .5], [36.34, "flutter", .3, 1.0], [36.99, "pop", .3], [37.2, "riser", .5, 1.4],
    [38.64, "boom", .8], [38.64, "bass_drop", .55], [38.64, "coins_pour", .45, 1.6], [38.9, "ding", .35],
    # KAIL: timbangan, deposito cuma 17 rb
    [41.2, "coins_pour", .25, .6], [42.2, "paper", .3, .45], [44.3, "pop", .3], [47.42, "coin", .35],
    [47.6, "clank", .4], [47.9, "impact", .35],
    # cepat naik, lambat turun
    [49.3, "paper", .3, .45], [50.6, "riser", .35, .25], [50.79, "whoosh", .45, .5], [51.72, "tick", .25],
    [52.07, "tick", .25], [52.42, "tick", .25],
    # siapa aman / siapa kena
    [53.77, "sparkle", .4], [54.82, "pop", .35], [55.3, "ding", .4], [58.84, "siren", .35, 1.2], [58.84, "stamp", .4],
    [61.38, "stamp", .45], [63.01, "stamp", .45],
    # KEJUTAN 2: jaga rupiah -> rekor terlemah
    [63.6, "pop", .3], [64.52, "pop", .35], [66.41, "sparkle", .3], [66.98, "riser", .55, 2.1], [68.0, "paper", .3, .45],
    [69.17, "boom", .85], [69.17, "bass_drop", .6], [69.17, "glitch", .4, .4], [70.4, "paper", .3, .45],
    [71.72, "stamp", .65], [71.72, "impact", .5],
    # CTA
    [74.0, "whoosh", .35, .7], [76.94, "pop", .45], [77.57, "pop", .45], [77.2, "notif", .45], [78.4, "notif", .45],
    [79.4, "sparkle", .3],
]
for h in HERO:
    if h.get("count"):
        c = h["count"]
        ev.append([c["t0"], "ticks", .26, c["t1"] - c["t0"]])
ev.sort(key=lambda e: e[0])
json.dump(ev, open("render/scenes/kpr_sfx.json", "w"), indent=0)
print(len(SUBS), "subtitle,", len(ev), "SFX")
