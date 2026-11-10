#!/usr/bin/env python3
"""Baut das Story-/Reel-Video (Musik, Foto-Animation, Text in Abschnitten).

Aufruf:
  python3 make_story_video.py <Arbeitsordner> <Repo-Ordner> <TAG>
Der Arbeitsordner braucht foto.jpg (RGB); die Textabschnitte werden dort als PNG abgelegt.
Ausgabe: <Arbeitsordner>/musik-<TAG>-story-text.mp4 (Reel-Kopie: musik-<TAG>-reel-text.mp4 separat kopieren).
Foto: 1080x1200, Unterkante fest bei y=1380 (direkt über dem Textband), wächst nach oben; gleitet in 0,9 s von links ins Bild und zoomt danach sanft rein und raus (zoompan, Zoom 1,00 bis 1,12, 8 s Zyklus).
Logo: wächst in 0,5 s auf 106 px oben links. Text: je Abschnitt 0,4 s ein, 3 s stehen, 0,4 s aus.
"""
import glob, os, random, subprocess, sys, shutil
AMP = float(os.environ.get('ZOOM_AMP','0.06'))
W = sys.argv[1]; R = sys.argv[2]; TAG = sys.argv[3]
SECTIONS = [
 "الأخضر تحت 16 عاما يبدأ تدريباته في معسكر جدة الاستكشافي",
 "انطلقت تدريبات المنتخب السعودي تحت 16 عاما في جدة",
 "ضمن معسكر استكشافي يستمر من التاسع حتى السادس عشر من نوفمبر",
 "قاد الحصة الأولى المدرب البرتغالي تياغو فارينيا مع جهازه المساعد",
 "وتضمنت تمارين لياقية ثم تدريبات تكتيكية متنوعة",
 "تضم المجموعة الأولى في المعسكر خمسة وعشرين لاعبا",
 "ويستأنف الفريق تدريباته مساء الأربعاء",
 "ما المراكز التي يحتاج الأخضر تحت 16 عاما إلى تعزيزها؟",
 "اكتبوا لنا أسماء المواهب التي تنتظرون تألقها",
]
n = len(SECTIONS); D = 0.5 + 3.0 * n
tracks = sorted(glob.glob(os.path.join(R, "Video", "*.mp3")))
track = random.choice(tracks)
L = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",track]).decode().strip())
maxstart = int((L - D - 8) // 8)
start = 8 * random.randint(0, max(0, maxstart))
print("TRACK", os.path.basename(track), "START", start, "D", D)
band = os.path.join(W, "band.png")
subprocess.check_call([sys.executable, os.path.join(R, "story_text.py"), "--out", band, "--mode", "band"], stdout=subprocess.DEVNULL)
pngs = []
for k, t in enumerate(SECTIONS, 1):
    out = os.path.join(W, f"rp{k}.png")
    subprocess.check_call([sys.executable, os.path.join(R, "story_text.py"), "--out", out, "--title", t, "--mode", "text", "--index", str(k), "--total", str(n)], stdout=subprocess.DEVNULL)
    pngs.append(out)
parts = []
# Hintergrund: unscharfes Foto, leicht abgedunkelt
parts.append("[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:3,eq=brightness=-0.2[bg]")
# Foto: 1080x1200, Unterkante fest bei y=1380 (direkt über dem Textband), wächst nach oben; gleitet in 0,9 s von links ins Bild (Ease-out), danach sanftes Schweben
parts.append(f"[0:v]scale=2160:2400:force_original_aspect_ratio=increase,crop=2160:2400,zoompan=z='1+{AMP}*(1+sin(2*PI*on/200))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1200:fps=25,format=rgba[fg]")
parts.append("[bg][fg]overlay=x='(W-w)/2-1100*max(0,1-t/0.9)*max(0,1-t/0.9)':y=180:eval=frame[v1]")
# Logo: wächst in 0,5 s von 0 auf 106 px (oben links), danach fest
parts.append("[2:v]format=rgba,scale=w='max(2,106*min(1,t/0.5))':h=-2:eval=frame[lg]")
parts.append("[v1][lg]overlay=x=40:y=130:eval=frame,vignette=angle=PI/5[v2]")
parts.append("[v2][3:v]overlay=0:0[v3]")
prev = "v3"
for k in range(1, n + 1):
    s = 0.5 + 3.0 * (k - 1); e = s + 3.0
    # Text: fährt in 0,4 s von unten ein, bleibt, blendet in den letzten 0,4 s aus
    parts.append(f"[{3+k}:v]format=rgba,fade=t=in:st={s}:d=0.4:alpha=1,fade=t=out:st={e-0.4}:d=0.4:alpha=1[t{k}]")
    parts.append(f"[{prev}][t{k}]overlay=x=0:y='40*max(0,1-(t-{s})/0.4)':enable='between(t,{s},{e})':eval=frame[v{k+3}]")
    prev = f"v{k+3}"
parts.append(f"[{prev}]drawbox=x=0:y=ih-16:w='iw*t/{D}':h=16:color=0xC9A227:t=fill[vbar]")
# Thumbnail: Cover (W/cover.jpg, 1080x1920) in den ersten 0,12 s, damit das automatische Vorschaubild nie dunkel/leer ist
COVER = os.path.join(W, "cover.jpg")
if os.path.exists(COVER):
    parts.append(f"[{4+n}:v]format=rgba[cv]")
    parts.append("[vbar][cv]overlay=0:0:enable='lt(t,0.12)'[vout]")
else:
    parts.append("[vbar]null[vout]")
parts.append(f"[1:a]afade=t=in:st=0:d=0.5,afade=t=out:st={D-2}:d=2[a]")
fc = ";".join(parts)
cmd = ["ffmpeg","-y","-loglevel","error",
       "-loop","1","-framerate","25","-t",str(D),"-i",os.path.join(W,"foto.jpg"),
       "-ss",str(start),"-t",str(D),"-i",track,
       "-loop","1","-t",str(D),"-i",os.path.join(R,"images","logo-saudi.png")]
cmd += ["-loop","1","-t",str(D),"-i",band]
for p in pngs:
    cmd += ["-loop","1","-t",str(D),"-i",p]
if os.path.exists(COVER):
    cmd += ["-loop","1","-t",str(D),"-i",COVER]
cmd += ["-filter_complex",fc,"-map","[vout]","-map","[a]","-t",str(D),
        "-c:v","libx264","-preset","veryfast","-crf","23","-pix_fmt","yuv420p","-r","25",
        "-c:a","aac","-b:a","192k","-movflags","+faststart",
        os.path.join(W, f"musik-{TAG}-story-text.mp4")]
subprocess.check_call(cmd)
print("OK", D)
