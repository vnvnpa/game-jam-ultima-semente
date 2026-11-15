"""Chefes, estrutura e auras de elite em pixel art (mesmas folhas do manifest)."""
import os, math, random
from pix import C, hx, BAYER4
from ui_pal import T, V, G, R, B, L, O, W, glow, orb, edge_color
from creat import *
from gen_enemies_pixel import assemble, counts, S, TAU, OUT, MAN


def moss(c, cx, cy, rx, ry, seed=1):
    rnd = random.Random(seed)
    for y in range(int(cy - ry), int(cy + ry + 1)):
        for x in range(int(cx - rx), int(cx + rx + 1)):
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if d < 1 and c.inb(x, y) and c.a[y, x, 3] and rnd.random() > d * 0.9:
                c.px(x, y, L[3] if rnd.random() < 0.7 else L[4])
                if rnd.random() < 0.15:
                    c.px(x, y - 1, L[5])


# ============================================================ GUARDIÃO DE RAÍZES (96x96)
def guardian(ph=0.0, arm=0.0, spread=0.0, core_r=7.5, rage=False, dust=0.0, pods=0.0, dx=0):
    c = C(96, 96)
    sway = S(ph) * 1.0 + dx
    for side in (-1, 1):
        fx = 48 + side * 22
        limb(c, [(48 + side * 13, 66), (48 + side * 19, 78), (fx, 90)], 11, 8, BARK[0:6])
        for k in (-1, 0, 1):
            tline(c, fx, 90, fx + k * 6 + side * 2, 94, 2.4, BARK[2])
    ell(c, 48 + sway * 0.5, 50, 22, 24, BARK[0:7])
    rnd = random.Random(5)
    for x in range(29, 68, 4):
        y = rnd.randint(28, 40)
        while y < 72:
            ln = rnd.randint(6, 14)
            for yy in range(y, min(72, y + ln)):
                if c.a[yy, x, 3]:
                    c.px(x, yy, BARK[1]); 
                    if c.a[yy, x + 1, 3]:
                        c.px(x + 1, yy, BARK[4])
            y += ln + rnd.randint(3, 8)
    ell(c, 48 + sway * 0.5, 52, 9.5, 11.5, [BARK[0], BARK[0], BARK[1], BARK[1], BARK[2]])
    core = [R[1], R[3], O[3], O[4], G[5], WHITE] if rage else [B[1], B[3], B[4], B[5], B[6], WHITE]
    glow(c, 48 + sway * 0.5, 52, core_r + 7, core[2], 0.5)
    orb(c, 48 + sway * 0.5, 52, core_r, core, spec=False)
    for k in range(8):
        a = k * TAU / 8 + ph * 0.5
        c.px(48 + sway * 0.5 + math.cos(a) * (core_r + 3.5), 52 + math.sin(a) * (core_r + 3.5) * 1.1, O[5] if rage else V[5])
    if rage:
        for (x0, y0, x1, y1) in ((36, 36, 40, 50), (60, 36, 56, 48), (42, 66, 46, 58), (56, 68, 52, 60)):
            c.line(x0, y0, x1, y1, O[4]); c.line(x0 + 1, y0, x1 + 1, y1, R[3])
    for side in (-1, 1):
        sx, sy = 48 + side * 25 + sway * 0.5, 37
        relax = (48 + side * 33, 76)
        up = (48 + side * 31, 17)
        fxp = relax[0] + (up[0] - relax[0]) * max(arm, -0.5) + side * spread * 7
        fyp = relax[1] + (up[1] - relax[1]) * max(arm, -0.5)
        if arm < 0:
            fyp = 82 + arm * -10
            fxp = 48 + side * 28
        elbow = ((sx + fxp) / 2 + side * (9 + spread * 5), (sy + fyp) / 2 - 2)
        ell(c, sx, sy, 9.5, 8, BARK[1:7])
        moss(c, sx, sy - 2, 8, 4, side + 3)
        limb(c, [(sx, sy), elbow, (fxp, fyp)], 10, 7.5, BARK[0:6])
        ell(c, fxp, fyp, 7.5, 6.5, BARK[1:7])
        for k in (-1, 0, 1):
            tline(c, fxp + k * 3, fyp + 3, fxp + k * 4.5, fyp + 9, 2.2, BARK[3])
    ell(c, 48 + sway * 0.4, 21, 10.5, 9.5, BARK[1:7])
    ecol = O[5] if rage else B[5]
    eye(c, 42 + int(sway * 0.4), 19, ecol, big=True); eye(c, 51 + int(sway * 0.4), 19, ecol, big=True)
    for xx in range(43, 54, 2):
        c.px(xx, 26, BARK[0]); c.px(xx + 1, 27, BARK[1])
    for side in (-1, 1):
        base = (48 + side * 7, 13)
        tline(c, base[0], base[1] + 1, 48 + side * 15, 4, 3.4, BARK[3])
        tline(c, 48 + side * 12, 7, 48 + side * 20, 6, 2.2, BARK[3])
        tline(c, 48 + side * 15, 4, 48 + side * 14, 1, 2, BARK[4])
    moss(c, 48, 14, 8, 3, 9)
    c.sel_outline(edge_color)
    if dust > 0:
        for a in range(0, 360, 3):
            r = 10 + dust * 36
            x = 48 + math.cos(math.radians(a)) * r
            y = 90 + math.sin(math.radians(a)) * r * 0.22
            if BAYER4[int(y) % 4, int(x) % 4] > dust * 0.7 - 0.1 and c.inb(x, y):
                c.px(x, y, BARK[5] if a % 6 else L[4])
                c.px(x, y - 1, BARK[4])
    for i in range(int(pods * 6)):
        px_ = 18 + i * 12 % 60
        orb(c, px_, 90 - (i % 2) * 2, 2.6, [L[1], L[2], L[3], L[4], L[5]], spec=False)
        c.px(px_, 86 - (i % 2) * 2, L[6])
    return c


def make_guardiao():
    n = counts("guardiao")
    idle = [guardian(i / n["idle"], arm=0.0, core_r=7.5 + 0.8 * S(i / n["idle"])) for i in range(n["idle"])]
    slam_p = [(0.35, 0.0), (0.75, 0.0), (1.0, 0.0), (-0.25, 0.3), (-0.2, 0.7), (0.0, 1.0)]
    slam = [guardian(0.0, arm=a, core_r=8, dust=d) for (a, d) in slam_p]
    summ = [guardian(0.2 + i * 0.1, arm=0.55, spread=[0.2, 0.6, 1.0, 1.0, 0.8, 0.4][i], core_r=[8, 9.5, 11.5, 12.5, 11, 9][i], pods=[0, 0.2, 0.5, 0.8, 1.0, 1.0][i]) for i in range(n["summon"])]
    ph2 = [guardian(i / 4.0, arm=0.15 + 0.1 * S(i / 4.0), core_r=8.5 + i % 2, rage=True, dx=[-1, 1, -1, 1][i]) for i in range(n["phase2"])]
    return {"idle": idle, "slam": slam, "summon": summ, "phase2": ph2,
            "death": death_frames(idle[0], n["death"], [BARK[5], L[4], B[5], WHITE], 11, foot=92, amt=3.0)}


# ============================================================ JARDINEIRO VAZIO (96x96)
def hexshield(c, cx, cy, r, ph, ramp=B):
    for y in range(int(cy - r), int(cy + r + 1)):
        for x in range(int(cx - r), int(cx + r + 1)):
            d = math.hypot(x - cx, (y - cy)) / r
            if d > 1:
                continue
            if d > 0.93:
                c.px(x, y, ramp[4] if d < 0.985 else ramp[3])
            else:
                hexv = ((x + 2 * y) % 14 == 0 or (x - 2 * y) % 14 == 0) and (x + y) % 2 == 0
                if hexv and d > 0.15:
                    c.px(x, y, ramp[3])
                elif (0.02 + d ** 3 * 0.12) > BAYER4[y % 4, x % 4]:
                    c.px(x, y, ramp[2])
    for a in range(int(ph * 360), int(ph * 360) + 60, 2):
        c.px(cx + (r - 1) * math.cos(math.radians(a)), cy + (r - 1) * math.sin(math.radians(a)), ramp[6])
        c.px(cx + (r - 2) * math.cos(math.radians(a)), cy + (r - 2) * math.sin(math.radians(a)), ramp[5])


def gardener(ph=0.0, mode="shielded", k=0.0):
    c = C(96, 96)
    bob = S(ph) * 1.6
    cy = 44 + bob
    # propulsor
    glow(c, 48, cy + 24, 11, B[3], 0.7)
    orb(c, 48, cy + 23, 4, [B[1], B[3], B[5], B[6], WHITE], spec=False)
    # braços de poda
    stab = k if mode == "roots" else 0
    for side in (-1, 1):
        for j, (ox, oy) in enumerate(((17, 7), (14, 14))):
            sx, sy = 48 + side * ox, cy + oy
            reach = 1 - stab
            tx = 48 + side * (30 + j * 6 - stab * 6)
            ty = (cy + 28 + j * 8 + bob) * reach + 86 * stab
            elbow = (sx + side * 12, (sy + ty) / 2 - 4)
            limb(c, [(sx, sy), elbow, (tx, ty)], 5, 3.5, W[0:6])
            c.line(int(tx), int(ty), int(tx + side * 4), int(ty + 6), W[5]); c.line(int(tx), int(ty), int(tx - side * 2), int(ty + 6), W[4])
    # corpo
    orb(c, 48, cy, 20, [W[0], W[1], W[2], W[3], W[4], W[5], W[6]])
    for a in range(200, 341, 2):
        for rr in (14.0, 15.0):
            x, y = 48 + rr * 1.35 * math.cos(math.radians(a)), cy + 6 + rr * 0.55 * math.sin(math.radians(a))
            c.px(x, y, O[3] if rr < 14.5 else O[5])
    for yy in range(int(cy + 7), int(cy + 10)):
        for xx in range(32, 65):
            if abs(xx - 48) < 17 and c.a[yy, xx, 3]:
                c.px(xx, yy, O[2] if yy == int(cy + 9) else O[3])
    # lente / núcleo
    if mode == "exposed":
        open_ = 4
        for side in (-1, 1):
            c.poly([(48 + side * (3 + open_), cy - 14), (48 + side * (17 + open_), cy - 6), (48 + side * (17 + open_), cy + 8), (48 + side * (3 + open_), cy + 12)], W[2])
            c.line(48 + side * (3 + open_), cy - 14, 48 + side * (3 + open_), cy + 12, W[5])
        glow(c, 48, cy, 14, R[3], 0.75)
        orb(c, 48, cy - 1, 7 + 0.8 * S(ph * 2), [R[1], R[3], R[4], O[4], G[5], WHITE], spec=False)
        for (x0, y0, x1, y1) in ((40, cy - 10, 44, cy - 4), (56, cy - 10, 52, cy - 4), (42, cy + 8, 45, cy + 3)):
            c.line(x0, int(y0), x1, int(y1), G[4])
    else:
        c.ell = None
        ell(c, 48, cy - 1, 10, 10, [W[0], W[0], W[1], W[2]])
        glowk = k if mode == "shoot" else 0
        orb(c, 48, cy - 1, 6.5 + glowk * 3, [B[1], B[3], B[5], B[6], WHITE] if glowk < 0.5 else [O[3], O[4], G[5], G[6], WHITE], spec=False)
        c.px(46, int(cy - 4), WHITE); c.px(47, int(cy - 4), WHITE)
        if mode == "shoot":
            for i in range(int(glowk * 8)):
                c.px(48 + i * 4 - 6, int(cy - 1 + (i % 2)), G[5])
    # broto de planta no topo e lanternas
    limb(c, [(48, cy - 19), (47 + S(ph) * 1.5, cy - 25), (50, cy - 31)], 3, 2, L[1:6])
    for side in (-1, 1):
        c.poly([(49, cy - 28), (49 + side * 9, cy - 33 + S(ph + side) * 1), (49 + side * 8, cy - 28)], L[4])
    for side in (-1, 1):
        tline(c, 48 + side * 13, cy - 13, 48 + side * 16, cy - 8, 1, W[4])
        orb(c, 48 + side * 16, cy - 6, 2.4, [G[2], G[4], G[5], G[6]], spec=False)
    c.sel_outline(edge_color)
    if mode == "shielded":
        hexshield(c, 48, 46, 41, ph)
    if mode == "roots":
        for i in range(int(2 + stab * 9)):
            x = 14 + i * 8
            h = int(stab * (6 + (i % 3) * 4))
            for yy in range(h):
                c.px(x + (yy % 3 == 0), 92 - yy, BARK[3] if yy % 2 else BARK[4])
            c.px(x, 92 - h, L[5])
    return c


def make_jardineiro():
    n = counts("jardineiro")
    sh = [gardener(i / n["shielded"], "shielded") for i in range(n["shielded"])]
    ex = [gardener(i / n["exposed"], "exposed") for i in range(n["exposed"])]
    shoot = [gardener(0.1, "shoot", [0.3, 0.7, 1.0, 0.5][i]) for i in range(n["shoot"])]
    roots = [gardener(0.1, "roots", (i + 1) / n["roots"]) for i in range(n["roots"])]
    return {"shielded": sh, "exposed": ex, "shoot": shoot, "roots": roots,
            "death": death_frames(ex[0], n["death"], [W[5], O[4], G[5], R[4]], 12, foot=90, amt=3.0)}


# ============================================================ CORAÇÃO DE NYMARA (128x128)
HEART = [hx(s) for s in ["#12061a", "#2a0a2e", "#4a1450", "#7a2a78", "#a84aa0", "#e08ad0", "#ffd0f6"]]
HEART_D = [HEART[0], HEART[0], HEART[1], HEART[1], HEART[2], HEART[2], HEART[3], HEART[4], HEART[5]]


def heart(ph=0.0, mode="shielded", k=0.0):
    c = C(128, 128)
    beat = 1.0 + 0.03 * max(0.0, S(ph * 2)) ** 2
    cx, cy = 64, 68
    rnd = random.Random(21)
    for i in range(16):
        x1 = rnd.uniform(4, 124)
        tline(c, 64 + (x1 - 64) * 0.35, 106, x1, 120 + rnd.uniform(-3, 5), 6 - (i % 3), BARK[1 + i % 3])
    # coroa de tentáculos curvos com pontas luminosas
    for i in range(5):
        a = -math.pi / 2 + (i - 2) * 0.5
        sw = S(ph + i * 0.2) * 4
        L_ = 24 + (2 - abs(i - 2)) * 6
        pts = [(cx + (i - 2) * 11 + math.sin(s_ * 1.1 + i + ph * TAU) * 6 * s_ / 6.0 + (i - 2) * s_ * 1.6, cy - 30 - s_ * L_ / 6.0) for s_ in range(7)]
        limb(c, pts, 9, 3, BARK[0:6])
        orb(c, pts[-1][0], pts[-1][1], 2.2, [HEART[2], HEART[4], HEART[5], WHITE], spec=False)
    lt = (-0.3, -0.5)
    ell(c, cx, cy + 14, 38 * beat, 34 * beat, HEART_D, light=lt)
    ell_rot(c, cx - 15, cy + 32, 2.2, 22 * beat, 13, HEART_D, light=lt)
    ell_rot(c, cx + 15, cy + 32, 0.94, 22 * beat, 13, HEART_D, light=lt)
    ell(c, cx - 21, cy - 8, 29 * beat, 27 * beat, HEART_D, light=lt)
    ell(c, cx + 21, cy - 8, 29 * beat, 27 * beat, HEART_D, light=lt)
    for sgn in (-1, 1):
        for j, (x0, y0) in enumerate(((cx + sgn * 40, cy - 22), (cx + sgn * 46, cy + 6), (cx + sgn * 26, cy + 38))):
            pts = [(x0, y0 + i * 3) for i in range(0, 9)]
            for i, (px_, py_) in enumerate(pts):
                xx = px_ - sgn * (i * 2.2) + math.sin(i * 0.9 + j) * 2
                c.px(xx, py_, V[4] if i % 3 else V[6]); c.px(xx + 1, py_, HEART[1])
    exposed = mode == "exposed"
    cr = 11 + (k * 4 if mode == "summon" else 0) + (2 if exposed else 0)
    ccy = cy + 2
    glow(c, cx, ccy, cr + 12, B[3], 0.8 if exposed or mode == "summon" else 0.3)
    orb(c, cx, ccy, cr, [B[1], B[3], B[4], B[5], B[6], WHITE], spec=False)
    for a in range(0, 360, 20):
        c.px(cx + (cr + 3) * math.cos(math.radians(a + ph * 90)), ccy + (cr + 3) * math.sin(math.radians(a + ph * 90)), V[5])
    if not exposed:
        ell(c, cx, ccy, 14, 14, STONE[0:7])
        ell(c, cx, ccy, 8, 8, [STONE[1], STONE[2], STONE[3]])
        c.px(cx, ccy, B[6]); c.px(cx - 1, ccy, B[5]); c.px(cx + 1, ccy, B[5]); c.px(cx, ccy - 1, B[5]); c.px(cx, ccy + 1, B[5])
    for i in range(8):
        a = math.radians(i * 45 + 22.5)
        if not exposed:
            rr, ang, ra, rb = 21, a + math.pi / 2, 12, 4.4
        else:
            rr, ang, ra, rb = 38 + 2 * S(ph + i * 0.1), a, 11, 4.4
        px_, py_ = cx + math.cos(a) * rr, ccy + math.sin(a) * rr * 0.92
        ell_rot(c, px_, py_, ang, ra, rb, STONE[0:7])
        c.px(int(px_), int(py_), G[5] if exposed else (V[5] if S(ph + i * 0.125) > 0 else V[3]))
    if mode == "slam":
        for side in (-1, 1):
            reach = k
            hi = reach < 0.6
            pts = [(cx + side * 40, cy - 6), (cx + side * 54, 44 if hi else 84), (cx + side * (50 - (0 if hi else 4)), 28 if hi else 110)]
            limb(c, pts, 15, 8, BARK[0:6])
            ell(c, pts[-1][0], pts[-1][1], 8, 7, BARK[1:7])
        if k > 0.6:
            for a in range(0, 360, 3):
                x, y = cx + math.cos(math.radians(a)) * (28 + k * 34), 117 + math.sin(math.radians(a)) * 6
                if BAYER4[int(y) % 4, int(x) % 4] > 0.3 and c.inb(x, y):
                    c.px(x, y, BARK[5])
    if mode == "summon":
        for i in range(int(k * 6)):
            px_ = 14 + i * 20
            orb(c, px_, 113, 5, [HEART[1], HEART[3], HEART[4], HEART[5], HEART[6]], spec=False)
            c.px(px_ - 1, 111, WHITE)
    c.sel_outline(edge_color)
    return c


def make_coracao():
    n = counts("coracao")
    idle = [heart(i / n["idle"], "shielded") for i in range(n["idle"])]
    slam = [heart(0.1, "slam", [0.2, 0.45, 0.7, 0.95, 1.0, 0.8][i]) for i in range(n["slam"])]
    summ = [heart(0.2, "summon", (i + 1) / n["summon"]) for i in range(n["summon"])]
    shl = [heart(i / n["shielded"], "shielded") for i in range(n["shielded"])]
    exp = [heart(i / n["exposed"], "exposed") for i in range(n["exposed"])]
    return {"idle": idle, "slam": slam, "summon": summ, "shielded": shl, "exposed": exp,
            "death": death_frames(exp[0], n["death"], [PINK[4], PINK[5], B[5], WHITE], 13, foot=118, amt=4.0)}


# ============================================================ ESTRUTURA (48x48)
def estrutura(ph=0.0):
    c = C(48, 48)
    pul = 0.5 + 0.5 * S(ph)
    for side in (-1, 1):
        limb(c, [(24 + side * 7, 44), (24 + side * 12, 42), (24 + side * 17, 46)], 4, 2.5, BARK[0:5])
    c.poly([(15, 44), (16, 16), (32, 16), (33, 44)], STONE[3])
    c.poly([(15, 44), (16, 16), (21, 16), (21, 44)], STONE[5])
    c.poly([(28, 44), (28, 16), (32, 16), (33, 44)], STONE[2])
    for yy in range(18, 44, 6):
        c.line(16, yy, 32, yy, STONE[1])
        c.line(17, yy + 1, 31, yy + 1, STONE[4])
    for i, yy in enumerate((22, 30, 38)):
        gx = 24 + (i % 2) * 2 - 1
        col = V[5] if pul > 0.4 + i * 0.1 else V[3]
        c.px(gx, yy, col); c.px(gx + 1, yy, col); c.px(gx, yy + 1, col); c.px(gx - 1, yy + 2, col)
    c.rect(13, 14, 22, 3, STONE[5]); c.rect(13, 16, 22, 1, STONE[1])
    glow(c, 24, 8, 12, B[3], 0.45 + pul * 0.3)
    c.poly([(24, -1 + 0), (31, 8), (24, 16), (17, 8)], B[4])
    c.poly([(24, 0), (17, 8), (24, 16)], B[5])
    c.poly([(24, 16), (31, 8), (24, 8)], V[4])
    c.px(22, 5, WHITE); c.px(23, 5, WHITE)
    for (mx, my) in ((17, 20), (30, 26), (19, 33)):
        c.px(mx, my, L[3]); c.px(mx + 1, my, L[4])
    c.sel_outline(edge_color)
    return c


def make_estrutura():
    n = counts("estrutura")
    idle = [estrutura(i / n["idle"]) for i in range(n["idle"])]
    return {"idle": idle, "hurt": hurt_frames(idle[0], n["hurt"]), "death": death_frames(idle[0], n["death"], [STONE[5], B[5], V[5]], 14, amt=1.5)}


# ============================================================ AURAS DE ELITE (64x64)
def aura(kind, ph):
    c = C(64, 64)
    cx = cy = 31.5
    if kind == "blindada":
        hexshield(c, 32, 32, 28, ph)
    elif kind == "veloz":
        for k in range(3):
            a0 = ph * 360 * 1.0 + k * 120
            for a in range(0, 70, 2):
                r = 25 + 2 * math.sin(math.radians(a * 3))
                x, y = cx + r * math.cos(math.radians(a0 - a)), cy + r * math.sin(math.radians(a0 - a))
                if a < 50 or a % 4 == 0:
                    c.px(x, y, WHITE if a < 8 else B[5] if a < 30 else B[3])
                    if a < 16:
                        c.px(x, y + 1, B[4])
    elif kind == "explosiva":
        pul = 0.5 + 0.5 * math.sin(ph * TAU)
        for k in range(10):
            a = math.radians(k * 36 + ph * 18)
            ln = 7 + pul * 4 + (k % 2) * 3
            bx, by = cx + math.cos(a) * 22, cy + math.sin(a) * 22
            tx, ty = cx + math.cos(a) * (22 + ln), cy + math.sin(a) * (22 + ln)
            px_, py_ = -math.sin(a) * 2.2, math.cos(a) * 2.2
            c.poly([(bx - px_, by - py_), (tx, ty), (bx + px_, by + py_)], O[3])
            c.poly([(bx - px_, by - py_), (tx, ty), (bx, by)], G[5])
        for a in range(0, 360, 8):
            c.px(cx + 21 * math.cos(math.radians(a)), cy + 21 * math.sin(math.radians(a)), R[4] if a % 16 else G[5])
    else:  # regenerante
        for a in range(0, 360, 6):
            if (a // 12) % 2 == 0:
                c.px(cx + 25 * math.cos(math.radians(a)), cy + 25 * math.sin(math.radians(a)), L[3])
        rnd = random.Random(2)
        for i in range(7):
            a = rnd.uniform(0, TAU)
            rr = 18 + rnd.uniform(0, 8)
            yy = cy + math.sin(a) * rr - ((ph + i * 0.15) % 1.0) * 8
            xx = cx + math.cos(a) * rr
            col = L[5] if (i + int(ph * 4)) % 2 == 0 else L[4]
            for d in range(-2, 3):
                c.px(xx + d, yy, col); c.px(xx, yy + d, col)
            c.px(xx, yy, WHITE)
    return c


def make_auras():
    n = counts("anomalia_auras")
    return {k: [aura(k, i / n[k]) for i in range(n[k])] for k in ("blindada", "veloz", "explosiva", "regenerante")}


MAKERS = {"guardiao": make_guardiao, "jardineiro": make_jardineiro, "coracao": make_coracao, "estrutura": make_estrutura, "anomalia_auras": make_auras}

if __name__ == "__main__":
    import sys
    from PIL import Image
    only = sys.argv[1:] or list(MAKERS)
    res = {}
    for nm in only:
        res[nm] = assemble(nm, MAKERS[nm]())
    tiles = []
    for nm, im in res.items():
        info = MAN["enemies/%s.png" % nm]
        fw, fh = info["frame"]
        src = im.img()
        row = Image.new("RGBA", (fw * 5, fh * 2), (30, 40, 42, 255))
        for r in (0, 1):
            if r < len(info["anims"]):
                a = info["anims"][r]
                for f in range(min(5, a["frames"])):
                    row.alpha_composite(src.crop((f * fw, a["row"] * fh, f * fw + fw, a["row"] * fh + fh)), (f * fw, r * fh))
        tiles.append(row)
    for i, t in enumerate(tiles):
        t.resize((t.width * 2, t.height * 2), Image.NEAREST).save("/tmp/boss_%d.png" % i)
    print("ok", len(tiles))
