"""Sprites dos inimigos comuns em pixel art (mesmas folhas/animações do manifest)."""
import os, math, json, random
from pix import C, hx, BAYER4, sheet, contact
from ui_pal import T, V, G, R, B, L, O, W, glow, orb, edge_color
from creat import *

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "assets", "art", "enemies")
MAN = json.load(open(os.path.join(ROOT, "assets", "art", "manifest.json")))
TAU = math.pi * 2


def S(ph, k=1.0):
    return math.sin(ph * TAU * k)


def assemble(name, anims):
    """anims: {nome_da_anim: [C, ...]} na ordem/linhas do manifest."""
    info = MAN["enemies/%s.png" % name]
    fw, fh = info["frame"]
    cols = max(a["frames"] for a in info["anims"])
    rows = max(a["row"] for a in info["anims"]) + 1
    out = C(cols * fw, rows * fh)
    for a in info["anims"]:
        frs = anims[a["name"]]
        assert len(frs) == a["frames"], (name, a["name"], len(frs), a["frames"])
        for i, fr in enumerate(frs):
            out.paste(fr, i * fw, a["row"] * fh)
    out.save(os.path.join(OUT, name + ".png"))
    return out


def counts(name):
    return {a["name"]: a["frames"] for a in MAN["enemies/%s.png" % name]["anims"]}


# ============================================================ LARVA-FÉRTIL
def larva(ph, walk=False):
    c = C(32, 32)
    # corpo segmentado de perfil (cabeça à direita); a onda percorre os segmentos
    segs = [(8.5, 4.6), (13.2, 5.2), (18.2, 5.6), (23.2, 4.9)]
    for i, (sx, sr) in enumerate(segs):
        wave = S(ph - i * 0.14) * (1.6 if walk else 0.7)
        cy = 21 - sr * 0.35 - wave
        # perninhas finas sob cada segmento
        for dx in ((1.5,) if i != 3 else ()):
            lift = max(0.0, S(ph * (1 if walk else 0) * 1 - i * 0.14 + dx * 0.1)) * 2 if walk else 0
            tline(c, sx + dx, cy + sr * 0.7, sx + dx + 1.2, 28 - lift, 1.4, V[3]); c.px(int(sx + dx + 1.2), int(29 - lift), V[5])
        ell(c, sx, cy, sr, sr * 0.92, R[1:7] if i < 3 else R[2:7])
        c.line(int(sx - sr * 0.55), int(cy - sr * 0.7), int(sx - sr * 0.55), int(cy + sr * 0.5), R[1])
        c.px(int(sx + 1), int(cy + sr * 0.35), B[4]) if i % 2 == 0 else c.px(int(sx + 1), int(cy + sr * 0.35), V[5])
    hx_, hy_ = 23.2, 21 - 4.9 * 0.35 - S(ph - 3 * 0.14) * (1.6 if walk else 0.7)
    # mandíbulas e olhos brilhantes
    c.poly([(hx_ + 4, hy_ + 1), (hx_ + 8, hy_ + 3), (hx_ + 4, hy_ + 4)], W[5])
    c.poly([(hx_ + 4, hy_ + 5), (hx_ + 8, hy_ + 4.5), (hx_ + 3, hy_ + 3)], W[4])
    eye(c, int(hx_ + 1), int(hy_ - 2), B[4], big=True)
    tline(c, hx_ - 1, hy_ - 5, hx_ + 1, hy_ - 8 + S(ph, 2), 1, R[3])
    c.px(hx_ + 1, hy_ - 9 + S(ph, 2), L[5])
    return finish(squash(c, 0.93, 1.0))


def make_larva():
    n = counts("larva")
    idle = [larva(i / n["idle"]) for i in range(n["idle"])]
    walk = [larva(i / n["walk"], True) for i in range(n["walk"])]
    return {"idle": idle, "walk": walk, "hurt": hurt_frames(idle[0], n["hurt"]),
            "death": death_frames(idle[0], n["death"], [R[4], R[5], B[4], V[5]], 1)}


# ============================================================ CORTARRAIZ
def corta(ph, mode="walk", k=0.0):
    c = C(32, 32)
    crouch = {"windup": 2 + k * 2, "recover": 1.5 - k}.get(mode, 0)
    stretch = 3 if mode == "charge" else 0
    by = 19 + crouch
    # cauda: chicote de raiz
    sw = S(ph) * (1.5 if mode != "charge" else 0.5)
    limb(c, [(7, by - 1), (3, by - 4 + sw), (1, by - 9 + sw * 2)], 3, 1.5, O[1:6])
    c.px(1, int(by - 10 + sw * 2), L[5])
    # pernas
    for i, (xh, back) in enumerate(((9, True), (12, True), (20, False), (23, False))):
        phs = ph * TAU + i * math.pi / 2
        if mode == "charge":
            fx = (-4 if back else 4) + math.cos(phs) * 1.5
            lift = 0
        elif mode == "windup":
            fx = (2 if not back else -1)
            lift = 0
        else:
            fx = math.cos(phs) * 3
            lift = max(0.0, math.sin(phs)) * 3
        foot_y = 29 - lift
        kx = xh + fx * 0.4 + (1 if not back else -1)
        limb(c, [(xh, by + 3), (kx, by + 7 - lift * 0.5 - crouch * 0.5), (xh + fx, foot_y)], 3, 1.8, O[0:5])
    ell(c, 15 - stretch * 0.4, by + 0.5, 10 + stretch, 4.6 - stretch * 0.3, [O[0], O[1], O[2], O[3], O[4], O[5]])

    # crista de raízes: poucas lâminas grandes de casca com ponta luminosa
    flare = 3 if mode == "windup" else 0
    ytop = by - 4.0 + stretch * 0.3
    for j, x in enumerate((9, 14, 19)):
        h = 8 + flare + int(1.2 * S(ph + j * 0.13)) - (3 if mode == "charge" else 0)
        lean = -3 if mode == "charge" else -1
        c.poly([(x - 2.5, ytop + 2), (x + lean, ytop - h), (x + 2.5, ytop + 2)], BARK[3])
        c.poly([(x - 2.5, ytop + 2), (x + lean, ytop - h), (x, ytop + 2)], BARK[5])
        c.line(int(x), int(ytop), int(x + lean), int(ytop - h + 2), BARK[1])
        c.px(int(x + lean), int(ytop - h), L[6]); c.px(int(x + lean), int(ytop - h + 1), L[5]); c.px(int(x + lean), int(ytop - h + 2), L[4])
    # cabeça
    hy = by - 3 + (1 if mode == "windup" else 0)
    ell(c, 24.5 + stretch * 0.5, hy, 5.5, 4.6, O[1:7])
    c.poly([(26.5 + stretch * 0.5, hy - 1), (31, hy + 1.5), (26.5 + stretch * 0.5, hy + 3.5)], O[3])
    c.px(30, int(hy + 1.5), O[0])
    eye(c, int(25 + stretch * 0.5), int(hy - 2), G[5])
    c.poly([(21 + stretch * 0.5, hy - 3), (22.5 + stretch * 0.5, hy - 9), (24.5 + stretch * 0.5, hy - 3)], BARK[4])
    c.px(int(22.5 + stretch * 0.5), int(hy - 9), L[5])
    if mode == "charge":
        for yy in (14, 19, 24):
            for xx in range(0, 8):
                if (xx + yy) % 2 == 0 and xx > (yy % 5):
                    c.px(xx, yy, O[3] if xx > 3 else O[2])
    return finish(squash(c, 0.93, 1.0))


def make_corta():
    n = counts("cortarraiz")
    walk = [corta(i / n["walk"]) for i in range(n["walk"])]
    return {"walk": walk, "windup": [corta(0.1, "windup", i / 2.0) for i in range(n["windup"])],
            "charge": [corta(i / 3.0, "charge") for i in range(n["charge"])],
            "recover": [corta(0.2, "recover", i) for i in range(n["recover"])],
            "death": death_frames(walk[0], n["death"], [O[4], L[5], G[5]], 2)}


# ============================================================ FLOR DE RUPTURA
def flor(ph, shoot=0.0):
    c = C(32, 32)
    sway = S(ph) * 1.3
    hx_, hy_ = 16 + sway, 13 - shoot * 0.5
    limb(c, [(16, 31), (15 + sway * 0.3, 25), (hx_, hy_ + 6)], 3.2, 2.6, L[1:6])
    for side in (-1, 1):
        c.poly([(16 + side * 1, 26), (16 + side * 8, 22 - side * 0 + S(ph + side) * 0.8), (16 + side * 9, 25), (16 + side * 2, 28.5)], L[3])
        c.poly([(16 + side * 1, 26), (16 + side * 8, 22), (16 + side * 4, 26)], L[4])
        c.line(16 + side * 2, 26, 16 + side * 8, 23, L[2])
    for k in range(6):
        a = k * TAU / 6 + 0.35 + S(ph) * 0.08 - shoot * 0.1
        rr = (8.0 + shoot * 2.5 + 0.8 * S(ph + k * 0.1))
        ell_rot(c, hx_ + math.cos(a) * rr * 0.62, hy_ + math.sin(a) * rr * 0.58, a, 6.2 + shoot, 2.7, [V[0], V[1], V[2], PINK[2], PINK[3], PINK[5]] if k % 2 else [V[0], V[2], V[3], V[4], PINK[3], PINK[4]])
        c.px(int(hx_ + math.cos(a) * (rr + 4 + shoot)), int(hy_ + math.sin(a) * (rr * 0.92 + 4 + shoot)), PINK[6])
    mr = 5.0 + shoot * 1.8
    c.disc(hx_, hy_, mr, V[0])
    c.ring(hx_, hy_, mr, PINK[3], 1.4)
    for k in range(10):
        a = k * TAU / 10 + 0.15
        ix, iy = hx_ + math.cos(a) * (mr - 1), hy_ + math.sin(a) * (mr - 1)
        c.poly([(ix, iy), (hx_ + math.cos(a + 0.2) * (mr - 3.2), hy_ + math.sin(a + 0.2) * (mr - 3.2)), (hx_ + math.cos(a - 0.2) * (mr - 3.2), hy_ + math.sin(a - 0.2) * (mr - 3.2))], WHITE)
    orb(c, hx_, hy_, 1.9 + shoot * 0.9, [R[2], R[3], O[4], G[5], WHITE], spec=False)
    if shoot > 0.5:
        for (dx, dy) in ((6, -3), (8, 0), (7, 3), (9, -1)):
            c.px(int(hx_ + dx), int(hy_ + dy), G[5] if (dx + dy) % 2 else PINK[5])
    return finish(c)


def make_flor():
    n = counts("flor")
    idle = [flor(i / n["idle"]) for i in range(n["idle"])]
    return {"idle": idle, "shoot": [flor(0.3, [0.4, 1.0, 0.7, 0.2][i]) for i in range(n["shoot"])],
            "death": death_frames(idle[0], n["death"], [PINK[4], V[5], G[5]], 3)}


# ============================================================ ESPORÍDEO
def espo(ph, mode="walk", k=0.0):
    c = C(32, 32)
    wob = S(ph) * 1.0 if mode == "walk" else 0
    puff = k if mode == "spore" else 0
    for xo in (-3, 3):
        limb(c, [(16 + xo, 25), (16 + xo * 1.6 + (S(ph + xo) * 1.5 if mode == "walk" else 0), 28), (16 + xo * 2, 30)], 3, 2.4, BARK[0:5])
    ell(c, 16 + wob * 0.5, 22.5, 6.8, 6, [hx("#2a3014"), hx("#5a6a2a"), hx("#8a9c44"), hx("#b8c868"), hx("#e2ea9c")])
    eye(c, 12 + int(wob * 0.5), 22, G[5]); eye(c, 18 + int(wob * 0.5), 22, G[5])
    cap_ry = 7.2 - puff * 1.6
    ell(c, 16 + wob, 13.5 + puff * 1.5, 11.8 + puff, cap_ry, OLIVE[0:6])
    for xx in range(6, 27):
        c.px(xx, int(14 + puff * 1.5 + cap_ry * 0.8), OLIVE[0])
        if xx % 2:
            c.px(xx, int(15 + puff * 1.5 + cap_ry * 0.8), OLIVE[1])
    for (sx, sy, r) in ((11, 11, 1.8), (18, 9.5, 1.5), (21, 13, 1.6), (14, 15, 1.2)):
        c.disc(sx + wob, sy + puff * 1.5, r, OLIVE[5])
        c.px(int(sx + wob), int(sy + puff * 1.5), OLIVE[1])
    rnd = random.Random(4)
    nb = [2, 3, 2, 2][int(ph * 4) % 4] if mode == "walk" else int(3 + puff * 5)
    for i in range(nb):
        a = rnd.uniform(-2.9, -0.2)
        rr = 10 + (puff * 6 if mode == "spore" else S(ph + i * 0.3) * 2 + 2) + rnd.uniform(0, 3)
        x, y = 16 + math.cos(a) * rr, 12 + math.sin(a) * rr * 0.8
        if mode == "spore":
            c.ring(x, y, 1.6 + (i % 2), L[5], 1.0)
        else:
            c.px(x, y, OLIVE[5])
    return finish(c)


def make_espo():
    n = counts("esporideo")
    walk = [espo(i / n["walk"]) for i in range(n["walk"])]
    return {"walk": walk, "spore": [espo(0.0, "spore", (i + 1) / n["spore"]) for i in range(n["spore"])],
            "death": death_frames(walk[0], n["death"], [OLIVE[5], L[5], OLIVE[4]], 4)}


# ============================================================ PARASITA DE SINAL
def para(ph, pulse=0.0, k=-1):
    c = C(32, 32)
    bob = S(ph) * 1.3
    cy = 14 + bob
    for i in range(4):
        x0 = 10.5 + i * 3.6
        ps = ph * TAU + i * 1.3
        pts = [(x0, cy + 5), (x0 + math.sin(ps) * 1.8, cy + 9), (x0 + math.sin(ps + 1.1) * 3, cy + 11), (x0 + math.sin(ps + 2.0) * 3.4, cy + 14)]
        limb(c, pts, 2.2, 1.2, B[1:6])
        c.px(int(pts[-1][0]), int(pts[-1][1]) + 1, B[6])
    ell(c, 16, cy, 9.5, 7, [B[0], B[1], B[2], B[3], B[4], B[5]])
    for xx in range(8, 25):
        yy = int(cy + 4.5 - ((xx - 16) / 9.0) ** 2 * 1.5)
        if xx % 2 == 0:
            c.px(xx, yy, B[5])
    orb(c, 16, cy, 3.2 + pulse * 1.2, [V[2], B[3], B[4], B[6], WHITE], spec=False)
    tline(c, 16, cy - 7, 16, cy - 11, 1, B[4])
    orb(c, 16, cy - 12, 1.6, [B[2], B[5], WHITE], spec=False)
    if k >= 0:
        rr = 9 + k * 3.2
        for a in range(0, 360, 6):
            if (a // 12 + k) % 2 == 0:
                c.px(16 + rr * math.cos(math.radians(a)), cy + rr * 0.8 * math.sin(math.radians(a)), B[5] if k < 3 else B[3])
    return finish(c)


def make_para():
    n = counts("parasita")
    fl = [para(i / n["float"]) for i in range(n["float"])]
    return {"float": fl, "pulse": [para(0.25, 1.0, i) for i in range(n["pulse"])],
            "death": death_frames(fl[0], n["death"], [B[4], B[6], WHITE], 5)}


# ============================================================ CASCA-TÚMULO
def casca(ph, mode="walk"):
    c = C(48, 48)
    bob = S(ph) * 1.0
    for i, x in enumerate((10, 17, 30, 37)):
        lift = max(0.0, S(ph + i * 0.25)) * 3 if mode == "walk" else 0
        c.rect(x - 3, 36 - int(lift), 7, 10 + int(lift) - 0, SHELL[1])
        c.rect(x - 3, 36 - int(lift), 3, 10, SHELL[2])
        c.rect(x - 3, 44 - int(lift), 7, 2, SHELL[0])
    ell(c, 41.5, 33 + bob * 0.5, 6.8, 5.2, SHELL[0:6])
    eye(c, 40, 31, G[5]); eye(c, 44, 31, G[5])
    for xx in range(38, 47):
        c.px(xx, 36, SHELL[0])
    ell(c, 23, 27 + bob, 19.5, 15.5, SHELL[0:7], light=(-0.45, -0.7))
    # placas: anéis de crista
    for (rx, ry, dy) in ((16, 11.5, 1), (11, 7.5, 3), (6, 4, 5)):
        for a in range(190, 351, 3):
            x = 23 + rx * math.cos(math.radians(a)); y = 27 + bob + dy + ry * math.sin(math.radians(a))
            c.px(x, y, SHELL[1]); c.px(x, y + 1, SHELL[5] if a % 6 else SHELL[4])
    # rachaduras com brilho âmbar
    for seed, (x0, y0) in enumerate(((22, 17), (14, 21), (31, 20))):
        rnd = random.Random(seed + 7)
        x, y = x0, y0 + bob
        for s in range(9):
            nx, ny = x + rnd.choice([-1, 0, 1, 1]) * (1 if seed != 1 else -1), y + 1
            c.px(nx, ny, G[4] if s % 3 else G[5])
            if s % 2 == 0:
                c.px(nx + 1, ny, G[2])
            x, y = nx, ny
    for (mx, my) in ((12, 18), (14, 20), (13, 21), (18, 15), (28, 16)):
        c.px(mx, my + int(bob), L[3]); c.px(mx + 1, my + int(bob), L[2])
    return finish(c)


def make_casca():
    n = counts("casca")
    walk = [casca(i / n["walk"]) for i in range(n["walk"])]
    return {"walk": walk, "hurt": hurt_frames(walk[0], n["hurt"]), "death": death_frames(walk[0], n["death"], [SHELL[5], G[5], L[4]], 6)}


# ============================================================ ANOMALIA (elite)
def anom(ph, hop=0.0):
    c = C(48, 48)
    pulse = 0.5 + 0.5 * S(ph)
    sq = hop
    cy = 28 - hop * 2
    for i, x in enumerate((13, 19, 29, 35, 24)):
        ps = ph * TAU + i
        pts = [(x, cy + 8), (x + math.sin(ps) * 2, cy + 12), (x + math.sin(ps + 1) * 3, 45)]
        limb(c, pts, 4, 2.4, R[0:5])
    ell(c, 24, cy, 14 + sq * 1.2, 13 - sq * 1.2, R[1:7])
    for k in range(9):
        a = math.radians(-172 + k * 19.5)
        ln = 8 + pulse * 3 + (k % 2) * 3
        bx, by = 24 + math.cos(a) * 11.5, cy + math.sin(a) * 11
        tx, ty = 24 + math.cos(a) * (11.5 + ln), cy + math.sin(a) * (11 + ln)
        px_, py_ = -math.sin(a) * 2.6, math.cos(a) * 2.6
        c.poly([(bx - px_, by - py_), (tx, ty), (bx + px_, by + py_)], G[3])
        c.poly([(bx - px_, by - py_), (tx, ty), (bx, by)], G[5])
        c.px(int(tx), int(ty), WHITE)
    for (x0, y0, x1, y1) in ((24, cy + 10, 18, cy + 2), (24, cy + 10, 30, cy + 3), (16, cy + 4, 12, cy - 2), (32, cy + 4, 36, cy - 1)):
        c.line(x0, y0, x1, y1, R[2])
    eye(c, 22, int(cy - 4), G[5], big=True)
    eye(c, 15, int(cy - 1), G[5]); eye(c, 30, int(cy - 1), G[5])
    for xx in range(19, 29):
        c.px(xx, int(cy + 4 + abs(xx - 24) * 0.0), R[0]) if xx % 2 == 0 else c.px(xx, int(cy + 5), WHITE)
    return finish(c)


def make_anom():
    n = counts("anomalia")
    walk = [anom(i / n["walk"], max(0.0, S(i / n["walk"], 1)) * 0.6) for i in range(n["walk"])]
    return {"walk": walk, "hurt": hurt_frames(walk[0], n["hurt"]), "death": death_frames(walk[0], n["death"], [R[4], G[5], R[5]], 7)}


# ============================================================ NINHO
def ninho(ph, mode="idle", k=0.0):
    c = C(64, 64)
    pul = S(ph)
    # base de raízes
    ell(c, 32, 55, 27, 8, BARK[0:5])
    rnd = random.Random(3)
    for i in range(16):
        a = rnd.uniform(0, math.pi)
        x0 = 32 + math.cos(a) * rnd.uniform(4, 20)
        tline(c, x0, 56, 32 + math.cos(a) * 29, 48 - math.sin(a) * 10 + rnd.uniform(-3, 5), 2 + (i % 2), BARK[2 + i % 2])
    # espiral de raízes no topo
    for i in range(5):
        x = 24 + i * 4
        limb(c, [(x, 40), (x + math.sin(ph * TAU + i) * 2 - 1, 30), (x + (i - 2) * 1.5, 20 - (i % 2) * 3)], 3, 1.5, BARK[1:6])
    sacs = [(20, 42, 9.5), (44, 43, 9), (32, 36, 11.5), (27, 50, 7.5), (40, 51, 7)]
    for j, (sx, sy, sr) in enumerate(sacs):
        r = sr + pul * 0.6 * (1 if j % 2 else -1)
        if mode == "spawn" and j == 2:
            r += k * 3.5
        ell(c, sx, sy, r, r * 0.92, PINK[0:6])
        # larva dentro (silhueta) e brilho
        c.disc(sx + 1, sy + 1, r * 0.45, PINK[0])
        eye(c, int(sx - 1), int(sy), B[4]) if j % 2 == 0 or j == 2 else None
        c.px(int(sx - r * 0.45), int(sy - r * 0.5), WHITE); c.px(int(sx - r * 0.45) + 1, int(sy - r * 0.5), PINK[6])
    if mode == "spawn":
        for i in range(int(2 + k * 5)):
            c.px(32 + (i - 3) * 2, int(44 + i * (k * 3)), PINK[5]); c.px(32 + (i - 3) * 2, int(45 + i * (k * 3)), PINK[3])
    # fios pegajosos
    for (x0, y0, x1, y1) in ((10, 50, 22, 40), (54, 50, 44, 41), (20, 33, 34, 26), (46, 32, 36, 26)):
        for t_ in range(0, 11, 2):
            c.px(x0 + (x1 - x0) * t_ / 10, y0 + (y1 - y0) * t_ / 10 - math.sin(t_ * 0.3) * 2, PINK[4])
    return finish(c)


def make_ninho():
    n = counts("ninho")
    idle = [ninho(i / n["idle"]) for i in range(n["idle"])]
    return {"idle": idle, "spawn": [ninho(0.25, "spawn", (i + 1) / n["spawn"]) for i in range(n["spawn"])],
            "death": death_frames(idle[0], n["death"], [PINK[4], PINK[5], B[4], V[5]], 8)}


MAKERS = {"larva": make_larva, "cortarraiz": make_corta, "flor": make_flor, "esporideo": make_espo,
          "parasita": make_para, "casca": make_casca, "anomalia": make_anom, "ninho": make_ninho}

if __name__ == "__main__":
    import sys
    only = sys.argv[1:] or list(MAKERS)
    os.makedirs(OUT, exist_ok=True)
    res = {}
    for nm in only:
        if nm in MAKERS:
            res[nm] = assemble(nm, MAKERS[nm]())
    from PIL import Image
    rows = []
    for nm, im in res.items():
        info = MAN["enemies/%s.png" % nm]
        fw, fh = info["frame"]
        im2 = Image.new("RGBA", (im.w, fh * 2), (30, 40, 42, 255))
        src = im.img()
        # linha 0 e a de morte
        im2.alpha_composite(src.crop((0, 0, im.w, fh)), (0, 0))
        dr = [a for a in info["anims"] if a["name"] == "death"][0]["row"]
        im2.alpha_composite(src.crop((0, dr * fh, im.w, dr * fh + fh)), (0, fh))
        rows.append(im2)
    cw = max(r.width for r in rows) * 3
    ch = sum(r.height * 3 + 6 for r in rows)
    S_ = Image.new("RGBA", (cw, ch), (30, 40, 42, 255))
    y = 0
    for r in rows:
        S_.alpha_composite(r.resize((r.width * 3, r.height * 3), Image.NEAREST), (0, y)); y += r.height * 3 + 6
    S_.save("/tmp/enemies_new.png")
    print("ok", S_.size)
