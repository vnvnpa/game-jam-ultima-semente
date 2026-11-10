"""Ícones, marcas do mapa, seta, cursor, vinhetas e logo (pixel art à mão)."""
import os, math
from pix import C, hx, mix, BAYER4, contact
from ui_pal import T, V, G, R, B, L, O, W, glow, orb, edge_color
from gen_ui_font import glyph_pixels

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "assets", "art", "ui")
WHITE = hx("#ffffff")


def finish(c, halo=None):
    c.sel_outline(edge_color)
    if halo:
        glow(c, c.w / 2, c.h / 2, c.w * 0.5, halo, 0.35)
    return c


def i_pulse():
    c = C(32, 32)
    for a in range(0, 360, 6):
        k = (a // 45) % 2
        r = 9
        x, y = 16 + r * math.cos(math.radians(a)), 16 + r * math.sin(math.radians(a))
        if k == 0:
            c.px(round(x), round(y), L[4])
            c.px(round(x + 1 if a < 180 else x), round(y), L[3])
    for a in range(0, 360, 14):
        x, y = 16 + 13.5 * math.cos(math.radians(a)), 16 + 13.5 * math.sin(math.radians(a))
        c.px(round(x), round(y), L[3] if (a // 14) % 2 else L[2])
    for (dx, dy) in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        c.line(16 + dx * 4, 16 + dy * 4, 16 + dx * 7, 16 + dy * 7, L[3])
        c.px(16 + dx * 7, 16 + dy * 8, L[2])
    orb(c, 16, 16, 4.2, [L[1], L[2], L[3], L[4], L[5], L[6]])
    return finish(c, T[3])


def i_dash():
    c = C(32, 32)
    for (y, x0, x1, col) in ((11, 5, 17, B[3]), (16, 2, 18, B[4]), (21, 7, 17, B[3])):
        for x in range(x0, x1):
            k = (x - x0) / (x1 - x0)
            if k > 0.35 or (x + y) % 2 == 0:
                c.px(x, y, col if k > 0.55 else B[2])
                if y == 16:
                    c.px(x, y + 1, B[2] if k > 0.5 else B[1])
    orb(c, 21, 16, 7, [B[1], B[2], B[3], B[4], B[5], B[6]])
    c.poly([(26, 16), (22, 11), (22, 21)], B[6])
    c.px(24, 16, B[3])
    return finish(c, B[1])


def i_emerg():
    c = C(32, 32)
    pts = []
    for k in range(16):
        r = 13 if k % 2 == 0 else 6.5
        a = math.radians(k * 22.5 - 90)
        pts.append((16 + r * math.cos(a), 16 + r * math.sin(a)))
    c.poly(pts, G[3])
    inner = []
    for k in range(16):
        r = 9.5 if k % 2 == 0 else 5
        a = math.radians(k * 22.5 - 90)
        inner.append((16 + r * math.cos(a), 16 + r * math.sin(a)))
    c.poly(inner, G[4])
    orb(c, 16, 16, 4, [G[3], G[4], G[5], G[6], hx("#ffffff")], spec=False)
    for a in range(0, 360, 45):
        x, y = 16 + 15.5 * math.cos(math.radians(a)), 16 + 15.5 * math.sin(math.radians(a))
        c.px(round(x), round(y), G[5])
    return finish(c, G[2])


def i_weapon():
    c = C(32, 32)
    c.poly([(6, 27), (4, 22), (22, 5), (27, 4), (26, 9), (11, 28)], L[3])
    c.poly([(5, 26), (4, 22), (22, 5), (24, 7)], L[4])
    c.poly([(7, 27), (11, 28), (26, 9), (25, 8)], L[2])
    c.line(7, 23, 24, 6, L[5])
    c.px(26, 5, L[6]); c.px(25, 5, L[6]); c.px(26, 6, L[5])
    orb(c, 8, 24, 4.2, [L[1], L[2], L[3], L[4], L[5]])
    for (x, y) in ((13, 21), (17, 17), (20, 14)):
        c.px(x, y, L[2]); c.px(x + 1, y + 1, L[2])
    return finish(c, L[1])


def i_dose():
    c = C(32, 32)
    c.rect(13, 3, 6, 4, O[3]); c.rect(13, 3, 6, 1, O[5]); c.rect(13, 6, 6, 1, O[2])
    c.rect(14, 7, 4, 4, W[4]); c.rect(14, 7, 1, 4, W[6])
    c.poly([(10, 12), (22, 12), (25, 16), (25, 25), (22, 28), (10, 28), (7, 25), (7, 16)], W[4])
    c.rect(9, 13, 14, 14, W[2])
    for j in range(17, 27):
        for i in range(9, 23):
            c.px(i, j, L[3] if (i + j) % 11 else L[4])
    for i in range(9, 23):
        c.px(i, 17, L[6] if i % 3 else L[5]); c.px(i, 18, L[4])
    for i in range(9, 23):
        c.px(i, 25, L[2]); c.px(i, 26, L[1])
    c.rect(9, 14, 2, 12, W[5]); c.px(9, 14, W[6]); c.px(9, 15, W[6])
    for (x, y) in ((15, 22), (18, 20), (17, 24)):
        c.px(x, y, L[6])
    c.px(19, 22, L[5])
    return finish(c, L[1])


def i_o2():
    c = C(32, 32)
    c.rect(13, 3, 6, 3, W[3]); c.rect(12, 5, 8, 2, W[5]); c.px(15, 2, W[6]); c.px(16, 2, W[5])
    c.rect(20, 5, 4, 2, W[4])
    c.poly([(9, 9), (23, 9), (24, 11), (24, 27), (22, 29), (10, 29), (8, 27), (8, 11)], B[3])
    c.rect(9, 10, 5, 18, B[4]); c.rect(9, 10, 2, 17, B[5])
    c.rect(19, 10, 5, 18, B[2])
    c.rect(8, 14, 16, 2, W[5]); c.rect(8, 15, 16, 1, W[3])
    c.rect(8, 22, 16, 2, W[5]); c.rect(8, 23, 16, 1, W[3])
    c.px(10, 10, B[6])
    c.ring(27, 14, 2, B[5], 1); c.ring(25, 20, 1.5, B[4], 1); c.px(28, 8, B[5]); c.px(28, 9, B[6])
    return finish(c, B[1])


def i_shield():
    c = C(32, 32)
    pts = [(16, 3), (27, 7), (27, 17), (22, 24), (16, 29), (10, 24), (5, 17), (5, 7)]
    c.poly(pts, B[3])
    c.poly([(16, 3), (5, 7), (5, 17), (10, 24), (16, 29)], B[4])
    c.poly([(16, 6), (8, 9), (8, 16), (12, 22), (16, 26)], B[5])
    c.poly([(16, 6), (24, 9), (24, 16), (20, 22), (16, 26)], B[2])
    c.line(16, 8, 16, 24, B[3])
    c.line(7, 8, 16, 4, B[6])
    c.line(16, 14, 16, 22, L[3])
    c.poly([(16, 17), (21, 12), (22, 17), (17, 19)], L[4])
    c.poly([(16, 20), (11, 16), (10, 20), (15, 22)], L[3])
    return finish(c, B[1])


def i_biomass():
    c = C(32, 32)
    ramp = [L[0], L[1], L[2], L[3], L[4], L[5], L[6]]
    orb(c, 16, 19, 8, ramp)
    orb(c, 9, 12, 5, ramp)
    orb(c, 23, 11, 4, ramp)
    c.px(14, 16, L[6]); c.px(15, 16, L[6]); c.px(7, 10, L[6]); c.px(22, 9, L[6])
    c.px(27, 5, L[5]); c.px(26, 4, L[4]); c.px(28, 4, L[4]); c.px(27, 3, L[5]); c.px(27, 6, L[4])
    return finish(c, L[1])


def i_nucleus():
    c = C(32, 32)
    top = [(16, 3), (25, 10), (16, 14), (7, 10)]
    c.poly(top, B[5])
    c.poly([(7, 10), (16, 14), (16, 29), (5, 14)], B[3])
    c.poly([(25, 10), (27, 14), (16, 29), (16, 14)], V[4])
    c.poly([(7, 10), (5, 14), (16, 29), (16, 14)], B[3])
    c.poly([(16, 14), (27, 14), (25, 10)], V[5])
    c.poly([(16, 14), (5, 14), (7, 10)], B[4])
    c.line(16, 14, 16, 29, B[2])
    c.line(16, 4, 9, 10, B[6]); c.px(15, 5, B[6])
    c.px(14, 8, hx("#ffffff")); c.px(15, 8, hx("#ffffff")); c.px(14, 9, B[6])
    c.px(24, 10, V[6]); c.px(20, 12, V[6])
    for (x, y) in ((27, 4), ):
        c.px(x, y, B[6]); c.px(x - 1, y, B[4]); c.px(x + 1, y, B[4]); c.px(x, y - 1, B[4]); c.px(x, y + 1, B[4])
    return finish(c, V[2])


def i_scanner():
    c = C(32, 32)
    for r, col in ((14, V[3]), (10, V[4]), (6, V[5])):
        for a in range(200, 341, 2):
            x, y = 16 + r * math.cos(math.radians(a)), 23 + r * math.sin(math.radians(a))
            c.px(round(x), round(y), col)
            if r < 14:
                c.px(round(x), round(y) + 1, col if a % 4 else V[2])
    c.line(16, 23, 24, 12, T[6])
    c.line(16, 24, 25, 13, T[4])
    orb(c, 16, 24, 3.5, [V[1], V[2], V[3], V[4], V[5], V[6]])
    c.px(25, 11, T[8]); c.px(26, 10, T[7])
    return finish(c, V[1])


def i_mutation():
    c = C(32, 32)
    pts = []
    for y in range(3, 30):
        a = math.sin(y * 0.46) * 8.5
        pts.append((y, 16 + a, 16 - a, math.cos(y * 0.46)))
    for (y, xa, xb, depth) in pts:
        if y % 5 == 2 and abs(xa - xb) > 6:
            lo, hi = int(min(xa, xb)), int(max(xa, xb))
            for x in range(lo + 3, hi - 2):
                c.px(x, y, W[5] if x % 2 else W[4])
    for pass_front in (False, True):
        for (y, xa, xb, depth) in pts:
            for (x, front_col, back_col, hi_col) in ((xa, L[4], L[2], L[6]), (xb, V[5], V[3], V[6])):
                is_front = (depth > 0) == (x == xa)
                if is_front != pass_front:
                    continue
                col = front_col if is_front else back_col
                for dx in (0, 1, 2):
                    c.px(round(x) + dx - 1, y, col)
                if is_front:
                    c.px(round(x) - 1, y, hi_col)
    return finish(c, V[1])


def i_suit():
    c = C(32, 32)
    c.poly([(5, 29), (6, 23), (11, 20), (21, 20), (26, 23), (27, 29)], O[3])
    c.rect(6, 26, 20, 3, O[2]); c.rect(7, 22, 18, 1, O[5]); c.rect(14, 24, 4, 2, W[5])
    orb(c, 16, 13, 10, [W[1], W[2], W[3], W[4], W[5], W[6]])
    c.ellipse(17, 14, 6.5, 5, B[2]); c.ellipse(17, 13, 5.5, 4, B[3])
    c.ellipse(16, 12, 3.5, 2, B[4]); c.px(14, 11, B[6]); c.px(15, 11, B[6]); c.px(20, 15, B[5])
    c.px(16, 2, O[5]); c.px(16, 3, W[4]); c.px(16, 1, G[5])
    return finish(c, T[2])


ICONS = [i_pulse, i_dash, i_emerg, i_weapon, i_dose, i_o2, i_shield, i_biomass, i_nucleus, i_scanner, i_mutation, i_suit]


def icons():
    from pix import sheet
    fr = [f() for f in ICONS]
    s = sheet(fr, 12)
    s.save(os.path.join(OUT, "icons.png"))
    return s


def marks():
    def mk(name, fn):
        c = C(16, 16)
        fn(c)
        c.sel_outline(edge_color)
        c.save(os.path.join(OUT, name))
    def nest(c):
        orb(c, 7, 9, 4.5, R[1:]); orb(c, 11, 6, 3, R[1:]); orb(c, 4, 6, 2.5, R[1:])
    def poi(c):
        c.poly([(5, 14), (6, 3), (10, 3), (11, 14)], V[4]); c.poly([(5, 14), (6, 3), (8, 3), (8, 14)], V[5])
        c.px(8, 7, T[8]); c.px(8, 8, T[7]); c.px(8, 9, T[7])
    def station(c):
        c.ring(8, 8, 5.5, B[5], 1.4); c.ring(8, 8, 2.5, B[4], 1); c.px(8, 8, B[6])
    def cache(c):
        c.poly([(8, 2), (13, 8), (8, 14), (3, 8)], L[4]); c.poly([(8, 2), (3, 8), (8, 8)], L[5]); c.px(7, 5, L[6])
    def player(c):
        c.poly([(8, 2), (13, 13), (8, 10), (3, 13)], O[4]); c.poly([(8, 2), (3, 13), (8, 10)], O[5]); c.px(8, 5, O[6])
    mk("mark_nest.png", nest); mk("mark_poi.png", poi); mk("mark_station.png", station)
    mk("mark_cache.png", cache); mk("mark_player.png", player)


def arrow():
    c = C(32, 32)
    c.poly([(4, 13), (18, 13), (18, 8), (29, 16), (18, 24), (18, 19), (4, 19)], W[5])
    c.poly([(4, 13), (18, 13), (18, 8), (29, 16)], W[6])
    c.poly([(4, 19), (18, 19), (18, 24), (29, 16)], W[3])
    c.line(5, 16, 18, 16, W[6])
    for x in range(5, 17, 4):
        c.px(x, 14, W[5]); c.px(x + 1, 18, W[2])
    c.sel_outline(lambda col: (30, 40, 44, 255))
    c.save(os.path.join(OUT, "arrow.png"))


def cursor():
    c = C(24, 24)
    c.poly([(1, 1), (1, 19), (5, 15), (8, 22), (11, 21), (8, 14), (14, 14)], T[7])
    c.poly([(1, 1), (1, 19), (5, 15)], T[8])
    c.poly([(8, 14), (14, 14), (5, 15)], T[6])
    c.line(2, 3, 2, 15, W[6])
    c.sel_outline(lambda col: T[0])
    c.px(0, 0, T[0])
    c.save(os.path.join(OUT, "cursor.png"))


def crosshair():
    """Retícula 4 frames x 2 linhas (livre / travada no alvo), 32x32 por frame."""
    from pix import sheet
    rows = []
    for locked in (False, True):
        frs = []
        for f in range(4):
            c = C(32, 32)
            d = [11, 10, 9, 10][f] if not locked else [9, 8, 8, 9][f]
            arm = 6 if not locked else 5
            main = T[8] if not locked else G[5]
            dark = T[6] if not locked else G[4]
            def X(sx, k):
                return 15 - k if sx < 0 else 16 + k
            for sx in (-1, 1):
                for sy in (-1, 1):
                    for k in range(arm):
                        c.px(X(sx, d - k), X(sy, d), main if k else WHITE)
                        c.px(X(sx, d), X(sy, d - k), main if k else WHITE)
                    c.px(X(sx, d - 1), X(sy, d - 1), dark)
            if not locked:
                c.px(15, 15, WHITE); c.px(16, 16, WHITE); c.px(15, 16, T[7]); c.px(16, 15, T[7])
                for (dx, dy) in ((-3, 0), (4, 0), (0, -3), (0, 4)):
                    c.px(15 + dx, 15 + dy, T[6])
            else:
                c.rect(15, 15, 2, 2, R[4]); c.px(15, 15, R[5])
                for (dx, dy, hor) in ((-(d + 2), 0, True), (d + 3, 0, True), (0, -(d + 2), False), (0, d + 3, False)):
                    for k in range(-1, 2):
                        c.px(15 + dx + (0 if hor else k), 15 + dy + (k if hor else 0), G[4] if k else G[5])
                # pontos que giram em volta do alvo (4 posições por frame)
                for k in range(4):
                    a = math.radians(f * 22.5 + k * 90)
                    c.px(round(15.5 + 6 * math.cos(a)), round(15.5 + 6 * math.sin(a)), R[4])
            c.sel_outline(lambda col: (4, 10, 12, 255))
            frs.append(c)
        rows += frs
    sheet(rows, 4).save(os.path.join(OUT, "crosshair.png"))


def vignettes():
    w, h = 320, 180
    for name, col in (("vignette_o2.png", V[4]), ("vignette_hurt.png", R[3])):
        c = C(w, h)
        for y in range(h):
            for x in range(w):
                nx, ny = (x + .5) / w * 2 - 1, (y + .5) / h * 2 - 1
                d = math.sqrt((nx * 0.92) ** 2 + (ny * 1.0) ** 2)
                t = max(0.0, min(1.0, (d - 0.62) / 0.5)) ** 1.4
                if t > BAYER4[y % 4, x % 4] * 0.98:
                    c.px(x, y, col)
        c.save(os.path.join(OUT, name))


# ------------------------------------------------------------------ logo
def text_mask(txt, spacing=1):
    pts, x = set(), 0
    for ch in txt:
        p, w = glyph_pixels(ch)
        for (px_, py_) in p:
            pts.add((x + px_, py_))
        x += w + spacing
    return pts, x - spacing


def bevel_text(c, txt, ox, oy, k, ramp, spacing=1, shadow=None, ramp_fn=None):
    pts, w = text_mask(txt, spacing)
    ymin = min(p[1] for p in pts)
    q = max(1, k // 5)
    if shadow:
        for (px_, py_) in sorted(pts):
            c.rect(ox + px_ * k + k // 2, oy + (py_ - ymin) * k + k // 2, k, k, shadow)
    for (px_, py_) in sorted(pts):
        rp = ramp_fn(ox + px_ * k + k // 2, oy + (py_ - ymin) * k + k // 2) if ramp_fn else ramp
        t_ = py_ / 6.0
        base = rp[0] if t_ < 0.2 else rp[1] if t_ < 0.5 else rp[2] if t_ < 0.8 else rp[3]
        x0, y0 = ox + px_ * k, oy + (py_ - ymin) * k
        c.rect(x0, y0, k, k, base)
        if (px_, py_ - 1) not in pts:
            c.rect(x0, y0, k, q, rp[0] if len(rp) > 4 else WHITE)
        if (px_ - 1, py_) not in pts:
            c.rect(x0, y0, q, k, rp[1])
        if (px_, py_ + 1) not in pts:
            c.rect(x0, y0 + k - q, k, q, darker(rp[3]))
        if (px_ + 1, py_) not in pts:
            c.rect(x0 + k - q, y0, q, k, darker(rp[3]))
    return w


def darker(c):
    return (int(c[0] * .55), int(c[1] * .6), int(c[2] * .7), 255)


LOGO_W, LOGO_H, LOGO_FRAMES = 480, 112, 24


def logo_frame(f, n=LOGO_FRAMES):
    import random
    W_, H_ = LOGO_W, LOGO_H
    c = C(W_, H_)
    ph = f / n
    ramp = [T[8], T[7], T[6], T[5]]
    k = 5
    title = "ÚLTIMA SEMENTE"
    pts, tw = text_mask(title)
    ox = (W_ - tw * k) // 2
    oy = 44
    for y in range(H_):
        for x in range(W_):
            dx = (x - W_ / 2) / (W_ * 0.5)
            dy = (y - 68) / 46.0
            d = math.sqrt(dx * dx * 0.9 + dy * dy)
            t = max(0.0, 1 - d) ** 1.8 * (0.55 + 0.05 * math.sin(ph * 6.2832))
            if t > BAYER4[y % 4, x % 4]:
                c.px(x, y, T[3] if t < 0.3 else T[4])
    # brilho que varre as letras na diagonal (frames 4..18), depois só cintila
    s0, s1 = 4, 18
    bx = -40 + (W_ + 120) * (f - s0) / (s1 - s0) if s0 <= f <= s1 else -999

    def ramp_fn(X, Y):
        d = abs((X + Y * 0.9) - bx)
        if d < 14:
            return [WHITE, WHITE, T[8], T[7]]
        if d < 28:
            return [T[8], T[8], T[7], T[6]]
        return ramp
    bevel_text(c, title, ox, oy, k, ramp, shadow=V[1], ramp_fn=ramp_fn)
    sub = "PROJETO"
    sp, sw = text_mask(sub, 2)
    k2 = 2
    sx = (W_ - sw * k2) // 2
    bevel_text(c, sub, sx, 14, k2, [V[6], V[5], V[5], V[4]], spacing=2, shadow=V[0])
    for side in (-1, 1):
        x0 = W_ // 2 + side * (sw * k2 // 2 + 14)
        for i in range(0, 70):
            xx = x0 + side * i
            c.px(xx, 21, V[4] if i % 3 else V[5])
            if i < 40:
                c.px(xx, 22, V[2])
        c.px(x0 - side * 6, 21, V[6]); c.px(x0 - side * 7, 20, V[5]); c.px(x0 - side * 7, 22, V[5])
    # raízes balançando
    rnd = random.Random(7)
    bottom = oy + 7 * k
    cols = sorted({p[0] for p in pts if p[1] == 6})
    for cx_ in cols[::3]:
        x = ox + cx_ * k + k // 2
        ln = rnd.randint(4, 15)
        for i in range(ln):
            xx = x + int(round(math.sin(i * 0.7 + cx_ + ph * 6.2832) * 1.3 * (i / max(ln, 1))))
            c.px(xx, bottom + 2 + i, T[4] if i < ln - 3 else T[3])
        c.px(x + int(round(math.sin(ln * 0.7 + cx_ + ph * 6.2832) * 1.3)), bottom + 2 + ln, L[5])
    cx = W_ // 2
    for i in range(1, 90):
        c.px(cx - 10 - i, 100, T[4] if i % 4 else T[6]); c.px(cx + 10 + i, 100, T[4] if i % 4 else T[6])
        if i < 60:
            c.px(cx - 10 - i, 101, T[2]); c.px(cx + 10 + i, 101, T[2])
    glow(c, cx, 100, 10 + 2.5 * math.sin(ph * 6.2832), L[3], 0.55)
    orb(c, cx, 100, 5.5, [L[0], L[1], L[2], L[3], L[4], L[5], L[6]])
    pulse = 1 if math.sin(ph * 6.2832) > 0 else 0
    for (dx, dy) in ((-9, 0), (9, 0), (0, -9), (0, 9)):
        c.px(cx + dx, 100 + dy, L[4] if pulse else L[3])
    # cintilâncias em forma de estrela (3 posições, fases diferentes)
    for (sx_, sy_, off) in ((ox + int(tw * k * 0.17), oy - 9, 0.0), (ox + int(tw * k * 0.58), oy - 13, 0.33), (ox + int(tw * k * 0.93), oy + 3, 0.66)):
        p_ = (ph + off) % 1.0
        if p_ < 0.3:
            r = 1 + int(round(3 * (1 - abs(p_ / 0.15 - 1))))
            for kk in range(-r, r + 1):
                c.px(sx_ + kk, sy_, T[8] if abs(kk) < r else T[6]); c.px(sx_, sy_ + kk, T[8] if abs(kk) < r else T[6])
            c.px(sx_, sy_, WHITE)
    return c


def logo():
    from pix import C as _C
    frames = [logo_frame(f) for f in range(LOGO_FRAMES)]
    frames[0].save(os.path.join(OUT, "logo.png"))
    sheet_ = _C(LOGO_W, LOGO_H * LOGO_FRAMES)
    for i, fr in enumerate(frames):
        sheet_.paste(fr, 0, i * LOGO_H)
    sheet_.save(os.path.join(OUT, "logo_anim.png"))


if __name__ == "__main__":
    s = icons(); marks(); arrow(); cursor(); crosshair(); vignettes(); logo()
    contact([s.img()], 3, 1, "/tmp/icons_new.png", pad=8)
    contact([os.path.join(OUT, f) for f in ("mark_nest.png", "mark_poi.png", "mark_station.png", "mark_cache.png", "mark_player.png", "arrow.png", "cursor.png")], 5, 7, "/tmp/marks_new.png")
    contact([os.path.join(OUT, "logo.png")], 2, 1, "/tmp/logo_new.png", bg=(8, 16, 18, 255))
    print("ok")
