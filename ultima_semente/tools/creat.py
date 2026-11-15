"""Ferramentas para criaturas em pixel art: elipses sombreadas, membros, olhos e
animações genéricas (dano, dissolução na morte)."""
import math, random
import numpy as np
from pix import C, hx, BAYER4
from ui_pal import T, V, G, R, B, L, O, W, glow, edge_color

WHITE = hx("#ffffff")
BARK = [hx(s) for s in ["#100a08", "#21160f", "#3a2818", "#58401f", "#7c5a30", "#a07a42", "#c9a468"]]
STONE = [hx(s) for s in ["#0b0d12", "#181c26", "#2a3040", "#434c60", "#65718a", "#8f9bb3", "#c4cfe0"]]


def ell(c, cx, cy, rx, ry, ramp, light=(-0.5, -0.6), dither=True):
    n = len(ramp)
    lx, ly = light
    lz = math.sqrt(max(0.0, 1 - lx * lx - ly * ly))
    for y in range(int(cy - ry - 1), int(cy + ry + 2)):
        for x in range(int(cx - rx - 1), int(cx + rx + 2)):
            dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            d2 = dx * dx + dy * dy
            if d2 > 1.0:
                continue
            dz = math.sqrt(1 - d2)
            lam = max(0.0, dx * lx + dy * ly + dz * lz)
            t = lam * (n - 1)
            lo = int(t)
            if dither and lo < n - 1:
                idx = lo + (1 if (t - lo) > BAYER4[y % 4, x % 4] else 0)
            else:
                idx = int(round(t))
            c.px(x, y, ramp[min(idx, n - 1)])


def tline(c, x0, y0, x1, y1, w, col):
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    for i in range(n + 1):
        t = i / max(n, 1)
        c.disc(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, w / 2.0, col)


def limb(c, pts, w0, w1, ramp):
    """Membro articulado: corpo em ramp[3], luz em ramp[4], sombra em ramp[2]."""
    for pass_, off, col in ((0, (1, 1), ramp[2]), (1, (0, 0), ramp[3]), (2, (-1, -1), ramp[4])):
        for i in range(len(pts) - 1):
            (xa, ya), (xb, yb) = pts[i], pts[i + 1]
            wa = w0 + (w1 - w0) * i / max(len(pts) - 1, 1)
            wb = w0 + (w1 - w0) * (i + 1) / max(len(pts) - 1, 1)
            if pass_ == 2:
                wa, wb = max(1, wa - 1.5), max(1, wb - 1.5)
            tline(c, xa + off[0] * 0.5, ya + off[1] * 0.5, xb + off[0] * 0.5, yb + off[1] * 0.5, (wa + wb) / 2, col)


def eye(c, x, y, col=None, big=False):
    col = col or G[5]
    if big:
        c.rect(x, y, 3, 2, col); c.px(x, y, WHITE); c.px(x + 1, y + 1, darker(col))
    else:
        c.px(x, y, WHITE); c.px(x + 1, y, col); c.px(x, y + 1, col); c.px(x + 1, y + 1, darker(col))


def darker(c, k=0.5):
    return (int(c[0] * k), int(c[1] * k), int(c[2] * k + 8), 255)


def tint(c, k):
    """Mistura os pixels com branco (flash de dano)."""
    a = c.a.copy()
    m = a[:, :, 3] > 0
    for ch in range(3):
        a[:, :, ch] = np.where(m, (a[:, :, ch] * (1 - k) + 255 * k).astype(np.uint8), a[:, :, ch])
    out = C(c.w, c.h)
    out.a = a
    return out


def shift(c, dx, dy):
    out = C(c.w, c.h)
    for y in range(c.h):
        for x in range(c.w):
            if c.a[y, x, 3] and 0 <= x + dx < c.w and 0 <= y + dy < c.h:
                out.a[y + dy, x + dx] = c.a[y, x]
    return out


def squash(c, sx, sy, foot=None):
    """Escala (vizinho mais próximo) ancorada no centro-baixo do frame."""
    foot = c.h - 2 if foot is None else foot
    out = C(c.w, c.h)
    for y in range(c.h):
        for x in range(c.w):
            nx = int((x - c.w / 2) / sx + c.w / 2)
            ny = int((y - foot) / sy + foot)
            if 0 <= nx < c.w and 0 <= ny < c.h and c.a[ny, nx, 3]:
                out.a[y, x] = c.a[ny, nx]
    return out


def hurt_frames(base, n):
    fr = []
    for i in range(n):
        k = 0.7 if i == 0 else 0.35
        s = squash(base, 1.06 if i == 0 else 1.03, 0.94 if i == 0 else 0.97)
        fr.append(shift(tint(s, k), -1 if i == 0 else 1, 0))
    return fr


def death_frames(base, n, spores, seed=1, foot=None, amt=1.0):
    rnd = random.Random(seed)
    noise = np.array([[rnd.random() for _ in range(base.w)] for _ in range(base.h)])
    pts = [(x, y) for y in range(base.h) for x in range(base.w) if base.a[y, x, 3]]
    out = []
    for i in range(n):
        t = (i + 1) / n
        s = squash(base, 1 + 0.18 * t, 1 - 0.55 * t, foot)
        c = C(base.w, base.h)
        for y in range(base.h):
            for x in range(base.w):
                if s.a[y, x, 3] and noise[y, x] > t * 1.05 - 0.15:
                    c.a[y, x] = s.a[y, x]
        if i == 0:
            c = tint(c, 0.6)
        elif i == 1:
            c = tint(c, 0.25)
        for k in range(int(14 * amt * math.sin(math.pi * min(1.0, t * 0.9 + 0.1)))):
            px_, py_ = pts[rnd.randrange(len(pts))]
            c.px(px_ + rnd.randint(-2, 2), py_ - int(t * 14 * (1 + amt * 0.5) * rnd.uniform(0.4, 1.0)) - 1, spores[rnd.randrange(len(spores))])
        out.append(c)
    return out


def finish(c, glow_col=None):
    c.sel_outline(edge_color)
    return c


PINK = [hx(s) for s in ["#2a0a2e", "#5b1458", "#9b2a8e", "#d84bbf", "#ff8ae6", "#ffd0f6", "#fff0fb"]]
OLIVE = [hx(s) for s in ["#141a0a", "#2a3a14", "#46601f", "#6c8a30", "#9ebc4c", "#d2e88a", "#f0fbc0"]]
SHELL = [hx(s) for s in ["#0c0a14", "#1a1828", "#2c2a44", "#444468", "#62628a", "#8788b0", "#b8bad8"]]


def ell_rot(c, cx, cy, ang, ra, rb, ramp, light=(-0.5, -0.6)):
    """Elipse girada (ra ao longo de `ang`) com sombreado."""
    n = len(ramp)
    lx, ly = light
    lz = math.sqrt(max(0.0, 1 - lx * lx - ly * ly))
    ca, sa = math.cos(ang), math.sin(ang)
    r = max(ra, rb) + 2
    for y in range(int(cy - r), int(cy + r + 1)):
        for x in range(int(cx - r), int(cx + r + 1)):
            u = ((x + 0.5 - cx) * ca + (y + 0.5 - cy) * sa) / ra
            v = (-(x + 0.5 - cx) * sa + (y + 0.5 - cy) * ca) / rb
            d2 = u * u + v * v
            if d2 > 1.0:
                continue
            dz = math.sqrt(1 - d2)
            nx, ny = u * ca - v * sa, u * sa + v * ca
            lam = max(0.0, nx * lx + ny * ly + dz * lz)
            t = lam * (n - 1)
            lo = int(t)
            idx = lo + (1 if lo < n - 1 and (t - lo) > BAYER4[y % 4, x % 4] else 0)
            c.px(x, y, ramp[min(idx, n - 1)])
