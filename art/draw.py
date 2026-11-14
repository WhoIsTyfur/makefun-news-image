"""Draw the entry: the world's news of Friday 13 November 2026, in one 1024x1024 image.

Build-time only (needs Pillow):   python art/draw.py [out.png]
Writes entry.png at the repo root by default; main.py copies that file at run time.
Every story is sourced in research/sources-2026-11-13.md.
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 2                       # supersample: draw at 2048 px, shrink to 1024
W = H = 1024
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = "C:/Windows/Fonts/"

PAPER = (244, 240, 230)
INK = (18, 20, 26)
RED = (204, 28, 36)
NAVY = (22, 30, 52)
WHITE = (255, 255, 255)
GREY = (110, 114, 124)
STEEL = (196, 202, 210)
GOLD = (232, 176, 40)


def F(name, px):
    return ImageFont.truetype(FONTS + name, int(round(px * S)))


def sc(*v):
    return [int(round(x * S)) for x in v]


class Canvas:
    def __init__(self):
        self.im = Image.new("RGB", (W * S, H * S), PAPER)
        self.d = ImageDraw.Draw(self.im)

    # ---- primitives in 1024-space -------------------------------------------------
    def rect(self, x0, y0, x1, y1, fill=None, outline=None, width=0, r=0):
        if r:
            self.d.rounded_rectangle(sc(x0, y0, x1, y1), radius=r * S, fill=fill,
                                     outline=outline, width=int(width * S))
        else:
            self.d.rectangle(sc(x0, y0, x1, y1), fill=fill, outline=outline,
                             width=int(width * S))

    def poly(self, pts, fill=None, outline=None, width=0):
        p = [(x * S, y * S) for x, y in pts]
        self.d.polygon(p, fill=fill)
        if outline:
            self.d.line(p + [p[0]], fill=outline, width=int(width * S), joint="curve")

    def line(self, pts, fill, width):
        self.d.line([(x * S, y * S) for x, y in pts], fill=fill, width=int(width * S),
                    joint="curve")

    def ellipse(self, x0, y0, x1, y1, fill=None, outline=None, width=0):
        self.d.ellipse(sc(x0, y0, x1, y1), fill=fill, outline=outline, width=int(width * S))

    def circle(self, cx, cy, r, **kw):
        self.ellipse(cx - r, cy - r, cx + r, cy + r, **kw)

    def text(self, x, y, s, font, fill, anchor="la"):
        self.d.text((x * S, y * S), s, font=font, fill=fill, anchor=anchor)

    def tw(self, s, font):
        b = self.d.textbbox((0, 0), s, font=font)
        return (b[2] - b[0]) / S

    def fit(self, s, name, px, maxw, minpx=10):
        while px > minpx and self.tw(s, F(name, px)) > maxw:
            px -= 0.5
        return F(name, px)

    def vgrad(self, x0, y0, x1, y1, top, bot):
        h = int((y1 - y0) * S)
        for i in range(h):
            t = i / max(1, h - 1)
            c = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
            self.d.line([(x0 * S, y0 * S + i), (x1 * S - 1, y0 * S + i)], fill=c)

    def clip(self, x0, y0, x1, y1):
        """Return a sub-canvas drawn separately and pasted back (for clipping scenes)."""
        return Sub(self, x0, y0, x1, y1)


class Sub(Canvas):
    def __init__(self, parent, x0, y0, x1, y1):
        self.parent, self.box = parent, (x0, y0, x1, y1)
        self.im = Image.new("RGB", (int((x1 - x0) * S), int((y1 - y0) * S)), PAPER)
        self.d = ImageDraw.Draw(self.im)
        self.w, self.h = x1 - x0, y1 - y0

    def done(self):
        x0, y0 = self.box[:2]
        self.parent.im.paste(self.im, (int(x0 * S), int(y0 * S)))


# ---- scene painters: each draws inside a Sub of size (w, h) -----------------------

def plane(c, x, y, k, col, nose_right=True):
    """Side-view airliner, length 100*k, at fuselage center (x, y)."""
    s = 1 if nose_right else -1
    L = 100 * k
    c.rect(x - L / 2, y - 7 * k, x + L / 2 - 8 * k, y + 7 * k, fill=col, r=7 * k)
    c.poly([(x + s * (L / 2 - 14 * k), y - 7 * k), (x + s * (L / 2 + 2 * k), y - 1 * k),
            (x + s * (L / 2 + 2 * k), y + 2 * k), (x + s * (L / 2 - 14 * k), y + 7 * k)], fill=col)
    c.poly([(x - s * (L / 2 - 6 * k), y - 6 * k), (x - s * (L / 2 + 2 * k), y - 26 * k),
            (x - s * (L / 2 - 10 * k), y - 26 * k), (x - s * (L / 2 - 22 * k), y - 6 * k)], fill=col)
    c.poly([(x - s * 6 * k, y + 2 * k), (x - s * 26 * k, y + 14 * k), (x - s * 8 * k, y + 14 * k),
            (x + s * 14 * k, y + 2 * k)], fill=tuple(max(0, v - 40) for v in col))
    for i in range(9):
        c.circle(x + s * (L / 2 - 22 * k - i * 8 * k), y - 2 * k, 1.6 * k, fill=(60, 80, 110))
    c.line([(x + s * (L / 2 - 20 * k), y + 7 * k), (x + s * (L / 2 - 20 * k), y + 13 * k)], INK, 1.5 * k)
    c.line([(x - s * 4 * k, y + 7 * k), (x - s * 4 * k), y + 13 * k], INK, 1.5 * k) if False else None
    c.circle(x + s * (L / 2 - 20 * k), y + 14 * k, 2.5 * k, fill=INK)
    c.circle(x - s * 4 * k, y + 14 * k, 2.5 * k, fill=INK)
    c.circle(x - s * 10 * k, y + 14 * k, 2.5 * k, fill=INK)


def scene_faa(c):
    w, h = c.w, c.h
    c.vgrad(0, 0, w, h * 0.62, (18, 28, 58), (64, 82, 124))
    c.rect(0, h * 0.62, w, h, fill=(70, 74, 82))
    c.rect(0, h * 0.62, w, h * 0.64, fill=(150, 150, 150))
    for i in range(12):
        c.rect(20 + i * 60, h * 0.83, 50 + i * 60, h * 0.845, fill=(230, 210, 90))
    # control tower with broken signal
    tx = w * 0.10
    c.rect(tx - 9, h * 0.30, tx + 9, h * 0.63, fill=(200, 204, 212))
    c.poly([(tx - 30, h * 0.24), (tx + 30, h * 0.24), (tx + 22, h * 0.32), (tx - 22, h * 0.32)],
           fill=(200, 204, 212))
    c.rect(tx - 24, h * 0.255, tx + 24, h * 0.30, fill=(110, 170, 210))
    c.rect(tx - 2, h * 0.14, tx + 2, h * 0.24, fill=(200, 204, 212))
    for rr in (14, 26, 38):
        c.d.arc(sc(tx - rr, h * 0.14 - rr, tx + rr, h * 0.14 + rr), 200, 340,
                fill=(240, 200, 60), width=3 * S)
    c.line([(tx - 30, h * 0.10), (tx + 30, h * 0.22)], RED, 7)
    c.line([(tx + 30, h * 0.10), (tx - 30, h * 0.22)], RED, 7)
    # parked planes, queue on the taxiway
    for i, (px, py, k) in enumerate([(w * 0.30, h * 0.70, 1.15), (w * 0.52, h * 0.76, 1.25),
                                      (w * 0.30, h * 0.90, 1.35)]):
        plane(c, px, py, k, (236, 238, 242))
    # departures board
    k = min(1.0, w / 600)
    bx0, by0, bx1 = w * 0.50, h * 0.05, w * 0.97
    rows = [("NEW YORK", "CANCELLED"), ("CHICAGO", "CANCELLED"), ("ATLANTA", "CANCELLED"),
            ("DALLAS", "CANCELLED"), ("DENVER", "CANCELLED"), ("LOS ANGELES", "CANCELLED")]
    nrow = max(3, min(6, int((h * 0.92 - 42) // 25)))
    rows = rows[:nrow]
    rh = min(27, (h * 0.90 - 42) / nrow)
    c.rect(bx0, by0, bx1, by0 + 34 + rh * len(rows) + 8, fill=(14, 16, 20), outline=(90, 90, 90),
           width=2, r=4)
    fh = F("arialbd.ttf", 17 * k)
    c.text(bx0 + 10, by0 + 8, "DEPARTURES", fh, (250, 200, 40))
    c.text(bx1 - 10, by0 + 8, "16:05 ET", fh, (250, 200, 40), anchor="ra")
    fr = F("bahnschrift.ttf", 17 * k)
    for i, (city, st) in enumerate(rows):
        y = by0 + 36 + i * rh
        c.text(bx0 + 10, y, city, fr, (235, 235, 235))
        c.rect(bx1 - 122 * k, y - 2, bx1 - 8, y + 20 * k, fill=RED)
        c.text(bx1 - 4 - 61 * k, y + 9 * k, st, F("arialbd.ttf", 15 * k), WHITE, anchor="mm")
    # STOP sign
    cx, cy, r = w * 0.40, h * 0.30, min(52, h * 0.19)
    oct_pts = [(cx + r * math.cos(math.radians(22.5 + 45 * i)), cy + r * math.sin(math.radians(22.5 + 45 * i)))
               for i in range(8)]
    c.poly(oct_pts, fill=WHITE)
    r2 = r - 5
    c.poly([(cx + r2 * math.cos(math.radians(22.5 + 45 * i)), cy + r2 * math.sin(math.radians(22.5 + 45 * i)))
            for i in range(8)], fill=RED)
    c.text(cx, cy, "STOP", F("arialbd.ttf", r * 0.52), WHITE, anchor="mm")
    c.rect(cx - 3, cy + r, cx + 3, h * 0.64, fill=(170, 170, 170))


def scene_iran(c):
    w, h = c.w, c.h
    c.vgrad(0, 0, w, h * 0.7, (238, 196, 140), (250, 226, 180))
    c.rect(0, h * 0.7, w, h, fill=(214, 176, 120))
    c.poly([(0, h * 0.7), (w * 0.25, h * 0.6), (w * 0.5, h * 0.7)], fill=(200, 160, 110))
    # radar: dome + dish
    rx, ry = w * 0.24, h * 0.92
    c.rect(rx - 6, ry - 60, rx + 6, ry, fill=(120, 120, 128))
    c.poly([(rx - 30, ry), (rx + 30, ry), (rx + 18, ry - 20), (rx - 18, ry - 20)], fill=(150, 150, 158))
    c.d.chord(sc(rx - 46, ry - 112, rx + 46, ry - 20), 200, 380, fill=(236, 238, 242), outline=(90, 90, 98),
              width=2 * S)
    c.line([(rx, ry - 64), (rx + 26, ry - 96)], (90, 90, 98), 3)
    c.circle(rx + 27, ry - 97, 4, fill=RED)
    # incoming drones from the right (shot down, per US)
    for (dx, dy) in [(w * 0.62, h * 0.24), (w * 0.84, h * 0.14)]:
        c.poly([(dx - 22, dy), (dx + 14, dy - 8), (dx + 14, dy + 8)], fill=(60, 64, 72))
        c.poly([(dx - 4, dy - 2), (dx + 6, dy - 22), (dx + 12, dy - 22), (dx + 8, dy)], fill=(60, 64, 72))
        c.poly([(dx - 4, dy + 2), (dx + 6, dy + 22), (dx + 12, dy + 22), (dx + 8, dy)], fill=(60, 64, 72))
        for k in range(1, 5):
            c.line([(dx + 16 + k * 10, dy), (dx + 22 + k * 10, dy)], (120, 100, 80), 2)
    # claim / denial tags
    c.rect(w * 0.50, h * 0.50, w * 0.98, h * 0.66, fill=(20, 110, 60), r=4)
    c.text(w * 0.74, h * 0.58, "IRAN: \u201cDESTROYED\u201d", c.fit("IRAN: DESTROYED   ", "arialbd.ttf", 15, w * 0.44), WHITE, anchor="mm")
    c.rect(w * 0.50, h * 0.72, w * 0.98, h * 0.88, fill=NAVY, r=4)
    c.text(w * 0.74, h * 0.80, "US: DRONES SHOT DOWN", c.fit("US: DRONES SHOT DOWN", "arialbd.ttf", 15, w * 0.44), WHITE, anchor="mm")


def scene_starship(c):
    w, h = c.w, c.h
    c.vgrad(0, 0, w, h, (8, 10, 30), (40, 60, 120))
    rnd = random.Random(15)
    for _ in range(60):
        c.circle(rnd.uniform(0, w), rnd.uniform(0, h * 0.7), rnd.uniform(0.6, 1.6), fill=(230, 230, 255))
    # earth limb
    c.ellipse(-w * 0.3, h * 0.80, w * 1.3, h * 2.0, fill=(40, 110, 190))
    c.ellipse(-w * 0.3, h * 0.80, w * 1.3, h * 2.0, outline=(140, 200, 255), width=3)
    # launch tower with chopsticks at left
    c.rect(w * 0.12, h * 0.30, w * 0.18, h, fill=(70, 72, 80))
    for yy in range(int(h * 0.32), int(h), 14):
        c.line([(w * 0.12, yy), (w * 0.18, yy + 12)], (110, 112, 120), 1.5)
    c.rect(w * 0.18, h * 0.42, w * 0.33, h * 0.45, fill=(90, 92, 100))
    c.rect(w * 0.18, h * 0.50, w * 0.33, h * 0.53, fill=(90, 92, 100))
    # rocket, tilted, climbing
    cx, cy = w * 0.60, h * 0.42
    ang = math.radians(12)

    def R(x, y):
        return (cx + x * math.cos(ang) - y * math.sin(ang), cy + x * math.sin(ang) + y * math.cos(ang))
    body = [R(-11, -78), R(11, -78), R(11, 60), R(-11, 60)]
    c.poly(body, fill=(214, 218, 226))
    c.poly([R(-11, -78), R(0, -100), R(11, -78)], fill=(214, 218, 226))
    c.poly([R(-11, -70), R(-20, -52), R(-11, -50)], fill=(160, 166, 176))
    c.poly([R(11, -70), R(20, -52), R(11, -50)], fill=(160, 166, 176))
    c.poly([R(-11, 30), R(-21, 58), R(-11, 58)], fill=(160, 166, 176))
    c.poly([R(11, 30), R(21, 58), R(11, 58)], fill=(160, 166, 176))
    c.line([R(-11, -6), R(11, -6)], (130, 136, 146), 1.5)
    # flame
    c.poly([R(-10, 60), R(10, 60), R(0, 130)], fill=(255, 150, 40))
    c.poly([R(-6, 60), R(6, 60), R(0, 100)], fill=(255, 240, 170))
    # orbit arc label
    c.d.arc(sc(w * 0.30, h * 0.06, w * 1.10, h * 0.90), 200, 290, fill=(255, 210, 90), width=2 * S)
    c.text(w * 0.96, h * 0.08, "ORBIT", F("arialbd.ttf", 15), (255, 210, 90), anchor="ra")


def scene_nola(c):
    w, h = c.w, c.h
    c.vgrad(0, 0, w, h * 0.55, (170, 200, 225), (215, 228, 238))
    c.rect(0, h * 0.55, w, h, fill=(110, 100, 72))
    for i in range(6):
        c.line([(10 + i * 50, h * 0.68 + (i % 2) * 18), (40 + i * 50, h * 0.68 + (i % 2) * 18)],
               (140, 130, 100), 2)
    # dock
    c.rect(0, h * 0.48, w * 0.22, h * 0.58, fill=(120, 110, 100))
    # capsized cruise ship: white decks tilted ~60 deg, half submerged
    cx, cy = w * 0.42, h * 0.62
    ang = math.radians(-62)

    def R(x, y):
        return (cx + x * math.cos(ang) - y * math.sin(ang), cy + x * math.sin(ang) + y * math.cos(ang))
    c.poly([R(-70, 0), R(70, 0), R(60, 26), R(-62, 26)], fill=(245, 245, 245), outline=(80, 80, 80), width=1.5)
    c.poly([R(-60, -22), R(55, -22), R(55, 0), R(-60, 0)], fill=(250, 250, 250), outline=(80, 80, 80), width=1.5)
    c.poly([R(-46, -40), R(40, -40), R(40, -22), R(-46, -22)], fill=(250, 250, 250), outline=(80, 80, 80), width=1.5)
    for i in range(8):
        c.poly([R(-52 + i * 13, -15), R(-44 + i * 13, -15), R(-44 + i * 13, -6), R(-52 + i * 13, -6)],
               fill=(70, 110, 150))
    c.rect(0, h * 0.68, w, h, fill=(110, 100, 72))   # water covers the low side
    for i in range(5):
        c.line([(w * 0.2 + i * 22, h * 0.70), (w * 0.24 + i * 22, h * 0.70)], (150, 140, 110), 2)
    # tanker bow coming in from right
    c.poly([(w * 0.62, h * 0.70), (w * 1.02, h * 0.70), (w * 1.02, h * 0.38), (w * 0.72, h * 0.38),
            (w * 0.64, h * 0.46)], fill=(150, 36, 36))
    c.rect(w * 0.70, h * 0.36, w * 1.02, h * 0.40, fill=(60, 60, 60))
    c.rect(w * 0.88, h * 0.18, w * 0.98, h * 0.36, fill=(235, 235, 235))
    # rescue boat
    c.poly([(w * 0.06, h * 0.82), (w * 0.24, h * 0.82), (w * 0.21, h * 0.88), (w * 0.08, h * 0.88)],
           fill=(240, 120, 30))


def scene_pope(c):
    w, h = c.w, c.h
    c.vgrad(0, 0, w, h * 0.5, (120, 180, 230), (200, 225, 245))
    c.rect(0, h * 0.5, w, h, fill=(196, 168, 120))
    # stage + canopy
    c.rect(w * 0.30, h * 0.30, w * 0.70, h * 0.52, fill=(250, 250, 250))
    c.poly([(w * 0.26, h * 0.30), (w * 0.74, h * 0.30), (w * 0.50, h * 0.12)], fill=(250, 220, 120))
    # Peru flags
    for fx in (w * 0.12, w * 0.86):
        c.rect(fx, h * 0.10, fx + 2, h * 0.52, fill=(90, 90, 90))
        c.rect(fx + 2, h * 0.10, fx + 14, h * 0.24, fill=(210, 16, 34))
        c.rect(fx + 14, h * 0.10, fx + 26, h * 0.24, fill=WHITE)
        c.rect(fx + 26, h * 0.10, fx + 38, h * 0.24, fill=(210, 16, 34))
    # the pope: white figure, arms raised
    px, py = w * 0.50, h * 0.36
    c.poly([(px - 13, py + 2), (px + 13, py + 2), (px + 17, py + 34), (px - 17, py + 34)], fill=WHITE,
           outline=(170, 170, 170), width=1)
    c.circle(px, py - 6, 8, fill=(236, 200, 170))
    c.d.pieslice(sc(px - 8, py - 15, px + 8, py - 3), 180, 360, fill=WHITE)
    c.line([(px - 12, py + 6), (px - 24, py - 12)], WHITE, 5)
    c.line([(px + 12, py + 6), (px + 24, py - 12)], WHITE, 5)
    # crowd of heads
    rnd = random.Random(500)
    for row in range(10):
        y = h * 0.56 + row * h * 0.048
        n = 18 + row * 3
        for i in range(n):
            x = (i + rnd.uniform(-0.3, 0.3)) * w / (n - 1)
            col = rnd.choice([(60, 40, 30), (40, 30, 26), (90, 60, 40), (210, 16, 34), (250, 250, 250),
                              (240, 200, 60)])
            c.circle(x, y + rnd.uniform(-3, 3), 3.2 + row * 0.35, fill=col)


def scene_nvidia(c):
    w, h = c.w, c.h
    c.rect(0, 0, w, h, fill=(16, 20, 24))
    for i in range(1, 6):
        c.line([(0, h * i / 6), (w, h * i / 6)], (40, 46, 52), 1)
    # $4T threshold
    yT = h * 0.40
    for x in range(0, int(w), 14):
        c.line([(x, yT), (x + 8, yT)], (240, 200, 60), 2)
    c.text(w * 0.03, yT - 20, "$4 TRILLION", F("arialbd.ttf", 14), (240, 200, 60))
    # falling line
    rnd = random.Random(4)
    pts, y = [], h * 0.14
    for i in range(16):
        x = w * 0.05 + i * w * 0.58 / 15
        y += rnd.uniform(-4, 14)
        pts.append((x, y))
    pts.append((w * 0.66, h * 0.50))
    c.line(pts, (230, 50, 50), 4)
    c.poly([(w * 0.66, h * 0.58), (w * 0.62, h * 0.46), (w * 0.71, h * 0.47)], fill=(230, 50, 50))
    # chip icon
    gx, gy, g = w * 0.81, h * 0.64, 34
    c.rect(gx - g, gy - g, gx + g, gy + g, fill=(118, 185, 0), r=5)
    c.rect(gx - g + 10, gy - g + 10, gx + g - 10, gy + g - 10, fill=(30, 34, 38), r=3)
    for i in range(5):
        o = -g + 8 + i * (2 * g - 16) / 4
        for a, b in (((gx + o, gy - g - 9), (gx + o, gy - g)), ((gx + o, gy + g), (gx + o, gy + g + 9)),
                     ((gx - g - 9, gy + o), (gx - g, gy + o)), ((gx + g, gy + o), (gx + g + 9, gy + o))):
            c.line([a, b], (118, 185, 0), 3)
    c.text(gx, gy, "NVDA", F("arialbd.ttf", 13), (118, 185, 0), anchor="mm")


def scene_ukraine(c):
    w, h = c.w, c.h
    c.vgrad(0, 0, w, h, (60, 64, 80), (150, 140, 130))
    # smoke
    for i, r in enumerate([30, 38, 46, 40]):
        c.circle(w * 0.55 + i * 14, h * 0.48 - i * 22, r, fill=(90 + i * 8, 90 + i * 8, 96 + i * 8))
    c.circle(w * 0.52, h * 0.66, 22, fill=(255, 140, 40))
    c.circle(w * 0.52, h * 0.66, 12, fill=(255, 230, 140))
    # skyline
    rnd = random.Random(7)
    x = 0
    while x < w:
        bw = rnd.uniform(26, 50)
        bh = rnd.uniform(h * 0.18, h * 0.42)
        c.rect(x, h - bh, x + bw - 3, h, fill=(36, 38, 46))
        for wy in range(int(h - bh + 8), int(h - 6), 12):
            for wx in range(int(x + 5), int(x + bw - 8), 10):
                if rnd.random() < 0.35:
                    c.rect(wx, wy, wx + 4, wy + 5, fill=(240, 210, 120))
        x += bw
    # Ukraine flag
    c.rect(w * 0.74, h * 0.08, w * 0.94, h * 0.17, fill=(0, 87, 183))
    c.rect(w * 0.74, h * 0.17, w * 0.94, h * 0.26, fill=(255, 215, 0))
    # drone/missile streak
    c.line([(w * 0.30, h * 0.04), (w * 0.62, h * 0.40)], (250, 220, 200), 3)
    c.circle(w * 0.62, h * 0.40, 5, fill=(255, 120, 40))


def scene_assam(c):
    w, h = c.w, c.h
    c.vgrad(0, 0, w, h * 0.5, (150, 200, 235), (220, 236, 245))
    c.ellipse(-w * 0.2, h * 0.30, w * 0.6, h * 0.8, fill=(70, 140, 70))
    c.ellipse(w * 0.4, h * 0.25, w * 1.3, h * 0.8, fill=(56, 120, 60))
    c.rect(0, h * 0.58, w, h, fill=(80, 150, 80))
    c.poly([(0, h * 0.70), (w, h * 0.66), (w, h * 0.92), (0, h * 0.96)], fill=(70, 70, 76))
    # bus (left, yellow) into truck (right) -- head-on
    c.rect(w * 0.06, h * 0.50, w * 0.48, h * 0.76, fill=(240, 190, 30), r=6)
    for i in range(5):
        c.rect(w * 0.09 + i * w * 0.07, h * 0.54, w * 0.14 + i * w * 0.07, h * 0.62, fill=(120, 170, 210))
    c.circle(w * 0.14, h * 0.77, 9, fill=INK)
    c.circle(w * 0.40, h * 0.77, 9, fill=INK)
    c.rect(w * 0.56, h * 0.40, w * 0.96, h * 0.74, fill=(60, 110, 170))
    c.rect(w * 0.50, h * 0.50, w * 0.60, h * 0.74, fill=(200, 60, 50), r=4)
    c.circle(w * 0.62, h * 0.76, 9, fill=INK)
    c.circle(w * 0.88, h * 0.76, 9, fill=INK)
    # impact burst
    cx, cy = w * 0.49, h * 0.60
    pts = []
    for i in range(16):
        r = 26 if i % 2 == 0 else 12
        a = math.radians(i * 22.5)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    c.poly(pts, fill=(255, 220, 60), outline=(230, 80, 30), width=2)


def scene_gaza(c):
    w, h = c.w, c.h
    c.vgrad(0, 0, w, h * 0.6, (150, 160, 175), (200, 200, 200))
    c.rect(0, h * 0.62, w, h, fill=(196, 186, 160))
    # hospital
    c.rect(w * 0.50, h * 0.22, w * 0.95, h * 0.64, fill=(232, 228, 220))
    for r in range(3):
        for i in range(5):
            c.rect(w * 0.53 + i * w * 0.08, h * 0.30 + r * h * 0.11, w * 0.58 + i * w * 0.08,
                   h * 0.36 + r * h * 0.11, fill=(90, 100, 110))
    c.rect(w * 0.68, h * 0.06, w * 0.77, h * 0.22, fill=WHITE)
    c.d.arc(sc(w * 0.693, h * 0.09, w * 0.757, h * 0.19), 60, 300, fill=RED, width=5 * S)
    # damage + smoke
    c.poly([(w * 0.86, h * 0.22), (w * 0.95, h * 0.22), (w * 0.95, h * 0.40), (w * 0.90, h * 0.30)],
           fill=(150, 160, 175))
    for i, r in enumerate([16, 22, 28]):
        c.circle(w * 0.91 - i * 6, h * 0.18 - i * 18, r, fill=(80 + i * 10, 80 + i * 10, 84 + i * 10))
    # tents
    for i, tx in enumerate([w * 0.04, w * 0.20, w * 0.34, w * 0.12, w * 0.28]):
        ty = h * (0.62 if i < 3 else 0.82)
        c.poly([(tx, ty + 30), (tx + 30, ty - 4), (tx + 60, ty + 30)],
               fill=[(236, 236, 230), (210, 220, 236), (236, 224, 200)][i % 3])
        c.poly([(tx + 24, ty + 30), (tx + 30, ty + 10), (tx + 36, ty + 30)], fill=(70, 70, 70))


def scene_guinea(c):
    w, h = c.w, c.h
    c.vgrad(0, 0, w, h * 0.45, (240, 200, 120), (250, 228, 170))
    c.rect(0, h * 0.45, w, h, fill=(170, 96, 50))
    c.ellipse(w * 0.15, h * 0.52, w * 0.85, h * 1.05, fill=(120, 64, 36))
    # gold nuggets
    rnd = random.Random(10)
    for _ in range(9):
        x, y = rnd.uniform(w * 0.3, w * 0.7), rnd.uniform(h * 0.66, h * 0.85)
        r = rnd.uniform(5, 10)
        c.poly([(x - r, y), (x - r * 0.4, y - r), (x + r * 0.7, y - r * 0.8), (x + r, y + r * 0.2),
                (x, y + r * 0.8)], fill=GOLD, outline=(150, 100, 20), width=1)
    # pickaxe and shovel
    c.line([(w * 0.12, h * 0.85), (w * 0.30, h * 0.40)], (110, 70, 40), 5)
    c.d.arc(sc(w * 0.16, h * 0.30, w * 0.44, h * 0.58), 200, 330, fill=(90, 94, 100), width=6 * S)
    c.line([(w * 0.88, h * 0.86), (w * 0.76, h * 0.42)], (110, 70, 40), 5)
    c.poly([(w * 0.70, h * 0.32), (w * 0.80, h * 0.30), (w * 0.79, h * 0.44), (w * 0.74, h * 0.45)],
           fill=(90, 94, 100))
    # Guinea flag
    c.rect(w * 0.42, h * 0.20, w * 0.49, h * 0.38, fill=(206, 17, 38))
    c.rect(w * 0.49, h * 0.20, w * 0.56, h * 0.38, fill=(252, 209, 22))
    c.rect(w * 0.56, h * 0.20, w * 0.63, h * 0.38, fill=(0, 148, 96))


# ---- extra scenes ----------------------------------------------------------------

def scene_msft(c):
    w, h = c.w, c.h
    c.vgrad(0, 0, w, h, (200, 214, 232), (232, 238, 246))
    c.rect(0, h * 0.78, w, h, fill=(150, 120, 90))
    c.rect(w * 0.22, h * 0.18, w * 0.78, h * 0.70, fill=(40, 44, 52), r=6)
    c.rect(w * 0.25, h * 0.22, w * 0.75, h * 0.66, fill=(236, 240, 246))
    c.poly([(w * 0.14, h * 0.80), (w * 0.86, h * 0.80), (w * 0.78, h * 0.70), (w * 0.22, h * 0.70)],
           fill=(80, 86, 96))
    ex0, ey0, ex1, ey1 = w * 0.36, h * 0.30, w * 0.64, h * 0.56
    c.rect(ex0, ey0, ex1, ey1, fill=WHITE, outline=(60, 90, 160), width=2)
    c.line([(ex0, ey0), ((ex0 + ex1) / 2, (ey0 + ey1) / 2), (ex1, ey0)], (60, 90, 160), 2)
    c.circle(ex1, ey1, 17, fill=RED)
    c.line([(ex1 - 8, ey1 - 8), (ex1 + 8, ey1 + 8)], WHITE, 4)
    c.line([(ex1 + 8, ey1 - 8), (ex1 - 8, ey1 + 8)], WHITE, 4)


def scene_kyiv(c):
    w, h = c.w, c.h
    c.vgrad(0, 0, w, h, (30, 30, 46), (80, 70, 80))
    c.rect(w * 0.18, h * 0.30, w * 0.82, h * 0.86, fill=(200, 196, 188))
    for r in range(4):
        for i in range(6):
            fire = (r == 0 and i in (1, 2, 3)) or (r == 1 and i == 2)
            c.rect(w * 0.22 + i * w * 0.10, h * 0.36 + r * h * 0.12, w * 0.28 + i * w * 0.10,
                   h * 0.43 + r * h * 0.12, fill=(255, 150, 40) if fire else (70, 80, 96))
    c.rect(w * 0.46, h * 0.20, w * 0.54, h * 0.30, fill=WHITE)
    c.rect(w * 0.485, h * 0.215, w * 0.515, h * 0.285, fill=RED)
    c.rect(w * 0.47, h * 0.235, w * 0.53, h * 0.265, fill=RED)
    for x, y, r in [(0.36, 0.22, 20), (0.44, 0.12, 26), (0.30, 0.10, 18)]:
        c.circle(w * x, h * y, r, fill=(90, 86, 92))
    for x in (0.34, 0.42, 0.50):
        c.poly([(w * (x - 0.03), h * 0.36), (w * x, h * 0.26), (w * (x + 0.03), h * 0.36)], fill=(255, 190, 60))
    c.rect(w * 0.0, h * 0.80, w * 0.20, h * 0.94, fill=(200, 30, 30), r=3)
    c.d.arc(sc(w * 0.10, h * 0.30, w * 0.50, h * 1.10), 220, 300, fill=(150, 200, 255), width=3 * S)
    c.rect(0, h * 0.94, w, h, fill=(50, 50, 56))


# ---- layout ----------------------------------------------------------------------

REGION = {
    "UNITED STATES": (190, 30, 45), "AMERICAS": (190, 30, 45), "MIDDLE EAST": (214, 110, 20),
    "EUROPE": (30, 80, 170), "ASIA": (20, 130, 80), "AFRICA": (140, 80, 30), "SCIENCE": (110, 60, 160),
    "MARKETS": (0, 120, 130), "WORLDWIDE": (90, 90, 100), "SPORT": (40, 120, 40), "CULTURE": (170, 50, 120),
    "CLIMATE": (40, 130, 90),
}


def wrap(cv, s, font, maxw):
    lines, cur = [], ""
    for wd in s.split():
        t = (cur + " " + wd).strip()
        if cv.tw(t, font) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    lines.append(cur)
    return lines


def panel(cv, box, painter, num, region, head, sub, scene_frac=0.55, head_px=22, sub_px=13.5,
          hfont="arialbd.ttf"):
    x0, y0, x1, y1 = box
    sy1 = y0 + (y1 - y0) * scene_frac
    sub_c = cv.clip(x0, y0, x1, sy1)
    painter(sub_c)
    sub_c.done()
    cv.rect(x0, sy1, x1, y1, fill=WHITE)
    cv.rect(x0, y0, x1, y1, outline=(60, 60, 66), width=1.5)
    col = REGION[region]
    y = sy1 + 7
    cv.circle(x0 + 16, y + 9, 9.5, fill=col)
    cv.text(x0 + 16, y + 9.5, str(num), F("arialbd.ttf", 12), WHITE, anchor="mm")
    cv.text(x0 + 31, y + 9.5, region, F("arialbd.ttf", 12), col, anchor="lm")
    y += 22
    maxw = (x1 - x0) - 18
    fh = F(hfont, head_px)
    lines = wrap(cv, head, fh, maxw)
    while len(lines) > 2:
        head_px -= 1
        fh = F(hfont, head_px)
        lines = wrap(cv, head, fh, maxw)
    for ln in lines:
        cv.text(x0 + 9, y, ln, fh, INK)
        y += head_px * 1.13
    fs = F("arial.ttf", sub_px)
    for ln in wrap(cv, sub, fs, maxw)[:2]:
        cv.text(x0 + 9, y + 2, ln, fs, (70, 72, 80))
        y += sub_px * 1.22


def listing(cv, box, items, start, cols=3, px=13):
    x0, y0, x1, y1 = box
    title = "ALSO ON FRIDAY 13 NOVEMBER"
    ftl = F("arialbd.ttf", 15)
    cv.text(x0, y0, title, ftl, RED)
    cv.line([(x0 + cv.tw(title, ftl) + 10, y0 + 9), (x1, y0 + 9)], (180, 180, 180), 1)
    rows = math.ceil(len(items) / cols)
    cw = (x1 - x0) / cols
    rh = (y1 - y0 - 24) / rows
    for i, (region, txt) in enumerate(items):
        cx = x0 + (i // rows) * cw
        cy = y0 + 24 + (i % rows) * rh
        col = REGION[region]
        cv.circle(cx + 9, cy + 8, 8.5, fill=col)
        cv.text(cx + 9, cy + 8.5, str(start + i), F("arialbd.ttf", 10.5), WHITE, anchor="mm")
        f = cv.fit(txt, "arialbd.ttf", px, cw - 30, minpx=10.5)
        cv.text(cx + 22, cy + 1, txt, f, INK)


# ---- world locator map (rough hand-made outlines, lon/lat) ---------------------------

LAND = [
    [(-168, 66), (-140, 70), (-95, 72), (-80, 63), (-60, 55), (-53, 47), (-70, 43), (-76, 35), (-81, 25),
     (-90, 30), (-97, 26), (-97, 20), (-87, 21), (-83, 10), (-78, 8), (-90, 14), (-105, 20), (-112, 30),
     (-118, 34), (-124, 40), (-125, 48), (-135, 58), (-150, 60), (-165, 60)],
    [(-52, 60), (-42, 60), (-20, 70), (-20, 80), (-60, 82), (-70, 77), (-55, 68)],
    [(-78, 8), (-60, 10), (-50, 0), (-35, -6), (-40, -22), (-48, -27), (-58, -35), (-65, -42), (-68, -55),
     (-75, -50), (-72, -30), (-70, -18), (-81, -5), (-80, 2)],
    [(-10, 36), (-9, 43), (-2, 44), (-4, 48), (5, 53), (8, 57), (5, 62), (15, 69), (28, 71), (40, 67), (60, 68),
     (60, 45), (40, 42), (28, 41), (26, 38), (20, 40), (15, 38), (12, 44), (5, 43), (0, 39), (-5, 36)],
    [(-6, 50), (2, 51), (0, 54), (-3, 58), (-6, 57)],
    [(-10, 52), (-6, 52), (-6, 55), (-10, 54)],
    [(-17, 21), (-10, 30), (-6, 36), (10, 37), (20, 32), (32, 31), (35, 28), (43, 12), (51, 12), (40, -2),
     (40, -15), (35, -25), (27, -34), (18, -34), (12, -17), (13, -5), (9, 4), (-8, 5), (-17, 14)],
    [(28, 41), (36, 36), (35, 32), (43, 13), (52, 16), (58, 22), (56, 26), (62, 25), (67, 24), (73, 20), (77, 8),
     (80, 15), (88, 22), (92, 21), (98, 16), (100, 7), (104, 1), (106, 10), (109, 12), (108, 21), (117, 23),
     (122, 30), (121, 40), (127, 38), (129, 35), (130, 42), (140, 48), (142, 53), (135, 55), (150, 60),
     (162, 60), (180, 66), (180, 70), (140, 73), (110, 77), (80, 73), (60, 68), (60, 45), (40, 42)],
    [(130, 31), (141, 35), (142, 43), (140, 41), (135, 34)],
    [(95, 5), (106, -6), (115, -8), (120, -9), (125, -8), (118, -4), (110, -2), (100, 2)],
    [(110, 1), (118, 6), (119, 1), (116, -4), (110, -2)],
    [(131, -1), (150, -6), (147, -10), (138, -8)],
    [(114, -22), (122, -17), (130, -12), (137, -12), (142, -11), (146, -19), (153, -27), (150, -37), (141, -38),
     (131, -31), (115, -34)],
    [(44, -25), (50, -15), (49, -12), (43, -17)],
    [(172, -34), (178, -38), (174, -41), (167, -46), (171, -44)],
]


def world_map(cv, box, panels, items):
    x0, y0, x1, y1 = box
    lon0, lon1, lat0, lat1 = -170, 180, -50, 78
    cv.rect(x0, y0, x1, y1, fill=(222, 232, 242))

    def P(lon, lat):
        return (x0 + (lon - lon0) / (lon1 - lon0) * (x1 - x0), y1 - (lat - lat0) / (lat1 - lat0) * (y1 - y0))
    for poly in LAND:
        cv.poly([P(*p) for p in poly], fill=(190, 196, 204))
    for region, _txt, (lon, lat) in items:
        x, y = P(lon, lat)
        cv.circle(x, y, 3.4, fill=REGION[region], outline=WHITE, width=1)
    for i, (region, (lon, lat)) in enumerate(panels):
        if lon is None:
            continue
        x, y = P(lon, lat)
        cv.circle(x, y, 7.5, fill=REGION[region], outline=WHITE, width=1.2)
        cv.text(x, y + 0.5, str(i + 1), F("arialbd.ttf", 9.5), WHITE, anchor="mm")
    cv.rect(x0, y0, x1, y1, outline=(150, 150, 160), width=1)


def build(path, variant="map"):
    cv = Canvas()
    items = LIST_ITEMS if variant.startswith("list") else [it for it in LIST_ITEMS if it[1] not in MAP_DROPS]
    cv.text(10, 10, "THE WORLD'S NEWS IN ONE PICTURE", F("arialbd.ttf", 16), RED)
    cv.text(W - 10, 10, f"{10 + len(items)} STORIES · ALL REPORTED ON FRIDAY", F("arialbd.ttf", 14),
            GREY, anchor="ra")
    fd = cv.fit("FRIDAY 13 NOVEMBER 2026", "arialbd.ttf", 76, W - 20)
    cv.text(W / 2, 30, "FRIDAY 13 NOVEMBER 2026", fd, NAVY, anchor="ma")
    cv.rect(10, 112, W - 10, 115, fill=NAVY)

    m, g = 10, 8
    y0, y1 = 123, 393
    (f1, r1, h1, s1, _), (f2, r2, h2, s2, _) = ROW1[::-1] if variant.endswith("swap") else ROW1
    panel(cv, (m, y0, 612, y1), f1, 1, r1, h1, s1, scene_frac=0.57, head_px=27, sub_px=14)
    panel(cv, (612 + g, y0, W - m, y1), f2, 2, r2, h2, s2, scene_frac=0.57, head_px=21, sub_px=13.5)
    y0, y1 = 401, 617
    cw = (W - 2 * m - 3 * g) / 4
    for i, (fn, rg, hd, sb, _) in enumerate(ROW2):
        x0 = m + i * (cw + g)
        panel(cv, (x0, y0, x0 + cw, y1), fn, 3 + i, rg, hd, sb, scene_frac=0.50, head_px=18, sub_px=12.5)
    y0, y1 = 625, 829
    for i, (fn, rg, hd, sb, _) in enumerate(ROW3):
        x0 = m + i * (cw + g)
        panel(cv, (x0, y0, x0 + cw, y1), fn, 7 + i, rg, hd, sb, scene_frac=0.47, head_px=18, sub_px=12.5)
    flat = [(it[0], it[1]) for it in items]
    if variant.startswith("list"):
        listing(cv, (m, 837, W - m, 1003), flat, 11)
    else:
        cv.text(m, 837, "WHERE IT HAPPENED", F("arialbd.ttf", 15), RED)
        world_map(cv, (m, 857, 370, 1003), [(r[1], r[4]) for r in ROW1 + ROW2 + ROW3], items)
        listing(cv, (382, 837, W - m, 1003), flat, 11, cols=2)
    cv.text(W / 2, 1009, "Every story here was reported on Friday 13 November 2026. Sources: AP, Reuters, NPR, "
            "CNBC, Al Jazeera, BBC, Vatican News, Space.com", F("ariali.ttf", 10.5), GREY, anchor="ma")

    out = cv.im.resize((W, H), Image.LANCZOS)
    out.save(path, optimize=True)
    return path


# (painter, region, headline, one factual line, (lon, lat) for the map)
ROW1 = [
    (scene_faa, "UNITED STATES", "FAA halts all US departures after air-traffic telecom outage",
     "First nationwide ground stop since Jan 2023; nearly 5,000 flights cancelled", (-98, 39)),
    (scene_iran, "MIDDLE EAST", "Iran says it destroyed a US radar in Bahrain",
     "Revenge for a US strike in Sirik, says the IRGC. The US says it downed both drones.", (50.5, 26)),
]
ROW2 = [
    (scene_starship, "SCIENCE", "SpaceX's Starship Flight 15 reaches orbit",
     "Booster catch called off; the ship stays up for a 22-hour test", (-97.2, 26)),
    (scene_nola, "UNITED STATES", "Tanker hits docked cruise ship in New Orleans",
     "American Heritage capsizes; all aboard accounted for, 32 in hospital", (-90, 30)),
    (scene_pope, "AMERICAS", "Pope Leo XIV says Mass in Chiclayo, Peru",
     "About 500,000 gather in his former diocese", (-79.8, -6.8)),
    (scene_nvidia, "MARKETS", "Nvidia closes below $4 trillion",
     "First time since July 2025, a day after CEO Jensen Huang quit", (-122, 37.4)),
]
ROW3 = [
    (scene_kyiv, "EUROPE", "Russian drone sets a Kyiv hospital ablaze",
     "About 30 evacuated; strikes also kill 3 in Odesa and Zaporizhzhia", (30.5, 50.4)),
    (scene_msft, "WORLDWIDE", "Microsoft outage hits Outlook and Teams",
     "Second day of disruption in at least 74 countries", (None, None)),
    (scene_gaza, "MIDDLE EAST", "Gaza: strike on Nasser Hospital complex",
     "Six killed in Khan Younis, a surgeon among them", (34.3, 31.3)),
    (scene_assam, "ASIA", "Bus-truck crash in India's Assam kills 24",
     "Minibus hits a container truck near Kaziranga", (93.9, 26.6)),
]
LIST_ITEMS = [
    ("EUROPE", "EU picks five nations to join Ukraine peace talks", (-6.3, 53.3)),
    ("ASIA", "Trump, Xi and Putin to meet at APEC in China", (114, 22.5)),
    ("MIDDLE EAST", "Turkey and Qatar sign a mutual defence pact", (29, 41)),
    ("MIDDLE EAST", "Iran says an LNG tanker hit a mine in Hormuz", (56.5, 26.5)),
    ("MIDDLE EAST", "UN: over 340,000 now displaced in Yemen", (45, 15)),
    ("EUROPE", "Moscow car bomb wounds ex-aide of Ukraine ex-PM", (37.6, 55.7)),
    ("ASIA", "Japan's PM Takaichi to make first China visit, for APEC", (139.7, 35.7)),
    ("ASIA", "Pakistan army says 74 militants killed in raids", (70, 33)),
    ("ASIA", "North Korea changes its flag, first since 1948", (125.7, 39)),
    ("AFRICA", "Building collapses near Nairobi, killing 6", (36.8, -1.3)),
    ("AFRICA", "Nigeria ends Ebola watch with no new cases", (7.5, 9)),
    ("EUROPE", "Suspected drones over US airbase RAF Lakenheath", (0.5, 52.4)),
    ("MARKETS", "US producer prices up 6.5% in a year", (-77, 38.9)),
    ("UNITED STATES", "Lauren Boebert loses her Colorado House seat", (-105, 39)),
    ("SCIENCE", "Shuttle Endeavour put on show upright in LA", (-118.3, 34)),
    ("CULTURE", "U2 album out with Dolly Parton's last vocal", (-6.3, 53.3)),
    ("SPORT", "Pochettino named Manchester United manager", (-2.2, 53.5)),
    ("SPORT", "Baseball: Japan beat South Korea 9-5 in Tokyo", (139.7, 35.7)),
]
# the map variant has room for 16 list lines
MAP_DROPS = {"Japan's PM Takaichi to make first China visit, for APEC", "Iran says an LNG tanker hit a mine in Hormuz"}


# ---- v6: three-story top row, serif headlines ----------------------------------------

def flag_us(c, x0, y0, x1, y1):
    h = (y1 - y0) / 7
    for i in range(7):
        c.rect(x0, y0 + i * h, x1, y0 + (i + 1) * h, fill=(178, 34, 52) if i % 2 == 0 else WHITE)
    c.rect(x0, y0, x0 + (x1 - x0) * 0.42, y0 + h * 4, fill=(60, 59, 110))


def flag_cn(c, x0, y0, x1, y1):
    c.rect(x0, y0, x1, y1, fill=(222, 41, 16))
    cx, cy, r = x0 + (x1 - x0) * 0.22, y0 + (y1 - y0) * 0.32, (y1 - y0) * 0.2
    c.poly([(cx + (r if i % 2 == 0 else r * 0.4) * math.cos(math.radians(-90 + i * 36)),
             cy + (r if i % 2 == 0 else r * 0.4) * math.sin(math.radians(-90 + i * 36))) for i in range(10)],
           fill=(255, 222, 0))


def flag_ru(c, x0, y0, x1, y1):
    h = (y1 - y0) / 3
    for i, col in enumerate([WHITE, (0, 57, 166), (213, 43, 30)]):
        c.rect(x0, y0 + i * h, x1, y0 + (i + 1) * h, fill=col)
    c.rect(x0, y0, x1, y1, outline=(160, 160, 160), width=1)


def scene_apec(c):
    w, h = c.w, c.h
    c.vgrad(0, 0, w, h, (246, 236, 214), (232, 214, 182))
    # round table seen from the front
    c.ellipse(w * 0.14, h * 0.56, w * 0.86, h * 0.84, fill=(150, 100, 60))
    c.ellipse(w * 0.14, h * 0.52, w * 0.86, h * 0.79, fill=(186, 130, 80))
    # three flags on stands
    fw, fh = w * 0.22, h * 0.24
    for i, (fn, label) in enumerate([(flag_us, "TRUMP"), (flag_cn, "XI"), (flag_ru, "PUTIN")]):
        cx = w * (0.22 + i * 0.28)
        top = h * (0.20 if i == 1 else 0.28)
        c.rect(cx - 1.5, top, cx + 1.5, h * 0.62, fill=(90, 90, 90))
        fn(c, cx - fw / 2, top, cx + fw / 2, top + fh)
        c.text(cx, top - 4, label, F("arialbd.ttf", 13), INK, anchor="md")
    c.text(w / 2, h * 0.925, "APEC · SHENZHEN · NEXT WEEK", F("arialbd.ttf", 12), (90, 60, 30), anchor="mm")


def scene_eu(c):
    w, h = c.w, c.h
    c.rect(0, 0, w, h, fill=(0, 51, 153))
    cx, cy, r = w * 0.50, h * 0.40, min(w, h) * 0.26
    for i in range(12):
        a = math.radians(i * 30)
        x, y, s = cx + r * math.cos(a), cy + r * math.sin(a), 6
        c.poly([(x + (s if k % 2 == 0 else s * 0.4) * math.cos(math.radians(-90 + k * 36)),
                 y + (s if k % 2 == 0 else s * 0.4) * math.sin(math.radians(-90 + k * 36))) for k in range(10)],
               fill=(255, 204, 0))
    c.text(cx, cy, "5", F("georgiab.ttf", 30), WHITE, anchor="mm")
    # five national flags along the bottom
    fw, fh, gap = w * 0.15, h * 0.16, w * 0.03
    x = (w - 5 * fw - 4 * gap) / 2
    y = h * 0.78
    def uk(c, a, b, cc, d):
        c.rect(a, b, cc, d, fill=(1, 33, 105))
        c.line([(a, b), (cc, d)], WHITE, 3)
        c.line([(a, d), (cc, b)], WHITE, 3)
        c.rect((a + cc) / 2 - 2.5, b, (a + cc) / 2 + 2.5, d, fill=(200, 16, 46))
        c.rect(a, (b + d) / 2 - 2, cc, (b + d) / 2 + 2, fill=(200, 16, 46))
    def vert(cols):
        def f(c, a, b, cc, d):
            ww = (cc - a) / 3
            for k, col in enumerate(cols):
                c.rect(a + k * ww, b, a + (k + 1) * ww, d, fill=col)
        return f
    def horiz(cols):
        def f(c, a, b, cc, d):
            hh = (d - b) / len(cols)
            for k, col in enumerate(cols):
                c.rect(a, b + k * hh, cc, b + (k + 1) * hh, fill=col)
        return f
    flags = [uk, vert([(0, 35, 149), WHITE, (237, 41, 57)]), horiz([(0, 0, 0), (221, 0, 0), (255, 206, 0)]),
             vert([(0, 146, 70), WHITE, (206, 43, 55)]), horiz([WHITE, (220, 20, 60)])]
    for fn in flags:
        fn(c, x, y, x + fw, y + fh)
        c.rect(x, y, x + fw, y + fh, outline=(200, 200, 200), width=1)
        x += fw + gap


def build_v6(path, list_items=None):
    items = list_items or LIST_6
    cv = Canvas()
    cv.text(10, 10, "THE WORLD'S NEWS IN ONE PICTURE", F("arialbd.ttf", 16), RED)
    cv.text(W - 10, 10, f"{11 + len(items)} STORIES · ALL REPORTED ON FRIDAY", F("arialbd.ttf", 14),
            GREY, anchor="ra")
    fd = cv.fit("Friday 13 November 2026", "georgiab.ttf", 80, W - 20)
    cv.text(W / 2, 28, "Friday 13 November 2026", fd, INK, anchor="ma")
    cv.rect(10, 112, W - 10, 115, fill=INK)
    m, g = 10, 8
    y0, y1 = 123, 393
    xs = [m, 440, 732, W - m]
    for i, (fn, rg, hd, sb, _) in enumerate(ROW1_6):
        panel(cv, (xs[i] + (g / 2 if i else 0), y0, xs[i + 1] - (g / 2 if i < 2 else 0), y1), fn, 1 + i, rg, hd, sb,
              scene_frac=0.50, head_px=24 if i == 0 else 19.5, sub_px=13 if i == 0 else 12.5, hfont="georgiab.ttf")
    y0, y1 = 401, 617
    cw = (W - 2 * m - 3 * g) / 4
    for i, (fn, rg, hd, sb, _) in enumerate(ROW2):
        x0 = m + i * (cw + g)
        panel(cv, (x0, y0, x0 + cw, y1), fn, 4 + i, rg, hd, sb, scene_frac=0.50, head_px=18, sub_px=12.5,
              hfont="georgiab.ttf")
    y0, y1 = 625, 829
    for i, (fn, rg, hd, sb, _) in enumerate(ROW3_6):
        x0 = m + i * (cw + g)
        panel(cv, (x0, y0, x0 + cw, y1), fn, 8 + i, rg, hd, sb, scene_frac=0.47, head_px=18, sub_px=12.5,
              hfont="georgiab.ttf")
    listing(cv, (m, 837, W - m, 1003), [(it[0], it[1]) for it in items], 12)
    cv.text(W / 2, 1009, "Every story here was reported on Friday 13 November 2026. Sources: AP, Reuters, NPR, "
            "CNBC, Al Jazeera, BBC, CNN, Vatican News, Space.com", F("ariali.ttf", 10.5), GREY, anchor="ma")
    out = cv.im.resize((W, H), Image.LANCZOS)
    out.save(path, optimize=True)
    return path


ROW1_6 = [
    (scene_faa, "UNITED STATES", "FAA halts all US departures for hours as air-traffic telecoms fail",
     "Lifted Friday night; 4,000+ flights cancelled, 10,000+ delayed. DHS: no sign of an attack",
     (-98, 39)),
    (scene_iran, "MIDDLE EAST", "Iran says it hit a US radar in Bahrain; US denies it",
     "US says it shot down both drones; IRGC cites a US strike in Sirik", (50.5, 26)),
    (scene_apec, "ASIA", "Trump, Xi and Putin to meet in China next week",
     "White House: first three-way talks, at the APEC summit", (114, 22.5)),
]
ROW3_6 = [
    (scene_kyiv, "EUROPE", "Russian drone sets a Kyiv hospital ablaze",
     "About 30 evacuated; strikes also kill 3 in Odesa and Zaporizhzhia", (30.5, 50.4)),
    (scene_eu, "EUROPE", "EU picks five nations for Ukraine peace talks",
     "UK, France, Germany, Italy, Poland; agreed in Dublin", (-6.3, 53.3)),
    (scene_gaza, "MIDDLE EAST", "Gaza: strike on Nasser Hospital complex",
     "Six killed in Khan Younis, a surgeon among them", (34.3, 31.3)),
    (scene_assam, "ASIA", "Bus-truck crash in India's Assam kills 24",
     "Minibus hits a container truck near Kaziranga", (93.9, 26.6)),
]
LIST_6 = [
    ("WORLDWIDE", "Microsoft outage hits Outlook and Teams for a second day", None),
    ("MIDDLE EAST", "Turkey and Qatar sign a mutual defence pact", None),
    ("MIDDLE EAST", "Iran says an LNG tanker hit a mine in Hormuz", None),
    ("MIDDLE EAST", "UN: over 340,000 now displaced in Yemen", None),
    ("EUROPE", "Moscow car bomb wounds ex-aide of Ukraine ex-PM", None),
    ("ASIA", "Japan's PM Takaichi to make first China visit, for APEC", None),
    ("ASIA", "Pakistan army says 74 militants killed in raids", None),
    ("ASIA", "North Korea changes its flag, first since 1948", None),
    ("AFRICA", "Building collapses near Nairobi, killing 6", None),
    ("AFRICA", "Nigeria ends Ebola watch with no new cases", None),
    ("EUROPE", "Suspected drones over US airbase RAF Lakenheath", None),
    ("MARKETS", "US producer prices up 6.5% in a year", None),
    ("UNITED STATES", "Lauren Boebert loses her Colorado House seat", None),
    ("SCIENCE", "Shuttle Endeavour put on show upright in LA", None),
    ("CULTURE", "U2 album out with Dolly Parton's last vocal", None),
    ("SPORT", "Pochettino named Manchester United manager", None),
    ("SPORT", "Baseball: Japan beat South Korea 9-5 in Tokyo", None),
]



if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "entry.png")
    v = sys.argv[2] if len(sys.argv) > 2 else "v6"
    build_v6(p) if v == "v6" else build(p, v)
    print(p, os.path.getsize(p))
