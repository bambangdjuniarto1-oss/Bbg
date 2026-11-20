"""Siapkan tekstur untuk video "Cara brand vape bertahan di tengah fatwa haram" (FOOM).

Sumber (TIDAK disimpan di repo, hanya diolah ke folder lokal):
  - logo resmi FOOM dari foom.id (diunduh) -> logo_w.png / logo_p.png (alfa) + foom.svg (hasil trace, untuk logo 3D)
  - screenshot grid Instagram @foom_id & postingan kolaborasi (dari user) -> poster campaign p_*.jpg, ig_post.jpg
  - tangkapan layar artikel berita asli (Katadata, CNN Indonesia, MUI, detik) -> art_*.jpg

  python3 render/fom_assets.py OUTDIR --grid IG_GRID.png --post IG_POST.png --web WEBDIR [--dl DLDIR]
"""
import argparse
import os
import subprocess

import numpy as np
from PIL import Image, ImageFilter

LOGO_URL = "https://foom.id/cdn/shop/files/logo_foom_4d788986-b42f-43bf-bcbb-adb13da4bc44.jpg?v=1777363620"
# kotak tile pada screenshot grid IG 1500x2000 (x0, y0, x1, y1)
COLS = [(270, 588), (591, 909), (912, 1230)]
ROWS = [(295, 720), (723, 1147), (1150, 1575), (1578, 2000)]
TILES = {
    "p_girl": (0, 0), "p_blue": (0, 1), "p_office": (0, 2),
    "p_sipaling": (1, 0), "p_pink": (1, 1), "p_yb": (1, 2),
    "p_collab": (2, 0), "p_wm": (2, 1), "p_ybglass": (2, 2),
    "p_bloom": (3, 0), "p_guy": (3, 1), "p_eksplor": (3, 2),
}
# artikel: indeks tangkapan (t{i}.png dari shot2.js) -> nama
ARTICLES = {"art_sewa": 0, "art_cnn": 1, "art_mui": 2, "art_phk": 3, "art_200": 4, "art_detik": 5}


def logo(dl, out):
    src = os.path.join(dl, "logo_og.jpg")
    if not os.path.exists(src):
        subprocess.run(["curl", "-sL", "-m", "60", "-A", "Mozilla/5.0", "-o", src, LOGO_URL], check=True)
    g = np.asarray(Image.open(src).convert("L"), dtype=np.float32)
    a = np.clip((235 - g) * 255 / 200, 0, 255).astype(np.uint8)          # hitam -> alfa
    ys, xs = np.where(a > 20)
    a = a[ys.min() - 8:ys.max() + 9, xs.min() - 8:xs.max() + 9]
    for nm, col in (("logo_w", (255, 255, 255)), ("logo_p", (255, 79, 168))):
        im = Image.new("RGBA", (a.shape[1], a.shape[0]), col + (0,))
        im.putalpha(Image.fromarray(a))
        im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS)
        im.save(os.path.join(out, nm + ".png"))
    # trace -> SVG (tanpa tanda ®: komponen kecil dibuang)
    import potrace
    bw = a > 128
    from scipy import ndimage
    lab, nlab = ndimage.label(bw)
    sizes = ndimage.sum(bw, lab, range(1, nlab + 1))
    keep = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s > .02 * bw.sum()])
    bm = potrace.Bitmap(~keep)
    paths = bm.trace(turdsize=10, alphamax=1.0, opticurve=True)
    H, Wd = keep.shape
    d = []
    for curve in paths:
        s = curve.start_point
        d.append(f"M{s.x:.2f},{s.y:.2f}")
        for seg in curve.segments:
            if seg.is_corner:
                d.append(f"L{seg.c.x:.2f},{seg.c.y:.2f}L{seg.end_point.x:.2f},{seg.end_point.y:.2f}")
            else:
                d.append(f"C{seg.c1.x:.2f},{seg.c1.y:.2f} {seg.c2.x:.2f},{seg.c2.y:.2f} "
                         f"{seg.end_point.x:.2f},{seg.end_point.y:.2f}")
        d.append("Z")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wd}" height="{H}" viewBox="0 0 {Wd} {H}">'
           f'<path fill="#ffffff" fill-rule="evenodd" d="{"".join(d)}"/></svg>')
    open(os.path.join(out, "foom.svg"), "w").write(svg)


def posters(grid, post, out):
    im = Image.open(grid).convert("RGB")
    sx, sy = im.width / 1500, im.height / 2000
    for nm, (r, c) in TILES.items():
        (x0, x1), (y0, y1) = COLS[c], ROWS[r]
        t = im.crop((int((x0 + 2) * sx), int((y0 + 2) * sy), int((x1 - 2) * sx), int((y1 - 2) * sy)))
        t = t.resize((t.width * 3, t.height * 3), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
        t.save(os.path.join(out, nm + ".jpg"), quality=92)
    if post:
        p = Image.open(post).convert("RGB")
        sx, sy = p.width / 2000, p.height / 1500
        p.crop((int(536 * sx), int(165 * sy), int(1466 * sx), int(1345 * sy))).save(
            os.path.join(out, "ig_post.jpg"), quality=92)


def articles(web, out):
    for nm, i in ARTICLES.items():
        src = os.path.join(web, f"t{i}.png")
        if not os.path.exists(src):
            continue
        im = Image.open(src).convert("RGB")
        im.crop((0, 0, im.width, min(im.height, 2600))).save(os.path.join(out, nm + ".jpg"), quality=90)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--grid", required=True)
    ap.add_argument("--post", default=None)
    ap.add_argument("--web", required=True)
    ap.add_argument("--dl", default=None)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    dl = a.dl or os.path.join(a.out, "_dl")
    os.makedirs(dl, exist_ok=True)
    logo(dl, a.out)
    posters(a.grid, a.post, a.out)
    articles(a.web, a.out)
    print("tekstur ->", a.out, sorted(os.listdir(a.out)))


if __name__ == "__main__":
    main()
