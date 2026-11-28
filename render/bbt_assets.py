"""Tekstur video "Sponsor terbesar Persib itu kamu": 16 logo resmi sponsor Persib 2026/27 (dari persib.co.id),
logo Persib, tangkapan berita (NexAI/MGLV, Glenn Sugita, Deputy CEO Adhitia, 16 sponsor, jersey).
Aset pihak ketiga TIDAK disimpan di repo — hanya skrip ini.

  python3 render/bbt_assets.py OUTDIR --dl DLDIR --web WEBDIR --web2 WEB2DIR --psb PSB_TEXDIR
"""
import argparse
import os
import shutil

from PIL import Image, ImageFilter

ARTS = {"web": {0: "art_bos", 1: "art_nxsp", 2: "art_kontan", 3: "art_rm16", 5: "art_glenn", 6: "art_bola",
                8: "art_jersey"},
        "web2": {0: "art_kujang", 1: "art_acl", 2: "art_acl2", 3: "art_bjb"}}


def logo(src, out):
    im = Image.open(src).convert("RGBA")
    bb = im.getbbox()
    im = im.crop(bb)
    im = im.resize((im.width * 5, im.height * 5), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 90, 2))
    im.save(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--dl", required=True)
    ap.add_argument("--web", required=True)
    ap.add_argument("--web2", required=True)
    ap.add_argument("--psb", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for i in range(1, 17):
        src = os.path.join(a.dl, f"sp{i:02d}.png")
        if i == 13:                                    # Se'Indonesia: versi berwarna di latar transparan
            src = os.path.join(a.dl, "sp13.png")
        logo(src, os.path.join(a.out, f"sp{i:02d}.png"))
    shutil.copy(os.path.join(a.psb, "lg_persib.png"), os.path.join(a.out, "lg_persib.png"))
    for ph in ("ph_koreo.jpg", "ph_jubelo1.jpg", "ph_pawai.jpg", "ph_store.jpg", "ph_jersey.jpg", "ph_gbla.jpg"):
        p = os.path.join(a.psb, ph)
        if os.path.exists(p):
            shutil.copy(p, os.path.join(a.out, ph))
    for key, d in (("web", a.web), ("web2", a.web2)):
        for i, n in ARTS[key].items():
            p = os.path.join(d, f"t{i}.png")
            if not os.path.exists(p):
                continue
            im = Image.open(p).convert("RGB")
            if n == "art_kontan":                      # buang blok gelap iklan di atas
                im = im.crop((0, 300 if im.height > 2000 else 0, im.width, im.height))
            im.crop((0, 0, im.width, min(im.height, 2600))).save(os.path.join(a.out, n + ".jpg"), quality=90)
    print("ok", sorted(os.listdir(a.out)))


if __name__ == "__main__":
    main()
