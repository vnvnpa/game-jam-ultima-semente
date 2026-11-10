"""Tiros, bolhas, explosões e efeitos em pixel art (mantém o layout de frames do manifest)."""
import os, math, random
from pix import C, hx, BAYER4, sheet, contact
from ui_pal import T, V, G, R, B, L, O, W, glow, orb, edge_color

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "assets", "art", "fx")
PINK = [hx(s) for s in ["#2a0a2e", "#5b1458", "#9b2a8e", "#d84bbf", "#ff8ae6", "#ffd0f6", "#fff0fb"]]
WHITE = hx("#ffffff")


def outline(c):
    c.sel_outline(edge_color)
    return c


# ------------------------------------------------------------ projéteis 16x16 (apontam para a direita)
def p_espinho(f):
    c = C(16, 16)
    j = [0, 1, 0][f]
    c.poly([(3, 8), (6, 6), (12, 7), (15, 8), (12, 9), (6, 10)], L[4])
    c.poly([(3, 8), (6, 6), (12, 7), (15, 8)], L[5])
    c.poly([(3, 8), (6, 10), (12, 9), (15, 8)], L[3])
    for x in range(5, 14):
        c.px(x, 8, L[6])
    c.px(14, 8, WHITE)
    c.px(4, 7, L[4]); c.px(4, 9, L[2])
    for k, x in enumerate((2, 1, 0)):
        if (k + f) % 3 != 2:
            c.px(x, 8 + (j if k == 1 else 0) - (1 if k == 2 else 0), L[3 - k] if k < 3 else L[2])
    return outline(c)


def p_cuspe(f):
    c = C(16, 16)
    wob = [(4.6, 4.2), (4.2, 4.7), (4.7, 4.3)][f]
    cx, cy = 10, 8
    # bolha: casca escura, corpo magenta, reflexo claro embaixo/direita e brilho no topo
    for y in range(16):
        for x in range(16):
            dx, dy = (x + .5 - cx) / wob[0], (y + .5 - cy) / wob[1]
            d = dx * dx + dy * dy
            if d <= 1.0:
                col = PINK[3]
                if d > 0.62:
                    col = PINK[2]
                if d > 0.86:
                    col = PINK[1]
                if dx > 0.1 and dy > 0.1 and 0.3 < d < 0.8:
                    col = PINK[4]
                c.px(x, y, col)
    c.px(cx - 2, cy - 2, PINK[6]); c.px(cx - 1, cy - 3, PINK[5]); c.px(cx - 3, cy - 1, PINK[5])
    # gotículas que ficam para trás
    for (x, y) in (((3, 8), (1, 7), (5, 11)), ((4, 7), (2, 9), (5, 10)), ((3, 9), (1, 8), (5, 6)))[f]:
        c.px(x, y, PINK[3])
    c.px(4, 8, PINK[2]) if f != 1 else c.px(4, 9, PINK[2])
    return outline(c)


def p_bolt(f):
    c = C(16, 16)
    for x in range(1, 14):
        t = x / 13.0
        c.px(x, 8, B[3] if t < 0.5 else B[5])
        if t > 0.3:
            c.px(x, 7, B[2]); c.px(x, 9, B[2])
    for x in range(3, 13):
        c.px(x, 8, B[6] if x > 6 else B[5])
    c.poly([(11, 6), (15, 8), (11, 10), (13, 8)], B[5])
    c.px(14, 8, WHITE); c.px(13, 8, WHITE)
    for k in range(3):
        c.px(1 + (k * 2 + f * 2) % 6, 5 + (k * 3 + f) % 2 * 6, B[4] if k else B[5])
    return outline(c)


def p_shard(f):
    c = C(16, 16)
    sh = [0, 1, -1][f]
    c.poly([(2, 8), (7, 5 + (1 if sh == 1 else 0)), (14, 8), (7, 11 + (-1 if sh == -1 else 0))], L[4])
    c.poly([(2, 8), (7, 5), (14, 8), (8, 8)], L[5])
    c.poly([(2, 8), (8, 8), (14, 8), (7, 11)], L[3])
    c.line(5, 8, 12, 8, L[6])
    c.px(9, 7, WHITE); c.px(8, 6, L[6])
    c.px(3, 6 + sh, G[5]); c.px(4, 10 - sh, G[4])
    return outline(c)


def projectiles():
    fr = [fn(f) for fn in (p_espinho, p_cuspe, p_bolt, p_shard) for f in range(3)]
    return sheet(fr, 3)


def muzzle():
    fs = []
    for f in range(3):
        c = C(16, 16)
        r = [4, 6, 3][f]
        c.poly([(2, 8), (2 + r * 1.2, 8 - r * 0.8), (2 + r * 2.2, 8), (2 + r * 1.2, 8 + r * 0.8)], L[5] if f < 2 else L[4])
        c.poly([(2, 8), (2 + r * 0.8, 7), (2 + r * 1.6, 8), (2 + r * 0.8, 9)], WHITE)
        if f == 1:
            for (x, y) in ((11, 4), (12, 12), (14, 8), (9, 3), (9, 13)):
                c.px(x, y, L[6])
        if f == 2:
            for (x, y) in ((9, 5), (10, 11), (12, 8)):
                c.px(x, y, L[5])
        fs.append(c)
    return sheet(fs, 3)


def burst():
    fs = []
    for f in range(6):
        c = C(32, 32)
        g = 255 - f * 30
        col = (g, g, g, 255)
        dim = (max(g - 55, 90),) * 3 + (255,)
        if f == 0:
            for k in range(-6, 7):
                c.px(16 + k, 16, WHITE); c.px(16, 16 + k, WHITE)
            for k in range(-3, 4):
                c.px(16 + k, 16 + k, col); c.px(16 + k, 16 - k, col)
            c.rect(15, 15, 2, 2, WHITE)
        else:
            r0 = [0, 5, 8, 11, 13, 14][f]
            ln = [0, 4, 4, 3, 2, 2][f]
            thick = 2 if f <= 2 else 1
            for k in range(8):
                a = math.radians(k * 45 + (22.5 if f % 2 == 0 else 0))
                for s in range(ln):
                    x, y = 16 + math.cos(a) * (r0 + s), 16 + math.sin(a) * (r0 + s)
                    c.px(round(x), round(y), col)
                    if thick == 2:
                        c.px(round(x) + 1, round(y), dim)
            for k in range(8):
                a = math.radians(k * 45 + (0 if f % 2 == 0 else 22.5))
                x, y = 16 + math.cos(a) * (r0 * 0.7 + 1), 16 + math.sin(a) * (r0 * 0.7 + 1)
                if f < 4:
                    c.px(round(x), round(y), dim)
        fs.append(c)
    return sheet(fs, 6)


def explosion():
    fs = []
    rnd = random.Random(5)
    for f in range(6):
        c = C(64, 64)
        r = [8, 15, 22, 26, 28, 29][f]
        if f <= 2:
            for y in range(64):
                for x in range(64):
                    d = math.hypot(x - 32, y - 32) / r
                    if d <= 1.0:
                        t = d + (math.sin(x * 0.7 + y * 0.5 + f) * 0.08)
                        col = G[6] if t < 0.3 else G[5] if t < 0.55 else O[4] if t < 0.75 else O[3] if t < 0.92 else R[3]
                        if t > 0.8 and BAYER4[y % 4, x % 4] > 0.5:
                            continue
                        c.px(x, y, col)
        elif f == 3:
            for a in range(0, 360, 2):
                for rr in (r, r - 1, r - 2):
                    c.px(round(32 + rr * math.cos(math.radians(a))), round(32 + rr * math.sin(math.radians(a))), O[4] if rr == r else O[3])
            c.disc(32, 32, 8, G[5]); c.disc(32, 32, 4, G[6])
        else:
            for a in range(0, 360, 5 if f == 4 else 10):
                rr = r + (rnd.random() * 2)
                c.px(round(32 + rr * math.cos(math.radians(a))), round(32 + rr * math.sin(math.radians(a))), O[3] if f == 4 else R[3])
        # fagulhas
        for k in range(10 - f):
            a = rnd.random() * 6.28
            rr = r * (0.7 + rnd.random() * 0.5) + 2
            c.px(round(32 + rr * math.cos(a)), round(32 + rr * math.sin(a)), G[5] if f < 4 else R[4])
        fs.append(c)
    return sheet(fs, 6)


def ring_img():
    c = C(128, 128)
    cx = cy = 63.5
    for a10 in range(0, 3600, 4):
        a = math.radians(a10 / 10)
        for (rr, col) in ((62, WHITE), (61, WHITE), (60, hx("#d8e8e4")), (58.5, hx("#9fb5b0"))):
            x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
            gap = (a10 // 300) % 2 == 0 and rr > 60.5 and (a10 % 300) in range(120, 180)
            if not gap:
                c.px(round(x), round(y), col)
    for y in range(128):
        for x in range(128):
            d = math.hypot(x - cx, y - cy) / 58.0
            if d < 1:
                t = d ** 6 * 0.22
                if t > BAYER4[y % 4, x % 4] and c.a[y, x, 3] == 0:
                    c.px(x, y, hx("#90a8a3"))
    for k in range(24):
        a = math.radians(k * 15)
        for rr in (64, 65):
            c.px(round(cx + rr * math.cos(a)), round(cy + rr * math.sin(a)), WHITE if k % 2 else hx("#b8cac6"))
    return c


def slam():
    c = C(128, 128)
    cx = cy = 63.5
    for y in range(128):
        for x in range(128):
            d = math.hypot(x - cx, y - cy) / 62.0
            if d <= 1.0:
                t = 0.07 + d ** 3 * 0.22
                if t > BAYER4[y % 4, x % 4]:
                    c.px(x, y, R[3])
    for a10 in range(0, 3600, 3):
        a = math.radians(a10 / 10)
        for (rr, col) in ((62, R[5]), (61, R[4]), (60, R[3])):
            c.px(round(cx + rr * math.cos(a)), round(cy + rr * math.sin(a)), col)
    for k in range(12):   # espinhos de raiz apontando para dentro
        a = math.radians(k * 30 + 7)
        for s in range(9):
            w = max(0, 3 - s // 3)
            for ww in range(-w, w + 1):
                x = cx + math.cos(a) * (60 - s) + math.cos(a + 1.57) * ww
                y = cy + math.sin(a) * (60 - s) + math.sin(a + 1.57) * ww
                c.px(round(x), round(y), R[5] if s < 3 else R[4])
    return c


def particle():
    c = C(8, 8)
    for (x, y, col) in ((3, 3, WHITE), (4, 3, WHITE), (3, 4, WHITE), (4, 4, WHITE), (3, 2, hx("#cfe3df")), (4, 2, hx("#cfe3df")), (2, 3, hx("#cfe3df")), (2, 4, hx("#cfe3df")),
                        (5, 3, hx("#cfe3df")), (5, 4, hx("#cfe3df")), (3, 5, hx("#cfe3df")), (4, 5, hx("#cfe3df"))):
        c.px(x, y, col)
    return c


def shadow():
    c = C(32, 16)
    for y in range(16):
        for x in range(32):
            d = math.hypot((x + .5 - 16) / 15.0, (y + .5 - 8) / 6.0)
            if d <= 0.7:
                c.px(x, y, (4, 8, 10, 150))
            elif d <= 1.0 and (1 - d) / 0.3 > BAYER4[y % 4, x % 4]:
                c.px(x, y, (4, 8, 10, 120))
    return c


# ------------------------------------------------------------ coletáveis 32x32
def pk_biomass(f):
    c = C(32, 32)
    r = [5.0, 5.6, 5.0, 4.4][f]
    glow(c, 16, 16, 12, L[2], 0.55)
    orb(c, 16, 16, r, [L[1], L[2], L[3], L[4], L[5], L[6]])
    a = f * math.pi / 2
    for k in range(3):
        ang = a + k * 2.09
        x, y = 16 + 9 * math.cos(ang), 16 + 7 * math.sin(ang)
        c.px(round(x), round(y), L[5])
        c.px(round(x) + 1, round(y), L[4])
    c.px(20, 10 - (f % 2), WHITE)
    return outline(c)


def pk_cache(f):
    c = C(32, 32)
    by = [0, -1, 0, 1][f]
    glow(c, 16, 16 + by, 15, L[2], 0.5)
    cx, cy = 16, 16 + by
    c.poly([(cx, cy - 10), (cx + 8, cy), (cx, cy + 10), (cx - 8, cy)], L[4])
    c.poly([(cx, cy - 10), (cx - 8, cy), (cx, cy)], L[5])
    c.poly([(cx, cy), (cx + 8, cy), (cx, cy + 10)], L[3])
    c.poly([(cx, cy - 10), (cx + 8, cy), (cx, cy)], L[4])
    c.line(cx, cy - 8, cx - 5, cy - 1, L[6])
    c.px(cx - 2, cy - 4, WHITE)
    sx, sy = [(6, 8), (24, 9), (23, 24), (7, 23)][f]
    for (dx, dy) in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
        c.px(sx + dx, sy + dy, L[6] if dx == dy == 0 else L[5])
    return outline(c)


def pk_nucleus(f):
    c = C(32, 32)
    k = abs(math.cos(f * math.pi / 6))
    w = max(3.5, 9 * k)
    glow(c, 16, 16, 15, V[3], 0.55)
    cx, cy = 16, 16
    top = [(cx, cy - 11), (cx + w, cy - 3), (cx, cy + 1), (cx - w, cy - 3)]
    c.poly(top, B[5])
    c.poly([(cx - w, cy - 3), (cx, cy + 1), (cx, cy + 12)], B[3])
    c.poly([(cx + w, cy - 3), (cx, cy + 1), (cx, cy + 12)], V[4])
    c.line(cx, cy - 9, cx - w * 0.6, cy - 4, B[6])
    c.px(cx - 1, cy - 6, WHITE)
    for (sx, sy) in (((26, 6), (5, 9), (24, 23), (7, 24), (16, 3), (27, 16)))[f:f + 1]:
        for (dx, dy) in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            c.px(sx + dx, sy + dy, B[6] if dx == dy == 0 else B[5])
    return outline(c)


def pickups():
    rows = [[pk_biomass(f) for f in range(4)], [pk_cache(f) for f in range(4)], [pk_nucleus(f) for f in range(6)]]
    s = C(192, 96)
    for r, fr in enumerate(rows):
        for i, f in enumerate(fr):
            s.paste(f, i * 32, r * 32)
    return s


# ------------------------------------------------------------ zonas e escudos
def spores():
    fs = []
    rnd = random.Random(11)
    base_b = [(rnd.uniform(0, 6.28), rnd.uniform(8, 40), rnd.choice([1.5, 2, 2.5, 3.2])) for _ in range(16)]
    for f in range(4):
        c = C(96, 96)
        for y in range(96):
            for x in range(96):
                d = math.hypot(x - 47.5, y - 47.5) / 46.0
                if d > 1.0:
                    continue
                n = (math.sin(x * 0.21 + f * 1.6) + math.sin(y * 0.27 - f * 1.1) + math.sin((x + y) * 0.13 + f)) / 3.0
                t = (0.65 - d * 0.35 + n * 0.22) * (1 if d < 0.9 else (1 - d) / 0.1)
                if t > BAYER4[y % 4, x % 4] * 0.9 + 0.12:
                    c.px(x, y, L[2] if t < 0.62 else L[3])
        for a10 in range(0, 3600, 5):
            a = math.radians(a10 / 10 + f * 2)
            if (a10 // 25) % 2 == 0:
                c.px(round(47.5 + 45 * math.cos(a)), round(47.5 + 45 * math.sin(a)), L[4])
        # bolhas subindo
        for (ph, rr, sz) in base_b:
            ang = ph + f * 0.35
            bx, by = 47.5 + rr * math.cos(ang), 47.5 + rr * math.sin(ang) * 0.9 - f * 1.5
            if math.hypot(bx - 47.5, by - 47.5) < 42:
                c.ring(bx, by, sz, L[5], 1.1)
                c.px(round(bx - sz * 0.5), round(by - sz * 0.5), WHITE)
                if sz > 2.2:
                    c.px(round(bx + sz * 0.4), round(by + sz * 0.5), L[4])
        c.sel_outline(lambda col: (12, 40, 20, 255)) if False else None
        fs.append(c)
    return sheet(fs, 4)


def decoy():
    fs = []
    for f in range(4):
        c = C(32, 32)
        pr = 8 + f * 2.5
        for a in range(0, 360, 6):
            if (a // 12) % 2 == 0:
                c.px(round(16 + pr * math.cos(math.radians(a))), round(18 + pr * 0.7 * math.sin(math.radians(a))), L[3] if f < 3 else L[2])
        glow(c, 16, 18, 9, L[2], 0.5)
        orb(c, 16, 19, 4.2, [L[1], L[2], L[3], L[4], L[5], L[6]])
        c.poly([(16, 14), (11, 9 - f % 2), (13, 14)], L[4])
        c.poly([(16, 14), (21, 8 + f % 2), (19, 14)], L[5])
        c.line(16, 15, 16, 12, L[3])
        c.px(16, 8 - (f % 2), G[5])
        fs.append(outline(c))
    return sheet(fs, 4)


def shield():
    fs = []
    for f in range(4):
        c = C(48, 48)
        for y in range(48):
            for x in range(48):
                d = math.hypot(x - 23.5, y - 23.5) / 21.0
                if d > 1.0:
                    continue
                if d > 0.88:
                    c.px(x, y, B[4] if d < 0.96 else B[3])
                elif (0.1 + d ** 3 * 0.35) > BAYER4[y % 4, x % 4]:
                    c.px(x, y, B[2])
        base = f * 90 + 200
        for a in range(base, base + 70, 2):
            x, y = 23.5 + 20 * math.cos(math.radians(a)), 23.5 + 20 * math.sin(math.radians(a))
            c.px(round(x), round(y), B[6]); c.px(round(x), round(y) + (1 if 0 < a % 360 < 180 else -1), B[5])
        for k in range(3):
            a = math.radians(f * 90 + k * 120 + 40)
            c.px(round(23.5 + 20 * math.cos(a)), round(23.5 + 20 * math.sin(a)), WHITE)
        fs.append(c)
    return sheet(fs, 4)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    items = {"projectiles.png": projectiles(), "muzzle.png": muzzle(), "burst.png": burst(), "explosion.png": explosion(),
             "ring.png": ring_img(), "slam.png": slam(), "particle.png": particle(), "shadow.png": shadow(),
             "pickups.png": pickups(), "spores.png": spores(), "decoy.png": decoy(), "shield.png": shield()}
    for n, im in items.items():
        im.save(os.path.join(OUT, n))
    contact([items["projectiles.png"].img(), items["muzzle.png"].img(), items["burst.png"].img(), items["particle.png"].img(), items["shadow.png"].img()], 6, 2, "/tmp/fx_new_a.png", bg=(24, 40, 42, 255))
    contact([items["pickups.png"].img(), items["decoy.png"].img(), items["shield.png"].img(), items["explosion.png"].img()], 4, 1, "/tmp/fx_new_b.png", bg=(24, 40, 42, 255))
    contact([items["spores.png"].img(), items["slam.png"].img(), items["ring.png"].img()], 3, 1, "/tmp/fx_new_c.png", bg=(24, 40, 42, 255))
    print("ok")
