#!/usr/bin/env python3
"""Setzt das runde Seitenlogo oben links in ein Foto (Seitenlogo Saudi).

Aufruf:
  python3 add_logo.py --in foto.jpg --out images/<name>.jpg
Voraussetzung: pip install pillow
Nur fuer Fotos aus externen Quellen verwenden, nicht fuer eigene Bilder
(make_post_image.py) und nicht fuer Videos.
"""
import argparse, os
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.join(HERE, "images", "logo-saudi.png")   # neues Logo (Nutzerwunsch 30.10.2026), transparent


def emblem(logo_path=LOGO):
    return Image.open(logo_path).convert("RGBA")


def apply(photo_path, out_path, frac=0.14, margin=0.025):
    im = ImageOps.exif_transpose(Image.open(photo_path)).convert("RGB")
    w, _ = im.size
    d = max(1, round(w * frac))
    em = emblem().resize((d, d), Image.LANCZOS)
    m = round(w * margin)
    im = im.convert("RGBA")
    im.alpha_composite(em, (m, m))
    im.convert("RGB").save(out_path, quality=92)
    return im.size


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    print(apply(a.inp, a.out))
