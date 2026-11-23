"""Grafis tekstur video "KPR & BI Rate 6%": notifikasi tagihan, riwayat cicilan di aplikasi bank (simulasi),
grafik tangga BI Rate 2026, grafik rekor rupiah, kartu hitungan per hari, plus tangkapan berita (WEBDIR).

  python3 render/kpr_assets.py OUTDIR --web WEBDIR

Simulasi: KPR Rp500 jt, tenor 20 th, bunga 9% saat BI Rate 4,75% -> bunga ikut naik 1:1 dengan BI Rate.
"""
import argparse
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
F8 = os.path.join(HERE, "fonts", "PlusJakartaSans-800.ttf")
F7 = os.path.join(HERE, "fonts", "PlusJakartaSans-700.woff")


def f(size, bold=True):
    return ImageFont.truetype(F8 if bold else F7, size)


def pmt(P, r, n=240):
    i = r / 12
    return P * i / (1 - (1 + i) ** -n)


def rp(v):
    return "Rp" + f"{int(round(v)):,}".replace(",", ".")


# BI Rate akhir bulan 2026 (RDG BI; diolah dari pemberitaan)
BI = [("Jan", 4.75), ("Feb", 4.75), ("Mar", 4.75), ("Apr", 4.75), ("Mei", 5.25), ("Jun", 5.75), ("Jul", 5.75),
      ("Agu", 5.75), ("Sep", 5.75), ("Okt", 5.75), ("Nov", 6.00)]
# rekor penutupan rupiah per US$ 2026 (Bisnis, Kontan)
IDR = [("17 Apr", 17185), ("4 Jun", 18049), ("16 Nov", 18268)]
NAVY, BLUE, RED, GREEN, WHITE, GREY = (10, 18, 40), (37, 99, 235), (225, 29, 72), (22, 163, 74), (255, 255, 255), (100, 116, 139)


def notif(out):
    im = Image.new("RGB", (1000, 360), (245, 247, 251))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, 999, 359), 48, fill=(255, 255, 255), outline=(220, 226, 235), width=4)
    d.rounded_rectangle((40, 50, 140, 150), 26, fill=BLUE)
    d.text((90, 100), "KPR", font=f(34), fill=WHITE, anchor="mm")
    d.text((170, 58), "m-Banking • baru saja", font=f(30, False), fill=GREY)
    d.text((170, 102), "Tagihan cicilan KPR bulan ini", font=f(42), fill=NAVY)
    d.text((40, 200), rp(pmt(500e6, .1025)), font=f(80), fill=NAVY)
    d.rounded_rectangle((40, 290, 520, 340), 25, fill=(254, 226, 226))
    d.text((60, 315), "naik +Rp83.109 dari bulan lalu", font=f(30), fill=RED, anchor="lm")
    im.save(os.path.join(out, "notif.png"))


def riwayat(out):
    W_, H_ = 900, 1900
    im = Image.new("RGB", (W_, H_), (244, 246, 250))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W_, 230), fill=BLUE)
    d.text((50, 60), "Riwayat Cicilan KPR", font=f(56), fill=WHITE)
    d.text((50, 145), "Plafon Rp500 jt • tenor 20 th • 2026", font=f(34, False), fill=(219, 234, 254))
    y = 270
    prev = None
    for m, bi in BI:
        r = .09 + (bi - 4.75) / 100
        v = pmt(500e6, r)
        up = prev is not None and v - prev > 1
        d.rounded_rectangle((36, y, W_ - 36, y + 135), 26, fill=WHITE)
        d.text((80, y + 30), f"{m} 2026", font=f(40), fill=NAVY)
        d.text((80, y + 82), f"bunga {r * 100:.2f}%".replace(".", ","), font=f(30, False), fill=GREY)
        d.text((W_ - 80, y + 40), rp(v), font=f(44), fill=RED if up else NAVY, anchor="ra")
        if up:
            d.text((W_ - 80, y + 92), f"▲ +{rp(v - prev)[2:]}", font=f(30), fill=RED, anchor="ra")
        prev = v
        y += 150
    im.save(os.path.join(out, "riwayat.png"))


def chart_bi(out):
    W_, H_ = 1600, 1000
    im = Image.new("RGB", (W_, H_), WHITE)
    d = ImageDraw.Draw(im)
    d.text((70, 50), "BI Rate 2026", font=f(70), fill=NAVY)
    d.text((70, 140), "suku bunga acuan Bank Indonesia (%)", font=f(36, False), fill=GREY)
    x0, x1, y0, y1 = 120, 1520, 860, 260
    lo, hi = 4.5, 6.25
    for v in (4.75, 5.25, 5.75, 6.0):
        yy = y0 - (v - lo) / (hi - lo) * (y0 - y1)
        d.line((x0, yy, x1, yy), fill=(226, 232, 240), width=3)
        d.text((x0 - 20, yy), f"{v:.2f}".replace(".", ","), font=f(28, False), fill=GREY, anchor="rm")
    n = len(BI)
    pts = []
    for k, (m, v) in enumerate(BI):
        xa = x0 + k * (x1 - x0) / n
        xb = x0 + (k + 1) * (x1 - x0) / n
        yy = y0 - (v - lo) / (hi - lo) * (y0 - y1)
        pts += [(xa, yy), (xb, yy)]
        d.text(((xa + xb) / 2, y0 + 40), m, font=f(28, False), fill=GREY, anchor="mm")
    d.line(pts, fill=RED, width=12, joint="curve")
    d.ellipse((pts[-1][0] - 18, pts[-1][1] - 18, pts[-1][0] + 18, pts[-1][1] + 18), fill=RED)
    d.text((pts[-1][0] - 30, pts[-1][1] - 70), "6,00%", font=f(54), fill=RED, anchor="rm")
    d.text((70, H_ - 60), "Sumber: RDG Bank Indonesia, diolah dari Bisnis.com & Kontan", font=f(26, False), fill=GREY)
    im.save(os.path.join(out, "chart_bi.png"))


def chart_idr(out):
    W_, H_ = 1600, 1000
    im = Image.new("RGB", (W_, H_), (12, 14, 22))
    d = ImageDraw.Draw(im)
    d.text((70, 50), "USD/IDR: rekor terlemah 2026", font=f(66), fill=WHITE)
    d.text((70, 140), "penutupan, rupiah per dolar AS", font=f(36, False), fill=(148, 163, 184))
    x0, x1, y0, y1 = 150, 1480, 860, 300
    lo, hi = 17000, 18400
    for v in (17000, 17500, 18000):
        yy = y0 - (v - lo) / (hi - lo) * (y0 - y1)
        d.line((x0, yy, x1, yy), fill=(40, 46, 60), width=3)
        d.text((x0 - 20, yy), f"{v:,}".replace(",", "."), font=f(28, False), fill=(148, 163, 184), anchor="rm")
    pts = []
    for k, (lab, v) in enumerate(IDR):
        xx = x0 + 80 + k * (x1 - x0 - 160) / (len(IDR) - 1)
        yy = y0 - (v - lo) / (hi - lo) * (y0 - y1)
        pts.append((xx, yy))
        d.text((xx, y0 + 40), lab, font=f(30, False), fill=(148, 163, 184), anchor="mm")
    d.line(pts, fill=RED, width=12, joint="curve")
    for (xx, yy), (lab, v) in zip(pts, IDR):
        d.ellipse((xx - 16, yy - 16, xx + 16, yy + 16), fill=RED)
        d.text((xx, yy - 50), f"{v:,}".replace(",", "."), font=f(44), fill=WHITE, anchor="mm")
    d.text((70, H_ - 60), "Sumber: Bisnis.com, Kontan • rupiah melemah = angka naik", font=f(26, False),
           fill=(148, 163, 184))
    im.save(os.path.join(out, "chart_idr.png"))


def per_hari(out):
    im = Image.new("RGB", (1200, 700), WHITE)
    d = ImageDraw.Draw(im)
    d.text((600, 120), "Rp83.000 ÷ 30 hari", font=f(84), fill=NAVY, anchor="mm")
    d.line((200, 230, 1000, 230), fill=(226, 232, 240), width=6)
    d.text((600, 380), "= Rp2.770", font=f(150), fill=GREEN, anchor="mm")
    d.text((600, 540), "per hari", font=f(60, False), fill=GREY, anchor="mm")
    im.save(os.path.join(out, "per_hari.png"))


ARTS = {0: "art_bi6", 1: "art_kata", 2: "art_rupiah", 3: "art_rupiah2", 4: "art_akurat", 5: "art_ekonom",
        6: "art_cnbc", 7: "art_ibp", 8: "art_floating", 9: "art_simulasi", 10: "art_bertahap", 11: "art_afu"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--web", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    notif(a.out)
    riwayat(a.out)
    chart_bi(a.out)
    chart_idr(a.out)
    per_hari(a.out)
    for i, n in ARTS.items():
        p = os.path.join(a.web, f"t{i}.png")
        if os.path.exists(p) and os.path.getsize(p) > 60000:
            im = Image.open(p).convert("RGB")
            im.crop((0, 0, im.width, min(im.height, 2600))).save(os.path.join(a.out, n + ".jpg"), quality=90)
    print("ok", sorted(os.listdir(a.out)))


if __name__ == "__main__":
    main()
