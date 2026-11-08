#!/usr/bin/env python3
"""Erzeugt Instagram-/Story-Bilder mit arabischem Text.

Aufruf:
  python3 make_post_image.py --title "..." --fmt feed|story --out datei.jpg [--tag "#..."]
Voraussetzung: pip install pillow arabic-reshaper python-bidi
"""
import argparse, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import arabic_reshaper
from bidi.algorithm import get_display

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.join(HERE, "INSTA_Short_Image_dunkel.jpg")
FONT_B = os.path.join(HERE, "fonts", "Tajawal-Bold.ttf")
FONT_R = os.path.join(HERE, "fonts", "Tajawal-Regular.ttf")
THEMES = {
    # name: (bg_oben, bg_unten, text, akzent, seitenname)
    "grau":  ((96, 108, 122), (66, 76, 88), (245, 245, 245), (212, 175, 90), (200, 206, 212)),
    "sand":  ((240, 231, 212), (219, 205, 178), (28, 34, 40), (150, 105, 25), (95, 90, 80)),
    "gruen": ((86, 150, 108), (52, 112, 78), (255, 255, 255), (245, 214, 130), (225, 240, 230)),
    "rot":   ((196, 88, 76), (150, 52, 46), (255, 255, 255), (245, 214, 130), (245, 225, 220)),
}
BG_TOP, BG_BOT, TXT, GOLD, NAMEC = THEMES["sand"]
W = 1080
SIZES = {"feed": (1080, 1350), "story": (1080, 1920)}


from PIL import features
RAQM = features.check("raqm")  # mit raqm formt Pillow selbst (Shaping + Bidi)


def ar(t):
    return t if RAQM else get_display(arabic_reshaper.reshape(t))


def wrap(text, font, maxw, draw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(ar(t), font=font) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def emblem(diam):
    im = Image.open(LOGO).convert("RGB")
    cx, cy, r = 467, 572, 292
    crop = im.crop((cx - r, cy - r, cx + r, cy + r)).resize((diam, diam), Image.LANCZOS)
    mask = Image.new("L", (diam * 4, diam * 4), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, diam * 4 - 1, diam * 4 - 1), fill=255)
    mask = mask.resize((diam, diam), Image.LANCZOS)
    out = Image.new("RGBA", (diam, diam))
    out.paste(crop, (0, 0))
    out.putalpha(mask)
    return out


def make(title, fmt, out, tag=None, theme="rot"):
    global BG_TOP, BG_BOT, TXT, GOLD, NAMEC
    BG_TOP, BG_BOT, TXT, GOLD, NAMEC = THEMES[theme]
    w, h = SIZES[fmt]
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        k = y / h
        d.line([(0, y), (w, y)], fill=tuple(int(BG_TOP[i] * (1 - k) + BG_BOT[i] * k) for i in range(3)))

    diam = 400 if fmt == "feed" else 460
    top = 70 if fmt == "feed" else 260  # Story: oberer Rand bleibt frei (UI)
    em = emblem(diam)
    shadow = Image.new("RGBA", (diam + 120, diam + 120), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse((60, 70, diam + 60, diam + 70), fill=(0, 0, 0, 150))
    shadow = shadow.filter(ImageFilter.GaussianBlur(25))
    img.paste(shadow, ((w - diam) // 2 - 60, top - 60), shadow)
    img.paste(em, ((w - diam) // 2, top), em)

    d = ImageDraw.Draw(img)
    margin = 90
    size = 58 if fmt == "feed" else 64
    f = ImageFont.truetype(FONT_B, size)
    lines = wrap(title, f, w - 2 * margin, d)
    lh = int(size * 1.7)
    area_top = top + diam + (50 if fmt == "feed" else 90)
    area_bot = h - (130 if fmt == "feed" else 330)  # Story: unten frei (UI)
    block = len(lines) * lh
    y = area_top + max(0, (area_bot - area_top - block) // 2 - 10)
    for ln in lines:
        t = ar(ln)
        d.text(((w - d.textlength(t, font=f)) / 2, y), t, font=f, fill=TXT)
        y += lh
    d.rectangle(((w - 160) // 2, y + 14, (w + 160) // 2, y + 18), fill=GOLD)

    if tag:
        ft = ImageFont.truetype(FONT_R, 30)
        d.text(((w - d.textlength(tag, font=ft)) / 2, y + 50), tag, font=ft, fill=GOLD)

    fn = ImageFont.truetype(FONT_R, 30)
    name = "Morocco Football & Futsal News"
    ny = h - (70 if fmt == "feed" else 270)
    d.text(((w - d.textlength(name, font=fn)) / 2, ny), name, font=fn, fill=NAMEC)
    img.save(out, quality=90)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--title", required=True)
    p.add_argument("--fmt", choices=SIZES, required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--tag")
    p.add_argument("--theme", choices=THEMES, default="rot")
    a = p.parse_args()
    make(a.title, a.fmt, a.out, a.tag, a.theme)
