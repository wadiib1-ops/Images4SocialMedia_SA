#!/usr/bin/env python3
"""Erzeugt den Facebook-Feed-Post im Design "Saudi Kora News" (1080x1080, PNG).

Layout (Vorlage aus dem Design-Artefakt): dunkelgrüner Grund #0B3D26, goldene Akzente #C9A227,
Logo oben links, Foto mittig (ganz sichtbar, nicht beschnitten), Kategorie in Gold,
Schlagzeile, Seitenname und Handle unten, goldene Leiste am unteren Rand.
Keine Quellenangabe, keine URL, keine Hashtags im Bild.

Aufruf:
  python3 make_feed_image.py --photo <foto.jpg> --title "<Schlagzeile>" \
      --category "<Kategorie>" --out <datei.png> [--repo <Repo-Ordner>]
Voraussetzung: Playwright mit Chromium (vorinstalliert), Logo unter images/logo-saudi.png.
"""
import argparse
import html
import os
from playwright.sync_api import sync_playwright

HANDLE = "@saudifootballfutsal"
PAGE_NAME = "أخبار الكرة السعودية"


def build_html(photo, title, category, logo, kind="feed", subtitle=""):
    if kind == "story":
        return story_html(photo, title, category, logo, subtitle)
    return f'''<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;600;800&display=swap" rel="stylesheet">
<style>body{{margin:0;background:transparent}}</style></head><body>
<div style="width:1080px;height:1080px;box-sizing:border-box;background:#0B3D26;color:#FFFFFF;font-family:'Noto Sans Arabic','DejaVu Sans',sans-serif;display:flex;flex-direction:column;padding:56px;gap:28px;position:relative;overflow:hidden">
  <div style="display:flex;align-items:center"><img src="file://{logo}" style="width:200px;height:200px" alt=""></div>
  <div style="width:968px;height:460px;box-sizing:border-box;background:#082F1E;display:flex;align-items:center;justify-content:center;overflow:hidden">
    <img src="file://{photo}" style="max-width:968px;max-height:460px;object-fit:contain"></div>
  <div style="font-size:28px;font-weight:800;color:#C9A227">{html.escape(category)}</div>
  <div style="font-size:60px;font-weight:800;line-height:1.3;color:#FFFFFF">{html.escape(title)}</div>
  <div style="margin-top:auto;display:flex;justify-content:space-between;align-items:center;font-size:24px;color:rgba(255,255,255,0.8)">
    <div style="font-weight:600;direction:ltr;unicode-bidi:isolate">{HANDLE}</div><div></div></div>
  <div style="position:absolute;left:0;bottom:0;width:1080px;height:12px;background:#C9A227"></div>
</div></body></html>'''


def story_html(photo, title, category, logo, subtitle=""):
    """Story-Layout 1080x1920 (Artefakt-Vorlage Story): Reel-Cover."""
    return f'''<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;600;800&display=swap" rel="stylesheet">
<style>body{{margin:0;background:transparent}}</style></head><body>
<div style="width:1080px;height:1920px;box-sizing:border-box;background:#0B3D26;color:#FFFFFF;font-family:'Noto Sans Arabic','DejaVu Sans',sans-serif;display:flex;flex-direction:column;padding:120px 72px 150px;gap:40px;position:relative;overflow:hidden">
  <div style="display:flex;align-items:center"><img src="file://{logo}" style="width:300px;height:300px" alt=""></div>
  <div style="width:936px;height:860px;box-sizing:border-box;background:#082F1E;display:flex;align-items:center;justify-content:center;overflow:hidden">
    <img src="file://{photo}" style="max-width:936px;max-height:860px;object-fit:contain"></div>
  <div style="font-size:34px;font-weight:800;color:#C9A227">{html.escape(category)}</div>
  <div style="font-size:88px;font-weight:800;line-height:1.3;color:#FFFFFF">{html.escape(title)}</div>
  <div style="font-size:34px;line-height:1.5;color:rgba(255,255,255,0.8)">{html.escape(subtitle)}</div>
  <div style="margin-top:auto;display:flex;justify-content:space-between;align-items:center;font-size:28px;color:rgba(255,255,255,0.8)">
    <div style="font-weight:600;direction:ltr;unicode-bidi:isolate">{HANDLE}</div><div></div></div>
  <div style="position:absolute;left:0;bottom:0;width:1080px;height:14px;background:#C9A227"></div>
</div></body></html>'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--photo", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--category", required=True)
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--kind", choices=["feed", "story"], default="feed",
                    help="feed = 1080x1080 (Facebook-Feed), story = 1080x1920 (Reel-Cover)")
    ap.add_argument("--repo", default=os.path.dirname(os.path.abspath(__file__)))
    a = ap.parse_args()
    photo = os.path.abspath(a.photo)
    logo = os.path.join(a.repo, "images", "logo-saudi.png")
    tmp = os.path.join(os.path.dirname(os.path.abspath(a.out)), "_feed_tmp.html")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(build_html(photo, a.title, a.category, logo, a.kind, a.subtitle))
    h = 1920 if a.kind == "story" else 1080
    with sync_playwright() as p:
        b = p.chromium.launch(**({'executable_path': '/opt/pw-browsers/chromium', 'args': ['--no-sandbox']} if os.path.exists('/opt/pw-browsers/chromium') else {}))
        pg = b.new_page(viewport={"width": 1080, "height": h})
        pg.goto("file://" + tmp, wait_until="load")
        pg.wait_for_timeout(800)
        pg.screenshot(path=a.out, clip={"x": 0, "y": 0, "width": 1080, "height": h})
        b.close()
    os.remove(tmp)
    print("OK", a.out)


if __name__ == "__main__":
    main()
