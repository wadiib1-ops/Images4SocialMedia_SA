#!/usr/bin/env python3
"""Rendert den sichtbaren Story-Text als transparentes 1080x1920-PNG.

Instagram zeigt den Begleittext von Stories NICHT an. Der Text muss daher
IM Bild stehen. Das PNG wird per ffmpeg über das Story-Video (oder ein
Foto) gelegt:

  ffmpeg -y -i story.mp4 -i story_text.png -filter_complex \
    "[0:v][1:v]overlay=0:0,format=yuv420p[v]" -map "[v]" -map 0:a? \
    -c:v libx264 -preset veryfast -crf 23 -c:a copy -movflags +faststart out.mp4

Aufruf (nur Bild):
  python3 story_text.py --out story_text.png --title "<Schlagzeile>" \
      --cta "<Call to Action>" --tags "#tag1 #tag2"

Aufruf (Story-Video mit eingebranntem Text, empfohlen):
  python3 story_text.py --out /tmp/st.png --video story.mp4 --out-video story-text.mp4 \
      --title "<Schlagzeile>" --cta "<Call to Action>" --tags "#tag1 #tag2"

Text steht im Feed-Textfeld (dunkelgrünes Band #0B3D26, volle Breite, goldene Leiste, rechtsbündig), Schrift Noto Sans Arabic 800, Titel 60 px (wie im Feed). Rendering per Chromium.
"""
import argparse
import os
import subprocess

import html
from playwright.sync_api import sync_playwright

W, H = 1080, 1920


def card_html(title, cta, tags, mode="full", index=0, total=0):
    """Text-Container wie im Feed-Post: dunkelgrünes Band #0B3D26, goldene Leiste,
    Noto Sans Arabic 800, Schriftgröße wie im Feed-Post (Titel 60 px)."""
    e = html.escape
    if mode == "band":
        title = cta = tags = ""
    parts = [] if mode == "band" else [f'<div style="font-size:60px;font-weight:800;line-height:1.3;color:#FFFFFF">{e(title)}</div>']
    bg = "transparent" if mode == "text" else "#0B3D26"
    deco = "" if mode == "text" else (
        '<div style="position:absolute;left:56px;right:113px;bottom:44px;font-size:28px;font-weight:600;color:rgba(255,255,255,0.8);direction:ltr;text-align:right;unicode-bidi:isolate">@saudifootballfutsal</div>'
        '<div style="position:absolute;left:0;right:113px;bottom:0;height:14px;background:#C9A227"></div>')
    if mode == "text" and total > 1 and index:
        segs = "".join(
            f'<div style="flex:1;height:8px;border-radius:4px;background:{"#C9A227" if i == index else "rgba(255,255,255,0.35)"}"></div>'
            for i in range(1, total + 1))
        parts.append(f'<div style="position:absolute;left:56px;right:113px;top:16px;display:flex;flex-direction:row-reverse;gap:8px;direction:ltr">{segs}</div>'
                     f'<div style="position:absolute;left:56px;top:30px;font-size:26px;font-weight:800;color:#C9A227;direction:ltr">{index}/{total}</div>')
    if cta and mode != "band":
        parts.append(f'<div style="margin-top:22px;font-size:34px;font-weight:800;color:#C9A227">{e(cta)}</div>')
    if tags and mode != "band":
        parts.append(f'<div style="margin-top:18px;font-size:28px;font-weight:600;color:rgba(255,255,255,0.8)">{e(tags)}</div>')
    return f'''<html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;600;800&display=swap" rel="stylesheet">
</head><body style="margin:0;background:transparent">
<div style="width:1080px;height:1920px;position:relative;font-family:'Noto Sans Arabic','DejaVu Sans',sans-serif">
<div id="card" style="position:absolute;left:0;right:0;bottom:0;height:540px;box-sizing:border-box;background:{bg};color:#FFFFFF;padding:92px 113px 150px 56px;text-align:right;direction:rtl">
{"".join(parts)}
{deco}
</div></div></body></html>'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", default="")
    ap.add_argument("--mode", choices=["full", "band", "text"], default="full",
                    help="band = fester Container mit Footer ohne Text, text = nur Text transparent")
    ap.add_argument("--index", type=int, default=0, help="Nummer des aktuellen Text-Teils (nur --mode text)")
    ap.add_argument("--total", type=int, default=0, help="Anzahl der Text-Teile (nur --mode text)")
    ap.add_argument("--cta", default="")
    ap.add_argument("--tags", default="")
    ap.add_argument("--video", default="",
                    help="optional: Story-Video, auf das der Text gelegt wird")
    ap.add_argument("--out-video", default="",
                    help="Ausgabe-Video mit eingebranntem Text (mit --video)")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    tmp = os.path.abspath(args.out) + ".html"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(card_html(args.title, args.cta, args.tags, args.mode, args.index, args.total))
    with sync_playwright() as p:
        b = p.chromium.launch(**({'executable_path': '/opt/pw-browsers/chromium', 'args': ['--no-sandbox']} if os.path.exists('/opt/pw-browsers/chromium') else {}))
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.goto("file://" + tmp, wait_until="load")
        pg.wait_for_timeout(800)
        pg.screenshot(path=args.out, omit_background=True,
                      clip={"x": 0, "y": 0, "width": W, "height": H})
        b.close()
    os.remove(tmp)
    print(args.out)

    if args.video:
        if not args.out_video:
            raise SystemExit("--video braucht --out-video")
        # Overlay auf die Videogröße skalieren, Ton unverändert übernehmen
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-i", args.video, "-i", args.out,
            "-filter_complex",
            "[1:v][0:v]scale2ref=w=iw:h=ih[ovl][base];[base][ovl]overlay=0:0,format=yuv420p[v]",
            "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-preset", "veryfast",
            "-crf", "23", "-c:a", "copy", "-movflags", "+faststart", args.out_video,
        ], check=True)
        print(args.out_video)


if __name__ == "__main__":
    main()
