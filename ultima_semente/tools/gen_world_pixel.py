"""Arte do mundo em pixel art (mesmo kit dos outros geradores: pix.py + ui_pal.py).

Gera, mantendo os layouts de folha já usados pelas cenas:
  trees.png (4x 64x72), crystals.png / pillars.png (4x 48x64)
  NOVOS: planters.png (64x72), capsules.png (48x64), roots.png (64x72), bulbs.png (48x64)
  decor.png, decor_estufa.png, decor_nucleo.png (16 itens de 32x32: índice = tipo + 4*variante)
  tileset_<bioma>.png (4 colunas x 5 linhas de 32x32: chão, trilha, pedra, contaminado, muralha)
    biomas: floresta, bacia, santuario, jardim, estufa, nucleo (tudo SEM emendas visíveis)
  wall_raizes.png (32x36, repete na horizontal) e wall_raizes_v.png (36x32, repete na vertical)
Atualiza assets/art/manifest.json. Rode: python3 tools/gen_world_pixel.py
"""
import os, json, math, random
import numpy as np
from pix import C, hx, BAYER4, sheet, mix, contact
from ui_pal import T, V, G, R, B, L, O, W, glow, orb, edge_color

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.path.join(ROOT, "assets", "art", "world")
SHADOW = (0, 0, 0, 78)
BARK = [hx(s) for s in ["#140b07", "#2a1a0f", "#47301f", "#6b4a2c", "#8f6a40", "#b58d5a"]]
MET = [hx(s) for s in ["#0d1517", "#1b2a2e", "#2f4448", "#4d6a6c", "#7c9a98", "#b4cdc8", "#e4f3ee"]]


def outline(c):
    c.sel_outline(edge_color)
    return c


def shadow(c, cx, cy, rx, ry):
    """Sombra só nos pixels vazios (depois do contorno), para não ganhar borda."""
    for y in range(int(cy - ry - 1), int(cy + ry + 2)):
        for x in range(int(cx - rx - 1), int(cx + rx + 2)):
            if c.inb(x, y) and c.a[y, x, 3] == 0 and ((x + .5 - cx) / rx) ** 2 + ((y + .5 - cy) / ry) ** 2 <= 1.0:
                c.px(x, y, SHADOW)


def dith(c, x, y, w, h, c1, c2, p):
    """Mistura c1/c2 num retângulo com probabilidade constante p (Bayer)."""
    c.dither_fill(x, y, w, h, c1, c2, lambda i, j: p)


def trunk(c, cx, y0, y1, w, ramp=BARK, flare=3):
    """Tronco sombreado (luz à esquerda) com base alargada."""
    for y in range(y0, y1 + 1):
        fl = max(0, flare - (y1 - y)) if y > y1 - flare else 0
        half = w // 2 + (1 if y > y1 - 4 else 0) + fl
        for x in range(cx - half, cx + half + 1):
            t = (x - (cx - half)) / max(1, 2 * half)
            idx = 4 if t < .22 else 3 if t < .5 else 2 if t < .8 else 1
            c.px(x, y, ramp[idx])
        if y % 5 == 0:
            c.px(cx + 1, y, ramp[1])
            c.px(cx - 1, y + 1, ramp[2])


# ============================================================ árvores 64x72 (base em y=64)
def tree_broadleaf(i):
    c = C(64, 72)
    trunk(c, 32, 40, 64, 6)
    # raízes
    c.line(29, 63, 24, 66, BARK[2]); c.line(35, 63, 40, 66, BARK[1])
    blobs = [(32, 33, 17), (20, 38, 12), (44, 37, 12), (27, 22, 13), (40, 21, 12), (33, 12, 9)]
    for (x, y, r) in blobs:
        orb(c, x, y, r, [L[0], L[1], mix(L[1], L[2], .6), L[2], L[3]], light=(-0.5, -0.7))
    # folhas soltas na borda
    rnd = random.Random(40 + i)
    for _ in range(14):
        a = rnd.random() * math.tau; r = rnd.uniform(15, 21)
        x, y = 32 + math.cos(a) * r, 28 + math.sin(a) * r * .8
        if c.get(int(x), int(y))[3] == 0 and any(c.get(int(x) + dx, int(y) + dy)[3] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            c.px(x, y, L[1])
    # flores
    for _ in range(5):
        x, y = rnd.randint(18, 46), rnd.randint(16, 40)
        if c.get(x, y)[3]:
            c.px(x, y, hx("#ff8ae6")); c.px(x + 1, y, hx("#ffd0f6"))
    outline(c); shadow(c, 32, 64, 19, 5)
    return c


def tree_pine(i):
    c = C(64, 72)
    trunk(c, 32, 52, 64, 5, flare=2)
    tiers = [(61, 16, 12), (51, 14, 12), (41, 12, 11), (31, 10, 10), (22, 8, 9), (14, 5, 8)]
    for (yb, hw, h) in tiers:
        top = yb - h
        for y in range(top, yb + 1):
            t = (y - top) / max(1, yb - top)
            half = int(hw * (0.15 + 0.85 * t))
            for x in range(32 - half, 32 + half + 1):
                u = (x - (32 - half)) / max(1, 2 * half)
                idx = 3 if u < .28 else 2 if u < .55 else 1 if u < .82 else 0
                if y > yb - 2:
                    idx = max(0, idx - 1)
                c.px(x, y, L[idx])
        # borda inferior irregular
        for x in range(32 - hw, 32 + hw + 1, 3):
            c.px(x, yb + 1, L[1])
    # neve/esporos claros no topo de cada camada
    for (yb, hw, h) in tiers:
        c.px(32 - 2, yb - h + 2, L[4]); c.px(32 - 5, yb - 3, L[4])
    outline(c); shadow(c, 32, 64, 15, 4)
    return c


def tree_glow(i):
    """Árvore retorcida com folhagem azul-esverdeada bioluminescente."""
    c = C(64, 72)
    # tronco torto
    pts = [(31, 64), (30, 56), (33, 48), (30, 40), (34, 33)]
    for a, b in zip(pts, pts[1:]):
        for k in range(-3, 4):
            c.line(a[0] + k, a[1], b[0] + k, b[1], BARK[4 - min(3, abs(k) + (1 if k > 0 else 0))] if abs(k) < 4 else BARK[1])
    c.line(33, 44, 44, 36, BARK[2]); c.line(32, 40, 20, 32, BARK[2]); c.line(34, 36, 38, 26, BARK[2])
    for (x, y, r) in ((34, 22, 13), (19, 29, 10), (46, 30, 10), (30, 11, 9), (43, 16, 8)):
        orb(c, x, y, r, T[2:8], light=(-0.5, -0.7))
    rnd = random.Random(7 + i)
    for _ in range(10):
        x, y = rnd.randint(14, 52), rnd.randint(6, 38)
        if c.get(x, y)[3]:
            c.px(x, y, T[8])
            if rnd.random() < .5:
                c.px(x + 1, y, T[7])
    outline(c)
    glow(c, 32, 26, 22, T[5], 0.18)
    shadow(c, 32, 64, 15, 4)
    return c


def tree_baobab(i):
    c = C(64, 72)
    # tronco grosso
    for y in range(34, 65):
        t = (y - 34) / 30
        half = int(6 + 7 * t ** 1.4)
        for x in range(32 - half, 32 + half + 1):
            u = (x - (32 - half)) / max(1, 2 * half)
            idx = 4 if u < .2 else 3 if u < .45 else 2 if u < .75 else 1
            c.px(x, y, BARK[idx])
        if y % 6 == 2:
            c.px(32 - half + 3, y, BARK[1]); c.px(32 + 2, y + 1, BARK[1])
    # copa larga e achatada
    for (x, y, r, rx) in ((32, 26, 11, 24), (14, 32, 8, 10), (50, 32, 8, 10), (23, 20, 9, 12), (42, 19, 9, 12)):
        for yy in range(y - r - 1, y + r + 2):
            for xx in range(x - rx - 1, x + rx + 2):
                dx, dy = (xx + .5 - x) / rx, (yy + .5 - y) / r
                d2 = dx * dx + dy * dy
                if d2 <= 1.0:
                    lam = max(0.0, -dx * 0.35 - dy * 0.8 + 0.45 + math.sqrt(1 - d2) * 0.4)
                    t = lam * 4.2
                    idx = int(t) + (1 if (t - int(t)) > BAYER4[yy % 4, xx % 4] else 0)
                    c.px(xx, yy, mix(L[min(4, idx)], T[3], .25) if True else 0)
    rnd = random.Random(90 + i)
    for _ in range(7):
        x, y = rnd.randint(12, 52), rnd.randint(14, 34)
        if c.get(x, y)[3]:
            c.px(x, y, O[4]); c.px(x, y + 1, O[3])
    outline(c); shadow(c, 32, 64, 21, 5)
    return c


# ============================================================ cristais 48x64 (base em y=58)
def prism(c, x, yb, w, h, ramp, tilt=0):
    """Prisma hexagonal: faces esquerda clara / direita escura e topo facetado."""
    ytip = yb - h
    yt = ytip + max(4, int(w * 1.9))
    for y in range(ytip, yb + 1):
        if y < yt:
            t = (y - ytip) / max(1, yt - ytip)
            half = int(round(w * t))
            cx = x + int(round(tilt * (1 - t)))
        else:
            half = w
            cx = x + 0
        for xx in range(cx - half, cx + half + 1):
            u = (xx - (cx - half)) / max(1, 2 * half)
            if y < yt:
                idx = 5 if u < .5 else 4
                if xx == cx - half or xx == cx - half + 1 and y > ytip + 3:
                    idx = 5
            else:
                idx = 4 if u < .33 else 3 if u < .66 else 2
                if u > .88:
                    idx = 1
            c.px(xx, y, ramp[idx])
    # reflexo
    for y in range(yt + 2, yb - 3):
        c.px(x - w + 2, y, ramp[6] if (y - yt) % 5 < 3 else ramp[5])
    c.px(x + tilt, ytip + 1, ramp[6])
    # linha de aresta central da base
    for y in range(yt, yb + 1):
        if (y + x) % 3 == 0:
            c.px(x + 1, y, ramp[3])


def rocks(c, cx, cy, n, seed):
    rnd = random.Random(seed)
    for _ in range(n):
        x = cx + rnd.randint(-14, 14); y = cy + rnd.randint(-2, 2); r = rnd.randint(2, 3)
        orb(c, x, y, r, W[1:5], light=(-0.5, -0.7), spec=False)


def crystal_cluster(i):
    c = C(48, 64)
    ramps = [V, V, B, R][i]
    glow_c = [V[4], V[4], B[4], R[4]][i]
    rocks(c, 24, 56, 4, 30 + i)
    layouts = [
        [(24, 57, 5, 38, 0), (14, 58, 4, 24, -2), (33, 58, 4, 28, 2), (20, 58, 3, 16, 0)],
        [(22, 57, 6, 34, -1), (33, 58, 4, 26, 2), (12, 58, 3, 18, -2), (28, 59, 3, 14, 1)],
        [(24, 57, 5, 44, 1), (13, 58, 4, 26, -2), (35, 58, 4, 22, 2), (6, 59, 3, 14, -1), (41, 59, 3, 12, 1)],
        [(18, 57, 5, 30, -1), (30, 58, 5, 36, 2), (24, 59, 3, 18, 0), (9, 58, 3, 16, -1)],
    ][i]
    for (x, yb, w, h, tl) in sorted(layouts, key=lambda t: t[1] - t[3]):
        prism(c, x, yb, w, h, ramps, tl)
    outline(c)
    glow(c, 24, 38, 20, glow_c, 0.20)
    shadow(c, 24, 58, 19, 4)
    return c


# ============================================================ pilares 48x64
def pillar(i):
    c = C(48, 64)
    # base
    c.rect(9, 54, 30, 5, W[2]); c.rect(9, 54, 30, 1, W[4]); c.rect(9, 58, 30, 1, W[1])
    c.rect(12, 51, 24, 3, W[3]); c.rect(12, 51, 24, 1, W[5])
    top = 14 if i != 1 else 22
    # fuste
    for y in range(top, 51):
        for x in range(14, 34):
            u = (x - 14) / 20
            idx = 4 if u < .2 else 3 if u < .5 else 2 if u < .82 else 1
            c.px(x, y, W[idx])
        if (y - top) % 9 == 4:
            for x in range(14, 34):
                if c.get(x, y)[3]:
                    c.px(x, y, W[1] if x > 22 else W[2])
    # caneluras
    for x in (20, 28):
        for y in range(top + 3, 49):
            if (y + x) % 5 > 1:
                c.px(x, y, W[2] if x < 24 else W[1])
    # capitel
    if i != 1:
        c.rect(11, top - 5, 26, 5, W[4]); c.rect(11, top - 5, 26, 1, W[6]); c.rect(11, top - 1, 26, 1, W[2])
        c.rect(13, top - 8, 22, 3, W[3]); c.rect(13, top - 8, 22, 1, W[5])
        c.rect(14, top - 1, 20, 2, W[1])
    else:
        # quebrado: topo irregular + entulho
        for x in range(14, 34):
            jag = [3, 1, 4, 0, 2, 5, 1, 3, 0, 4, 2, 1, 5, 2, 0, 3, 4, 1, 2, 3][x - 14]
            for y in range(top - jag, top + 1):
                u = (x - 14) / 20
                c.px(x, y, W[4 if u < .2 else 3 if u < .5 else 2 if u < .82 else 1])
        c.rect(34, 50, 5, 3, W[2]); c.rect(8, 51, 4, 3, W[3]); c.px(36, 49, W[4])
    # musgo: manchas em dither perto da base e do topo
    for (y0, h, p) in ((45, 6, .5), (top + 1, 3, .22)):
        for y in range(y0, y0 + h):
            for x in range(14, 34):
                if c.get(x, y)[3] and BAYER4[y % 4, x % 4] < p * (1 - abs((y - y0) / h - .5) * 1.2) * (1.0 if (x * 3 + y) % 5 < 3 else .4):
                    c.px(x, y, L[2 if x < 24 else 1])
    # trepadeira
    if i in (0, 2, 3):
        x = 17 + 4 * (i % 3)
        for y in range(top + 2, 52):
            xx = x + int(2 * math.sin(y * .45 + i))
            c.px(xx, y, L[3]); c.px(xx + 1, y, L[1])
            if y % 6 == 0:
                c.px(xx - 1, y, L[4])
    # runa luminosa (variantes 0, 2, 3)
    rune = [T, None, T, B][i]
    if rune:
        cx, cy = 24, top + 14
        for (dx, dy) in ((0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (-2, 2), (-1, 2), (1, 2), (2, 2), (-2, 0), (2, 0), (-2, 4), (2, 4)):
            c.px(cx + dx, cy + dy, rune[-2])
        c.px(cx, cy + 2, rune[-1])
        glow(c, cx, cy + 2, 11, rune[-4], 0.5)
    outline(c); shadow(c, 24, 58, 19, 4)
    return c


# ============================================================ estufa: vasos e cápsulas
def planter(i):
    c = C(64, 72)
    # caixa metálica (frente + topo)
    c.rect(14, 46, 36, 18, MET[2]); c.rect(14, 46, 36, 2, MET[5]); c.rect(14, 62, 36, 2, MET[1])
    for x in range(14, 50):
        u = (x - 14) / 36
        for y in range(48, 62):
            c.px(x, y, MET[4] if u < .12 else MET[3] if u < .5 else MET[2] if u < .88 else MET[1])
    for x in (22, 32, 42):
        for y in range(50, 61):
            c.px(x, y, MET[1])
    c.rect(18, 55, 5, 3, hx("#f2994d")); c.px(19, 55, O[5])  # luzinha laranja
    # terra
    c.ellipse(32, 46, 17, 4, hx("#3a2616")); c.ellipse(32, 45, 15, 3, hx("#4d331d"))
    # planta
    rnd = random.Random(60 + i)
    if i == 0:      # folhagem grande
        for (x, y, r) in ((32, 30, 11), (22, 36, 8), (42, 36, 8), (30, 20, 7)):
            orb(c, x, y, r, L[1:6], light=(-0.5, -0.7))
        trunk(c, 32, 36, 46, 3, flare=0)
    elif i == 1:    # florida
        for (x, y, r) in ((32, 32, 10), (22, 38, 7), (42, 38, 7)):
            orb(c, x, y, r, L[1:5], light=(-0.5, -0.7))
        for _ in range(9):
            x, y = rnd.randint(18, 46), rnd.randint(24, 42)
            if c.get(x, y)[3]:
                c.px(x, y, hx("#ff8ae6")); c.px(x + 1, y, hx("#ffd0f6")); c.px(x, y + 1, hx("#d84bbf"))
    elif i == 2:    # trepadeiras bioluminescentes subindo
        for k in range(4):
            x0 = 22 + k * 7
            for y in range(46, 14 + k * 3, -1):
                x = x0 + int(3 * math.sin(y * .3 + k))
                c.px(x, y, T[4]); c.px(x + 1, y, T[3])
                if y % 7 == 0:
                    c.disc(x + 2, y, 1.4, T[7])
        glow(c, 32, 30, 20, T[6], 0.25)
    else:           # seca
        for k in range(5):
            x0 = 20 + k * 6
            c.line(x0, 46, x0 + rnd.randint(-5, 5), 26 + rnd.randint(0, 10), BARK[3])
        for _ in range(8):
            x, y = rnd.randint(18, 46), rnd.randint(28, 44)
            c.px(x, y, mix(BARK[4], O[2], .5))
    outline(c); shadow(c, 32, 64, 20, 4)
    return c


def capsule(i):
    c = C(48, 64)
    c.rect(10, 52, 28, 6, MET[3]); c.rect(10, 52, 28, 1, MET[5]); c.rect(10, 57, 28, 1, MET[1])
    c.rect(12, 49, 24, 3, MET[2])
    # vidro
    for y in range(10, 50):
        for x in range(14, 34):
            u = (x - 14) / 20
            base = B[2] if u < .25 else B[1] if u < .8 else B[0]
            if BAYER4[y % 4, x % 4] < .3:
                base = B[3] if u < .5 else B[1]
            c.px(x, y, base)
    # tampa
    c.rect(12, 6, 24, 5, MET[4]); c.rect(12, 6, 24, 1, MET[6]); c.rect(12, 10, 24, 1, MET[1])
    c.rect(18, 3, 12, 3, MET[3])
    # reflexo do vidro
    for y in range(14, 44):
        if y % 9 < 6:
            c.px(16, y, B[6]); c.px(17, y, B[5])
    # conteúdo
    if i == 0:      # muda verde
        c.line(24, 48, 24, 28, L[3]); c.line(25, 48, 25, 30, L[2])
        orb(c, 20, 30, 5, L[1:6], spec=False); orb(c, 29, 26, 5, L[1:6], spec=False); orb(c, 24, 21, 4, L[2:6], spec=False)
        glow(c, 24, 32, 12, L[5], 0.3)
    elif i == 1:    # vidro rachado, vazia
        for (a, b) in (((18, 14), (24, 30)), ((24, 30), (21, 44)), ((24, 30), (31, 36))):
            c.line(a[0], a[1], b[0], b[1], B[0])
        for y in range(22, 30):
            for x in range(26, 34):
                if (x + y) % 2 == 0:
                    c.px(x, y, CLEAR if False else B[1])
    elif i == 2:    # broto violeta brilhante
        c.line(24, 48, 24, 24, V[3])
        orb(c, 24, 22, 6, V[2:7], spec=True)
        orb(c, 19, 36, 3, V[2:7], spec=False); orb(c, 30, 32, 3, V[2:7], spec=False)
        glow(c, 24, 26, 14, V[5], 0.4)
    else:           # vinhas rompendo o vidro
        for k in range(3):
            x0 = 18 + k * 5
            for y in range(48, 12, -1):
                x = x0 + int(2 * math.sin(y * .4 + k * 2))
                c.px(x, y, L[2]); c.px(x + 1, y, L[3] if y % 3 else L[4])
        for y in range(4, 14):
            c.px(33 + (y % 2), y, L[3])
    outline(c); shadow(c, 24, 58, 17, 4)
    return c


CLEAR = (0, 0, 0, 0)


# ============================================================ coração: raízes e bulbos
def root_mass(i):
    c = C(64, 72)
    rnd = random.Random(300 + i)
    # montículo base escuro
    for y in range(34, 66):
        t = (y - 34) / 31
        half = int(8 + 20 * math.sin(min(1, t * 1.05) * math.pi / 2) ** 1.2)
        for x in range(32 - half, 32 + half + 1):
            u = (x - (32 - half)) / max(1, 2 * half)
            idx = 3 if u < .25 else 2 if u < .6 else 1
            c.px(x, y, mix(V[idx], R[1], .35))
    # raízes que se cruzam
    for k in range(7 + i):
        x0 = rnd.randint(14, 50); y0 = rnd.randint(50, 64)
        pts = [(x0, y0)]
        x, y = x0, y0
        for s in range(rnd.randint(4, 7)):
            x = min(56, max(8, x + rnd.randint(-5, 5))); y = max(8, y - rnd.randint(4, 9))
            pts.append((x, y))
        for a, b in zip(pts, pts[1:]):
            for dx in (0, 1, 2):
                c.line(a[0] + dx, a[1], b[0] + dx, b[1], [R[3], R[2], R[1]][dx])
            c.line(a[0], a[1], b[0], b[1], R[4] if k % 2 else V[4])
    # veios brilhantes
    for _ in range(9):
        x, y = rnd.randint(16, 48), rnd.randint(36, 62)
        if c.get(x, y)[3]:
            c.px(x, y, B[5]); c.px(x, y + 1, B[3])
    outline(c)
    glow(c, 32, 48, 22, V[4], 0.16)
    shadow(c, 32, 64, 24, 5)
    return c


def bulb(i):
    c = C(48, 64)
    ramps = [B, V, B, T][i]
    # haste de raiz
    for y in range(58, 24, -1):
        x = 24 + int(3 * math.sin(y * .22 + i))
        for dx, col in ((-1, R[3]), (0, R[2]), (1, R[1])):
            c.px(x + dx, y, col)
    for (x0, y0) in ((24, 58), (14, 58), (34, 58)):
        c.line(x0, y0, x0 + (x0 - 24) // 2, 52, R[2])
    # bulbo
    cx, cy, r = 24 + int(3 * math.sin(26 * .22 + i)), 20, 11
    orb(c, cx, cy, r, ramps[1:7], light=(-0.45, -0.65))
    c.ring(cx, cy, r + 2, ramps[3], 1)
    # folhinhas
    for dx in (-1, 1):
        c.line(cx, cy + r, cx + dx * 7, cy + r + 5, R[3])
    outline(c)
    glow(c, cx, cy, 17, ramps[5], 0.34)
    shadow(c, 24, 58, 15, 3.6)
    return c


# ============================================================ decoração 32x32
def pebble_set(c, rnd, ramp, n=3):
    for _ in range(n):
        x, y, r = rnd.randint(8, 24), rnd.randint(18, 26), rnd.choice((2, 3, 4))
        orb(c, x, y, r, ramp, light=(-0.5, -0.7), spec=False)
        c.px(x - 1, y + r, (0, 0, 0, 70)); c.px(x, y + r, (0, 0, 0, 70)); c.px(x + 1, y + r, (0, 0, 0, 70))


def decor_item(kind, var, pal):
    c = C(32)
    rnd = random.Random(kind * 131 + var * 17 + pal["seed"])
    if kind == 0:
        for _ in range(7 + var):
            x = rnd.randint(7, 25); h = rnd.randint(5, 10 + var); lean = rnd.randint(-3, 3)
            for s in range(h):
                col = pal["a"][min(3, 1 + s * 3 // h)]
                c.px(x + int(lean * s / h), 26 - s, col)
            c.px(x + lean, 26 - h, pal["a"][4])
    elif kind == 1:
        for _ in range(3 + var % 2):
            x, y = rnd.randint(8, 24), rnd.randint(13, 21)
            c.line(x, y, x, y + 7, pal["a"][2])
            c.px(x - 1, y + 4, pal["a"][3])
            hc = pal["flowers"][rnd.randint(0, len(pal["flowers"]) - 1)]
            c.px(x, y - 1, hc[2]); c.px(x - 1, y, hc[1]); c.px(x + 1, y, hc[1]); c.px(x, y, hc[0]); c.px(x, y + 1, hc[1])
    elif kind == 2:
        pebble_set(c, rnd, pal["stone"], 2 + var % 3)
    else:
        # manchas / poças / pulsos
        cx, cy = 16 + rnd.randint(-2, 2), 18 + rnd.randint(-2, 2)
        rx, ry = 5 + var * 2, 3 + var
        for y in range(cy - ry - 1, cy + ry + 2):
            for x in range(cx - rx - 1, cx + rx + 2):
                d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
                wob = math.sin(x * .8 + var) * .12
                if d + wob <= 1.0:
                    k = d + wob
                    col = pal["stain"][0 if k > .66 else 1 if k > .3 else 2]
                    if k > .5 and BAYER4[y % 4, x % 4] < .45:
                        continue
                    c.px(x, y, col)
        for _ in range(3):
            c.px(cx + rnd.randint(-rx // 2, rx // 2), cy + rnd.randint(-ry // 2, ry // 2), pal["stain"][3])
    return c


DECOR = {
    "decor.png": dict(seed=11, a=L, flowers=[(hx("#ff78e6"), hx("#d84bbf"), hx("#ffd0f6")), (hx("#96ffdc"), hx("#4fb097"), hx("#e8fff6")), (hx("#ffe678"), hx("#e8b640"), hx("#fff7c8"))],
                      stone=W[1:5], stain=[hx("#5a2a66"), hx("#7a3a8a"), hx("#9b4ab0"), hx("#d98aef")]),
    "decor_estufa.png": dict(seed=23, a=T[2:8], flowers=[(hx("#9be8ff"), hx("#2a94bd"), hx("#f0fdff")), (hx("#ffd08a"), hx("#d8782a"), hx("#fff0d0"))],
                             stone=MET[1:5], stain=[hx("#173a3a"), hx("#1f5a58"), hx("#2f7f73"), hx("#8fe0be")]),
    "decor_nucleo.png": dict(seed=37, a=[R[1], R[2], R[3], R[4], R[5]], flowers=[(hx("#8fe0ff"), hx("#2a94bd"), hx("#f0fdff")), (hx("#c4a0ff"), hx("#7b52c4"), hx("#f0e6ff"))],
                             stone=[hx("#2c1a2e"), hx("#4a2d4d"), hx("#6e4a70"), hx("#a07ca4")], stain=[hx("#3b0f1f"), hx("#7a1d36"), hx("#c2395a"), hx("#ff8ae6")]),
}


def make_decor(name, pal):
    items = []
    for i in range(16):
        kind, var = i % 4, i // 4
        c = decor_item(kind, var, pal)
        if kind != 3 or name != "decor.png":
            pass
        items.append(c)
    return sheet(items, 16)


# ============================================================ tilesets (sem emendas)
def tnoise(seed, cells, size=32):
    rng = np.random.RandomState(seed)
    g = rng.rand(cells, cells)
    xs = np.arange(size) * cells / size
    i0 = np.floor(xs).astype(int); f = xs - i0; f = f * f * (3 - 2 * f); i1 = (i0 + 1) % cells
    rows = np.zeros((cells, size))
    for r in range(cells):
        rows[r] = g[r, i0] * (1 - f) + g[r, i1] * f
    out = np.zeros((size, size))
    for y in range(size):
        a, fy = i0[y], f[y]
        out[y] = rows[a] * (1 - fy) + rows[i1[y]] * fy
    return out


def field(seed):
    return 0.18 * tnoise(seed, 4) + 0.47 * tnoise(seed + 1, 8) + 0.35 * tnoise(seed + 2, 16)


def quant(c, n, ramp, spread=.16, bias=0.0, gain=1.5):
    """Preenche o tile pelo campo n (0..1) usando a rampa, com dither de Bayer entre faixas."""
    k = len(ramp)
    nn = np.clip((n - float(n.mean())) * gain + 0.5, 0.0, 1.0)   # centra na média: variantes com o mesmo brilho
    for y in range(32):
        for x in range(32):
            v = nn[y, x] + bias + (BAYER4[y % 4, x % 4] - .5) * spread
            c.px(x, y, ramp[int(np.clip(v * k, 0, k - 1e-3))])


def wput(c, x, y, col):
    c.px(x % 32, y % 32, col)


PAL = {
    "floresta": dict(ground=[hx("#14301d"), hx("#1d4528"), hx("#265a31"), hx("#336e3b")], trail=[hx("#3a2a1c"), hx("#4d3822"), hx("#634830"), hx("#7a5c3e")],
                     stone=[hx("#3a4244"), hx("#4f5a5a"), hx("#687474"), hx("#8a9894")], tuft=[L[2], L[3], L[4]], fleck=[hx("#ff78e6"), hx("#ffe678"), hx("#96ffdc")]),
    "bacia": dict(ground=[hx("#142034"), hx("#1c2e48"), hx("#25405e"), hx("#2f5272")], trail=[hx("#2a3a4c"), hx("#3a4e62"), hx("#4d6680"), hx("#6482a0")],
                  stone=[hx("#1c2840"), hx("#2a3a58"), hx("#3c5070"), hx("#566e90")], tuft=[T[3], T[4], T[5]], fleck=[hx("#8fe0ff"), hx("#c4f6ff"), hx("#6fd8f0")]),
    "santuario": dict(ground=[hx("#262c28"), hx("#343c36"), hx("#444e46"), hx("#586258")], trail=[hx("#4c4f48"), hx("#60645a"), hx("#767a6e"), hx("#8e9284")],
                      stone=[hx("#30363a"), hx("#444c50"), hx("#5e686c"), hx("#7c888a")], tuft=[L[1], L[2], L[3]], fleck=[hx("#8fe0be"), hx("#d2fbe6"), hx("#4fb097")]),
    "jardim": dict(ground=[hx("#1a1430"), hx("#241c42"), hx("#30265a"), hx("#3e3170")], trail=[hx("#3a2d58"), hx("#4a3a70"), hx("#5e4b8a"), hx("#7762a6")],
                   stone=[hx("#2a2438"), hx("#3c3452"), hx("#52486c"), hx("#706488")], tuft=[V[2], V[3], V[4]], fleck=[hx("#8fe0be"), hx("#dcc4ff"), hx("#4fb097")]),
    "estufa": dict(ground=[hx("#112326"), hx("#183034"), hx("#203e42"), hx("#2b4f52")], trail=[hx("#2a3a38"), hx("#384c48"), hx("#4a6460"), hx("#617e78")],
                   stone=[hx("#1c2a2e"), hx("#2c4044"), hx("#3f585c"), hx("#587478")], tuft=[L[2], L[3], T[5]], fleck=[hx("#f2994d"), hx("#96ffdc"), hx("#ffe678")]),
    "nucleo": dict(ground=[hx("#1a0c1c"), hx("#2a1230"), hx("#3b1a42"), hx("#4e2456")], trail=[hx("#3d1a2c"), hx("#552440"), hx("#733250"), hx("#924464")],
                   stone=[hx("#241626"), hx("#38223c"), hx("#52325a"), hx("#744a7c")], tuft=[R[2], R[3], V[4]], fleck=[hx("#8fe0ff"), hx("#c4a0ff"), hx("#ff8ae6")]),
}
CONTAM = [hx("#2a0c2a"), hx("#431244"), hx("#5e1a5e"), hx("#7a2278")]


def tile_ground(pal, seed, var, bio):
    c = C(32)
    quant(c, field(seed), pal["ground"], spread=.16, gain=1.25)
    rnd = random.Random(seed * 3 + var)
    if bio in ("floresta", "jardim", "santuario"):
        for _ in range(3 + var * 3):
            x, y = rnd.randint(0, 31), rnd.randint(2, 31)
            h = rnd.randint(2, 4)
            for s in range(h):
                wput(c, x + (s // 2) * rnd.choice((-1, 1)) * 0, y - s, pal["tuft"][min(2, s)])
    if bio == "bacia":
        for _ in range(2 + var * 2):
            x, y = rnd.randint(0, 31), rnd.randint(0, 31)
            for s in range(rnd.randint(3, 6)):
                wput(c, x + s, y, pal["fleck"][2])
    if bio == "estufa":
        # placas metálicas com junta e parafusos; a vegetação brota das rachaduras
        for y in range(32):
            wput(c, 0, y, pal["ground"][0]); wput(c, 16, y, pal["ground"][0] if var % 2 else pal["ground"][1])
        for x in range(32):
            wput(c, x, 0, pal["ground"][0]); wput(c, x, 16, pal["ground"][1])
        for (x, y) in ((2, 2), (14, 2), (18, 18), (30, 30), (2, 30), (30, 14)):
            wput(c, x, y, pal["ground"][3])
        for _ in range(var * 2):
            x, y = rnd.choice((rnd.randint(0, 31), 16)), rnd.randint(1, 31)
            for s in range(rnd.randint(2, 4)):
                wput(c, x, y - s, pal["tuft"][min(2, s)])
    if bio == "nucleo":
        # veios de raiz pulsando sob o chão
        for _ in range(1 + var):
            x, y = rnd.randint(0, 31), rnd.randint(0, 31)
            for s in range(rnd.randint(8, 16)):
                wput(c, x + s, y + int(2 * math.sin(s * .5)), R[2]); wput(c, x + s, y + int(2 * math.sin(s * .5)) - 1, R[1])
        for _ in range(var):
            wput(c, rnd.randint(0, 31), rnd.randint(0, 31), pal["fleck"][rnd.randint(0, 2)])
    for _ in range(var + 1):
        wput(c, rnd.randint(0, 31), rnd.randint(0, 31), pal["fleck"][rnd.randint(0, 2)] if bio in ("floresta", "jardim", "santuario") and var >= 2 else pal["ground"][3])
    return c


def tile_trail(pal, seed, var, bio):
    c = C(32)
    quant(c, field(seed + 40), pal["trail"], spread=.16, gain=1.35)
    rnd = random.Random(seed * 5 + var)
    for _ in range(5 + var * 2):  # seixos
        x, y = rnd.randint(0, 31), rnd.randint(0, 31)
        wput(c, x, y, pal["trail"][3]); wput(c, x + 1, y, pal["trail"][3]); wput(c, x, y + 1, pal["trail"][0]); wput(c, x + 1, y + 1, pal["trail"][0])
    if bio in ("estufa", "santuario"):
        for x in range(32):
            wput(c, x, 15 + (var % 2), pal["trail"][0]); wput(c, x, 14 + (var % 2), pal["trail"][3])
    return c


def tile_stone(pal, seed, var, bio):
    c = C(32)
    quant(c, field(seed + 70), pal["stone"], spread=.12, bias=.05, gain=1.3)
    rnd = random.Random(seed * 7 + var)
    # lajes
    cuts_y = [0, 11 + rnd.randint(-2, 2), 22 + rnd.randint(-2, 2)]
    for ci, y0 in enumerate(cuts_y):
        for x in range(32):
            wput(c, x, y0, pal["stone"][0]); wput(c, x, y0 + 1, pal["stone"][3] if bio != "bacia" else pal["stone"][2])
        xo = [4, 17, 10][ci] + var * 3
        for yy in range(y0, cuts_y[(ci + 1) % 3] if ci < 2 else 32 + 0):
            wput(c, xo + (var % 2) * 11, yy, pal["stone"][0])
    # rachadura
    x, y = rnd.randint(4, 27), rnd.randint(4, 27)
    for s in range(rnd.randint(4, 8)):
        wput(c, x + s // 2 * rnd.choice((-1, 1)), y + s, pal["stone"][0])
    return c


def tile_contam(pal, seed, var, bio):
    c = C(32)
    quant(c, field(seed + 100), CONTAM, spread=.2, gain=1.6)
    rnd = random.Random(seed * 11 + var)
    for _ in range(1 + var):
        x, y = rnd.randint(2, 29), rnd.randint(2, 29); rx, ry = rnd.randint(2, 3), rnd.randint(1, 2)
        for yy in range(-ry - 1, ry + 2):
            for xx in range(-rx - 1, rx + 2):
                d = (xx / rx) ** 2 + (yy / max(ry, .5)) ** 2
                if d <= 1.0:
                    wput(c, x + xx, y + yy, hx("#b438a8") if d < .4 else hx("#8a2a86"))
        wput(c, x - 1, y - 1, hx("#e890e0"))
    for _ in range(2 + var):
        wput(c, rnd.randint(0, 31), rnd.randint(0, 31), hx("#a040a0"))
    return c


def tile_wall(pal, seed, var, bio):
    c = C(32)
    base = [hx("#2a1234"), hx("#40204e"), hx("#58306a"), hx("#76468a")]
    quant(c, field(seed + 130), base, spread=.1)
    for y in (0, 16):
        for x in range(32):
            wput(c, x, y, base[0]); wput(c, x, y + 1, base[3])
    off = 0 if var % 2 == 0 else 8
    for (y0, o) in ((1, off), (17, (off + 16) % 32)):
        for yy in range(y0, y0 + 15):
            wput(c, o, yy, base[0]); wput(c, o + 16, yy, base[0])
    return c


def make_tileset(bio, seed):
    pal = PAL[bio]
    img = C(128, 160)
    for row, fn in enumerate((tile_ground, tile_trail, tile_stone, tile_contam, tile_wall)):
        for var in range(4):
            img.paste(fn(pal, seed + row * 10 + var * 3, var, bio), var * 32, row * 32)
    return img


# ============================================================ muralha de raízes
def wall_h():
    c = C(32, 36)
    top = [hx("#8a62a0"), hx("#6e4a86"), hx("#563868")]
    front = [hx("#2a1234"), hx("#40204e"), hx("#58306a"), hx("#76468a")]
    for y in range(0, 12):
        for x in range(32):
            c.px(x, y, top[0] if y < 2 else top[1] if y < 9 else top[2])
    for x in range(32):
        c.px(x, 11, front[0])
    # raízes sobre o topo
    for x in range(32):
        y = 5 + int(2.2 * math.sin(x / 32 * math.tau * 2))
        c.px(x, y, hx("#b07ac4")); c.px(x, y + 1, hx("#4a2a5c"))
    for y in range(12, 36):
        for x in range(32):
            c.px(x, y, front[2] if y < 14 else front[1])
    for (y0, off) in ((12, 0), (24, 16)):
        for x in range(32):
            c.px(x, y0, front[3] if y0 > 12 else front[3]); c.px(x, y0 + 11, front[0])
        for x in (off, off + 16):
            for yy in range(y0, y0 + 12):
                c.px(x % 32, yy, front[0])
    for x in range(32):
        c.px(x, 35, front[0])
    for (x, y) in ((6, 18), (22, 30), (13, 29), (27, 17)):
        c.px(x, y, hx("#b07ac4")); c.px(x + 1, y, hx("#7a4a92"))
    return c


def wall_v():
    c = C(36, 32)
    for y in range(32):
        for x in range(36):
            u = x / 35
            c.px(x, y, hx("#8a62a0") if u < .08 else hx("#6e4a86") if u < .6 else hx("#563868") if u < .92 else hx("#2a1234"))
    for y in range(32):
        x = 17 + int(2.2 * math.sin(y / 32 * math.tau * 2))
        c.px(x, y, hx("#b07ac4")); c.px(x + 1, y, hx("#4a2a5c"))
    for y in (0, 16):
        for x in range(36):
            c.px(x, y, hx("#2a1234")); c.px(x, y + 1, hx("#76468a"))
    for x in (0, 35):
        for y in range(32):
            c.px(x, y, hx("#2a1234"))
    return c


# ============================================================ saída
def save(c, name):
    c.save(os.path.join(OUT, name))


def reg(man, name, fw, fh, n, anim="variants", extra=None):
    man["world/" + name] = {"frame": [fw, fh], "anims": [{"name": anim, "row": 0, "frames": n, "fps": 1 if anim == "variants" else 0, "loop": False}]}
    if extra:
        man["world/" + name].update(extra)


def main():
    man_path = os.path.join(ROOT, "assets", "art", "manifest.json")
    man = json.load(open(man_path, encoding="utf-8"))
    sheets = {
        "trees.png": ([tree_broadleaf(0), tree_pine(1), tree_glow(2), tree_baobab(3)], 64, 72),
        "crystals.png": ([crystal_cluster(i) for i in range(4)], 48, 64),
        "pillars.png": ([pillar(i) for i in range(4)], 48, 64),
        "planters.png": ([planter(i) for i in range(4)], 64, 72),
        "capsules.png": ([capsule(i) for i in range(4)], 48, 64),
        "roots.png": ([root_mass(i) for i in range(4)], 64, 72),
        "bulbs.png": ([bulb(i) for i in range(4)], 48, 64),
    }
    for name, (frames, w, h) in sheets.items():
        save(sheet(frames, 4), name)
        reg(man, name, w, h, 4)
    for name, pal in DECOR.items():
        save(make_decor(name, pal), name)
        reg(man, name, 32, 32, 16, anim="decor")
    for k, bio in enumerate(("floresta", "bacia", "santuario", "jardim", "estufa", "nucleo")):
        save(make_tileset(bio, 100 + k * 50), f"tileset_{bio}.png")
        reg(man, f"tileset_{bio}.png", 32, 32, 4, anim="grid", extra={"rows": ["chao", "trilha", "pedra", "contaminado", "muralha"]})
    save(wall_h(), "wall_raizes.png"); save(wall_v(), "wall_raizes_v.png")
    json.dump(man, open(man_path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("OK: arte do mundo gerada em", OUT)


if __name__ == "__main__":
    main()
