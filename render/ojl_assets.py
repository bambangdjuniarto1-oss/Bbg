"""Tekstur video "Ojol & GoTo": logo resmi (goto, gojek, gopay), slide earnings & laporan keuangan GoTo Q3 2026,
tangkapan berita, layar aplikasi driver Android (rincian Rp15.500 -> Rp11.040), layar dompet digital.
Aset pihak ketiga TIDAK disimpan di repo — hanya skrip ini.

  python3 render/ojl_assets.py OUTDIR --dl DLDIR --pdf PDFDIR --web WEBDIR
"""
import argparse
import glob
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
F8 = os.path.join(HERE, "fonts", "PlusJakartaSans-800.ttf")
F7 = os.path.join(HERE, "fonts", "PlusJakartaSans-700.woff")
GREEN, DARK, GREY, RED, WHITE = (0, 170, 19), (16, 24, 32), (100, 110, 120), (225, 29, 72), (255, 255, 255)
ARTS = {0: "art_detik441", 1: "art_kata441", 2: "art_kontan", 3: "art_hitung", 4: "art_jawapos8", 5: "art_insentif",
        7: "art_gopay", 10: "art_ir", 11: "art_warta"}


def f(size, bold=True):
    return ImageFont.truetype(F8 if bold else F7, size)


def rp(v):
    return "Rp" + f"{int(v):,}".replace(",", ".")


def app_driver(out):
    """layar aplikasi driver (Android, generik) — rincian satu order GoRide."""
    W_, H_ = 900, 1900
    im = Image.new("RGB", (W_, H_), (245, 247, 246))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W_, 70), fill=(20, 20, 20))
    d.text((40, 35), "09.41", font=f(30), fill=WHITE, anchor="lm")
    d.text((W_ - 40, 35), "4G  87%", font=f(28, False), fill=WHITE, anchor="rm")
    d.rectangle((0, 70, W_, 300), fill=GREEN)
    d.text((50, 130), "Order selesai", font=f(40, False), fill=(220, 255, 225))
    d.text((50, 190), "Rincian pendapatan", font=f(60), fill=WHITE)
    rows = [("Tarif dibayar penumpang", 15500, DARK), ("Biaya aplikasi", -2500, RED), ("Biaya asuransi", -1000, RED),
            ("Dasar komisi", 12000, DARK), ("Komisi aplikasi 8%", -960, RED)]
    y = 350
    for lab, v, col in rows:
        d.rounded_rectangle((36, y, W_ - 36, y + 150), 28, fill=WHITE)
        d.text((76, y + 75), lab, font=f(40, False), fill=GREY, anchor="lm")
        d.text((W_ - 76, y + 75), ("- " if v < 0 else "") + rp(abs(v)), font=f(50), fill=col, anchor="rm")
        y += 170
    d.rounded_rectangle((36, y + 20, W_ - 36, y + 300), 32, fill=(232, 250, 236), outline=GREEN, width=6)
    d.text((W_ / 2, y + 95), "Kamu terima", font=f(44, False), fill=GREEN, anchor="mm")
    d.text((W_ / 2, y + 205), rp(11040), font=f(110), fill=GREEN, anchor="mm")
    d.text((W_ / 2, H_ - 120), "Simulasi dari contoh SPAI • 8% dari dasar komisi", font=f(30, False), fill=GREY,
           anchor="mm")
    im.save(os.path.join(out, "app_driver.png"))


def app_wallet(out):
    """layar dompet digital generik (tanpa meniru UI resmi): saldo, bayar, pinjaman."""
    W_, H_ = 900, 1900
    im = Image.new("RGB", (W_, H_), (240, 248, 255))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W_, 70), fill=(20, 20, 20))
    d.text((40, 35), "09.41", font=f(30), fill=WHITE, anchor="lm")
    d.rectangle((0, 70, W_, 560), fill=(0, 136, 204))
    d.text((60, 150), "Dompet digital", font=f(46, False), fill=(210, 236, 255))
    d.text((60, 260), "Saldo", font=f(40, False), fill=WHITE)
    d.text((60, 370), "Rp1.250.000", font=f(96), fill=WHITE)
    for i, lab in enumerate(("Bayar", "Transfer", "Pinjaman", "Tagihan")):
        x = 70 + i * 200
        d.rounded_rectangle((x, 620, x + 160, 780), 36, fill=WHITE, outline=(0, 136, 204), width=5)
        d.text((x + 80, 820), lab, font=f(34), fill=DARK, anchor="mm")
    d.rounded_rectangle((40, 920, W_ - 40, 1250), 36, fill=WHITE)
    d.text((80, 990), "Pinjaman tersedia", font=f(44, False), fill=GREY)
    d.text((80, 1080), "Cair dalam menit", font=f(64), fill=DARK)
    d.rounded_rectangle((80, 1170, 420, 1225), 27, fill=(255, 233, 160))
    d.text((250, 1198), "cicil 3x", font=f(32), fill=DARK, anchor="mm")
    d.rounded_rectangle((40, 1300, W_ - 40, 1700), 36, fill=WHITE)
    for k, (lab, v) in enumerate((("Bayar ojek", "-Rp15.500"), ("Pesan makanan", "-Rp48.000"),
                                   ("Cicilan pinjaman", "-Rp210.000"))):
        y = 1360 + k * 110
        d.text((80, y + 40), lab, font=f(40, False), fill=DARK, anchor="lm")
        d.text((W_ - 80, y + 40), v, font=f(40), fill=RED, anchor="rm")
    im.save(os.path.join(out, "app_wallet.png"))


def fare_card(out):
    im = Image.new("RGB", (1400, 760), WHITE)
    d = ImageDraw.Draw(im)
    d.text((700, 110), "Penumpang bayar", font=f(60, False), fill=GREY, anchor="mm")
    d.text((700, 230), rp(15500), font=f(150), fill=DARK, anchor="mm")
    d.line((250, 360, 1150, 360), fill=(226, 232, 240), width=6)
    d.text((700, 450), "Driver bawa pulang", font=f(60, False), fill=GREY, anchor="mm")
    d.text((700, 590), rp(11040), font=f(170), fill=GREEN, anchor="mm")
    im.save(os.path.join(out, "fare_card.png"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--dl", required=True)
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--web", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    Image.open(os.path.join(a.dl, "goto_logo.png")).convert("RGBA").save(os.path.join(a.out, "goto_logo.png"))
    Image.open(os.path.join(a.dl, "gojek.png")).convert("RGBA").save(os.path.join(a.out, "gojek.png"))
    gp = Image.open(os.path.join(a.dl, "gopay.webp")).convert("RGBA")
    gp = gp.resize((gp.width * 6, gp.height * 6), Image.LANCZOS).filter(ImageFilter.UnsharpMask(3, 120, 2))
    gp.save(os.path.join(a.out, "gopay_logo.png"))
    card = Image.new("RGBA", (gp.width + 160, gp.height + 120), (0, 0, 0, 0))     # kartu putih: teks logo gelap
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 60, fill=WHITE)  # tetap terbaca
    card.alpha_composite(gp, (80, 60))                                            # di langit malam
    card.save(os.path.join(a.out, "gopay_card.png"))
    for pat, n in (("pres_4-*.png", "sl_profit"), ("pres_8-*.png", "sl_ods"), ("pres_12-*.png", "sl_fintech"),
                   ("pres_15-*.png", "sl_loan"), ("lk_cover-*.png", "lk_cover"), ("lk_pl-*.png", "lk_pl")):
        src = glob.glob(os.path.join(a.pdf, pat))[0]
        Image.open(src).convert("RGB").save(os.path.join(a.out, n + ".jpg"), quality=93)
    for i, n in ARTS.items():
        p = os.path.join(a.web, f"t{i}.png")
        if os.path.exists(p) and os.path.getsize(p) > 60000:
            im = Image.open(p).convert("RGB")
            im.crop((0, 0, im.width, min(im.height, 2600))).save(os.path.join(a.out, n + ".jpg"), quality=90)
    app_driver(a.out)
    app_wallet(a.out)
    fare_card(a.out)
    print("ok", sorted(os.listdir(a.out)))


if __name__ == "__main__":
    main()
