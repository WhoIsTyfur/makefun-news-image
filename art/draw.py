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
    bx0, by0, bx1 = w * 0.53, h * 0.05, w * 0.97
    rows = [("NEW YORK", "CANCELLED"), ("CHICAGO", "CANCELLED"), ("ATLANTA", "CANCELLED"),
            ("DALLAS", "CANCELLED"), ("DENVER", "CANCELLED"), ("LOS ANGELES", "CANCELLED")]
    rh = 27
    c.rect(bx0, by0, bx1, by0 + 34 + rh * len(rows) + 8, fill=(14, 16, 20), outline=(90, 90, 90),
           width=2, r=4)
    fh = F("arialbd.ttf", 17)
    c.text(bx0 + 10, by0 + 8, "DEPARTURES", fh, (250, 200, 40))
    c.text(bx1 - 10, by0 + 8, "16:05 ET", fh, (250, 200, 40), anchor="ra")
    fr = F("bahnschrift.ttf", 17)
    for i, (city, st) in enumerate(rows):
        y = by0 + 36 + i * rh
        c.text(bx0 + 10, y, city, fr, (235, 235, 235))
        c.rect(bx1 - 122, y - 2, bx1 - 8, y + 20, fill=RED)
        c.text(bx1 - 65, y + 9, st, F("arialbd.ttf", 15), WHITE, anchor="mm")
    # STOP sign
    cx, cy, r = w * 0.40, h * 0.30, 52
    oct_pts = [(cx + r * math.cos(math.radians(22.5 + 45 * i)), cy + r * math.sin(math.radians(22.5 + 45 * i)))
               for i in range(8)]
    c.poly(oct_pts, fill=WHITE)
    r2 = r - 5
    c.poly([(cx + r2 * math.cos(math.radians(22.5 + 45 * i)), cy + r2 * math.sin(math.radians(22.5 + 45 * i)))
            for i in range(8)], fill=RED)
    c.text(cx, cy, "STOP", F("arialbd.ttf", 27), WHITE, anchor="mm")
    c.rect(cx - 3, cy + r, cx + 3, h * 0.63, fill=(170, 170, 170))


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
    c.text(w * 0.74, h * 0.58, "IRAN: \u201cDESTROYED\u201d", F("arialbd.ttf", 15), WHITE, anchor="mm")
    c.rect(w * 0.50, h * 0.72, w * 0.98, h * 0.88, fill=NAVY, r=4)
    c.text(w * 0.74, h * 0.80, "US: DRONES SHOT DOWN", F("arialbd.ttf", 15), WHITE, anchor="mm")


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


# ---- panel frame -----------------------------------------------------------------

def panel(cv, box, painter, tag, head, sub, head_px=24, sub_px=15, label_h=None, tag_col=RED):
    x0, y0, x1, y1 = box
    lh = label_h or (head_px * 1.1 + sub_px * 1.3 + 16)
    sx1, sy1 = x1, y1 - lh
    sub_c = cv.clip(x0, y0, sx1, sy1)
    painter(sub_c)
    sub_c.done()
    cv.rect(x0, sy1, x1, y1, fill=WHITE)
    cv.rect(x0, y0, x1, y1, outline=INK, width=2)
    cv.line([(x0, sy1), (x1, sy1)], INK, 2)
    # region tag on the scene
    ft = F("arialbd.ttf", 13)
    tw = cv.tw(tag, ft)
    cv.rect(x0 + 6, y0 + 6, x0 + 18 + tw, y0 + 26, fill=tag_col)
    cv.text(x0 + 12, y0 + 16, tag, ft, WHITE, anchor="lm")
    # headline + one factual line
    maxw = (x1 - x0) - 16
    fh = cv.fit(head, "arialbd.ttf", head_px, maxw)
    cv.text(x0 + 8, sy1 + 7, head, fh, INK)
    fs = cv.fit(sub, "arial.ttf", sub_px, maxw)
    cv.text(x0 + 8, sy1 + 9 + head_px * 1.12, sub, fs, (60, 62, 70))


def build(path):
    cv = Canvas()
    # masthead
    cv.rect(0, 0, W, 118, fill=NAVY)
    cv.text(W / 2, 14, "THE WORLD ON", F("arialbd.ttf", 20), (200, 210, 230), anchor="ma")
    fd = cv.fit("FRIDAY 13 NOVEMBER 2026", "arialbd.ttf", 66, W - 40)
    cv.text(W / 2, 40, "FRIDAY 13 NOVEMBER 2026", fd, WHITE, anchor="ma")
    cv.rect(0, 118, W, 124, fill=RED)

    m, g = 8, 8
    top = 132
    # row A: lead (FAA) + right column
    lead = (m, top, 640, 540)
    panel(cv, lead, scene_faa, "USA \u00b7 LEAD STORY", "ALL US FLIGHTS GROUNDED",
          "FAA halts departures nationwide after air-traffic comms outage; thousands of flights cancelled",
          head_px=46, sub_px=17)
    rc = (640 + g, top, W - m, top + 200)
    panel(cv, rc, scene_iran, "GULF \u00b7 US-IRAN WAR", "IRAN CLAIMS HIT ON US RADAR",
          "IRGC says Bahrain radar destroyed; US denies it", head_px=22, sub_px=14)
    rc2 = (640 + g, top + 208, W - m, 540)
    panel(cv, rc2, scene_starship, "SPACE", "STARSHIP FLIGHT 15 IN ORBIT",
          "SpaceX ship reaches orbit; booster catch called off", head_px=22, sub_px=14)
    # row B
    yB0, yB1 = 548, 786
    cols = [m, 344, 680, W - m]
    panel(cv, (cols[0], yB0, cols[1] - g / 2, yB1), scene_nola, "NEW ORLEANS", "TANKER CAPSIZES CRUISE SHIP",
          "American Heritage rolls over; all aboard accounted for", head_px=22, sub_px=14)
    panel(cv, (cols[1] + g / 2, yB0, cols[2] - g / 2, yB1), scene_pope, "PERU", "POPE LEO MASS IN CHICLAYO",
          "About 500,000 hear Leo XIV in his former diocese", head_px=22, sub_px=14)
    panel(cv, (cols[2] + g / 2, yB0, cols[3], yB1), scene_nvidia, "MARKETS", "NVIDIA SINKS BELOW $4T",
          "First time since July 2025, after CEO Huang quits", head_px=22, sub_px=14)
    # row C: four panels
    yC0, yC1 = 794, 1016
    cw = (W - 2 * m - 3 * g) / 4
    rowc = [
        (scene_ukraine, "UKRAINE", "RUSSIAN STRIKES KILL 3", "Odesa and Zaporizhzhia hit"),
        (scene_gaza, "GAZA", "STRIKE AT NASSER HOSPITAL", "Six killed in Khan Younis complex"),
        (scene_assam, "INDIA", "ASSAM BUS CRASH: 24 DEAD", "Minibus hits truck near Kaziranga"),
        (scene_guinea, "WEST AFRICA", "GUINEA GOLD CLASHES", "10 killed over mining ban"),
    ]
    for i, (fn, tag, hd, sb) in enumerate(rowc):
        x0 = m + i * (cw + g)
        panel(cv, (x0, yC0, x0 + cw, yC1), fn, tag, hd, sb, head_px=19, sub_px=13)

    out = cv.im.resize((W, H), Image.LANCZOS)
    out.save(path, optimize=True)
    return path


if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "entry.png")
    build(p)
    print(p, os.path.getsize(p))
