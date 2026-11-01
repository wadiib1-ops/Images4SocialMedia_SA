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

Alle Texte arabisch (RTL) gerendert; Schrift DejaVuSans-Bold.
Die Schlagzeile wird ohne vorheriges reshaping übergeben (raqm übernimmt die
Verbindung der Buchstaben).
"""
import argparse
import os
import subprocess

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MARGIN = 80


def wrap(draw, text, font, max_w):
    """Zeilenumbruch nach Pixelbreite (Wörter bleiben zusammen)."""
    lines, current = [], ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font, direction="rtl", language="ar") <= max_w:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_lines(draw, lines, font, y, color, line_gap):
    for line in lines:
        w = draw.textlength(line, font=font, direction="rtl", language="ar")
        draw.text(((W - w) / 2, y), line, font=font, fill=color,
                  direction="rtl", language="ar")
        y += font.size + line_gap
    return y


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--cta", default="")
    ap.add_argument("--tags", default="")
    ap.add_argument("--video", default="",
                    help="optional: Story-Video, auf das der Text gelegt wird")
    ap.add_argument("--out-video", default="",
                    help="Ausgabe-Video mit eingebranntem Text (mit --video)")
    args = ap.parse_args()

    measure = ImageDraw.Draw(Image.new("RGBA", (W, H)))
    title_font = ImageFont.truetype(FONT, 44)
    cta_font = ImageFont.truetype(FONT, 30)
    tag_font = ImageFont.truetype(FONT, 30)
    max_w = W - 2 * MARGIN

    # Blöcke: (Zeilen, Schrift, Farbe, Zeilenabstand, Abstand davor)
    blocks = [(wrap(measure, args.title, title_font, max_w), title_font,
               (255, 255, 255, 255), 16, 0)]
    if args.cta:
        blocks.append((wrap(measure, args.cta, cta_font, max_w), cta_font,
                       (255, 215, 0, 255), 8, 20))
    if args.tags:
        blocks.append((wrap(measure, args.tags, tag_font, max_w), tag_font,
                       (255, 255, 255, 230), 10, 36))

    pad = 24
    total = pad * 2
    for lines, font, _, gap, before in blocks:
        total += before + len(lines) * (font.size + gap)
    if total > 1000:
        raise SystemExit("Text zu lang für die Story: Titel oder CTA kürzen")

    # Streifen klein, unten (Mitte bei ca. 1600 px, über Instagram-Bedienleiste)
    box_top = 1600 - total // 2
    box_bottom = box_top + total

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # halbtransparenter Streifen für Lesbarkeit auf jedem Foto/Video
    draw.rectangle([0, box_top, W, box_bottom], fill=(0, 0, 0, 170))

    y = box_top + pad
    for lines, font, color, gap, before in blocks:
        y += before
        y = draw_lines(draw, lines, font, y, color, gap)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    img.save(args.out)
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
