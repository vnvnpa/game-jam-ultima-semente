"""Paleta etérea e utilitários de sombreamento compartilhados pelos geradores de arte."""
import math
from pix import C, hx, BAYER4, mix

# rampas (escuro -> claro), sempre com mudança de matiz nas sombras
T = [hx(s) for s in ["#050d0f", "#0a1a1d", "#0f2a2e", "#163f43", "#1f5a58", "#2f7f73", "#4fb097", "#8fe0be", "#d2fbe6"]]
V = [hx(s) for s in ["#120a24", "#1b1033", "#2e1a57", "#4d2f8a", "#7b52c4", "#ad84ee", "#dcc4ff"]]
G = [hx(s) for s in ["#24160a", "#3a280c", "#6b4713", "#b07a1c", "#e8b640", "#ffe27a", "#fff7c8"]]
R = [hx(s) for s in ["#240812", "#3b0f1f", "#7a1d36", "#c2395a", "#f0708a", "#ffb0be", "#ffe3e8"]]
B = [hx(s) for s in ["#04141f", "#0b2d45", "#14587c", "#2a94bd", "#6fd8f0", "#c4f6ff", "#f0fdff"]]
L = [hx(s) for s in ["#0a1c0e", "#16331a", "#29682d", "#4fa23d", "#98d85a", "#dcf7a0", "#f6ffd8"]]
O = [hx(s) for s in ["#2a1208", "#4a2410", "#8a4416", "#d8782a", "#f5a640", "#ffd08a", "#fff0d0"]]
W = [hx(s) for s in ["#0c1214", "#1e2a2c", "#3c4e50", "#6b8486", "#a4bdbb", "#d6e6e2", "#ffffff"]]
CLEAR = (0, 0, 0, 0)


def orb(c, cx, cy, r, ramp, light=(-0.55, -0.65), dither=True, spec=True):
    """Esfera sombreada pixel a pixel: lambert quantizado na rampa com dither nas transições."""
    n = len(ramp)
    lx, ly = light
    lz = math.sqrt(max(0.0, 1 - lx * lx - ly * ly))
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            dx, dy = (x + 0.5 - cx) / r, (y + 0.5 - cy) / r
            d2 = dx * dx + dy * dy
            if d2 > 1.0:
                continue
            dz = math.sqrt(1 - d2)
            lam = max(0.0, dx * lx + dy * ly + dz * lz)
            t = lam * (n - 1)
            lo = int(t)
            fr = t - lo
            if dither and lo < n - 1:
                thr = BAYER4[y % 4, x % 4]
                idx = lo + (1 if fr > thr else 0)
            else:
                idx = int(round(t))
            c.px(x, y, ramp[min(idx, n - 1)])
    if spec:
        c.px(int(cx + lx * r * 0.45), int(cy + ly * r * 0.45), ramp[-1])


def glow(c, cx, cy, r, col, strength=0.5, bayer=BAYER4):
    """Halo de dithering (brilho etéreo): só pinta pixels vazios, sem translucidez."""
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            if not c.inb(x, y) or c.a[y, x, 3] > 0:
                continue
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / r
            if d >= 1:
                continue
            t = (1 - d) ** 1.6 * strength
            if t > bayer[y % 4, x % 4]:
                c.px(x, y, col)


def edge_color(col):
    """Cor do contorno seletivo: mais escura e fria que a cor da forma."""
    return (max(0, int(col[0] * 0.30 + 6)), max(0, int(col[1] * 0.34 + 8)), max(0, int(col[2] * 0.42 + 14)), 255)
