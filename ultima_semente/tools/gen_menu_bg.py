"""Fundo do menu principal em pixel art (3 camadas de parallax, 640x360 ampliado 2x)."""
import os, math, random
import numpy as np
from pix import C, hx, BAYER4, contact
from ui_pal import T, V, G, R, B, L, O, W, orb, glow

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "assets", "art", "ui")
W_, H_ = 640, 360


def ridge(seed, base, amp, n=5):
    rnd = random.Random(seed)
    comps = [(rnd.uniform(.004, .03) * (k + 1) * 0.8, rnd.uniform(0, 6.28), 1.0 / (k + 1)) for k in range(n)]
    def f(x):
        return base - amp * (0.5 + 0.5 * sum(a * math.sin(fr * x + ph) for fr, ph, a in comps) / sum(a for _, _, a in comps))
    return f


def thick_line(c, x0, y0, x1, y1, w0, w1, col):
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    for i in range(n + 1):
        t = i / max(n, 1)
        c.disc(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, (w0 + (w1 - w0) * t) / 2, col)


def rim_light(c, col_hi, col_lo=None):
    """Luz de contorno: pixels de silhueta voltados para cima-esquerda ficam claros."""
    m = c.mask()
    up = np.zeros_like(m); up[1:, :] = m[:-1, :]
    lf = np.zeros_like(m); lf[:, 1:] = m[:, :-1]
    edge = m & (~up | ~lf)
    for y, x in zip(*np.nonzero(edge)):
        c.px(x, y, col_hi)
    if col_lo is not None:
        dn = np.zeros_like(m); dn[:-1, :] = m[1:, :]
        rt = np.zeros_like(m); rt[:, :-1] = m[:, 1:]
        e2 = m & ~dn & ~rt
        for y, x in zip(*np.nonzero(e2)):
            c.px(x, y, col_lo)


def far():
    c = C(W_, H_)
    stops = [(0.0, hx("#03070d")), (0.30, hx("#06151d")), (0.52, hx("#0a2a30")), (0.72, hx("#14504c")), (1.0, hx("#1f6b5f"))]
    bands = [s[1] for s in stops]
    for y in range(H_):
        t = y / (H_ - 1)
        for i in range(len(stops) - 1):
            if stops[i][0] <= t <= stops[i + 1][0]:
                u = (t - stops[i][0]) / (stops[i + 1][0] - stops[i][0])
                lo, hi = stops[i][1], stops[i + 1][1]
                for x in range(W_):
                    c.px(x, y, hi if u > BAYER4[y % 4, x % 4] else lo)
                break
    # aurora: duas fitas luminosas pontilhadas
    for (y0, amp, fr, col_a, col_b, w) in ((70, 26, 0.011, V[2], V[3], 15.0), (112, 18, 0.017, hx("#0f3a45"), hx("#14586a"), 11.0)):
        for x in range(W_):
            yc = y0 + amp * math.sin(x * fr + 1.3) + 10 * math.sin(x * fr * 2.7)
            pulse = 0.55 + 0.45 * math.sin(x * 0.021 + y0)
            for y in range(int(yc - w * 2), int(yc + w * 2)):
                t = math.exp(-((y - yc) / w) ** 2) * pulse * 0.8
                if t > BAYER4[y % 4, x % 4]:
                    c.px(x, y, col_b if t > 0.5 else col_a)
    rnd = random.Random(3)
    for _ in range(190):
        x, y = rnd.randrange(W_), rnd.randrange(0, 210)
        col = rnd.choice([T[7], T[8], V[6], B[5], T[6]])
        c.px(x, y, col)
        if rnd.random() < 0.08:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                c.px(x + dx, y + dy, T[5])
    # orbe luminoso (a Última Semente) + halo + anel
    cx, cy = 478, 150
    for y in range(H_):
        for x in range(W_):
            d = math.hypot(x - cx, (y - cy)) / 120.0
            if d < 1:
                t = (1 - d) ** 2.2 * 0.75
                if t > BAYER4[y % 4, x % 4]:
                    c.px(x, y, T[4] if t < 0.35 else T[5])
    for a in range(0, 360):
        x = cx + 74 * math.cos(math.radians(a)); y = cy + 18 * math.sin(math.radians(a)) + 0.35 * (x - cx) * 0.4
        if a < 180 or True:
            if (a // 3) % 2 == 0:
                c.px(round(x), round(y), V[5] if 0 < a < 180 else V[3])
    orb(c, cx, cy, 44, [T[2], T[3], T[4], T[5], T[6], T[7], T[8]], light=(-0.4, -0.5))
    # manchas (mares) na superfície do orbe
    for (dx, dy, rr) in ((10, 12, 9), (-14, 5, 6), (18, -10, 5), (-5, -20, 4)):
        for y in range(cy + dy - rr, cy + dy + rr):
            for x in range(cx + dx - rr, cx + dx + rr):
                if (x - cx - dx) ** 2 + (y - cy - dy) ** 2 < rr * rr and (x - cx) ** 2 + (y - cy) ** 2 < 42 ** 2:
                    if (x + y) % 2 == 0:
                        c.px(x, y, T[4])
    for a in range(0, 180):  # parte frontal do anel por cima do orbe
        x = cx + 74 * math.cos(math.radians(a)); y = cy + 18 * math.sin(math.radians(a)) + 0.35 * (x - cx) * 0.4
        if (a // 3) % 2 == 0:
            c.px(round(x), round(y), V[6] if a % 6 else V[5])
    # cordilheiras com névoa pontilhada entre elas
    layers = [(ridge(11, 250, 70), hx("#0b2528"), 0.0), (ridge(23, 285, 60), hx("#0a2023"), 0.0), (ridge(37, 318, 50), hx("#071619"), 0.0)]
    for k, (f, col, _) in enumerate(layers):
        for x in range(W_):
            top = int(f(x))
            for y in range(top, H_):
                c.px(x, y, col)
            # luz de contorno na crista
            c.px(x, top, T[4] if k == 0 else T[3])
        # névoa na base de cada camada
        for y in range(int(max(f(x) for x in range(0, W_, 8))) , H_):
            for x in range(W_):
                if y < f(x) + 70 and y >= f(x) + 6:
                    t = (1 - (y - f(x) - 6) / 64.0) * 0.28
                    if t > BAYER4[y % 4, x % 4]:
                        c.px(x, y, hx("#1d6a60") if k == 0 else hx("#164f4b"))
    # luzes distantes (vilas dos Arquitetos)
    for _ in range(14):
        x = rnd.randrange(30, W_ - 30)
        y = int(layers[0][0](x)) + rnd.randrange(8, 24)
        c.px(x, y, G[5]); c.px(x + 1, y, G[4])
    return c


def tree(c, x, y, h, seed, trunk_col, canopy_col, fruit=None):
    rnd = random.Random(seed)
    def branch(px, py, ang, ln, wd, depth):
        nx, ny = px + math.cos(ang) * ln, py + math.sin(ang) * ln
        thick_line(c, px, py, nx, ny, wd, max(1.5, wd * 0.7), trunk_col)
        if depth == 0 or ln < 10:
            r = rnd.randint(14, 26)
            for yy in range(int(ny - r), int(ny + r)):
                for xx in range(int(nx - r * 1.2), int(nx + r * 1.2)):
                    d = math.hypot((xx - nx) / 1.2, yy - ny) / r
                    if d < 1.0 and (d < 0.72 or rnd.random() > (d - 0.72) * 3.2):
                        c.px(xx, yy, canopy_col)
            if fruit and rnd.random() < 0.7:
                fx, fy = int(nx + rnd.randint(-r // 2, r // 2)), int(ny + rnd.randint(0, r // 2))
                c.px(fx, fy, fruit); c.px(fx, fy + 1, fruit)
            return
        for da in (-0.55, 0.45):
            branch(nx, ny, ang + da + rnd.uniform(-0.2, 0.2), ln * rnd.uniform(0.62, 0.78), wd * 0.68, depth - 1)
    branch(x, y, -math.pi / 2 + rnd.uniform(-0.08, 0.08), h * 0.36, 11, 3)


def mid():
    c = C(W_, H_)
    base, can = hx("#07191c"), hx("#0a2326")
    for (x, h, s) in ((60, 230, 1), (190, 200, 2), (330, 250, 3), (470, 215, 4), (600, 240, 5)):
        tree(c, x, H_ + 6, h, s, base, can, fruit=(B[5] if s % 2 else V[5]))
    # ruína dos Arquitetos: arco quebrado entre as árvores, com blocos e glifos
    ruin, ruin_hi = hx("#0a2227"), hx("#0f3036")
    for (x0, w, top) in ((322, 12, 196), (388, 12, 214)):
        c.rect(x0, top, w, H_ - top, ruin)
        for yy in range(top + 8, H_, 14):
            c.rect(x0, yy, w, 1, ruin_hi)
        c.rect(x0 - 3, top - 5, w + 6, 6, ruin_hi)
    c.rect(322, 178, 44, 13, ruin)
    c.poly([(366, 178), (392, 178), (394, 190), (372, 191), (368, 186)], ruin)
    c.rect(322, 191, 44, 1, ruin_hi)
    for (gx, gy) in ((326, 224), (326, 238), (393, 236), (393, 250)):
        c.px(gx, gy, V[5]); c.px(gx + 1, gy, V[4]); c.px(gx, gy + 1, V[4]); c.px(gx + 2, gy + 2, V[3])
    c.px(340, 184, T[7]); c.px(341, 184, T[6]); c.px(352, 184, V[5])
    rim_light(c, hx("#14474a"), hx("#050f12"))
    # névoa pontilhada
    for y in range(255, 340):
        for x in range(W_):
            t = max(0.0, 1 - abs(y - 300) / 45.0) * 0.30
            if t > BAYER4[y % 4, x % 4] and not c.mask()[y, x] if False else (t > BAYER4[y % 4, x % 4] and c.a[y, x, 3] == 0):
                c.px(x, y, hx("#194f4b"))
    # frutas luminosas (já desenhadas) ganham halo
    return c


def fern(c, x, y, ln, ang, col, seed):
    rnd = random.Random(seed)
    pts = []
    for i in range(ln):
        t = i / ln
        a = ang + t * 0.9
        pts.append((x + math.cos(a) * i, y + math.sin(a) * i * 1.0))
    for i, (px_, py_) in enumerate(pts):
        c.px(px_, py_, col); c.px(px_, py_ + 1, col)
        if i % 3 == 0 and i > 3:
            t = i / ln
            ll = int((1 - t) * 13) + 2
            for side in (-1, 1):
                a = ang + t * 0.9 + side * 1.1
                for k in range(ll):
                    c.px(px_ + math.cos(a) * k, py_ + math.sin(a) * k, col)
                    if k < ll - 1:
                        c.px(px_ + math.cos(a) * k, py_ + math.sin(a) * k + 1, col)


def mushroom(c, x, y, r, cap, stem):
    c.rect(x - 1, y - 1, 3, int(r * 1.3) + 2, stem)
    for yy in range(y - r, y + 2):
        for xx in range(x - r, x + r + 1):
            if ((xx - x) / r) ** 2 + ((yy - y + 1) / (r * 0.8)) ** 2 <= 1 and yy <= y:
                c.px(xx, yy, cap[3] if (xx - x) > 0 else cap[4])
    c.rect(x - r + 1, y, 2 * r - 1, 1, cap[2])
    c.px(x - r // 2, y - r // 2, cap[5]); c.px(x - r // 2 + 1, y - r // 2, cap[5])
    for k in range(-r + 2, r - 1, 3):
        c.px(x + k, y - 1, cap[5])


def near():
    c = C(W_, H_)
    dark = hx("#030a0c")
    rnd = random.Random(9)
    # chão
    f = ridge(5, 338, 14, 3)
    for x in range(W_):
        for y in range(int(f(x)), H_):
            c.px(x, y, dark)
    for i, x in enumerate(range(-10, W_ + 10, 23)):
        fern(c, x, int(f(x)) + 4, rnd.randint(40, 90), -math.pi / 2 + rnd.uniform(-1.1, 1.1), dark, i)
    # cipós pendurados do topo
    for x in range(0, W_, 37):
        ln = rnd.randint(25, 95) if (x < 160 or x > 420) else rnd.randint(8, 30)
        for i in range(ln):
            c.px(x + math.sin(i * 0.13 + x) * 3, i, dark); c.px(x + math.sin(i * 0.13 + x) * 3 + 1, i, dark)
        for k in range(0, ln, 9):
            xx = x + math.sin(k * 0.13 + x) * 3
            for side in (-1, 1):
                for j in range(5):
                    c.px(xx + side * j, k + j // 2, dark)
    for (x, y, r, cap) in ((520, 344, 7, V), (545, 349, 5, V), (586, 346, 8, B), (40, 348, 6, B), (110, 352, 5, V)):
        mushroom(c, x, y, r, cap, hx("#8fb7b3") if cap is B else hx("#b79ae0"))
        glow(c, x, y - r // 2, r * 3, cap[4], 0.4)
    rim_light(c, hx("#0f2f31"))
    # esporos / vaga-lumes
    for _ in range(46):
        x, y = rnd.randrange(W_), rnd.randrange(30, 340)
        col = rnd.choice([T[7], G[5], V[5], L[5]])
        c.px(x, y, col); c.px(x + 1, y, col)
        if rnd.random() < 0.35:
            c.px(x, y + 1, col); c.px(x + 1, y + 1, col)
            glow(c, x, y, 5, col, 0.25)
    return c


def save2x(c, name):
    c.save(os.path.join(OUT, name), scale=2)


if __name__ == "__main__":
    a, b, n = far(), mid(), near()
    save2x(a, "menu_bg_far.png"); save2x(b, "menu_bg_mid.png"); save2x(n, "menu_bg_near.png")
    from PIL import Image
    im = Image.new("RGBA", (1280, 720), (0, 0, 0, 255))
    for nm in ("far", "mid", "near"):
        im.alpha_composite(Image.open(os.path.join(OUT, "menu_bg_%s.png" % nm)).convert("RGBA"))
    im.resize((960, 540), Image.NEAREST).save("/tmp/menu_bg_all.png")
    print("ok")
