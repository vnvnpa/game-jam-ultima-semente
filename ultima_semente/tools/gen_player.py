#!/usr/bin/env python3
"""Arte do Kael (3 direções), da arma biológica, do clarão do disparo e dos projéteis.
Chamado por gen_art.py. Estilo: explorador espacial laranja com visor ciano e um
dispositivo de contenção biológica verde nas costas/ombros."""
import math
from PIL import Image, ImageDraw
from pixelkit import HD, tone, tint_white, with_alpha

SUIT = (242, 140, 51, 255); WHITE = (242, 251, 246, 255); HELM = (210, 214, 220, 255)
VISOR = (77, 230, 255, 255); VISOR_D = (31, 143, 168, 255); GREY = (140, 148, 150, 255); GREY_D = (70, 78, 84, 255)
GREEN = (102, 217, 128, 255); GREEN_D = (47, 143, 77, 255); PURPLE = (166, 102, 255, 255); YELLOW = (255, 209, 89, 255)


def _legs(h, d, a, b):
    """a, b = (dx, dy) das duas pernas."""
    if d == "side":
        for x0, (dx, dy) in ((13.2, a), (16.2, b)):
            h.shaded_rect(x0 + dx, 22.4 + dy, x0 + 3.4 + dx, 27.6 + dy, GREY_D, r=1.0)
            h.shaded_rect(x0 + dx - .3, 26.4 + dy, x0 + 4.4 + dx, 29.6 + dy, GREY, r=1.0)
    else:
        for x0, (dx, dy) in ((11.4, a), (16.8, b)):
            h.shaded_rect(x0 + dx, 22.6 + dy, x0 + 3.8 + dx, 27.8 + dy, GREY_D, r=1.0)
            h.shaded_rect(x0 + dx - .2, 26.4 + dy, x0 + 4.2 + dx, 29.6 + dy, GREY, r=1.0)


def draw_player(d, bob=0.0, a=(0, 0), b=(0, 0), lean=0.0, shake=0.0):
    h = HD(32, 32, S=6)
    _legs(h, d, (a[0] + shake, a[1]), (b[0] + shake, b[1]))
    y = bob
    x = shake
    if d == "down":
        h.shaded_rect(6.6 + x, 12.6 + y, 10.2 + x, 22 + y, SUIT, r=1.4)
        h.shaded_rect(21.8 + x, 12.6 + y, 25.4 + x, 22 + y, SUIT, r=1.4)
        h.rect(6.4 + x, 20.2 + y, 10.4 + x, 22.8 + y, GREY, r=1.0); h.rect(21.6 + x, 20.2 + y, 25.6 + x, 22.8 + y, GREY, r=1.0)
        h.shaded_rect(10 + x, 12 + y, 22 + x, 24 + y, SUIT, r=2.2)
        h.rect(10 + x, 17.2 + y, 22 + x, 18.5 + y, WHITE)
        h.rect(10 + x, 21.4 + y, 22 + x, 22.6 + y, GREY_D)
        h.ellipse(16 + x, 14.8 + y, 1.3, 1.3, VISOR); h.ellipse(16 + x, 14.8 + y, .5, .5, WHITE)
        h.shaded_rect(6.8 + x, 10.6 + y, 10.6 + x, 14.4 + y, GREEN, r=1.5)
        h.shaded_rect(21.4 + x, 10.6 + y, 25.2 + x, 14.4 + y, GREEN, r=1.5)
        h.shaded_ellipse(16 + x, 8.2 + y, 6.9, 6.7, HELM)
        h.ellipse(16 + x, 9.3 + y, 4.9, 3.5, VISOR_D)
        h.ellipse(15.5 + x, 9 + y, 3.9, 2.7, VISOR)
        h.ellipse(13.6 + x, 7.9 + y, 1.3, .7, WHITE)
    elif d == "up":
        h.shaded_rect(6.6 + x, 12.6 + y, 10.2 + x, 22 + y, SUIT, r=1.4)
        h.shaded_rect(21.8 + x, 12.6 + y, 25.4 + x, 22 + y, SUIT, r=1.4)
        h.shaded_rect(10 + x, 12 + y, 22 + x, 24 + y, SUIT, r=2.2)
        h.rect(10 + x, 21.4 + y, 22 + x, 22.6 + y, GREY_D)
        h.shaded_rect(10.8 + x, 11 + y, 21.2 + x, 21.6 + y, GREEN, r=2.2)
        h.rect(12 + x, 13 + y, 20 + x, 14 + y, GREEN_D); h.rect(12 + x, 17 + y, 20 + x, 18 + y, GREEN_D)
        h.line([(16 + x, 12 + y), (16 + x, 20.6 + y)], PURPLE, .9)
        h.ellipse(16 + x, 16 + y, 1.5, 1.5, WHITE)
        h.shaded_ellipse(16 + x, 8.2 + y, 6.9, 6.7, HELM, hi=False)
        h.line([(11 + x, 7 + y), (21 + x, 7 + y)], tone(HELM, -.3), .8)
        h.rect(14.6 + x, 2.4 + y, 17.4 + x, 4 + y, YELLOW, r=.6)
    else:  # side (olhando para a direita)
        px = lean
        h.shaded_rect(9.2 + x, 11 + y, 14 + x, 20.6 + y, GREEN, r=1.8)
        h.line([(10.4 + x, 13 + y), (12.8 + x, 13 + y)], GREEN_D, .8); h.line([(10.4 + x, 16.4 + y), (12.8 + x, 16.4 + y)], GREEN_D, .8)
        h.shaded_rect(12 + x + px * .5, 12 + y, 20.4 + x + px * .5, 24 + y, SUIT, r=2.2)
        h.rect(12 + x + px * .5, 17.2 + y, 20.4 + x + px * .5, 18.5 + y, WHITE)
        h.rect(12 + x + px * .5, 21.4 + y, 20.4 + x + px * .5, 22.6 + y, GREY_D)
        h.shaded_rect(14.4 + x + px * .5, 12.8 + y, 18.4 + x + px * .5, 21.6 + y, SUIT, r=1.4)
        h.rect(14.2 + x + px * .5, 20 + y, 18.6 + x + px * .5, 22.6 + y, GREY, r=1.0)
        h.shaded_ellipse(16.4 + x + px, 8.2 + y, 6.4, 6.6, HELM)
        h.ellipse(19.6 + x + px, 9.2 + y, 3.3, 3.2, VISOR_D)
        h.ellipse(19.9 + x + px, 8.9 + y, 2.5, 2.4, VISOR)
        h.ellipse(19.2 + x + px, 7.9 + y, .9, .6, WHITE)
    return h.img()


def tint_cyan(img):
    import numpy as np
    a = np.array(img).astype(float); m = a[..., 3] > 0
    a[..., 0][m] = a[..., 0][m] * .3 + 80 * .7; a[..., 1][m] = a[..., 1][m] * .3 + 230 * .7; a[..., 2][m] = a[..., 2][m] * .3 + 255 * .7
    return Image.fromarray(a.astype("uint8"), "RGBA")


def pose(d, anim, t):
    s = math.sin(t * math.tau)
    if anim == "idle":
        return draw_player(d, bob=s * .35)
    if anim == "walk":
        up, up2 = max(0.0, s) * 1.9, max(0.0, -s) * 1.9
        if d == "side":
            return draw_player(d, bob=-abs(s) * .9, a=(s * 3.0, -up), b=(-s * 3.0, -up2))
        return draw_player(d, bob=-abs(s) * .9, a=(0, -up), b=(0, -up2))
    if anim == "hurt":
        return tint_white(draw_player(d, bob=.6, shake=(-1.2 if t < .5 else 1.2)), .7)
    if anim == "dash":
        base = draw_player(d, lean=1.8 if d == "side" else 0.0, bob=.2, a=(2.5, -1.0) if d == "side" else (0, 0), b=(-2.5, 0) if d == "side" else (0, 0))
        out = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        off = {"side": (-1, 0), "down": (0, -1), "up": (0, 1)}[d]
        for n, al in ((3, .16), (2, .26), (1, .4)):
            out.alpha_composite(tint_cyan(with_alpha(base, al)), (off[0] * n * 4, off[1] * n * 4))
        out.alpha_composite(base)
        return out
    raise ValueError(anim)


def death_frame(t):
    """Kael desaba: achata em direção ao chão, esmaece e solta esporos."""
    base = draw_player("side", bob=0)
    k = min(1.0, t * 1.4)
    sx, sy = 1 + 0.25 * k, max(0.28, 1 - 0.72 * k)
    nw, nh = round(32 * sx), round(32 * sy)
    r = base.resize((nw, nh), Image.NEAREST)
    im = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    crop_x = max(0, (nw - 32) // 2)
    im.alpha_composite(r.crop((crop_x, 0, crop_x + min(32, nw), nh)), (max(0, 16 - nw // 2), 29 - nh + 3 if nh < 32 else 0))
    if t > .5:
        im = with_alpha(im, max(.25, 1 - (t - .5) * 1.5))
    d = ImageDraw.Draw(im)
    for i in range(5):
        px = 10 + i * 3 + int(t * 3); py = 26 - int(t * 14) - i % 3 * 2
        if t > .15 and 0 <= py < 32:
            d.rectangle([px, py, px + 1, py + 1], fill=(160, 255, 170, int(255 * (1 - t))))
    return im


def make_weapon():
    h = HD(20, 10, S=8)
    h.shaded_rect(0.4, 3.0, 5.6, 7.2, GREY_D, r=1.0)
    h.rect(1.2, 2.2, 4.4, 3.6, GREY, r=.5)
    h.poly([(5, 2.9), (15.2, 3.5), (16.6, 5), (15.2, 6.5), (5, 7.1)], GREEN)
    h.poly([(5, 2.9), (15.2, 3.5), (16.6, 5), (6, 4.4)], tone(GREEN, .3))
    h.poly([(5, 7.1), (15.2, 6.5), (16.6, 5), (6, 5.7)], GREEN_D)
    for x in (7.4, 9.8, 12.2):
        h.line([(x, 3.1), (x, 6.9)], GREEN_D, .6)
    h.poly([(8, 7), (9.4, 9.2), (10.8, 7)], GREEN_D)
    h.poly([(11.6, 7), (12.8, 8.8), (13.8, 6.8)], GREEN_D)
    h.ellipse(16.6, 5, 1.9, 1.9, PURPLE)
    h.ellipse(16.7, 5, .9, .9, WHITE)
    return h.img()


def muzzle_frames():
    fr = []
    for i in range(3):
        h = HD(16, 16, S=8)
        r = (3.2, 5.2, 3.0)[i]
        h.ellipse(7.5, 8, r + 1.6, r + .6, (120, 255, 190, 90))
        for k in range(6):
            a = k * math.tau / 6 + i * .5
            h.poly([(7.5 + math.cos(a - .25) * 1.2, 8 + math.sin(a - .25) * 1.2), (7.5 + math.cos(a) * (r + 2.4), 8 + math.sin(a) * (r + 2.4)), (7.5 + math.cos(a + .25) * 1.2, 8 + math.sin(a + .25) * 1.2)], (190, 255, 210, 255))
        h.ellipse(7.5, 8, r * .55, r * .55, (255, 255, 255, 255))
        fr.append(h.img(outline=False))
    return fr


def proj_frames():
    rows = []
    fr = []   # espinho simbiótico (jogador)
    for i in range(3):
        h = HD(16, 16, S=8)
        h.ellipse(9.6, 8, 6.4 + i * .3, 3.2 + i * .25, (120, 255, 170, 55))
        h.ellipse(2.4, 8 + (i - 1) * .7, 1.1, .6, (150, 255, 175, 150)); h.ellipse(4.4, 8.3 - (i - 1) * .3, .9, .5, (170, 255, 195, 210))
        h.poly([(4.8, 8), (7, 5.8), (12, 6.8), (15.3, 8), (12, 9.2), (7, 10.2)], (96, 222, 112, 255))
        h.poly([(7, 5.8), (12, 6.8), (15.3, 8), (9, 7.5)], (176, 255, 150, 255))
        h.poly([(7, 10.2), (12, 9.2), (15.3, 8), (9, 8.7)], (46, 140, 76, 255))
        h.poly([(8.2, 6.2), (9.4, 4.6), (10.4, 6.5)], (60, 170, 90, 255)); h.poly([(8.2, 9.8), (9.4, 11.4), (10.4, 9.5)], (46, 140, 76, 255))
        h.ellipse(14.4, 8, .9, .7, (255, 255, 255, 255))
        fr.append(h.img())
    rows.append(("espinho", fr))
    fr = []   # cuspe (inimigos)
    for i in range(3):
        h = HD(16, 16, S=8)
        h.ellipse(11, 8, 4.4 + i * .2, 4.0, (255, 100, 220, 60))
        h.ellipse(4.2, 8 + (i - 1) * .5, 1.0, .8, (230, 70, 200, 200)); h.ellipse(6.4, 8.2, 1.5, 1.2, (240, 80, 210, 235))
        h.shaded_ellipse(11, 8, 3.8, 3.6, (232, 70, 200, 255))
        h.ellipse(10, 6.8, 1.1, .8, (255, 220, 250, 255))
        fr.append(h.img())
    rows.append(("cuspe", fr))
    fr = []   # dardo de fotossíntese
    for i in range(3):
        h = HD(16, 16, S=8)
        h.ellipse(9, 8, 7, 3 + i * .2, (110, 245, 255, 50))
        h.poly([(2, 8), (5.2, 5.4), (7, 7.4)], (40, 170, 150, 255)); h.poly([(2, 8), (5.2, 10.6), (7, 8.6)], (30, 140, 125, 255))
        h.poly([(3, 8), (11.4, 7.1), (15.6, 8), (11.4, 8.9)], (90, 235, 240, 255))
        h.poly([(3, 8), (11.4, 7.1), (15.6, 8), (8, 7.8)], (190, 255, 255, 255))
        h.ellipse(14.6, 8, .8, .6, (255, 255, 255, 255))
        fr.append(h.img())
    rows.append(("bolt", fr))
    fr = []   # estilhaço
    for i in range(3):
        h = HD(16, 16, S=8)
        h.ellipse(9, 8, 5.2 + i * .2, 4.4, (230, 255, 110, 55))
        h.poly([(4, 8), (9, 4.6), (14.4, 8), (9, 11.4)], (217, 245, 90, 255))
        h.poly([(9, 4.6), (14.4, 8), (9, 8)], (250, 255, 170, 255))
        h.poly([(9, 11.4), (14.4, 8), (9, 8)], (150, 190, 50, 255))
        h.ellipse(9, 8, .9, .9, (255, 255, 255, 255))
        fr.append(h.img())
    rows.append(("estilhaco", fr))
    return rows


def spines_frames():
    fr = []
    for n in range(1, 9):
        h = HD(32, 32, S=6)
        for i in range(n):
            a = math.pi + (i - (n - 1) / 2) * .42
            cx, cy = 16 + math.cos(a) * 8.5, 17 + math.sin(a) * 6.5
            tx, ty = 16 + math.cos(a) * 15.5, 17 + math.sin(a) * 12.5
            nx, ny = -math.sin(a) * 1.5, math.cos(a) * 1.5
            h.poly([(cx + nx, cy + ny), (tx, ty), (cx - nx, cy - ny)], (176, 96, 240, 255))
            h.poly([(cx + nx, cy + ny), (tx, ty), (cx, cy)], (214, 150, 255, 255))
        fr.append(h.img())
    return fr


def generate(save, register, sheet):
    """save(img, group, name); register(group, name, fw, fh, anims); sheet(rows, s, fw)."""
    rows, anims = [], []
    plan = (("idle", 4, 6, True), ("walk", 6, 12, True), ("hurt", 2, 10, False), ("dash", 3, 14, False))
    for d in ("down", "up", "side"):
        for an, n, fps, loop in plan:
            frames = [pose(d, an, (i / n) if loop else (i / max(1, n - 1))) for i in range(n)]
            rows.append(("%s_%s" % (an, d), frames)); anims.append(("%s_%s" % (an, d), n, fps, loop))
    rows.append(("death", [death_frame(i / 5) for i in range(6)])); anims.append(("death", 6, 8, False))
    save(sheet(rows, 32), "player", "player_sheet.png")
    register("player", "player_sheet.png", 32, 32, anims)
    save(make_weapon(), "player", "weapon.png")
    save(sheet([("flash", muzzle_frames())], 16), "fx", "muzzle.png"); register("fx", "muzzle.png", 16, 16, [("flash", 3, 24, False)])
    pr = proj_frames()
    save(sheet(pr, 16), "fx", "projectiles.png"); register("fx", "projectiles.png", 16, 16, [(n, 3, 12, True) for n, _ in pr])
    save(sheet([("spines", spines_frames())], 32), "player", "mutation_spines.png"); register("player", "mutation_spines.png", 32, 32, [("spines", 8, 1, False)])
