"""Siapkan folder tekstur video "Persib Part 2: mesin uang" dari aset yang sudah diunduh (tidak disimpan di repo).

  python3 render/ps2_assets.py OUTDIR --base PSB_TEX --web WEBDIR --dl DLDIR

PSB_TEX : folder tekstur Part 1 (logo, pemain, foto resmi) -> ditautkan (symlink)
WEBDIR  : t0..t14.png + yt.png (tangkapan halaman, urutan tetap — lihat ARTS)
DLDIR   : foto resmi persib.co.id untuk Part 2 (lihat PHOTOS)
"""
import argparse
import os

from PIL import Image

# (berkas, nama, potong-atas px) — potong banner aplikasi/navigasi
ARTS = {"t0": ("art_vidiq", 0), "yt": ("art_yt", 0), "t2": ("art_subsidi", 0), "t3": ("art_jersey10", 0),
        "t4": ("art_store", 0), "t5": ("art_loyalty", 0), "t6": ("art_denda", 0), "t8": ("art_seoul", 0),
        "t9": ("art_klasemen", 0), "t10": ("art_penonton", 0), "t11": ("art_po", 0), "t12": ("art_ptv", 0),
        "t13": ("art_aleagues", 300), "t14": ("art_wiki2", 520)}
PHOTOS = {"seoul_selebrasi": "ph_seoul", "seoul_tolic": "ph_seoul2", "viettel_walsh": "ph_viettel",
          "jersey_asia": "ph_jersey_asia", "jersey_lives": "ph_jersey_lives", "store_cibubur": "ph_store2",
          "membersib": "ph_member", "persibtv_award": "ph_ptv", "pesta_biru": "ph_pesta"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--base", required=True)
    ap.add_argument("--web", required=True)
    ap.add_argument("--dl", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for f in os.listdir(a.base):
        dst = os.path.join(a.out, f)
        if not os.path.exists(dst):
            os.symlink(os.path.join(os.path.abspath(a.base), f), dst)
    for k, (n, top) in ARTS.items():
        im = Image.open(os.path.join(a.web, k + ".png")).convert("RGB")
        im.crop((0, top, im.width, min(im.height, top + 2600))).save(os.path.join(a.out, n + ".jpg"), quality=90)
    for k, n in PHOTOS.items():
        src = [f for f in os.listdir(a.dl) if os.path.splitext(f)[0] == k][0]
        im = Image.open(os.path.join(a.dl, src)).convert("RGB")
        im.thumbnail((2000, 2000), Image.LANCZOS)
        im.save(os.path.join(a.out, n + ".jpg"), quality=92)
    print("ok ->", a.out, len(os.listdir(a.out)), "berkas")


if __name__ == "__main__":
    main()
