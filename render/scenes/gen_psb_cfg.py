"""buat render/scenes/psb.json (overlay dokumenter + subtitle 2 bahasa) + render/scenes/psb_sfx.json —
Persib Bandung: juara 3x beruntun, rahasianya di luar lapangan.
Subtitle: EN (atas, kata kunci kuning) + terjemahan ID (bawah), dipetakan ke timestamp kata VO.

  python3 render/scenes/gen_psb_cfg.py WORDS.json CROWD.wav
"""
import json
import re
import sys

WORDS = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "render/scenes/psb_words.json"))
CROWD = sys.argv[2] if len(sys.argv) > 2 else "crowd.wav"

src = open("render/scenes_psb.py").read()
TL = [(a, float(b)) for a, b in re.findall(r'\("(P\d\d)", ([\d.]+)\)', src)]
END = float(re.search(r"END_T = ([\d.]+)", src).group(1))
T0 = dict(TL)
STADIUM = set(re.search(r"STADIUM = \{([^}]*)\}", src).group(1).replace('"', "").replace(" ", "").split(","))

# (jumlah token VO, EN dengan **kata kunci**, terjemahan ID)
CUES = [
    (6, "In Indonesia, there's a **football club**", "Di Indonesia, ada klub sepak bola"),
    (10, "that just won the league **three times in a row**,", "yang baru juara liga tiga kali beruntun,"),
    (5, "and its squad isn't even", "padahal skuadnya bahkan bukan"),
    (6, "the **most expensive** in Southeast Asia.", "yang termahal di Asia Tenggara."),
    (4, "It's called **Persib Bandung**,", "Namanya Persib Bandung,"),
    (7, "the **first club** in Indonesia's professional era", "klub pertama di era profesional Indonesia"),
    (6, "to win **three straight** league titles.", "yang juara liga tiga musim beruntun."),
    (8, "Its squad is worth around **9 million euros**.", "Nilai skuadnya sekitar 9 juta euro."),
    (5, "That's only about **half** of", "Cuma sekitar separuh dari"),
    (5, "Southeast Asia's **most valuable** club,", "klub termahal di Asia Tenggara,"),
    (3, "**Johor Darul Ta'zim**.", "Johor Darul Ta'zim."),
    (4, "So, what's the **secret**?", "Terus, rahasianya di mana?"),
    (6, "The answer is, **off the pitch**.", "Jawabannya: di luar lapangan."),
    (6, "Persib is run like a **company**.", "Persib dikelola seperti perusahaan."),
    (4, "**Professional**, **transparent** business practices,", "Praktik bisnisnya profesional dan transparan,"),
    (6, "something still **rare** in Indonesian football.", "hal yang masih langka di sepak bola Indonesia."),
    (8, "Match tickets are sold through an **official app**.", "Tiket dijual lewat aplikasi resmi."),
    (6, "Stadium **waste** is handled with a", "Sampah stadion dikelola dengan sistem"),
    (5, "**zero-waste-to-landfill** system.", "zero waste to landfill (tanpa dibuang ke TPA)."),
    (7, "Fans are engaged **365 days** a year,", "Suporter dirawat 365 hari setahun,"),
    (5, "not just for **90 minutes**.", "bukan cuma 90 menit."),
    (7, "And their **jerseys** are bought by fans", "Jersey-nya dibeli fans"),
    (6, "as far away as **Japan**, **Taiwan**,", "sampai Jepang, Taiwan,"),
    (5, "**Hong Kong**, and even **Brazil**.", "Hong Kong, bahkan Brasil."),
    (5, "They also have a **dream**", "Mereka juga punya mimpi"),
    (5, "few Indonesian clubs ever have,", "yang jarang dimiliki klub Indonesia:"),
    (6, "going public on the **stock exchange**.", "masuk bursa saham."),
    (6, "Their **IPO** plan has been **delayed**.", "Rencana IPO-nya sempat tertunda."),
    (6, "But once their assets are **consolidated**,", "Tapi kalau asetnya sudah dirapikan,"),
    (5, "the club's **valuation** is estimated", "valuasi klubnya ditaksir"),
    (5, "to reach **1 trillion rupiah**,", "bisa tembus Rp1 triliun,"),
    (5, "around **60 million US dollars**.", "sekitar 60 juta dolar AS."),
    (5, "Now comes the **hardest test**.", "Sekarang ujiannya lebih berat."),
    (4, "**Four competitions** at once,", "Empat kompetisi sekaligus,"),
    (7, "up to **64 matches** in one season,", "potensi 64 laga dalam semusim,"),
    (7, "with a squad of just **29 players**.", "dengan skuad cuma 29 pemain."),
    (9, "Does **your country** have a club run this well?", "Di negaramu, ada klub yang dikelola serapi ini?"),
    (7, "Drop the **club's name** in the comments.", "Tulis nama klubnya di komentar."),
    (7, "**Tag** a football fan from another country,", "Tag temen pecinta bola dari negara lain,"),
    (5, "and **follow** for Part 2:", "dan follow buat part 2:"),
    (4, "Inside **Persib's Money Machine**.", "mesin uang Persib."),
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


def lb(anchor, title, t, color="cyan", sub="", lift=80, until=None):
    d = dict(anchor=anchor, title=title, sub=sub, color=color, t=t, lift=lift)
    if until is not None:
        d["until"] = until
    return d


def hero(t0, t1, text, sub="", count=None, style="cyan", size=110, y=1460, font="slab"):
    d = dict(t0=t0, t1=t1, text=text, sub=sub, style=style, size=size, y=y, font=font)
    if count:
        d["count"] = count
    return d


S = [
    ("P01", "Juara **3x beruntun**", [lb("TR", "3 TROFI LIGA", 3.3, "gold", "3 musim beruntun", 60)]),
    ("P02", "Padahal **bukan termahal**", [lb("PH", "BOJAN HODAK", 4.3, "cyan", "pelatih 3 gelar • foto: persib.co.id", 50)]),
    ("P03", "Namanya **Persib Bandung**", [lb("PK", "KOMPAS (EN)", 9.0, "cyan", "media internasional", 50, 12.0),
                                          lb("PW", "WIKIPEDIA (EN)", 9.4, "purple", "", 50, 12.0)]),
    ("P04", "Nilai skuad **±€9 juta**", [lb("PP", "PERSIB", 14.3, "cyan", "€8,93 jt", 50),
                                        lb("PJ", "JOHOR DARUL TA'ZIM", 19.0, "red", "€15,93 jt • termahal ASEAN", 50),
                                        lb("GS", "GOODSTATS", 13.7, "purple", "data Transfermarkt", 50, 16.0)]),
    ("P05", "Rahasianya **di luar lapangan**", []),
    ("P06", "Dikelola **seperti perusahaan**", [lb("GRAHA", "GRAHA PERSIB", 25.1, "cyan", "Jl. Sulanjana 17, Bandung", 50, 28.4),
                                                lb("AI", "I.LEAGUE", 29.0, "purple", "operator liga", 50)]),
    ("P07", "Tiket lewat **aplikasi resmi**", [lb("APP", "PERSIB APP", 31.7, "cyan", "kanal tiket resmi", 50)]),
    ("P08", "Sampah stadion: **zero waste**", [lb("BIN", "DIPILAH 3 JENIS", 33.9, "green", "organik • anorganik • residu", 60, 34.8),
                                               lb("AZ", "65,4 TON", 35.4, "green", "sampah dikelola 2025/26", 50)]),
    ("P09", "Bobotoh dirawat **365 hari**", []),
    ("P10", "Jersey sampai **luar negeri**", [lb("JS", "JERSEY PERSIB", 41.4, "cyan", "", 50, 42.9)]),
    ("P11", "Mimpi **masuk bursa**", [lb("AK", "KATADATA", 48.0, "purple", "", 50, 51.0),
                                     lb("AD", "DETIKFINANCE", 51.9, "purple", "", 50)]),
    ("P12", "Valuasi **Rp1 triliun**?", [lb("PG", "GRAHA PERSIB", 53.9, "cyan", "", 50),
                                         lb("PB", "STADION GBLA", 54.4, "red", "Gedebage", 50)]),
    ("P13", "**4 kompetisi** sekaligus", [lb("AF", "AFC.COM", 61.2, "purple", "media luar negeri", 50, 62.0),
                                          lb("ES", "ESPN", 61.6, "purple", "media luar negeri", 50, 62.0)]),
    ("P14", "**64 laga**, **29 pemain**", [lb("RB", "RADAR BANDUNG", 66.7, "purple", "", 50)]),
    ("P15", "Di negaramu **ada nggak**?", []),
    ("P16", "Part 2: **mesin uang Persib**", []),
]

HERO = [
    hero(2.64, 3.85, "**3x** JUARA BERUNTUN", "Liga Indonesia 2023/24 • 2024/25 • 2025/26", style="gold", size=104),
    hero(4.92, 6.95, "bukan skuad **termahal**", "di Asia Tenggara", style="red", size=96),
    hero(7.54, 9.0, "**PERSIB BANDUNG**", "", style="cyan", size=118),
    hero(10.38, 12.8, "klub **pertama**", "juara 3 musim beruntun di era profesional", style="gold", size=104),
    hero(14.02, 16.0, "**€8,93** juta", "nilai pasar skuad (Transfermarkt via GoodStats)", style="cyan", size=118),
    hero(16.16, 20.1, "± **separuh** JDT", "JDT €15,93 juta — termahal di Asia Tenggara", style="red", size=104),
    hero(23.26, 24.6, "**DI LUAR** LAPANGAN", "", style="cyan", size=108),
    hero(25.0, 26.4, "seperti **perusahaan**", "PT Persib Bandung Bermartabat", style="cyan", size=100),
    hero(32.0, 33.45, "tiket via **aplikasi**", "PERSIB App", style="cyan", size=100),
    hero(34.88, 36.55, "**65,4 ton** sampah", "terkelola sepanjang 2025/26 (data klub)", style="green", size=104),
    hero(37.41, 39.6, "**365** hari", "", style="gold", size=124),
    hero(39.9, 40.75, "bukan cuma **90'**", "", style="cyan", size=110),
    hero(43.08, 46.45, "Jepang • Taiwan • HK • **Brasil**", "pembeli jersey luar negeri (menurut manajemen)", style="gold",
         size=80),
    hero(49.24, 51.3, "masuk **bursa**", "rencana IPO", style="gold", size=110),
    hero(52.63, 53.28, "IPO **TERTUNDA**", "", style="red", size=104),
    hero(56.86, 60.4, "**Rp1 triliun**", "≈ US$60 juta • taksiran bila aset dikonsolidasi", style="gold", size=118),
    hero(62.18, 63.95, "**4** KOMPETISI", "Super League • I.League Cup • Shopee Cup • ACL Two", style="cyan", size=110),
    hero(64.21, 66.6, "**64** laga", "potensi semusim", dict(t0=64.21, t1=65.1, frm=0, to=64, fmt="{}"), style="gold",
         size=118),
    hero(66.88, 68.25, "**29** pemain", "skuad 2026/27", dict(t0=66.88, t1=67.5, frm=0, to=29, fmt="{}"), style="red",
         size=118),
    hero(74.81, 78.9, "PART 2", "mesin uang Persib", style="gold", size=118),
]

COMMENTS = [dict(t=71.1, text="Buriram United, Thailand!", y=1395), dict(t=72.4, text="@kawan_bola wajib nonton ini", y=1545)]

PUNCH = [(2.64, .7), (2.94, .5), (3.19, .5), (4.92, .6), (7.54, 1.0), (11.23, .5), (14.02, .8), (16.16, .6),
         (18.75, .8), (21.57, .6), (23.26, .8), (25.31, .6), (26.49, .4), (27.18, .4), (31.9, .5), (34.88, .7),
         (37.41, .8), (39.9, .6), (43.08, .5), (43.76, .5), (44.51, .5), (45.55, .7), (49.53, .8), (52.63, 1.0),
         (54.2, .5), (56.86, 1.0), (62.18, .6), (62.45, .5), (62.72, .5), (62.98, .6), (64.21, .7), (66.88, .8),
         (71.1, .4), (72.4, .4), (74.81, .9)]
FLASH = [(7.54, .2, "w"), (52.63, .18, "r"), (56.86, .2, "w")]
CHROMA = [(52.63, .25), (74.81, .15)]
PALE = [0, 0, "NONE"]

scenes = []
for sid, bub, labels in S:
    t0 = T0[sid]
    for l_ in labels:
        l_["t"] = round(l_["t"] - t0, 3)
        if "until" in l_:
            l_["until"] = round(l_["until"] - t0, 3)
    scenes.append(dict(id=sid, bubble=bub, labels=labels, tilt=0, theme="neon", look="doc"))

cfg = dict(scenes=scenes, hero=HERO, comments=COMMENTS, comment_scene="P15", bisubs=BISUBS, sub_y=1228,
           fx=dict(punch=PUNCH, flash=FLASH, chroma=CHROMA, pale=PALE), keywords=[])
json.dump(cfg, open("render/scenes/psb.json", "w"), ensure_ascii=False, indent=1)


# ---------------------------------------------------------------- SFX: gemuruh bobotoh (rekaman stadion asli
# CC BY 4.0) + efek sintetis per kata VO
def smp(t, st, d, g, fi=.4, fo=.8):
    return [t, "smp", g, [CROWD, st, d, fi, fo]]


ev = []
# latar riuh tribun tipis sepanjang video (dokumenter), lebih keras di adegan stadion
for k, t in enumerate(range(0, int(END) + 1, 20)):
    ev.append(smp(max(0, t - .5), 100 + (k % 2) * 2, 21.0, .28, 1.0, 1.5))
for sid, t in TL[1:]:
    ev.append([t - .22, "whoosh_low", .26, .55])
ev += [
    # P01 hook: gemuruh naik, 3 trofi
    smp(0.0, 46.5, 4.6, .95, .25, 1.2), [0.05, "boom", .45], [2.5, "whoosh", .35, .5],
    [2.64, "impact", .5], [2.94, "impact", .32], [3.19, "impact", .32], [3.4, "goal", .35, 2.4],
    # P02
    smp(3.9, 76.0, 3.4, .35, .5, 1.0), [4.3, "swoosh", .25], [4.92, "stamp", .45],
    # P03 logo: sorak besar
    [7.1, "riser", .45, .45], smp(7.3, 58.5, 4.2, 1.05, .1, 1.5), [7.54, "boom", .6], [7.54, "drum", .5, 2.4],
    [8.6, "paper", .4, .45], [9.0, "paper", .35, .45], [11.23, "sparkle", .4], [11.41, "ding", .25], [11.59, "ding", .25],
    # P04 pilar
    [13.6, "riser", .3, .45], [14.02, "impact", .45], [14.02, "coin", .35], [16.16, "whoosh", .25, .4],
    [18.4, "riser", .3, .4], [18.75, "impact", .5], [18.75, "coins_pour", .3, 1.2],
    # P05 rahasia: peluit wasit, riuh tipis, naik keluar stadion
    smp(20.3, 103.0, 4.4, .55, .6, 1.2), [20.42, "whistle", .5, .7], [21.57, "pop", .4], [23.0, "whoosh", .4, .7],
    [23.26, "impact", .45],
    # P06 perusahaan
    [25.31, "stamp", .35], [26.49, "pop", .3], [27.18, "pop", .3], [28.6, "paper", .35, .45], [28.95, "type", .25, 8],
    # P07 tiket
    [31.45, "notif", .45], [31.9, "swoosh", .3], [32.08, "swoosh", .3], [32.26, "swoosh", .3], [32.3, "scan", .3, 1.0],
    # P08 zero waste
    [34.3, "whoosh_rev", .25, .4], [34.75, "impact", .22], [35.0, "impact", .22], [35.25, "impact", .22],
    [34.88, "sparkle", .35],
    # P09 365 vs 90
    [37.41, "impact", .45], [37.0, "flutter", .3], [39.3, "ticks", .3, 1.5], [39.9, "ding", .35],
    smp(37.5, 186.5, 3.2, .4, .6, 1.0),
    # P10 jersey & globe
    [40.9, "whoosh", .3, .5], [43.08, "ping", .4], [43.76, "ping", .4], [44.51, "ping", .4], [44.7, "whoosh", .3, .8],
    [45.55, "ping", .45], [45.6, "sparkle", .3],
    # P11 IPO
    [47.1, "ticks", .28, 2.8], [49.53, "ding", .45], [49.53, "coin", .3], [52.4, "riser", .25, .3],
    [52.63, "stamp", .65], [52.63, "glitch", .35, .3],
    # P12 peta
    [53.7, "pop", .4], [54.2, "pop", .45], [54.4, "scan", .35, 1.3], [56.6, "riser", .35, .3],
    [56.86, "impact", .6], [56.86, "cash", .45], [57.2, "coins_pour", .3, 1.4],
    # P13 ujian terberat: drum suporter + 4 logo
    [60.55, "drum", .55, 3.2], smp(60.6, 124.5, 3.5, .5, .4, 1.0), [62.18, "impact", .4], [62.45, "impact", .35],
    [62.72, "impact", .35], [62.98, "impact", .4],
    # P14 galeri pemain + hitungan
    [64.1, "flutter", .3, 1.2], [65.3, "flutter", .3, 1.2], [66.6, "flutter", .25, .8], [66.88, "impact", .45],
    # P15 CTA: tribun bergemuruh + yel
    smp(68.2, 76.0, 6.2, .9, .6, 1.2), [68.35, "boom", .35], smp(70.8, 129.0, 2.8, .7, .1, 1.0),
    [71.1, "notif", .4], [72.4, "notif", .4], [72.3, "chant", .35, 2.0],
    # P16 part 2: mesin uang
    [74.4, "clank", .4], [74.81, "boom", .55], [74.81, "impact", .45], [75.2, "chain", .3, .9],
    [75.6, "coins_pour", .45, 2.6], [76.6, "cash", .4], [77.5, "coins_pour", .35, 1.6],
    smp(76.0, 189.0, 3.2, .45, .6, 1.4),
]
for h in HERO:
    if h.get("count"):
        c = h["count"]
        ev.append([c["t0"], "ticks", .26, c["t1"] - c["t0"]])
        ev.append([c["t1"], "ding", .35])
ev.sort(key=lambda e: e[0])
json.dump(ev, open("render/scenes/psb_sfx.json", "w"), indent=0)
print(len(BISUBS), "subtitle,", len(ev), "SFX")
