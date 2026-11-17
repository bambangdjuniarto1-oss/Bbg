"""buat render/scenes/vap.json (overlay & efek) + render/scenes/vap_sfx.json (efek suara) dari waktu absolut.
Label/HUD: detik absolut -> lokal adegan. hero/fx/komentar: detik absolut (timeline video)."""
import json
import re

src = open("render/scenes_vap.py").read()
TL = [(a, float(b)) for a, b in re.findall(r'\("(V\d\d)", ([\d.]+)\)', src)]
END = float(re.search(r"END_T = ([\d.]+)", src).group(1))
T0 = dict(TL)


def lb(anchor, title, t, color="purple", sub="", lift=90, until=None):
    d = dict(anchor=anchor, title=title, sub=sub, color=color, t=t, lift=lift)
    if until is not None:
        d["until"] = until
    return d


def hero(t0, t1, text, sub="", count=None, style="pink", size=124):
    d = dict(t0=t0, t1=t1, text=text, sub=sub, style=style, size=size)
    if count:
        d["count"] = count          # dict(t0, t1, frm, to, fmt) ; fmt mis. "Rp{}" (angka bertitik)
    return d


# (id, bubble, labels, hud, tilt-shift)
S = [
    ("V01", "1 botol liquid **Rp120 ribu**", [lb("BOTOL", "LIQUID 60 ML", .9, "pink", "", 70)], None, 0),
    ("V02", "Siapa dapat **bagian terbesar**?", [lb("SHOP", "PENJUAL?", 6.3, "cyan", "", 70),
                                                 lb("FAC", "PABRIK?", 7.15, "purple", "", 70)], None, .5),
    ("V03", "Kita **bedah** 1 botol 60 ml", [lb("TOP", "???", 10.0, "gold", "", 60),
                                             lb("BRAND", "BRAND", 10.5, "purple", "", 60),
                                             lb("TOKO", "TOKO", 10.9, "cyan", "", 60)], None, 0),
    ("V04", "Toko ambil **margin**", [lb("SHOP", "TOKO VAPE", 12.2, "cyan", "", 70)], None, 0),
    ("V05", "Brand dapat **Rp48 ribu**… tapi", [
        lb("IC0", "BAHAN BAKU", 17.23, "green", "", 40), lb("IC1", "BOTOL", 17.93, "cyan", "", 70),
        lb("IC2", "PRODUKSI", 18.19, "orange", "", 40), lb("IC3", "DISTRIBUSI", 18.64, "gold", "", 70),
        lb("IC4", "MARKETING", 19.19, "pink", "", 40)], None, 0),
    ("V06", "Untung bersih **jauh lebih kecil**", [lb("GHOST", "Rp48 RB (KOTOR)", 20.0, "purple", "", 40),
                                                   lb("SMALL", "UNTUNG BERSIH", 20.6, "green", "", 50)], None, .45),
    ("V07", "**Rp42 ribu** sisanya ke mana?", [lb("TOP", "???", 25.3, "gold", "", 70)], None, 0),
    ("V08", "Wajib pakai **pita cukai**", [lb("PITA", "PITA CUKAI", 30.75, "cyan", "", 60),
                                           lb("DROP", "1 ML", 31.9, "gold", "", 50)], None, 0),
    ("V09", "60 ml × **Rp636**", [lb("GRID", "60 ML = 60 × Rp636", 35.5, "gold", "", 60)],
     dict(title="CUKAI 1 BOTOL", start=0, keys=[[35.5, 0], [37.15, 38160]], max=42000, unit="", t=35.0, dur=1.6,
          prefix="Rp ", target_text="60 ml × Rp636"), .5),
    ("V10", "Ditambah **pajak rokok**", [lb("BIG", "CUKAI ±Rp38 RB", 38.95, "gold", "", 60),
                                         lb("SMALL", "PAJAK ROKOK ±Rp4 RB", 39.65, "orange", "±10% dari cukai", 60)],
     None, 0),
    ("V11", "**Rp42 ribu** masuk ke negara", [lb("GOV", "NEGARA", 43.4, "gold", "", 60)], None, 0),
    ("V12", "Bagian **paling besar**", [lb("TOKO", "TOKO Rp30 RB", 44.5, "cyan", "", 50),
                                        lb("BRAND", "BRAND Rp48 RB", 44.9, "purple", "sebagian besar biaya", 70),
                                        lb("NEGARA", "NEGARA Rp42 RB", 45.35, "gold", "utuh", 50)], None, 0),
    ("V13", "Pasar liquid jadi **\"aneh\"**", [lb("ODD", "TANPA PITA CUKAI?", 48.0, "red", "", 60)], None, .35),
    ("V14", "Tanpa pita cukai = **lebih murah**", [lb("L", "RESMI", 51.45, "green", "ada pita cukai", 60),
                                                   lb("R", "TANPA PITA CUKAI", 51.9, "red", "jauh lebih murah", 60)],
     None, 0),
    ("V15", "Bukan efisien, tapi **ilegal**", [lb("GEAR", "LEBIH EFISIEN?", 55.2, "orange", "bukan", 50, 4.0),
                                               lb("CHEAP", "KEWAJIBAN DILEWATI", 56.6, "red", "", 60)], None, .45),
    ("V16", "**Pelajarannya**", [lb("TOKO", "TOKO Rp30 RB", 61.9, "cyan", "", 60),
                                 lb("BRAND", "BRAND Rp48 RB", 62.3, "purple", "", 60),
                                 lb("NEGARA", "NEGARA Rp42 RB", 62.7, "gold", "", 60)], None, .4),
    ("V17", "Kamu **tahu nggak**?", [lb("PL", "CUKAI + PAJAK", 65.0, "gold", "", 70)], None, 0),
    ("V18", "Ketik **TAHU** / **BARU TAHU**", [], None, 0),
    ("V19", "Kirim ke temen yang **ngeluh mahal**", [lb("P1", "KAMU", 72.6, "cyan", "", 50),
                                                     lb("P2", "TEMEN YANG NGELUH", 73.9, "red", "\"liquid mahal!\"",
                                                        50)], None, 0),
    ("V20", "Part 2: **modal bikin brand**", [lb("BOX", "MODAL BIKIN BRAND?", 77.9, "pink", "", 60)], None, 0),
]

HERO = [
    hero(1.55, 3.75, "**Rp120.000**", "1 botol liquid 60 ml",
         dict(t0=1.55, t1=2.25, frm=0, to=120000, fmt="Rp{}")),
    hero(8.0, 8.85, "BUKAN **DUA-DUANYA**", "", style="red", size=92),
    hero(10.3, 11.9, "**60 ml**", "dibedah jadi 3 bagian"),
    hero(13.35, 14.5, "**Rp30.000**", "margin toko (contoh)", dict(t0=13.35, t1=13.85, frm=0, to=30000, fmt="Rp{}"),
         style="cyan"),
    hero(15.2, 17.1, "**Rp48.000**", "bagian brand (kotor)", dict(t0=15.2, t1=15.75, frm=0, to=48000, fmt="Rp{}"),
         style="purple"),
    hero(20.0, 24.3, "Untung bersih: **kecil**", "setelah semua biaya", style="green", size=96),
    hero(25.1, 29.2, "**Rp42.000** ?", "sisanya ke mana?", dict(t0=25.1, t1=25.6, frm=0, to=42000, fmt="Rp{}"),
         style="gold"),
    hero(31.75, 34.3, "**Rp636**/ml", "tarif cukai liquid", style="gold"),
    hero(40.35, 41.55, "+ **Rp4.000**", "pajak rokok", style="orange"),
    hero(41.85, 44.2, "Total **Rp42.000**", "masuk ke negara", dict(t0=41.85, t1=42.5, frm=38000, to=42000,
                                                                     fmt="Rp{}"), style="gold", size=110),
    hero(49.8, 51.15, "**\"ANEH\"**", "", style="pink", size=150),
    hero(58.4, 59.25, "**ILEGAL**", "", style="red", size=170),
    hero(59.5, 61.2, "**Rp120.000**", "harga jual, dibagi ke siapa saja?", style="pink", size=110),
    hero(66.5, 68.6, "**Rp42.000**", "buat negara. Kamu tahu?", style="gold"),
]

COMMENTS = [dict(t=69.38, text="TAHU", y=1395), dict(t=70.24, text="BARU TAHU", y=1545)]

# efek kamera/pasca: impact = guncang + zoom-punch (+kilat); glitch = RGB split; transisi di tiap batas adegan
IMPACT = [(1.68, .7), (8.03, .8), (8.85, 1.0), (13.43, .6), (15.27, .6), (24.47, .9), (25.13, .6), (29.38, 1.0),
          (30.67, .5), (31.77, .6), (37.13, .7), (40.39, .6), (41.88, .7), (43.6, .8), (45.35, .6), (51.26, 1.0),
          (58.43, 1.4), (61.4, .6), (66.6, .6), (69.41, .6), (70.26, .6), (77.03, .8)]
GLITCH = [(24.47, .3), (25.1, .25), (46.7, .2), (49.85, .55), (58.43, .5), (58.95, .2)]
FLASH = [(8.85, .6, "w"), (29.38, .6, "w"), (51.26, .6, "w"), (58.43, .8, "r"), (24.47, .4, "w")]
TRANS = ["zoom", "whip", "whip_l", "zoom_out", "whip", "zoom", "whip_l", "zoom", "whip", "zoom_out", "whip_l",
         "zoom", "whip", "zoom", "whip_l", "zoom_out", "whip", "zoom", "whip_l"]

scenes = []
for i, (sid, bub, labels, hud, ts) in enumerate(S):
    t0 = T0[sid]
    for l_ in labels:
        l_["t"] = round(l_["t"] - t0, 3)
        if "until" in l_:
            l_["until"] = round(l_["until"], 3)
    d = dict(id=sid, bubble=bub, labels=labels, tilt=ts)
    if hud:
        hud = dict(hud)
        hud["t"] = round(hud["t"] - t0, 3)
        hud["keys"] = [[round(a - t0, 3), b] for a, b in hud["keys"]]
        hud["pos"] = [56, 1430]
        d["hud"] = hud
    if sid == "V20":
        d["cta"] = 2.0
    scenes.append(d)

trans = [dict(t=T0[sid], kind=TRANS[i - 1]) for i, (sid, _) in enumerate(TL) if i > 0]
cfg = dict(scenes=scenes, hero=HERO, comments=COMMENTS,
           fx=dict(impact=IMPACT, glitch=GLITCH, flash=FLASH, trans=trans),
           keywords=["Rp120.000", "bagian", "besar", "bedah", "60", "ml", "margin", "Rp30.000", "Rp48.000",
                     "bersihnya", "kecil", "Rp42.000", "pita", "cukai", "Rp636", "Rp38.000", "pajak", "rokok",
                     "Rp4.000", "negara", "aneh", "murah", "efisien", "dilewati", "ilegal", "Pelajarannya", "untung",
                     "jualmu", "TAHU", "BARU", "komentar", "temen", "mahal", "follow", "part", "modal", "brand"])
json.dump(cfg, open("render/scenes/vap.json", "w"), ensure_ascii=False, indent=1)

# ---------------------------------------------------------------- SFX
ev = []
for tr in trans:
    k = tr["kind"]
    ev.append([tr["t"] - .28, "whoosh" if "whip" in k else ("whoosh_low" if k == "zoom" else "whoosh_rev"), .55])
for t, g in IMPACT:
    ev.append([t, "impact" if g >= .9 else "pop", .55 * g if g >= .9 else .7])
for t, d in GLITCH:
    ev.append([t, "glitch", .5, d])
for h in HERO:
    if h.get("count"):
        c = h["count"]
        ev.append([c["t0"], "ticks", .32, c["t1"] - c["t0"]])
        ev.append([c["t1"], "coin", .45])
ev += [[0.05, "boom", .5], [9.4, "scan", .4, 1.6], [13.55, "coin", .4], [16.0, "swoosh", .3],
       [17.23, "pop", .5], [17.93, "pop", .5], [18.19, "pop", .5], [18.64, "pop", .5], [19.19, "pop", .5],
       [20.5, "swoosh", .35], [30.5, "sticker", .7], [35.5, "ticks", .3, 1.6], [37.15, "coin", .45],
       [40.35, "stamp", .35], [43.55, "boom", .45], [45.35, "ding", .4], [55.7, "stamp", .4],
       [56.4, "whoosh", .3, .9], [58.43, "stamp", .9], [58.43, "siren", .35, 1.0], [61.3, "whoosh_low", .45],
       [69.38, "type", .45, 4], [69.7, "notif", .45], [70.24, "type", .45, 9], [70.7, "notif", .45],
       [72.6, "whoosh", .45, .9], [73.75, "notif", .4], [74.2, "stamp", .4], [77.4, "ding", .35],
       [77.45, "notif", .3]]
ev.sort(key=lambda e: e[0])
json.dump(ev, open("render/scenes/vap_sfx.json", "w"))
print(len(scenes), "adegan,", len(ev), "sfx")
