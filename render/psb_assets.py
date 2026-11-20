"""Siapkan folder tekstur video "Persib Bandung" (dokumenter) dari aset yang sudah diunduh.
Aset (logo resmi, foto resmi persib.co.id, logo kompetisi, tangkapan artikel, peta Google Maps kiriman user) TIDAK
disimpan di repo — hanya skrip ini.

  python3 render/psb_assets.py OUTDIR --dl DLDIR --web WEBDIR --web2 WEB2DIR --map MAP.png

DLDIR  : persib_logo.png, persib_app.png, jdt.png, gbla_wiki.jpg, logos/*, players/*, photos/a00..a19.jpg
WEBDIR : t0..t14.png (tangkapan artikel, urutan tetap — lihat ARTS)
WEB2DIR: t1..t3.png (artikel tambahan)
"""
import argparse
import glob
import os
import re

from PIL import Image, ImageFilter

ARTS = {0: "art_kompas", 1: "art_wiki", 2: "art_goodstats", 3: "art_ileague", 4: "art_tiket", 5: "art_zw",
        8: "art_ipo", 9: "art_cnn4", 10: "art_radar29", 11: "art_afc", 12: "art_espn", 13: "art_detik3",
        14: "art_katadata"}
ARTS2 = {1: "art_detikipo", 2: "art_jersey", 3: "art_graha"}
PHOTOS = {"a00": "ph_klok", "a01": "ph_pawai", "a02": "ph_bus", "a03": "ph_koreo", "a04": "ph_trophies",
          "a05": "ph_graha", "a07": "ph_store", "a08": "ph_jersey", "a09": "ph_asia", "a10": "ph_ticket",
          "a11": "ph_jubelo1", "a12": "ph_jubelo2", "a13": "ph_gbla_full", "a15": "ph_tolic", "a17": "ph_xi",
          "a18": "ph_nobar"}


def save(im, out, name, max_side=1800, jpg=True):
    im = im.copy()
    im.thumbnail((max_side, max_side), Image.LANCZOS)
    if jpg:
        im.convert("RGB").save(os.path.join(out, name + ".jpg"), quality=92)
    else:
        im.save(os.path.join(out, name + ".png"))


def up(im, k=2):
    im = im.resize((im.width * k, im.height * k), Image.LANCZOS)
    return im.filter(ImageFilter.UnsharpMask(2, 80, 2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--dl", required=True)
    ap.add_argument("--web", required=True)
    ap.add_argument("--web2", required=True)
    ap.add_argument("--map", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    L = os.path.join(a.dl, "logos")
    # logo
    save(up(Image.open(os.path.join(a.dl, "persib_logo.png")).convert("RGBA")), a.out, "lg_persib", 1200, False)
    save(Image.open(os.path.join(L, "bri_sl.png")).convert("RGBA"), a.out, "lg_bri", 1000, False)
    save(Image.open(os.path.join(L, "comp_102.png")).convert("RGBA"), a.out, "lg_ileague_cup", 1000, False)
    save(Image.open(os.path.join(L, "shopee_cup.png")).convert("RGBA"), a.out, "lg_shopee", 1000, False)
    save(Image.open(os.path.join(L, "acl2.png")).convert("RGBA"), a.out, "lg_acl2", 1000, False)
    save(up(Image.open(os.path.join(a.dl, "jdt.png")).convert("RGBA")), a.out, "lg_jdt", 1000, False)
    save(Image.open(os.path.join(a.dl, "persib_app.png")).convert("RGB"), a.out, "app_persib", 1600)
    # pemain (foto studio resmi)
    names = []
    for f in sorted(glob.glob(os.path.join(a.dl, "players", "*.[jp][pn]g"))):
        n = "pl_" + re.sub(r"[^a-z0-9]+", "_", os.path.splitext(os.path.basename(f))[0])
        im = Image.open(f).convert("RGB")
        if im.height < 600:
            im = up(im)
        save(im, a.out, n, 1100)
        names.append(n)
    print(len(names), "pemain")
    # foto dokumentasi resmi
    for k, n in PHOTOS.items():
        save(Image.open(os.path.join(a.dl, "photos", k + ".jpg")), a.out, n)
    save(Image.open(os.path.join(a.dl, "gbla_wiki.jpg")), a.out, "ph_gbla")
    # artikel (430x2200 @2x -> 860x4400; simpan 2600 px teratas)
    for i, n in ARTS.items():
        im = Image.open(os.path.join(a.web, f"t{i}.png")).convert("RGB")
        im.crop((0, 0, im.width, min(im.height, 2600))).save(os.path.join(a.out, n + ".jpg"), quality=90)
    for i, n in ARTS2.items():
        im = Image.open(os.path.join(a.web2, f"t{i}.png")).convert("RGB")
        im.crop((0, 0, im.width, min(im.height, 2600))).save(os.path.join(a.out, n + ".jpg"), quality=90)
    # peta Google Maps (kiriman user): bagian peta + kartu info GBLA
    m = Image.open(a.map).convert("RGB")
    sx, sy = m.width / 2000, m.height / 1500
    m.crop((int(785 * sx), int(60 * sy), m.width, m.height)).save(os.path.join(a.out, "map_area.jpg"), quality=93)
    m.crop((int(30 * sx), int(60 * sy), int(785 * sx), int(1500 * sy))).save(os.path.join(a.out, "map_card.jpg"),
                                                                            quality=93)
    print("ok ->", a.out)


if __name__ == "__main__":
    main()
