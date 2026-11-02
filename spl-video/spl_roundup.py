#!/usr/bin/env python3
"""Sammelmeldung "Scoreboard Night": alle Ergebnisse eines Spieltags plus Tabelle.

  python3 spl-video/spl_roundup.py --data roundup.json --kind feed  --out images/feed-...png     (1080x1350)
  python3 spl-video/spl_roundup.py --data roundup.json --kind cover --out images/cover-...jpg     (1080x1920)
  python3 spl-video/spl_roundup.py --data roundup.json --kind reel  --out reel.mp4
  python3 spl-video/spl_roundup.py --data roundup.json --kind story --out story.mp4  (mit Call to Action)

roundup.json:
{ "round": "الجولة 12", "title": "...", "sections": ["..."], "cta": "...",
  "results": [ {"home": "Al_Nassr", "away": "Al_Kholood", "score": [5, 3]}, ... ],
  "table": [ {"team": "Al-Hilal", "played": 11, "pts": 30}, ... ] }   # in Tabellenreihenfolge
"""
import argparse, json, os, subprocess
from PIL import Image, ImageDraw
import spl_render as R

W = R.W
_cr = {}
def crest(key, box):
    k = (key, box)
    if k not in _cr:
        _cr[k] = R.load_crest(os.path.join(R.REPO, "Wappen", key + ".png"), box)
    return _cr[k]

def paste_c(img, im, cx, cy):
    img.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)), im)

def result_row(teams, r, w, h, cb, fs):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), h // 3, fill=R.NAVY2)
    hs, as_ = r["score"]
    d.rectangle((0, 8, 6, h - 9), fill=R.CYAN)
    d.rectangle((w - 7, 8, w - 1, h - 9), fill=R.MAG)
    paste_c(im, crest(r["home"], cb), 22 + cb // 2, h // 2)
    paste_c(im, crest(r["away"], cb), w - 22 - cb // 2, h // 2)
    f = R.font(fs)
    R.txt(d, (22 + cb + 14, h // 2), teams[r["home"]], f, R.WHITE, "lm")
    R.txt(d, (w - 22 - cb - 14, h // 2), teams[r["away"]], f, R.WHITE, "rm")
    pw = int(fs * 3.0)
    d.rounded_rectangle((w // 2 - pw // 2, h // 2 - int(fs * 0.75), w // 2 + pw // 2, h // 2 + int(fs * 0.75)),
                        int(fs * 0.4), fill=R.NAVY)
    sf = R.font(int(fs * 1.25))
    R.txt(d, (w // 2, h // 2 - 2), f"{hs} - {as_}", sf, R.WHITE, "mm", ltr=True)
    return im

def table_row(teams, rank, e, w, h, cb, fs, hi):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), h // 3, fill=R.PANEL_H if hi else R.NAVY2)
    col = R.CYAN if rank <= 3 else (R.MAG if rank >= 16 else R.WHITE)
    R.txt(d, (int(fs * 1.1), h // 2), str(rank), R.font(fs), col, "mm", ltr=True)
    paste_c(im, crest(e["team"], cb), int(fs * 2.4) + cb // 2, h // 2)
    R.txt(d, (int(fs * 2.4) + cb + 12, h // 2), teams[e["team"]], R.font(fs), R.WHITE, "lm")
    R.txt(d, (w - int(fs * 3.4), h // 2), str(e["played"]), R.font(int(fs * 0.85), False), R.MUTE, "mm", ltr=True)
    R.txt(d, (w - int(fs * 1.3), h // 2), str(e["pts"]), R.font(int(fs * 1.1)), R.WHITE, "mm", ltr=True)
    return im

def with_alpha(im, a):
    if a >= 0.999: return im
    c = im.copy(); c.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    return c

class Roundup:
    def __init__(self, cfg, H, mode, sections=None, D=1.0):
        self.cfg, self.H, self.mode, self.D = cfg, H, mode, D
        self.teams = json.load(open(os.path.join(R.HERE, "teams.json"), encoding="utf-8"))
        g = Image.linear_gradient("L").resize((W, H))
        top, bot = (7, 12, 36), (16, 30, 78)
        self.bg = Image.merge("RGB", [g.point(lambda v, a=top[i], b=bot[i]: int(a + (b - a) * v / 255)) for i in range(3)]).convert("RGBA")
        grid = Image.new("RGBA", (W + 120, H + 120), (0, 0, 0, 0))
        gd = ImageDraw.Draw(grid)
        for x in range(0, W + 121, 60): gd.line([(x, 0), (x, H + 120)], fill=(25, 211, 243, 22), width=2)
        for y in range(0, H + 121, 60): gd.line([(0, y), (W + 120, y)], fill=(25, 211, 243, 22), width=2)
        self.grid = grid
        self.logo = R.load_crest(os.path.join(R.REPO, "Wappen", "Saudi_Pro_League_LOGO.png"), 130)
        res, tab, T = cfg["results"], cfg["table"], self.teams
        if mode == "feed":
            self.res_rows = [result_row(T, r, 960, 54, 40, 30) for r in res]
            self.tab_rows = [table_row(T, i + 1, e, 480, 38, 28, 24, i < 3) for i, e in enumerate(tab)]
        else:
            self.res_rows = [result_row(T, r, 960, 104, 80, 38) for r in res]
            self.tab_rows = [table_row(T, i + 1, e, 960, 58, 42, 32, i < 3) for i, e in enumerate(tab)]
        self.secs = []
        if sections:
            for s in sections:
                self.secs.append((R.Scene.panel_img(None, s["text"], s["cta"])[0], s["start"], s["end"]))

    def header(self, img, d, T, y0):
        ls = R.e_back(T / 0.5)
        if ls > 0:
            lg = self.logo.resize((max(1, int(self.logo.width * ls)), max(1, int(self.logo.height * ls))), Image.LANCZOS)
            img.paste(lg, (54 + (self.logo.width - lg.width) // 2, y0 + (self.logo.height - lg.height) // 2), lg)
        if T > 0.3:
            R.txt(d, (1026, y0 + 30), R.LEAGUE_AR, R.font(36), R.CYAN, "rm")
            R.txt(d, (1026, y0 + 92), self.cfg["round"], R.font(54), R.WHITE, "rm")

    def label(self, d, y, text, T=99):
        R.txt(d, (1026, y), text, R.font(36), R.CYAN, "rm")
        d.line([(60, y + 30), (1020, y + 30)], fill=(40, 60, 120), width=3)

    def put_row(self, img, row, x, y, t0, T, slide=True):
        if T < t0: return
        k = R.e_out((T - t0) / 0.35)
        dx = int((1 - k) * (-300)) if slide else 0
        img.paste(with_alpha(row, k), (x + dx, y), with_alpha(row, k))

    def frame(self, t):
        H = self.H
        stat = self.mode != "video"
        img = self.bg.copy()
        off = (0, 0) if stat else (int(t * 14) % 60, int(t * 9) % 60)
        img.alpha_composite(self.grid, (-off[0], -off[1]))
        d = ImageDraw.Draw(img)
        T = 99 if stat else t
        if self.mode == "feed":
            self.header(img, d, T, 40)
            self.label(d, 205, "نتائج الجولة")
            for i, row in enumerate(self.res_rows):
                img.paste(row, (60, 252 + i * 60), row)
            self.label(d, 808, "الترتيب بعد الجولة")
            for i, row in enumerate(self.tab_rows):
                col, rr = divmod(i, 9)
                img.paste(row, (45 + col * 495, 858 + rr * 44), row)
            R.txt(d, (400, H - 26), R.PAGE_AR, R.font(28, False), R.MUTE)
            R.txt(d, (640, H - 26), R.HANDLE, R.font(28, False), R.MUTE, ltr=True)
            return img.convert("RGB")
        self.header(img, d, T, 130)
        sw = 7.6  # Wechsel von Ergebnissen zu Tabelle
        if stat or T < sw + 0.3:
            self.label(d, 330, "نتائج الجولة")
            fade = 1.0 if stat else 1 - R.clamp((T - sw) / 0.3)
            for i, row in enumerate(self.res_rows):
                y = 390 + i * 112
                if stat: img.paste(row, (60, y), row)
                else:
                    r2 = with_alpha(row, fade)
                    self.put_row(img, r2, 60, y, 0.8 + 0.45 * i, T)
        if stat:
            pass
        elif T >= sw:
            self.label(d, 330, "الترتيب بعد الجولة")
            for i, row in enumerate(self.tab_rows):
                self.put_row(img, row, 60, 390 + i * 62, sw + 0.3 + 0.18 * i, T)
        if self.mode == "video":
            prog = R.clamp(t / self.D)
            d.rectangle((0, 0, int(W * prog), 10), fill=R.CYAN)
            y = 1560
            for pim, s, e in self.secs:
                if s <= t < e:
                    k = R.e_out((t - s) / 0.4)
                    pw = pim.width; rw = int(pw * k)
                    if rw > 1:
                        crop = pim.crop((pw - rw, 0, pw, pim.height))
                        img.paste(crop, (60 + pw - rw, y), crop)
                    break
        else:  # cover
            title = self.cfg["title"]
            pim = R.Scene.panel_img(None, title, False)[0]
            img.paste(pim, (60, 1560), pim)
        d.line([(300, 1840 - 20), (780, 1840 - 20)], fill=(40, 60, 120), width=3)
        R.txt(d, (540, 1850), R.PAGE_AR, R.font(34), R.WHITE)
        R.txt(d, (540, 1890), R.HANDLE, R.font(26, False), R.MUTE, ltr=True)
        return img.convert("RGB")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--kind", required=True, choices=["feed", "cover", "reel", "story"])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cfg = json.load(open(a.data, encoding="utf-8"))
    if a.kind in ("feed", "cover"):
        H = 1350 if a.kind == "feed" else 1920
        im = Roundup(cfg, H, a.kind).frame(99)
        if a.out.lower().endswith((".jpg", ".jpeg")): im.save(a.out, quality=92)
        else: im.save(a.out)
        print(a.out, im.size); return
    secs, t0 = [], 0.5
    for s in cfg["sections"]:
        secs.append(dict(text=s, cta=False, start=t0, end=t0 + 3.0)); t0 += 3.0
    D = max(12.0, t0)
    if a.kind == "story" and cfg.get("cta"):
        secs.append(dict(text=cfg["cta"], cta=True, start=D, end=D + 4.5)); D += 4.5
    secs[-1]["end"] = D
    sc = Roundup(cfg, 1920, "video", secs, D)
    music, start = R.pick_music(D)
    nfr = int(round(D * R.FPS))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x1920", "-r", str(R.FPS), "-i", "-",
           "-ss", str(start), "-t", str(D), "-i", music,
           "-vf", "format=yuv420p", "-af", f"afade=t=in:st=0:d=1,afade=t=out:st={D-2}:d=2",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-c:a", "aac", "-b:a", "160k", "-t", str(D),
           "-movflags", "+faststart", a.out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(nfr):
        p.stdin.write(sc.frame(i / R.FPS).tobytes())
    p.stdin.close(); p.wait()
    print(f"{a.out} D={D}s Track={os.path.basename(music)} Start={start}s")

if __name__ == "__main__":
    main()
