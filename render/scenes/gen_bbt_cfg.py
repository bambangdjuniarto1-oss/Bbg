"""buat render/scenes/bbt.json + render/scenes/bbt_sfx.json — "Sponsor terbesar Persib itu kamu (bobotoh)".
Rumus 3K: KORBAN (sponsor terbesar bukan Indofood / bjb, tapi KAMU) -> KEJUTAN 1 (16 sponsor Rp43–77 M vs bobotoh
Rp68–118 M; per kepala Rp10 rb vs jersey Rp1,19 jt = 119 bobotoh) -> KAIL (dada jersey milik NexAI, kontrak paling
kecil, padahal nilai perusahaannya naik Rp24 T; Glenn Sugita di dua kubu) -> CTA (logo apa di jersey? komentar + tag).
Tiap KEJUTAN diberi bom efek: flash + chroma + punch + SFX boom/gemuruh stadion.

  python3 render/scenes/gen_bbt_cfg.py [WORDS.json]
"""
import json
import re
import sys

WORDS = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "render/scenes/bbt_words.json"))
src = open("render/scenes_bbt.py").read()
TL = [(a, float(b)) for a, b in re.findall(r'\("(B\d\d)", ([\d.]+)\)', src)]
T0 = dict(TL)
CITY = set(re.search(r"CITY = \{([^}]*)\}", src).group(1).replace('"', "").replace(" ", "").split(","))

CUES = [
    (4, "**Sponsor terbesar** Persib itu"),
    (5, "bukan **Indofood**, bukan **bank bjb**,"),
    (2, "tapi **kamu**."),
    (7, "**16 sponsor** Persib musim ini diperkirakan menyetor"),
    (3, "**Rp43–77 miliar** setahun."),
    (7, "Sementara **bobotoh**, dari **tiket** dan **jersey** aja,"),
    (4, "bisa menyumbang **Rp68–118 miliar**."),
    (5, "Jadi kalau bobotoh itu **perusahaan**,"),
    (4, "dia **sponsor terbesar** Persib,"),
    (8, "lebih besar dari **semua brand** itu kalau digabung."),
    (6, "Bedanya makin kerasa kalau dihitung **per kepala**."),
    (9, "Uang sponsor kalau dibagi ke sekitar **6 juta bobotoh**,"),
    (7, "cuma sekitar **Rp10 ribu** per orang setahun."),
    (8, "Sedangkan **kamu**, buat satu jersey versi pemain aja,"),
    (2, "keluar **Rp1,19 juta**,"),
    (6, "artinya satu jersey yang kamu beli,"),
    (7, "setara jatah **119 bobotoh** dari uang sponsor."),
    (5, "Tapi yang **bayar paling besar**,"),
    (6, "justru **nggak dapat tempat** di jersey."),
    (5, "**Bagian dada**, posisi **paling mahal**,"),
    (2, "ditempati **NexAI**,"),
    (6, "yang nilai kontraknya diperkirakan **paling kecil**,"),
    (3, "cuma **Rp0,8–2 miliar**."),
    (6, "Padahal, dari **Januari** sampai akhir **September**,"),
    (6, "nilai perusahaannya naik sekitar **Rp24 triliun**,"),
    (6, "setara **400 tahun** uang sponsor Persib."),
    (7, "Dan di jajaran manajemennya ada **Glenn Sugita**,"),
    (5, "orang yang juga **mengendalikan Persib**."),
    (9, "Jadi, kalau bobotoh boleh pasang **logo sendiri** di jersey,"),
    (4, "kamu mau tulis **apa**?"),
    (8, "**Tulis di komentar**, terus **tag** teman bobotoh kamu."),
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


def lb(anchor, title, t, color="cyan", sub="", lift=60, until=None, dy=0):
    d = dict(anchor=anchor, title=title, sub=sub, color=color, t=t, lift=lift)
    if dy:
        d["dy"] = dy
    if until is not None:
        d["until"] = until
    return d


def hero(t0, t1, text, sub="", count=None, style="pink", size=104, y=1480):
    d = dict(t0=t0, t1=t1, text=text, sub=sub, style=style, size=size, y=y)
    if count:
        d["count"] = count
    return d


S = [
    ("B01", "Sponsor terbesar **Persib**?", [lb("GBLA", "STADION GBLA", 1.3, "cyan", "Gelora Bandung Lautan Api", 50)]),
    ("B02", "Bukan **Indofood**, bukan **bjb**", []),
    ("B03", "Tapi **KAMU**", []),
    ("B04", "**16 sponsor** musim 2026/27", [lb("BD", "16 MITRA SPONSOR PERSIB", 6.4, "cyan", "logo resmi • persib.co.id", 50)]),
    ("B05", "Sponsor: **Rp43–77 M**/tahun", [lb("RM", "RM.ID", 10.5, "purple", "Deputy CEO Adhitia: sponsor masuk > keluar", 50)]),
    ("B06", "Bobotoh: **tiket + jersey**", [lb("ST", "PERSIB STORE", 14.0, "cyan", "jersey & merchandise resmi", 50)]),
    ("B07", "Bobotoh: **Rp68–118 M**", []),
    ("B08", "Bobotoh = **sponsor terbesar**", []),
    ("B09", "Hitung **per kepala**", [lb("AL", "ALUN-ALUN BANDUNG", 27.6, "green", "", 50)]),
    ("B10", "Cuma **Rp10 ribu**/orang", []),
    ("B11", "1 jersey = **Rp1,19 juta**", []),
    ("B12", "= jatah **119 bobotoh**", [lb("AJ", "ANTARA", 42.0, "purple", "Deputy CEO Adhitia Putra Herawan • jersey 2026/27", 50)]),
    ("B13", "Bobotoh **nggak dapat tempat**", []),
    ("B14", "Dada jersey: **NexAI**", []),
    ("B15", "Kontrak **paling kecil**", [lb("AN", "EMITENNEWS", 57.5, "purple", "NexAI (MGLV) masuk daftar sponsor Persib", 50)]),
    ("B16", "NexAI naik **Rp24 T**", [lb("AK", "KONTAN", 62.2, "purple", "saham MGLV melesat 457% sepanjang 2026", 50)]),
    ("B17", "= **400 tahun** sponsor", []),
    ("B18", "**Glenn Sugita** di dua kubu", [lb("A1", "EMITENNEWS", 70.2, "purple", "bos Persib kendalikan NexAI", 12, until=71.85, dy=200),
                                       lb("A2", "ANTARA", 71.9, "purple", "Glenn Sugita, CEO PT PBB", 12, dy=200)]),
    ("B19", "Logo **kamu** di jersey?", []),
]

HERO = [
    hero(4.72, 5.83, "**KAMU**", "sponsor terbesar Persib", style="cyan", size=140),
    hero(9.30, 13.55, "Rp**43–77** miliar", "estimasi setoran 16 sponsor / tahun", style="cyan", size=104),
    hero(17.41, 21.2, "Rp**68–118** miliar", "estimasi tiket + jersey dari bobotoh / tahun", style="gold", size=100),
    hero(23.06, 24.6, "sponsor **#1**", "kalau bobotoh itu perusahaan", style="gold", size=112),
    hero(33.40, 35.3, "cuma Rp**10** ribu", "uang sponsor per bobotoh / tahun", style="cyan", size=112),
    hero(38.94, 41.45, "Rp**1.191.919**", "jersey player issue 2026/27", style="pink", size=104),
    hero(44.40, 47.3, "= **119** bobotoh", "jatah uang sponsor setahun", dict(t0=44.40, t1=45.2, frm=0, to=119, fmt="{}"),
         style="cyan", size=110),
    hero(58.30, 60.75, "Rp**0,8–2** miliar", "estimasi kontrak NexAI • paling kecil", style="pink", size=104),
    hero(65.00, 66.8, "+Rp**24** triliun", "naik nilai pasar NexAI (MGLV) Jan–Sep 2026", dict(t0=65.0, t1=65.8, frm=0, to=24, fmt="{}"),
         style="green", size=110),
    hero(67.10, 69.4, "**400** tahun", "uang sponsor Persib", dict(t0=67.1, t1=67.9, frm=0, to=400, fmt="{}"), style="gold",
         size=120, y=1720),
]

COMMENTS = [dict(t=76.6, text="BOBOTOH SAJAGAT", y=1400),
            dict(t=77.4, text="Logo Viking dong!", y=1550),
            dict(t=78.3, text="@balad_bobotoh liat ini", y=1700)]

PUNCH = [(0.05, .6), (2.68, .6), (3.30, .5), (3.81, .6), (4.30, .5), (4.75, 1.3), (5.83, .5), (9.30, .9),
         (13.69, .4), (14.98, .5), (15.48, .5), (17.41, .9), (22.20, .5), (23.06, 1.0), (25.21, .6), (27.25, .4),
         (29.53, .5), (31.94, .5), (33.46, .8), (35.78, .5), (38.94, .9), (44.43, .9), (47.40, .4), (48.12, .5),
         (50.75, .8), (52.38, .5), (53.26, .5), (55.00, 1.3), (57.37, .5), (58.37, .8), (61.63, .4), (65.07, 1.0),
         (67.15, .9), (70.91, 1.0), (72.24, .6), (73.53, .5), (76.66, .6), (77.48, .5), (78.20, .5)]
FLASH = [(4.75, .22, "w"), (23.06, .16, "w"), (44.43, .16, "w"), (55.00, .26, "r"), (65.07, .22, "w"), (70.91, .2, "r")]
CHROMA = [(4.75, .35), (23.06, .25), (50.75, .3), (55.00, .4), (65.07, .3), (70.91, .35)]
PALE = [0, 0, "NONE"]

scenes = []
for sid, bub, labels in S:
    t0 = T0[sid]
    for l_ in labels:
        l_["t"] = round(l_["t"] - t0, 3)
        if "until" in l_:
            l_["until"] = round(l_["until"] - t0, 3)
    scenes.append(dict(id=sid, bubble=bub, labels=labels, tilt=0, theme="city" if sid in CITY else "neon"))

cfg = dict(scenes=scenes, hero=HERO, comments=COMMENTS, comment_scene="B19", bisubs=SUBS, sub_y=1190,
           sub_style=dict(en_size=60, id_size=34, max_w=860),
           fx=dict(punch=PUNCH, flash=FLASH, chroma=CHROMA, pale=PALE), keywords=[])
json.dump(cfg, open("render/scenes/bbt.json", "w"), ensure_ascii=False, indent=1)

# ---------------------------------------------------------------- SFX padat: tiap animasi berbunyi; gemuruh stadion,
# yel, peluit, pop logo, stempel silang, uang/koin, berita, bom kejutan (sedikit sebelum kata kunci).
ev = []
for sid, t in TL[1:]:
    ev.append([t - .25, "whoosh_low", .2, .55])
ev += [
    # KORBAN: stadion, logo dicoret, KAMU
    [0.0, "whistle", .2, .7], [0.1, "roar", .26, 2.4], [1.2, "whoosh", .26, .9], [2.62, "whoosh", .2, .4],
    [2.85, "impact", .22], [3.30, "stamp", .3], [3.70, "whoosh", .2, .4], [3.92, "impact", .22], [4.30, "stamp", .3],
    [4.55, "boom", .3], [4.72, "goal", .3, 2.4],
    # 16 papan sponsor
    [5.9, "pop", .2], [6.25, "pop", .2], [6.6, "pop", .2], [6.95, "pop", .2], [7.3, "pop", .2], [7.65, "pop", .2],
    [8.0, "pop", .2], [8.35, "pop", .2], [6.2, "motor", .16, 1.5], [8.6, "horn", .1],
    # dinding logo + uang
    [9.2, "riser", .2, .5], [9.35, "sparkle", .24, .9], [9.5, "cash", .26], [10.2, "news", .22], [11.0, "coins_pour", .16, 1.2],
    # toko persib: tiket & jersey
    [13.9, "drum", .22, 2.4], [14.95, "ding", .24], [15.45, "ding", .24],
    # pilar
    [17.5, "swoosh", .22], [18.6, "riser", .22, 1.2], [19.9, "pop", .22], [20.1, "cheer", .2, 1.4],
    # timbangan
    [21.4, "pop", .2], [22.2, "pop", .22], [22.9, "boom", .28], [23.1, "clank", .26], [24.3, "flutter", .2, 1.0],
    [25.2, "clank", .22], [25.3, "stamp", .22], [26.0, "roar", .18, 1.4],
    # alun-alun per kepala
    [27.4, "bed", .2, 3.0], [29.5, "ding", .2],
    # dibagi 6 juta
    [30.6, "flutter", .2, .9], [31.9, "pop", .2], [32.35, "coins_pour", .24, 1.6], [33.4, "impact", .22],
    # jersey Rp1,19 juta
    [35.5, "whoosh", .2, .5], [36.6, "pop", .2], [38.85, "cash", .28], [38.9, "ding", .2],
    # 119 bobotoh
    [41.7, "news", .2], [43.6, "pop", .2], [43.75, "ticks", .16, 1.2], [44.35, "impact", .24], [45.0, "cheer", .18, 1.4],
    # KAIL: nggak dapat tempat
    [47.5, "whoosh", .2, .5], [47.9, "pop", .16], [48.1, "pop", .16], [48.3, "pop", .16], [48.5, "pop", .16],
    [48.7, "scan", .2, 1.0], [50.0, "whoosh", .22, .6], [50.7, "glitch", .3, .4], [50.75, "stamp", .28],
    # dada jersey: NexAI
    [52.3, "sparkle", .2, .9], [53.25, "pop", .22], [54.1, "riser", .28, .8], [54.86, "boom", .32], [55.0, "flash", .2],
    # kontrak paling kecil
    [56.0, "swoosh", .2], [57.3, "news", .22], [58.2, "pop", .24], [58.35, "impact", .18],
    # nilai perusahaan naik Rp24 T
    [60.95, "pop", .2], [61.5, "ticks", .18, 2.8], [62.0, "news", .2], [64.3, "riser", .28, .7], [64.95, "boom", .3],
    # 400 tahun
    [66.0, "pop", .2], [66.9, "coins_pour", .24, 1.6], [67.15, "impact", .26],
    # Glenn Sugita
    [69.6, "pop", .2], [69.8, "pop", .2], [70.0, "news", .2], [70.78, "boom", .28], [71.6, "scan", .2, .9],
    [71.7, "news", .2],
    # CTA
    [73.5, "whistle", .2, .7], [74.6, "drum", .22, 2.4], [75.0, "pop", .24],
    [76.6, "notif", .26], [76.7, "goal", .22, 2.4], [77.4, "notif", .26], [78.3, "notif", .26],
]
ev.sort(key=lambda e: e[0])
json.dump(ev, open("render/scenes/bbt_sfx.json", "w"), indent=0)
print(len(SUBS), "subtitle,", len(ev), "SFX")
