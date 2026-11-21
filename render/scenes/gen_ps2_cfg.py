"""buat render/scenes/ps2.json (overlay dokumenter + subtitle 2 bahasa proporsional) + render/scenes/ps2_sfx.json —
Persib Part 2: mesin uang Persib.

  python3 render/scenes/gen_ps2_cfg.py WORDS.json CROWD.wav
"""
import json
import re
import sys

WORDS = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "render/scenes/ps2_words.json"))
CROWD = sys.argv[2] if len(sys.argv) > 2 else "crowd.wav"

src = open("render/scenes_ps2.py").read()
TL = [(a, float(b)) for a, b in re.findall(r'\("(Q\d\d)", ([\d.]+)\)', src)]
END = float(re.search(r"END_T = ([\d.]+)", src).group(1))
T0 = dict(TL)

# (jumlah token VO, EN dengan **kata kunci**, terjemahan ID) — kalimat pendek supaya teks tidak melebar
CUES = [
    (9, "Persib's **YouTube** channel has more than **2 million** subscribers.",
     "Channel YouTube Persib punya lebih dari 2 juta subscriber."),
    (6, "But its **ad revenue** is estimated", "Tapi pendapatan iklannya diperkirakan"),
    (7, "at only around **$2,700** a month.", "cuma sekitar Rp45 juta sebulan."),
    (8, "So... where does the **big money** come from?", "Terus... uang besarnya dari mana?"),
    (6, "The **first door** is **the league**.", "Pintu pertama: liga."),
    (9, "This season, every club gets about **$1.6 million**", "Musim ini, tiap klub dapat Rp27 miliar"),
    (4, "from the **league operator**,", "dari operator liga,"),
    (5, "up from **$1.1 million**.", "naik dari Rp19 miliar."),
    (8, "And that's before **TV rights** and **ranking bonuses**.", "Belum termasuk hak siar dan bonus peringkat."),
    (5, "But **every club** gets that.", "Tapi semua klub dapat itu."),
    (9, "What makes Persib different is its fans, the **Bobotoh**.", "Yang bikin Persib beda: bobotoh."),
    (7, "This season, Persib plays in **four competitions**,", "Musim ini, Persib main di empat kompetisi,"),
    (5, "at least **24 home matches**.", "minimal 24 laga kandang."),
    (9, "If each match draws **14 to 20,000** fans,", "Kalau tiap laga ditonton 14–20 ribu orang,"),
    (5, "**tickets** alone could bring in", "tiketnya saja bisa menghasilkan"),
    (7, "**$2.7 to $5 million** a season.", "Rp46–90 miliar semusim."),
    (8, "**Jerseys?** The first **pre-order** alone reportedly made", "Jersey, dari PO pertama aja, kabarnya laku"),
    (4, "**$400 to $600,000**.", "Rp7–10 miliar."),
    (6, "Add **official stores** in **seven locations**,", "Ditambah toko resmi di tujuh lokasi,"),
    (7, "and a **membership** program inside their app.", "dan membership di aplikasi."),
    (5, "The Bobotoh aren't just **fans**.", "Bobotoh bukan cuma penonton."),
    (3, "They're **loyal customers**.", "Mereka pelanggan tetap."),
    (6, "And from **Asia**, there's **extra money**.", "Dan dari Asia, ada uang tambahan."),
    (6, "In the **AFC Champions League Two**,", "Di Liga Champions Asia Two,"),
    (5, "every win pays **$50,000**.", "tiap kemenangan dibayar 50 ribu dolar."),
    (5, "The **first two wins** alone", "Dua kemenangan pertama aja,"),
    (5, "brought in around **$400,000**.", "sekitar tujuh miliar rupiah."),
    (9, "But **one incident** can make all these doors **leak**.", "Tapi satu insiden bisa bikin semua pintu ini bocor."),
    (7, "A **$200,000 fine** from the AFC", "Denda AFC 3,5 miliar rupiah,"),
    (7, "plus two home matches with **no fans**.", "plus dua laga kandang tanpa penonton."),
    (8, "In total, around **half a million dollars**, gone.", "Totalnya 8 sampai hampir 10 miliar rupiah, melayang."),
    (9, "So, **millions of followers** don't automatically turn into money.",
     "Jadi, follower jutaan nggak otomatis jadi uang."),
    (6, "Persib turns them into **cash** through", "Persib mengubahnya jadi uang lewat"),
    (3, "**tickets**, **jerseys**, **stores**,", "tiket, jersey, toko,"),
    (3, "**memberships** and **sponsors**.", "membership, dan sponsor."),
    (7, "And once its **assets** are sorted out,", "Kalau asetnya sudah beres,"),
    (10, "the club's value is estimated to reach **1 trillion rupiah**.", "nilai klubnya ditaksir tembus Rp1 triliun."),
    (5, "That's around **60 million dollars**.", "Sekitar 60 juta dolar AS."),
    (12, "Which club in **your country** makes money from its fans like this?",
     "Klub mana di negaramu yang dapat uang dari fans seperti ini?"),
    (6, "Drop the **name** in the comments.", "Tulis namanya di komentar."),
    (8, "**Save** this, and **follow** for more business breakdowns.", "Simpan, dan follow buat bedah bisnis lainnya."),
]
assert sum(c[0] for c in CUES) == len(WORDS), (sum(c[0] for c in CUES), len(WORDS))
BISUBS = []
i = 0
for k, (nw, en, idt) in enumerate(CUES):
    ws = WORDS[i:i + nw]
    i += nw
    t0 = ws[0][0] - .06
    end = ws[-1][1] + .4
    if k + 1 < len(CUES):
        nxt = WORDS[i][0] - .06
        end = nxt if nxt - ws[-1][1] < .7 else ws[-1][1] + .45
    BISUBS.append([round(t0, 3), round(end, 3), en, idt])


def lb(anchor, title, t, color="cyan", sub="", lift=60, until=None, dx=0, dy=0):
    d = dict(anchor=anchor, title=title, sub=sub, color=color, t=t, lift=lift)
    if dx or dy:
        d["dx"], d["dy"] = dx, dy
    if until is not None:
        d["until"] = until
    return d


def hero(t0, t1, text, sub="", count=None, style="cyan", size=96, y=1500, font="slab"):
    d = dict(t0=t0, t1=t1, text=text, sub=sub, style=style, size=size, y=y, font=font)
    if count:
        d["count"] = count
    return d


S = [
    ("Q01", "YouTube **2,5 juta** subscriber", [lb("YT", "PERSIB YOUTUBE", .7, "red", "2,54 jt subscriber • 3,2 rb video")]),
    ("Q02", "Iklannya cuma **±$2,7 rb**", [lb("VQ", "VIDIQ", 4.4, "purple", "estimasi, bukan laporan resmi", 60, 6.9)]),
    ("Q03", "Uang besarnya **dari mana**?", []),
    ("Q04", "Pintu 1: **liga**", []),
    ("Q05", "Subsidi **Rp27 miliar**/klub", [lb("AR", "BOLA.COM", 15.6, "purple", "RUPS I.League, 26 Agu 2026")]),
    ("Q06", "+ **hak siar** & bonus", []),
    ("Q07", "Bedanya: **bobotoh**", []),
    ("Q08", "**24 laga** kandang", []),
    ("Q09", "Tiket **Rp46–90 M**/musim", [lb("AP", "GOODSTATS", 30.4, "purple", "185.574 penonton GBLA s.d. pekan 17")]),
    ("Q10", "Jersey: PO **Rp7–10 M**", [lb("AJ", "BOLA.COM", 38.9, "purple", "angka kabar, belum dikonfirmasi klub")]),
    ("Q11", "**7 toko** + membership", [lb("ST", "PERSIB STORE CIBUBUR", 42.9, "cyan", "toko ke-7 • Juli 2025", 60, 44.6),
                                     lb("MP", "MEMBERSIB", 44.0, "purple", "4 kategori membership")]),
    ("Q12", "Fans = **pelanggan tetap**", []),
    ("Q13", "Uang tambahan **dari Asia**", [lb("ACL", "ACL TWO", 51.7, "gold", "AFC Champions League Two", 50, 53.0),
                                        lb("AA", "A-LEAGUES (AUSTRALIA)", 52.6, "purple", "media luar negeri")]),
    ("Q14", "**2 kemenangan** pertama", [lb("SB1", "16 SEP 2026", 55.6, "cyan", "di Seoul", 40),
                                       lb("SB2", "14 OKT 2026", 56.0, "cyan", "di Si Jalak Harupat", 40)]),
    ("Q15", "Satu insiden, **semua bocor**", []),
    ("Q16", "Denda **Rp3,5 M** + tanpa penonton", [lb("AD", "METROTV", 63.2, "red", "sanksi AFC, 13 Mei 2026")]),
    ("Q17", "Follower **bukan** uang", []),
    ("Q18", "Valuasi **Rp1 triliun**", [lb("AW", "WIKIPEDIA (EN)", 78.9, "purple", "2026–27 Persib season", 60, 80.9)]),
    ("Q19", "Klub negaramu **gimana**?", []),
]

HERO = [
    hero(1.62, 3.0, "**2,54 juta**", "subscriber YouTube PERSIB (Nov 2026)", style="red", size=110),
    hero(5.57, 7.35, "**$2,7 rb**/bulan", "≈ Rp45 juta • estimasi iklan YouTube", style="red"),
    hero(10.32, 11.6, "PINTU **#1**", "liga", style="gold", size=104),
    hero(13.73, 16.2, "**Rp27 M**/klub", "≈ US$1,6 jt • subsidi I.League 2026/27", style="gold", size=104),
    hero(16.79, 17.8, "dari **Rp19 M**", "2025/26 ≈ US$1,1 jt", style="cyan"),
    hero(18.62, 20.3, "+ **hak siar** + bonus", "di luar subsidi", style="cyan", size=88),
    hero(24.28, 24.88, "**BOBOTOH**", "", style="cyan", size=110),
    hero(26.44, 27.9, "**4** kompetisi", "Super League • I.League Cup • Shopee Cup • ACL Two", style="cyan"),
    hero(28.0, 29.3, "**24** laga kandang", "minimal semusim", dict(t0=28.0, t1=28.65, frm=0, to=24, fmt="{}"),
         style="gold"),
    hero(30.41, 32.4, "**14–20 rb**/laga", "asumsi penonton per laga kandang", style="cyan"),
    hero(33.70, 36.05, "**$2,7–5 jt**", "≈ Rp46–90 M tiket semusim (estimasi)", style="gold", size=104),
    hero(38.77, 40.9, "**$400–600 rb**", "≈ Rp7–10 M dari PO pertama (kabarnya)", style="gold"),
    hero(42.35, 43.5, "**7** lokasi", "PERSIB Store", style="cyan", size=104),
    hero(47.85, 48.95, "**pelanggan** tetap", "", style="gold"),
    hero(53.79, 55.0, "**$50 rb**/menang", "+ biaya partisipasi fase grup US$300 rb", style="gold"),
    hero(57.22, 58.85, "± **$400 rb**", "≈ Rp7 M • partisipasi grup + bonus 2 kemenangan", style="gold", size=104),
    hero(62.06, 63.9, "**- $200 rb**", "denda AFC ≈ Rp3,5 M", style="red", size=104),
    hero(64.49, 66.4, "**2 laga** tanpa penonton", "laga kandang kompetisi AFC", style="red", size=88),
    hero(67.61, 69.5, "± **$0,5 jt** melayang", "≈ Rp8–10 M • denda + tiket hilang (estimasi)", style="red", size=88),
    hero(70.42, 72.4, "follower **≠** uang", "", style="red", size=96),
    hero(81.48, 84.7, "**Rp1 triliun**", "≈ US$60 jt • taksiran bila aset dibereskan", style="gold", size=110),
]

COMMENTS = [dict(t=88.6, text="Buriram United, Thailand!", y=1420), dict(t=89.6, text="Johor Darul Ta'zim, Malaysia", y=1570)]

PUNCH = [(1.62, .7), (3.6, .4), (5.57, .8), (8.54, .5), (10.32, .9), (12.73, .4), (13.73, .8), (16.79, .5),
         (18.62, .5), (19.36, .5), (20.6, .4), (22.3, .6), (24.28, 1.0), (26.44, .6), (28.0, .7), (30.41, .5),
         (32.53, .5), (33.70, .8), (36.32, .6), (37.51, .5), (38.77, .8), (41.75, .5), (42.35, .6), (43.66, .5),
         (46.84, .5), (47.85, .8), (49.63, .6), (51.56, .5), (53.79, .7), (55.43, .5), (55.83, .5), (57.22, .9),
         (59.54, .8), (61.18, .7), (62.06, 1.0), (64.49, .8), (67.61, .8), (70.42, .5), (73.88, .6), (74.41, .4),
         (75.03, .4), (75.69, .4), (76.37, .4), (77.11, .5), (79.11, .5), (81.48, 1.0), (85.73, .5), (88.6, .4),
         (89.6, .4), (90.69, .5)]
FLASH = [(10.32, .18, "w"), (24.28, .16, "w"), (59.54, .2, "r"), (62.06, .2, "r"), (81.48, .2, "w")]
CHROMA = [(59.54, .3), (61.18, .2), (62.06, .3), (64.49, .2), (70.42, .15)]
PALE = [0, 0, "NONE"]

scenes = []
for sid, bub, labels in S:
    t0 = T0[sid]
    for l_ in labels:
        l_["t"] = round(l_["t"] - t0, 3)
        if "until" in l_:
            l_["until"] = round(l_["until"] - t0, 3)
    scenes.append(dict(id=sid, bubble=bub, labels=labels, tilt=0, theme="neon", look="doc"))

cfg = dict(scenes=scenes, hero=HERO, comments=COMMENTS, comment_scene="Q19", bisubs=BISUBS, sub_y=1165,
           sub_style=dict(en_size=54, id_size=34, max_w=840),
           fx=dict(punch=PUNCH, flash=FLASH, chroma=CHROMA, pale=PALE), keywords=[])
json.dump(cfg, open("render/scenes/ps2.json", "w"), ensure_ascii=False, indent=1)


# ---------------------------------------------------------------- SFX: tiap gerakan visual punya suara
def smp(t, st, d, g, fi=.4, fo=.8):
    return [t, "smp", g, [CROWD, st, d, fi, fo]]


ev = []
for sid, t in TL[1:]:                                       # transisi antar adegan
    ev.append([t - .22, "whoosh_low", .26, .55])
# riuh tribun tipis di bagian bobotoh (20-49 s) + Asia
for t in (20.4, 40.4):
    ev.append(smp(t, 100 + (t > 30) * 2, 20.5, .22, 1.0, 1.5))
ev += [
    # Q01 YouTube: notifikasi + subscriber beterbangan
    [0.05, "boom", .35], [0.25, "notif", .45], [.4, "pop", .35], [1.0, "shutter", .3], [1.5, "flutter", .3, 1.3],
    [1.62, "impact", .45], [1.62, "sparkle", .3],
    # Q02 iklan kecil
    [3.15, "pop", .35], [4.0, "paper", .35, .45], [5.5, "coin", .35], [5.62, "coin", .3], [5.74, "coin", .28],
    [5.9, "swoosh", .3], [6.06, "ding", .3],
    # Q03 pintu brankas + tanya
    [7.45, "clank", .45], [8.5, "sparkle", .3], [8.54, "coins_pour", .25, .9], [8.6, "pop", .4], [9.03, "riser", .3, .5],
    # Q04 lima pintu, pintu liga terbuka
    [9.62, "clank", .3], [9.8, "clank", .25], [10.0, "clank", .25], [10.3, "door", .55], [10.32, "boom", .5],
    [10.4, "riser", .3, .6], [11.03, "impact", .35],
    # Q05 subsidi: koin klub, pilar naik
    [11.8, "pop", .35], [12.73, "coins_pour", .3, 1.0], [13.8, "riser", .35, .7], [14.4, "impact", .5],
    [14.4, "cash", .35], [15.3, "paper", .35, .45], [16.6, "riser", .25, .5], [17.0, "pop", .35],
    # Q06 TV & podium
    [18.55, "news", .4], [18.62, "pop", .3], [19.3, "clank", .3], [19.4, "pop", .3], [19.66, "ding", .3],
    [19.76, "ding", .25], [19.86, "ding", .22],
    # Q07 stadion: koin hilang, logo naik, bobotoh bergemuruh
    smp(20.45, 46.5, 4.6, .8, .3, 1.2), [20.6, "coins_pour", .3, .8], [21.9, "whoosh_rev", .3, .5],
    [22.2, "riser", .4, .5], [22.3, "boom", .55], smp(22.6, 58.5, 2.4, .9, .1, 1.0), [24.28, "drum", .5, 1.0],
    # Q08 4 kompetisi + 24 laga
    [26.44, "impact", .35], [26.53, "impact", .3], [26.62, "impact", .3], [26.71, "impact", .35],
    [27.6, "ticks", .28, 1.0], [28.45, "pop", .35],
    # Q09 tiket: gerbang berputar, tiket mengalir, koin menumpuk
    [29.4, "shutter", .3], [29.5, "clank", .3], [30.4, "scan", .3, 2.8], [30.6, "tick", .2], [31.1, "tick", .2],
    [31.6, "tick", .2], [32.1, "tick", .2], [32.6, "coins_pour", .3, 2.4], [33.7, "impact", .45],
    [33.7, "cash", .4], smp(32.4, 186.5, 3.4, .45, .5, 1.0),
    # Q10 jersey: PO, harga, hujan koin
    [36.3, "whoosh", .35, .5], [36.5, "shutter", .3], [37.51, "pop", .4], [37.9, "ding", .35],
    [38.6, "paper", .3, .45], [38.77, "impact", .45], [38.8, "coins_pour", .4, 1.6], [38.9, "cash", .35],
    # Q11 toko & membership
    [41.75, "pop", .3], [41.95, "pop", .26], [42.15, "pop", .26], [42.35, "ding", .25], [42.5, "pop", .24],
    [42.7, "pop", .24], [42.9, "shutter", .3], [43.66, "notif", .45], [44.2, "sparkle", .3],
    # Q12 fans -> pelanggan
    [45.6, "shutter", .3], [46.6, "pop", .35], [47.55, "whoosh_rev", .3, .4], [47.85, "impact", .5],
    [47.85, "sparkle", .35], [48.1, "coins_pour", .3, 1.0], smp(45.6, 129.0, 3.0, .45, .4, 1.0),
    # Q13 Asia: globe, pin, logo ACL, bonus
    [49.1, "whoosh", .35, .7], [49.63, "ping", .4], [50.34, "ping", .4], [50.6, "ping", .4], [51.56, "impact", .4],
    [52.2, "paper", .3, .45], [53.09, "pop", .4], [53.79, "coins_pour", .35, 1.0], [53.79, "cash", .35],
    # Q14 2 kemenangan: peluit + sorak
    [55.43, "whistle", .4, .6], [55.43, "impact", .35], [55.83, "impact", .35], smp(55.5, 46.5, 2.8, .7, .2, 1.0),
    [56.6, "coins_pour", .35, 1.4], [57.22, "cash", .45], [57.22, "ding", .3],
    # Q15 insiden: sirene, koin bocor
    [58.95, "clank", .3], [59.4, "bass_drop", .5], [59.54, "siren", .4, 2.0], [60.6, "coins_pour", .35, 1.6],
    [61.18, "glitch", .35, .35],
    # Q16 denda + stadion kosong + koin menguap
    [62.0, "gavel", .55], [62.06, "stamp", .5], [62.9, "paper", .3, .45], [64.49, "stamp", .55], [64.5, "glitch", .3, .3],
    [66.6, "whoosh_rev", .4, 1.2], [67.61, "impact", .45], [68.9, "whoosh", .35, .6],
    # Q17 corong: follower jatuh, 5 pipa
    [69.8, "glass", .35], [70.4, "flutter", .35, 2.4], [72.38, "whoosh", .3, .5], [73.0, "clank", .3],
    [73.88, "riser", .3, .5], [74.41, "cash", .35], [75.03, "cash", .35], [75.69, "cash", .35], [76.37, "cash", .35],
    [77.11, "cash", .4], [74.45, "coins_pour", .25, 3.2],
    # Q18 brankas terbuka, emas, Rp1 T
    [77.9, "clank", .35], [79.11, "door", .55], [80.2, "coins_pour", .35, 1.3], [81.3, "riser", .4, .3],
    [81.48, "boom", .6], [81.48, "impact", .5], [81.6, "sparkle", .35],
    # Q19 CTA: sorak + chant + notif komentar
    smp(84.9, 76.0, 8.4, .8, .6, 1.4), [84.9, "boom", .35], [85.1, "sparkle", .3], [85.73, "pop", .35],
    [86.6, "chant", .3, 2.0], [88.6, "notif", .45], [89.6, "notif", .45], [90.69, "ding", .3],
]
for h in HERO:
    if h.get("count"):
        c = h["count"]
        ev.append([c["t0"], "ticks", .26, c["t1"] - c["t0"]])
        ev.append([c["t1"], "ding", .35])
ev.sort(key=lambda e: e[0])
json.dump(ev, open("render/scenes/ps2_sfx.json", "w"), indent=0)
print(len(BISUBS), "subtitle,", len(ev), "SFX")
