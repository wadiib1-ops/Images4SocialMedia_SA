#!/usr/bin/env python3
"""Design "Scoreboard Night" für Saudi-Pro-League-Ergebnisse.

Nachtblau + Cyan + Magenta, geteiltes Scoreboard, Wappen-Kollision,
Torschützen-Zeitleiste, Ring-Fortschritt. Kein Foto nötig.

  python3 spl_render.py --data match.json --kind feed  --out images/feed-...png
  python3 spl_render.py --data match.json --kind cover --out images/cover-...png
  python3 spl_render.py --data match.json --kind reel  --out reel.mp4
  python3 spl_render.py --data match.json --kind story --out story.mp4   (mit Call to Action)

match.json:
{ "home": "Al_Nassr", "away": "Al_Hilal", "score": [2, 1],
  "matchday": "الجولة 9", "title": "<Schlagzeile>",
  "sections": ["<Abschnitt 1>", "<Abschnitt 2>"],      # arabischer Facebook-Text ohne Hashtags
  "cta": "<Call to Action>",                           # nur Story
  "scorers": [{"side": "home", "name": "...", "minute": 23}, ...] }
"""
import argparse, glob, json, math, os, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
FB = os.path.join(REPO, "fonts", "Tajawal-Bold.ttf")
FR = os.path.join(REPO, "fonts", "Tajawal-Regular.ttf")
W = 1080
FPS = 25
NAVY = (10, 18, 48)
NAVY2 = (16, 28, 70)
PANEL_H = (17, 36, 92)
PANEL_A = (40, 18, 84)
CYAN = (25, 211, 243)
MAG = (255, 46, 136)
WHITE = (255, 255, 255)
MUTE = (150, 170, 215)
LEAGUE_AR = "دوري روشن السعودي للمحترفين"
PAGE_AR = "أخبار الكرة السعودية"
HANDLE = "@saudifootballfutsal"

_fc = {}
def font(size, bold=True):
    k = (size, bold)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(FB if bold else FR, size, layout_engine=ImageFont.Layout.RAQM)
    return _fc[k]

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def e_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def e_in(x): x = clamp(x); return x ** 3
def e_back(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def tw(d, text, f):
    return d.textlength(text, font=f, direction="rtl", language="ar")

def txt(d, xy, text, f, fill, anchor="mm", ltr=False):
    if ltr: d.text(xy, text, font=f, fill=fill, anchor=anchor, direction="ltr")
    else: d.text(xy, text, font=f, fill=fill, anchor=anchor, direction="rtl", language="ar")

def wrap(d, text, f, max_w):
    lines, cur = [], ""
    for w in text.split():
        c = f"{cur} {w}".strip()
        if tw(d, c, f) <= max_w: cur = c
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def load_crest(path, box):
    """Wappen laden: weißen Rand-Hintergrund entfernen, auf box hochskalieren."""
    im = Image.open(path).convert("RGB")
    w, h = im.size
    m = im.copy()
    for p in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        if m.getpixel(p)[0] > 235 and m.getpixel(p)[1] > 235 and m.getpixel(p)[2] > 235:
            ImageDraw.floodfill(m, p, (255, 0, 255), thresh=28)
    a = Image.new("L", (w, h), 255)
    ap = a.load(); mp = m.load()
    for y in range(h):
        for x in range(w):
            if mp[x, y] == (255, 0, 255): ap[x, y] = 0
    a = a.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.6))
    rgba = im.convert("RGBA"); rgba.putalpha(a)
    s = min(box / w, box / h)
    return rgba.resize((max(1, int(w * s)), max(1, int(h * s))), Image.LANCZOS)

def aa_poly(size, polys):
    """Antialiaste Polygone (3x Supersampling). polys = [(points, rgba)]"""
    k = 3
    big = Image.new("RGBA", (size[0] * k, size[1] * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    for pts, col in polys:
        d.polygon([(x * k, y * k) for x, y in pts], fill=col)
    return big.resize(size, Image.LANCZOS)

def aa_circle(d_px, col):
    k = 3
    big = Image.new("RGBA", (d_px * k, d_px * k), (0, 0, 0, 0))
    ImageDraw.Draw(big).ellipse((0, 0, d_px * k - 1, d_px * k - 1), fill=col)
    return big.resize((d_px, d_px), Image.LANCZOS)

class Scene:
    def __init__(self, cfg, H, dy, text_mode, sections=None, D=1.0):
        self.cfg, self.H, self.dy, self.mode = cfg, H, dy, text_mode  # mode: video|cover|feed
        self.D = D
        teams = json.load(open(os.path.join(HERE, "teams.json"), encoding="utf-8"))
        self.hn, self.an = teams[cfg["home"]], teams[cfg["away"]]
        self.sh, self.sa = cfg["score"]
        wp = os.path.join(REPO, "Wappen")
        self.ch = load_crest(os.path.join(wp, cfg["home"] + ".png"), 250)
        self.ca = load_crest(os.path.join(wp, cfg["away"] + ".png"), 250)
        self.logo = Image.open(os.path.join(wp, "Saudi_Pro_League_LOGO.png")).convert("RGBA")
        self.logo = load_crest(os.path.join(wp, "Saudi_Pro_League_LOGO.png"), 130)
        self.d = D
        Y = lambda y: y + dy
        self.Y = Y
        # Hintergrund
        g = Image.linear_gradient("L").resize((W, H))
        top, bot = (7, 12, 36), (16, 30, 78)
        self.bg = Image.merge("RGB", [g.point(lambda v, a=top[i], b=bot[i]: int(a + (b - a) * v / 255)) for i in range(3)])
        grid = Image.new("RGBA", (W + 120, H + 120), (0, 0, 0, 0))
        gd = ImageDraw.Draw(grid)
        for x in range(0, W + 121, 60): gd.line([(x, 0), (x, H + 120)], fill=(25, 211, 243, 22), width=2)
        for y in range(0, H + 121, 60): gd.line([(0, y), (W + 120, y)], fill=(25, 211, 243, 22), width=2)
        self.grid = grid
        # Panels (antialiast)
        p0, p1 = Y(300), Y(760)
        self.p0, self.p1 = p0, p1
        hp = [(0, p0), (600, p0), (470, p1), (0, p1)]
        ap = [(620, p0), (W, p0), (W, p1), (490, p1)]
        self.pan_h = aa_poly((W, H), [(hp, PANEL_H + (255,)), ([(594, p0), (610, p0), (480, p1), (464, p1)], CYAN + (255,))])
        self.pan_a = aa_poly((W, H), [(ap, PANEL_A + (255,)), ([(614, p0), (630, p0), (500, p1), (484, p1)], MAG + (255,))])
        self.disc = aa_circle(330, (255, 255, 255, 30))
        self.glow = Image.new("RGBA", (700, 700), (0, 0, 0, 0))
        gdr = ImageDraw.Draw(self.glow)
        for r in range(350, 0, -7):
            gdr.ellipse((350 - r, 350 - r, 350 + r, 350 + r), fill=(255, 255, 255, int(255 * (1 - r / 350) ** 2)))
        self.hx, self.ax, self.cy = 265, 815, Y(500)
        self.ringc = (540, Y(530))
        # Sektionen
        self.secs = []
        if sections:
            for s in sections: self.secs.append(self.panel_img(s["text"], s["cta"]) + (s["start"], s["end"]))
        self.bar_y = Y(1200); self.x0, self.x1 = 110, 970
        sc = [s for s in cfg.get("scorers", [])]
        self.axis = 90 if all(s["minute"] <= 90 for s in sc) else 120
        self.markers = self.layout_markers(sc)

    def panel_img(self, text, cta=False):
        pw, ph = 960, 250
        im = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, pw - 1, ph - 1), 26, fill=MAG if cta else NAVY2)
        if not cta: d.rectangle((0, 0, pw - 1, 7), fill=CYAN)
        size = 58
        while size >= 34:
            f = font(size)
            lines = wrap(d, text, f, pw - 90)
            if len(lines) * (size + 14) <= ph - 40 and len(lines) <= 3: break
            size -= 3
        f = font(size)
        total = len(lines) * (size + 14) - 14
        y = (ph - total) / 2 + size / 2
        for ln in lines:
            txt(d, (pw / 2, y), ln, f, WHITE); y += size + 14
        return (im,)

    def layout_markers(self, sc):
        out = []
        for side in ("home", "away"):
            prev_x, lvl = -999, 0
            for s in sorted([s for s in sc if s["side"] == side], key=lambda s: s["minute"]):
                x = self.x0 + (self.x1 - self.x0) * s["minute"] / self.axis
                lvl = (lvl + 1) % 2 if x - prev_x < 175 else 0
                prev_x = x
                out.append(dict(s, x=x, lvl=lvl, t=2.6 + 3.0 * s["minute"] / self.axis))
        return out

    def frame(self, t, static_text=None):
        H, Y = self.H, self.Y
        stat = self.mode != "video"
        img = self.bg.convert("RGBA")
        off = (0, 0) if stat else (int(t * 14) % 60, int(t * 9) % 60)
        img.alpha_composite(self.grid, (-off[0], -off[1]))
        d = ImageDraw.Draw(img)
        T = 99 if stat else t
        # Kopfzeile
        ls = e_back((T - 0.0) / 0.5)
        if ls > 0:
            lg = self.logo.resize((max(1, int(self.logo.width * ls)), max(1, int(self.logo.height * ls))), Image.LANCZOS)
            img.paste(lg, (54 + (self.logo.width - lg.width) // 2, Y(145) + (self.logo.height - lg.height) // 2), lg)
        if T > 0.3:
            txt(d, (1026, Y(168)), LEAGUE_AR, font(36), CYAN, "rm")
            txt(d, (1026, Y(228)), self.cfg.get("matchday", ""), font(52), WHITE, "rm")
        # Panels
        sh = (1 - e_out(T / 0.6)) * 700
        img.paste(self.pan_h, (int(-sh), 0), self.pan_h)
        img.paste(self.pan_a, (int(sh), 0), self.pan_a)
        # Wappen
        hxp = self.hx - 165; axp = self.ax - 165
        if T > 1.6:
            for cx, im_ in ((self.hx, self.disc), (self.ax, self.disc)):
                img.paste(im_, (cx - 165, self.cy - 165), im_)
        for side, crest, fx in (("h", self.ch, self.hx), ("a", self.ca, self.ax)):
            sgn = -1 if side == "h" else 1
            start_x = 540 + sgn * 900
            if T < 0.3: continue
            if T < 1.0:
                x = start_x + (540 - start_x) * e_in((T - 0.3) / 0.7); sc_ = 1.0
            elif T < 1.7:
                x = 540 + (fx - 540) * e_back((T - 1.0) / 0.7); sc_ = 1.0
            else:
                x, sc_ = fx, 1.0
            im_ = crest
            if abs(sc_ - 1) > 0.01: im_ = crest.resize((int(crest.width * sc_), int(crest.height * sc_)), Image.LANCZOS)
            img.paste(im_, (int(x - im_.width / 2), int(self.cy - im_.height / 2)), im_)
        # Blitz
        if 1.0 <= T < 1.5:
            k = (1 - (T - 1.0) / 0.5)
            gl = self.glow.copy(); gl.putalpha(gl.getchannel("A").point(lambda v: int(v * k)))
            img.paste(gl, (540 - 350, self.cy - 350), gl)
        # Namen
        if T > 1.7:
            a = clamp((T - 1.7) / 0.4)
            c = tuple(int(NAVY[i] + (WHITE[i] - NAVY[i]) * a) for i in range(3))
            txt(d, (self.hx, Y(690)), self.hn, font(54), c)
            txt(d, (self.ax, Y(690)), self.an, font(54), c)
        # Ring
        if T > 1.3:
            cx, cy = self.ringc; r = 72
            rs = e_back((T - 1.3) / 0.4)
            rr = int(r * rs)
            if rr > 4:
                d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=NAVY)
                d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=(40, 60, 120), width=8)
                prog = 1.0 if stat else clamp(t / self.D)
                if prog > 0.003:
                    d.arc((cx - rr, cy - rr, cx + rr, cy + rr), -90, -90 + 360 * prog, fill=CYAN, width=8)
                txt(d, (cx, cy), "FT", font(46), WHITE)
        # Ergebnis (Count-up + Schlag)
        if T > 1.8:
            base_y = Y(905)
            for val, cx in ((self.sh, 330), (self.sa, 750)):
                p = clamp((T - 1.8) / 0.7)
                shown = min(val, int(math.floor(e_out(p) * (val + 1))))
                punch = 1.0
                if T > 2.5: punch = 1 + 0.35 * max(0.0, 1 - (T - 2.5) / 0.35)
                self.big(img, str(shown), cx, base_y, punch)
            txt(d, (540, base_y), "–", font(150), CYAN)
        # Zeitleiste
        self.timeline(img, d, T)
        # Textbereich
        if self.mode == "video":
            self.sections(img, d, t)
        elif self.mode == "cover":
            self.draw_panel(img, self.panel_img(static_text)[0], Y(1430), 1.0)
        else:
            self.band(img, d, static_text)
        # Fuß
        fy = self.H - 180 if self.mode != "feed" else H - 42
        if self.mode != "feed":
            d.line([(300, fy - 40), (780, fy - 40)], fill=(40, 60, 120), width=3)
            txt(d, (540, fy), PAGE_AR, font(38), WHITE)
            txt(d, (540, fy + 46), HANDLE, font(30, False), MUTE, ltr=True)
        else:
            txt(d, (400, fy), PAGE_AR, font(28, False), MUTE)
            txt(d, (640, fy), HANDLE, font(28, False), MUTE, ltr=True)
        return img.convert("RGB")

    def big(self, img, s, cx, cy, k):
        f = font(260)
        lay = Image.new("RGBA", (400, 360), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        ld.text((200, 180), s, font=f, fill=WHITE, anchor="mm")
        if abs(k - 1) > 0.01:
            lay = lay.resize((int(400 * k), int(360 * k)), Image.LANCZOS)
        img.paste(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)), lay)

    def timeline(self, img, d, T):
        by = self.bar_y
        if T < 2.0: return
        a = e_out((T - 2.0) / 0.4)
        x0, x1 = self.x0, self.x1
        d.line([(x0, by), (x0 + (x1 - x0) * a, by)], fill=(40, 60, 120), width=8)
        for m in (0, 45, 90, 120):
            if m > self.axis: break
            x = x0 + (x1 - x0) * m / self.axis
            d.line([(x, by - 14), (x, by + 14)], fill=(70, 95, 160), width=3)
            txt(d, (x, by + 34 if False else by - 28), f"{m}'" if False else "", font(24), MUTE)
        p = clamp((T - 2.6) / 3.0)
        if p > 0:
            d.line([(x0, by), (x0 + (x1 - x0) * p, by)], fill=CYAN, width=8)
            sx = x0 + (x1 - x0) * p
            if p < 1: d.ellipse((sx - 12, by - 12, sx + 12, by + 12), fill=WHITE)
        for m in self.markers:
            if T < m["t"]: continue
            s = e_back((T - m["t"]) / 0.35)
            col = CYAN if m["side"] == "home" else MAG
            r = int(17 * s)
            if r < 2: continue
            d.ellipse((m["x"] - r, by - r, m["x"] + r, by + r), fill=col, outline=WHITE, width=4)
            ox = min(max(m["x"], 110), 970)
            up = m["side"] == "home"
            lv = m["lvl"] * 88
            if up:
                ym, yn = by - 52 - lv, by - 92 - lv
            else:
                ym, yn = by + 52 + lv, by + 92 + lv
            al = clamp((T - m["t"]) / 0.3)
            fadec = lambda c: tuple(int(NAVY[i] + (c[i] - NAVY[i]) * al) for i in range(3))
            txt(d, (ox, ym), f"{m['minute']}'", font(36), fadec(col))
            txt(d, (ox, yn), m["name"], font(32), fadec(WHITE))

    def draw_panel(self, img, pim, y, k):
        pw = pim.width
        rw = int(pw * k)
        if rw < 2: return
        crop = pim.crop((pw - rw, 0, pw, pim.height))
        x = 60 + (pw - rw)
        img.paste(crop, (x, y), crop)
        if k < 1:
            ImageDraw.Draw(img).rectangle((x, y, x + 8, y + pim.height), fill=WHITE)

    def sections(self, img, d, t):
        y = self.Y(1430)
        for pim, s, e in self.secs:
            if s <= t < e:
                k = e_out((t - s) / 0.4)
                self.draw_panel(img, pim, y, k)
                tt = t - s
                if s > 1 and tt < 0.35:
                    ly = int(self.H * tt / 0.35)
                    d.rectangle((0, ly, W, ly + 4), fill=CYAN)
                if s > 1 and tt < 0.18:
                    rnd = random.Random(int(t * 1000))
                    for _ in range(5):
                        sy = y + rnd.randint(0, 220); sh_ = rnd.randint(14, 40)
                        dx = rnd.randint(-40, 40)
                        strip = img.crop((0, sy, W, sy + sh_))
                        img.paste(strip, (dx, sy))
                break

    def band(self, img, d, text):
        y = self.Y(1260) + 0
        y = self.H - 130
        size = 46
        while size > 28 and tw(d, text, font(size)) > 960: size -= 2
        d.rounded_rectangle((60, y - 40, W - 60, y + 40), 20, fill=NAVY2)
        d.rectangle((60, y - 40, W - 60, y - 36), fill=CYAN)
        txt(d, (540, y), text, font(size), WHITE)

def pick_music(D):
    tr = sorted(glob.glob(os.path.join(REPO, "Video", "*.mp3")))
    f = random.choice(tr)
    ln = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]).strip())
    hi = int((ln - D - 8) // 8)
    start = 8 * random.randint(0, hi) if hi > 0 else 0
    return f, start

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--kind", required=True, choices=["feed", "cover", "reel", "story"])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cfg = json.load(open(a.data, encoding="utf-8"))
    if a.kind in ("feed", "cover"):
        H, dy = (1350, -190) if a.kind == "feed" else (1920, 0)
        sc = Scene(cfg, H, dy, a.kind)
        im = sc.frame(99, cfg["title"])
        if a.out.lower().endswith((".jpg", ".jpeg")): im.save(a.out, quality=92)
        else: im.save(a.out)
        print(a.out, im.size); return
    n = len(cfg["sections"])
    secs, t0 = [], 0.5
    for s in cfg["sections"]:
        secs.append(dict(text=s, cta=False, start=t0, end=t0 + 3.0)); t0 += 3.0
    D = max(12.0, t0)
    if a.kind == "story" and cfg.get("cta"):
        secs.append(dict(text=cfg["cta"], cta=True, start=D, end=D + 4.5)); D += 4.5
    secs[-1]["end"] = D
    sc = Scene(cfg, 1920, 0, "video", secs, D)
    music, start = pick_music(D)
    nfr = int(round(D * FPS))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x1920", "-r", str(FPS), "-i", "-",
           "-ss", str(start), "-t", str(D), "-i", music,
           "-vf", "format=yuv420p", "-af", f"afade=t=in:st=0:d=1,afade=t=out:st={D-2}:d=2",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-c:a", "aac", "-b:a", "160k", "-t", str(D),
           "-movflags", "+faststart", a.out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(nfr):
        p.stdin.write(sc.frame(i / FPS).tobytes())
    p.stdin.close(); p.wait()
    print(f"{a.out} D={D}s Track={os.path.basename(music)} Start={start}s")

if __name__ == "__main__":
    main()
