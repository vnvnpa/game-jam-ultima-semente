#!/usr/bin/env python3
"""Gera TODA a arte do projeto (pixel art, determinística) em assets/art/.
Uso (na raiz do projeto):  python3 tools/gen_art.py
Requer Pillow e numpy. Cada PNG é uma spritesheet: uma animação por LINHA, um
frame por COLUNA. O arquivo assets/art/manifest.json descreve tamanho de frame e
animações (usado para montar os SpriteFrames). Para trocar qualquer arte, substitua
o PNG mantendo o mesmo nome, tamanho de frame e layout de linhas/colunas.
"""
import json, math, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.path.join(ROOT, "assets", "art")
PAL = json.load(open(os.path.join(ROOT, "tools", "palette.json")))
TAU = math.tau
MANIFEST: dict = {}


def col(name_or_hex, a=255):
    h = PAL.get(name_or_hex, name_or_hex).lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def shade(c, k):
    """k>0 clareia, k<0 escurece."""
    if k >= 0:
        return tuple(int(v + (255 - v) * k) for v in c[:3]) + (c[3],)
    return tuple(int(v * (1 + k)) for v in c[:3]) + (c[3],)


def new(w, h=None):
    return Image.new("RGBA", (w, h or w), (0, 0, 0, 0))


def save(img, group, name):
    d = os.path.join(OUT, group)
    os.makedirs(d, exist_ok=True)
    img.save(os.path.join(d, name))


# ------------------------------------------------------------ primitivas
def blob(img, cx, cy, rx, ry, base):
    """Elipse sombreada (luz de cima-esquerda, 3 tons)."""
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=255)
    tmp = new(w, h)
    d = ImageDraw.Draw(tmp)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=shade(base, -0.35))
    d.ellipse([cx - rx * 0.9 - 0.5, cy - ry * 0.9 - 0.5, cx + rx * 0.8, cy + ry * 0.8], fill=base)
    d.ellipse([cx - rx * 0.62, cy - ry * 0.7, cx - rx * 0.05, cy - ry * 0.18], fill=shade(base, 0.35))
    img.paste(tmp, (0, 0), mask)


def outline(img, c=None):
    c = c or col("outline")
    a = np.array(img)
    alpha = a[..., 3] > 0
    pad = np.pad(alpha, 1)
    dil = (pad[1:-1, 1:-1] | pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:])
    edge = dil & ~alpha
    a[edge] = c
    return Image.fromarray(a, "RGBA")


def tint(img, c, k):
    a = np.array(img).astype(float)
    m = a[..., 3] > 0
    for i in range(3):
        a[..., i][m] = a[..., i][m] * (1 - k) + c[i] * k
    return Image.fromarray(a.astype("uint8"), "RGBA")


def xf(img, sx=1.0, sy=1.0, dx=0, dy=0, pivot=None, alpha=1.0):
    """Escala (nearest) em torno do pivô (pés) e desloca."""
    w, h = img.size
    px, py = pivot or (w / 2, h * 0.9)
    nw, nh = max(1, round(w * sx)), max(1, round(h * sy))
    r = img.resize((nw, nh), Image.NEAREST)
    out = new(w, h)
    ox, oy = round(px - px * sx + dx), round(py - py * sy + dy)
    out.paste(r, (ox, oy), r)
    if alpha < 1.0:
        a = np.array(out)
        a[..., 3] = (a[..., 3] * alpha).astype("uint8")
        out = Image.fromarray(a, "RGBA")
    return out


def line(d, pts, c, w=1):
    d.line(pts, fill=c, width=w)


def sheet(rows, s, fw=None):
    """rows: lista de (nome, [frames]) -> imagem + descrição."""
    fw = fw or s
    maxn = max(len(f) for _, f in rows)
    img = new(maxn * fw, len(rows) * s)
    for r, (_, frames) in enumerate(rows):
        for i, f in enumerate(frames):
            img.paste(f, (i * fw, r * s), f)
    return img


def register(group, name, frame_w, frame_h, anims):
    MANIFEST[f"{group}/{name}"] = {"frame": [frame_w, frame_h], "anims": [
        {"name": n, "row": i, "frames": c, "fps": fps, "loop": lp} for i, (n, c, fps, lp) in enumerate(anims)]}


# ------------------------------------------------------------ modificadores de animação
def mods(anim, t, s):
    """Devolve dict(dx, dy, sx, sy, tint, alpha) para a animação no instante t (0..1)."""
    sn = math.sin(t * TAU)
    m = dict(dx=0, dy=0, sx=1.0, sy=1.0, tint=0.0, alpha=1.0)
    k = s / 32.0
    if anim in ("idle", "float", "shielded", "exposed"):
        m.update(dy=sn * 0.8 * k, sy=1 + 0.04 * sn, sx=1 - 0.02 * sn)
    elif anim == "walk":
        m.update(dy=-abs(sn) * 1.6 * k, sx=1 + 0.05 * sn, sy=1 - 0.04 * sn)
    elif anim == "hurt":
        m.update(dx=(-1 if t < 0.5 else 1) * 1.5 * k, sx=0.92, sy=1.06, tint=0.65)
    elif anim == "death":
        m.update(sy=max(0.12, 1 - 0.88 * t), sx=1 + 0.5 * t, alpha=1 - 0.85 * t * t, tint=0.4 * t)
    elif anim in ("windup", "slam"):
        m.update(sy=1 - 0.22 * math.sin(t * math.pi), sx=1 + 0.12 * math.sin(t * math.pi), tint=0.25 * t)
    elif anim in ("charge", "dash"):
        m.update(sx=1.28, sy=0.82)
    elif anim == "recover":
        m.update(sx=1.1 - 0.1 * t, sy=0.9 + 0.1 * t)
    elif anim in ("shoot", "spore", "pulse", "summon", "attack", "spawn", "roots", "phase2"):
        m.update(sy=1 + 0.1 * math.sin(t * math.pi), sx=1 - 0.05 * math.sin(t * math.pi), tint=0.3 * math.sin(t * math.pi))
    return m


def build(base_fn, s, anims, pal_key):
    """Monta uma sheet de criatura: base_fn(s, anim, t) -> imagem (sem contorno)."""
    rows, desc = [], []
    for name, n, fps, loop in anims:
        frames = []
        for i in range(n):
            t = i / n if loop else (i / max(1, n - 1))
            b = outline(base_fn(s, name, t))
            m = mods(name, t, s)
            f = xf(b, m["sx"], m["sy"], m["dx"], m["dy"], alpha=m["alpha"])
            if m["tint"] > 0:
                f = tint(f, (255, 255, 255), min(0.9, m["tint"]))
            frames.append(f)
        rows.append((name, frames))
        desc.append((name, n, fps, loop))
    return sheet(rows, s), desc


# ------------------------------------------------------------ criaturas (base sem contorno)
def eyes(d, s, x, y, gap=0.09, r=0.045, c=(255, 255, 255, 255)):
    for sx in (-1, 1):
        px, py = s * (x + sx * gap), s * y
        d.ellipse([px - s * r, py - s * r, px + s * r, py + s * r], fill=c)
        d.rectangle([px, py - 0.5, px + 1, py + 1], fill=(20, 10, 20, 255))


def b_player(s, a, t):
    img = new(s); d = ImageDraw.Draw(img)
    sn = math.sin(t * TAU)
    wk = sn * 3 if a in ("walk", "dash") else 0
    dark = (66, 72, 80, 255)
    d.rectangle([s * .38 + wk * .4, s * .70, s * .47 + wk * .4, s * .92], fill=dark)
    d.rectangle([s * .53 - wk * .4, s * .70, s * .62 - wk * .4, s * .92], fill=dark)
    blob(img, s * .5, s * .56, s * .17, s * .21, col("player_suit"))
    d.rectangle([s * .34, s * .56, s * .66, s * .60], fill=col("white"))
    blob(img, s * .5, s * .3, s * .17, s * .15, col("player_helmet"))
    d.ellipse([s * .53, s * .25, s * .70, s * .36], fill=col("player_visor"))
    d.rectangle([s * .55, s * .26, s * .60, s * .28], fill=col("white"))
    d.line([s * .52, s * .50, s * .84, s * .48], fill=col("player_gun"), width=max(2, int(s * .1)))
    d.rectangle([s * .82, s * .44, s * .88, s * .52], fill=shade(col("player_gun"), .4))
    if a == "death" and t > .5:
        d.ellipse([s * .2, s * .8, s * .8, s * .95], fill=(0, 0, 0, 0))
    return img


def b_larva(s, a, t):
    img = new(s); d = ImageDraw.Draw(img)
    for i, x in enumerate((-.2, -.07, .07, .2)):
        o = math.sin(t * TAU + i * 1.6) * s * .03 if a == "walk" else 0
        d.rectangle([s * (.5 + x) - 1, s * .78, s * (.5 + x) + 1, s * .9 + o], fill=shade(col("larva"), -.5))
    blob(img, s * .5, s * .58, s * .3, s * .26, col("larva"))
    d.ellipse([s * .38, s * .66, s * .62, s * .8], fill=shade(col("larva"), .25))
    eyes(d, s, .5, .52)
    d.polygon([(s * .42, s * .7), (s * .46, s * .76), (s * .5, s * .7)], fill=col("larva_det"))
    return img


def b_cortarraiz(s, a, t):
    img = new(s); d = ImageDraw.Draw(img)
    c = col("cortarraiz")
    for i, x in enumerate((.3, .45, .6)):
        o = math.sin(t * TAU + i * 2) * s * .04 if a == "walk" else 0
        d.line([s * x, s * .66, s * x - s * .04 + o, s * .9], fill=shade(c, -.5), width=2)
    d.polygon([(s * .9, s * .55), (s * .55, s * .34), (s * .1, s * .44), (s * .18, s * .64), (s * .55, s * .74)], fill=shade(c, -.3))
    d.polygon([(s * .86, s * .55), (s * .55, s * .38), (s * .16, s * .47), (s * .24, s * .62), (s * .55, s * .7)], fill=c)
    d.polygon([(s * .5, s * .37), (s * .6, s * .14), (s * .68, s * .4)], fill=col("cortarraiz_det"))
    d.ellipse([s * .66, s * .46, s * .74, s * .54], fill=col("cortarraiz_det"))
    if a in ("windup", "charge"):
        d.polygon([(s * .9, s * .55), (s * .98, s * .5), (s * .98, s * .6)], fill=col("white"))
    return img


def b_flor(s, a, t):
    img = new(s); d = ImageDraw.Draw(img)
    d.line([s * .5, s * .92, s * .5, s * .58], fill=col("leaf_mid"), width=3)
    d.ellipse([s * .36, s * .78, s * .5, s * .86], fill=col("leaf_light"))
    for i in range(6):
        ang = t * 1.2 + i * TAU / 6
        px, py = s * .5 + math.cos(ang) * s * .2, s * .42 + math.sin(ang) * s * .17
        blob(img, px, py, s * .13, s * .11, col("flor"))
    blob(img, s * .5, s * .42, s * .1, s * .09, col("flor_det"))
    if a == "shoot":
        g = int(150 + 100 * math.sin(t * math.pi))
        d.ellipse([s * .44, s * .36, s * .56, s * .48], fill=(255, 230, 255, g))
    return img


def b_casca(s, a, t):
    img = new(s); d = ImageDraw.Draw(img)
    c = col("casca")
    d.ellipse([s * .1, s * .72, s * .9, s * .92], fill=shade(c, -.6))
    blob(img, s * .5, s * .56, s * .4, s * .32, c)
    for r in (.2, .3):
        d.arc([s * (.5 - r), s * (.56 - r * .8), s * (.5 + r), s * (.56 + r * .8)], 180, 360, fill=col("casca_det"), width=2)
    d.ellipse([s * .46, s * .46, s * .54, s * .54], fill=col("casca_det"))
    eyes(d, s, .5, .64, .12, .035, col("warn"))
    return img


def b_esporideo(s, a, t):
    img = new(s); d = ImageDraw.Draw(img)
    blob(img, s * .5, s * .6, s * .3, s * .26, col("esporideo"))
    blob(img, s * .5, s * .38, s * .14, s * .12, shade(col("esporideo"), .1))
    for i in range(5):
        ang = i * TAU / 5 + t * 1.2
        px, py = s * .5 + math.cos(ang) * s * .26, s * .6 + math.sin(ang) * s * .2
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=col("esporideo_det"))
    eyes(d, s, .5, .58, .08, .04)
    if a == "spore":
        r = s * (.28 + .2 * t)
        d.arc([s * .5 - r, s * .78 - r * .4, s * .5 + r, s * .78 + r * .4], 0, 360, fill=col("esporideo_det"), width=2)
    return img


def b_parasita(s, a, t):
    img = new(s); d = ImageDraw.Draw(img)
    c = col("parasita")
    d.line([s * .5, s * .28, s * .5, s * .12], fill=col("parasita_det"), width=1)
    d.ellipse([s * .46, s * .08, s * .54, s * .16], fill=col("parasita_det"))
    blob(img, s * .5, s * .5, s * .2, s * .2, c)
    d.arc([s * .18, s * .36, s * .82, s * .64], 0, 360, fill=col("parasita_det"), width=1)
    d.ellipse([s * .46, s * .46, s * .54, s * .54], fill=col("parasita_det"))
    if a == "pulse":
        r = s * (.25 + .22 * t)
        d.ellipse([s * .5 - r, s * .5 - r, s * .5 + r, s * .5 + r], outline=(180, 255, 255, int(255 * (1 - t))), width=2)
    return img


def spikes(img, s, cx, cy, r, n, c, ph=0.0, ln=.35):
    d = ImageDraw.Draw(img)
    for i in range(n):
        a = i * TAU / n + ph
        p0 = (cx + math.cos(a) * r * .8, cy + math.sin(a) * r * .8)
        p1 = (cx + math.cos(a - .18) * r, cy + math.sin(a - .18) * r)
        p2 = (cx + math.cos(a + .18) * r, cy + math.sin(a + .18) * r)
        d.polygon([p1, (cx + math.cos(a) * r * (1 + ln), cy + math.sin(a) * r * (1 + ln)), p2], fill=c)


def b_anomalia(s, a, t):
    img = new(s)
    spikes(img, s, s * .5, s * .58, s * .27, 7, col("anomalia_det"), t * .5)
    blob(img, s * .5, s * .58, s * .27, s * .24, col("anomalia"))
    d = ImageDraw.Draw(img)
    eyes(d, s, .5, .52, .1, .05, col("anomalia_det"))
    return img


def b_ninho(s, a, t):
    img = new(s); d = ImageDraw.Draw(img)
    c = col("ninho")
    for i in range(6):
        ang = i * TAU / 6 + .3
        d.line([s * .5, s * .85, s * .5 + math.cos(ang) * s * .4, s * .88 + math.sin(ang) * s * .08], fill=shade(c, -.5), width=3)
    pu = 1 + .05 * math.sin(t * TAU)
    blob(img, s * .5, s * .58, s * .34 * pu, s * .3 * pu, c)
    blob(img, s * .3, s * .46, s * .14, s * .12, shade(c, .15))
    blob(img, s * .7, s * .5, s * .12, s * .11, shade(c, .1))
    open_k = math.sin(t * math.pi) if a == "spawn" else 0.15
    d.ellipse([s * .42, s * (.7 - .02), s * .58, s * (.7 + .06 + .1 * open_k)], fill=(30, 5, 20, 255))
    d.ellipse([s * .46, s * .64, s * .54, s * .68], fill=col("ninho_det"))
    return img


def b_guardiao(s, a, t):
    img = new(s); d = ImageDraw.Draw(img)
    c = col("guardiao")
    up = {"slam": math.sin(t * math.pi), "summon": 0.5, "phase2": 0.8}.get(a, 0.0)
    for side in (-1, 1):
        pts = [(s * .5 + side * s * .22, s * .55), (s * .5 + side * s * (.38 + .06 * up), s * (.62 - .3 * up)), (s * .5 + side * s * (.44 + .05 * up), s * (.8 - .55 * up))]
        d.line(pts, fill=shade(c, -.4), width=int(s * .1))
        d.line(pts, fill=c, width=int(s * .06))
    for i in range(8):
        ang = math.pi * (.15 + .7 * i / 7)
        x0, y0 = s * .5 + math.cos(ang) * s * .12, s * .85
        d.line([x0, y0, s * .5 + math.cos(ang) * s * .42, s * .92 + math.sin(t * TAU + i) * 2], fill=shade(c, -.5), width=3)
    blob(img, s * .5, s * .56, s * .26, s * .32, shade(c, -.1))
    blob(img, s * .5, s * .26, s * .15, s * .12, c)
    for i in range(5):
        x = s * (.38 + .06 * i)
        d.polygon([(x - 3, s * .18), (x, s * (.04 + (i % 2) * .04)), (x + 3, s * .18)], fill=col("guardiao_det"))
    g = .6 + .4 * math.sin(t * TAU)
    d.ellipse([s * .4, s * .46, s * .6, s * .66], fill=col("core") if a != "death" else (90, 90, 100, 255))
    d.ellipse([s * .46, s * .52, s * .54, s * .6], fill=col("core_violet"))
    eyes(d, s, .5, .26, .06, .025, col("warn"))
    return img


def b_jardineiro(s, a, t):
    img = new(s); d = ImageDraw.Draw(img)
    c = col("jardineiro")
    for i in range(4):
        ang = math.pi * (.2 + i * .2) + (math.pi / 2)
        x1, y1 = s * .5 + math.cos(ang - 1.57 + 1.57) * s * .3 * (1 if i % 2 else -1), s * .88
        d.line([s * .5, s * .6, x1, y1], fill=shade(c, -.5), width=int(s * .05))
    d.ellipse([s * .2, s * .26, s * .8, s * .86], fill=shade(c, -.45))
    blob(img, s * .5, s * .55, s * .3, s * .3, c)
    d.ellipse([s * .3, s * .35, s * .7, s * .75], outline=col("jardineiro_det"), width=2)
    ex = a == "exposed"
    gl = (255, 255, 160, 255) if ex else col("core")
    d.ellipse([s * .4, s * .45, s * .6, s * .65], fill=gl)
    d.ellipse([s * .46, s * .51, s * .54, s * .59], fill=col("core_violet"))
    if a == "shoot":
        d.rectangle([s * .78, s * .5, s * .98, s * .58], fill=col("white"))
    if a == "roots":
        for i in range(6):
            x = s * (.2 + .12 * i)
            d.line([x, s * .9, x + math.sin(t * TAU + i) * 3, s * (.9 - .12 * math.sin(t * math.pi))], fill=col("leaf_light"), width=3)
    if a in ("shielded", "shoot", "roots", "death") and a != "death":
        d.ellipse([s * .12, s * .18, s * .88, s * .9], outline=(120, 230, 255, 200), width=2)
    return img


def b_companion(s, a, t):
    img = new(s); d = ImageDraw.Draw(img)
    for sx in (-1, 1):
        d.ellipse([s * (.5 + sx * .2) - 4, s * .35, s * (.5 + sx * .2) + 4, s * .5], fill=(220, 190, 255, 150))
    blob(img, s * .5, s * .55, s * .2, s * .2, col("core_violet"))
    d.ellipse([s * .46, s * .5, s * .54, s * .58], fill=(255, 230, 255, 255))
    if a == "attack":
        d.ellipse([s * .3, s * .35, s * .7, s * .75], outline=(255, 200, 255, 220), width=2)
    return img


def b_coracao(s, a, t):
    img = new(s); d = ImageDraw.Draw(img)
    c = (170, 40, 90, 255)
    up = {"slam": math.sin(t * math.pi), "summon": 0.6}.get(a, 0.0)
    for i in range(12):  # raízes na base
        ang = math.pi * (0.05 + 0.9 * i / 11)
        x1 = s * .5 + math.cos(ang) * s * .46
        d.line([s * .5 + math.cos(ang) * s * .1, s * .84, x1, s * .93 + math.sin(t * TAU + i) * 2], fill=(90, 30, 70, 255), width=4)
    for side in (-1, 1):  # braços de raiz
        pts = [(s * .5 + side * s * .2, s * .5), (s * .5 + side * s * (.36 + .05 * up), s * (.55 - .25 * up)), (s * .5 + side * s * (.42 + .04 * up), s * (.76 - .5 * up))]
        d.line(pts, fill=(70, 25, 60, 255), width=int(s * .08)); d.line(pts, fill=(130, 50, 100, 255), width=int(s * .045))
    pu = 1 + .05 * math.sin(t * TAU)
    blob(img, s * .5, s * .52, s * .27 * pu, s * .3 * pu, c)
    blob(img, s * .38, s * .42, s * .13, s * .15, (200, 70, 120, 255))
    blob(img, s * .62, s * .42, s * .13, s * .15, (190, 60, 115, 255))
    shield = a == "shielded"
    glow = (140, 150, 170, 255) if shield else (110, 245, 255, 255)
    if a == "exposed":
        glow = (255, 245, 170, 255)
    d.ellipse([s * .4, s * .42, s * .6, s * .62], fill=glow)
    d.ellipse([s * .46, s * .48, s * .54, s * .56], fill=(180, 110, 255, 255))
    for i in range(6):
        ang = i * TAU / 6 + t * 1.5
        d.ellipse([s * .5 + math.cos(ang) * s * .36 - 2, s * .52 + math.sin(ang) * s * .34 - 2, s * .5 + math.cos(ang) * s * .36 + 2, s * .52 + math.sin(ang) * s * .34 + 2], fill=(255, 200, 230, 255))
    if shield:
        d.ellipse([s * .16, s * .18, s * .84, s * .86], outline=(120, 230, 255, 200), width=2)
    return img


def b_estrutura(s, a, t):
    img = new(s); d = ImageDraw.Draw(img)
    d.ellipse([s * .2, s * .8, s * .8, s * .95], fill=(0, 0, 0, 0))
    for i in range(5):
        x = s * (.22 + .14 * i)
        d.line([x, s * .9, s * .5 + (x - s * .5) * .4, s * .35], fill=(70, 30, 60, 255), width=3)
    d.rectangle([s * .32, s * .3, s * .68, s * .88], fill=(87, 94, 92, 255)); d.rectangle([s * .32, s * .3, s * .42, s * .88], fill=(112, 120, 116, 255))
    d.polygon([(s * .3, s * .3), (s * .5, s * .08), (s * .7, s * .3)], fill=(130, 60, 120, 255))
    g = .6 + .4 * math.sin(t * TAU)
    d.ellipse([s * .42, s * .42, s * .58, s * .58], fill=(int(120 + 100 * g), 230, 255, 255))
    return img


CREATURES = [
    ("player", "companion.png", b_companion, 32, [("idle", 4, 6, True), ("attack", 3, 12, False)]),
    ("enemies", "larva.png", b_larva, 32, [("idle", 4, 6, True), ("walk", 6, 12, True), ("hurt", 2, 10, False), ("death", 5, 10, False)]),
    ("enemies", "cortarraiz.png", b_cortarraiz, 32, [("walk", 6, 12, True), ("windup", 3, 8, False), ("charge", 3, 14, True), ("recover", 2, 6, False), ("death", 5, 10, False)]),
    ("enemies", "flor.png", b_flor, 32, [("idle", 4, 6, True), ("shoot", 4, 10, False), ("death", 5, 10, False)]),
    ("enemies", "casca.png", b_casca, 48, [("walk", 6, 8, True), ("hurt", 2, 10, False), ("death", 6, 8, False)]),
    ("enemies", "esporideo.png", b_esporideo, 32, [("walk", 6, 10, True), ("spore", 3, 8, False), ("death", 5, 10, False)]),
    ("enemies", "parasita.png", b_parasita, 32, [("float", 4, 6, True), ("pulse", 4, 8, False), ("death", 5, 10, False)]),
    ("enemies", "anomalia.png", b_anomalia, 48, [("walk", 6, 10, True), ("hurt", 2, 10, False), ("death", 6, 8, False)]),
    ("enemies", "ninho.png", b_ninho, 64, [("idle", 4, 5, True), ("spawn", 4, 8, False), ("death", 6, 8, False)]),
    ("enemies", "guardiao.png", b_guardiao, 96, [("idle", 4, 5, True), ("slam", 6, 8, False), ("summon", 6, 8, False), ("phase2", 4, 8, False), ("death", 8, 8, False)]),
    ("enemies", "coracao.png", b_coracao, 128, [("idle", 4, 5, True), ("slam", 6, 8, False), ("summon", 6, 8, False), ("shielded", 4, 5, True), ("exposed", 4, 6, True), ("death", 8, 8, False)]),
    ("enemies", "estrutura.png", b_estrutura, 48, [("idle", 4, 5, True), ("hurt", 2, 10, False), ("death", 6, 10, False)]),
    ("enemies", "jardineiro.png", b_jardineiro, 96, [("shielded", 4, 5, True), ("exposed", 4, 6, True), ("shoot", 4, 10, False), ("roots", 6, 8, False), ("death", 8, 8, False)]),
]


def gen_creatures():
    for group, name, fn, s, anims in CREATURES:
        img, desc = build(fn, s, anims, name)
        save(img, group, name)
        register(group, name, s, s, desc)


def gen_enemy_extras():
    # auras da Anomalia (4 modificadores x 4 frames)
    rows = []
    for nm, c in (("blindada", (170, 190, 210)), ("veloz", (80, 230, 255)), ("explosiva", (255, 150, 60)), ("regenerante", (120, 255, 140))):
        fr = []
        for i in range(4):
            im = new(64); d = ImageDraw.Draw(im); r = 20 + 2 * math.sin(i / 4 * TAU)
            d.ellipse([32 - r, 34 - r, 32 + r, 34 + r], outline=c + (200,), width=2)
            d.ellipse([32 - r - 3, 34 - r - 3, 32 + r + 3, 34 + r + 3], outline=c + (90,), width=1)
            fr.append(im)
        rows.append((nm, fr))
    save(sheet(rows, 64), "enemies", "anomalia_auras.png")
    register("enemies", "anomalia_auras.png", 64, 64, [(n, 4, 6, True) for n, _ in rows])


# ------------------------------------------------------------ projéteis, FX, coletáveis
def glow_dot(s, c, r, core=True):
    im = new(s); d = ImageDraw.Draw(im); m = s / 2
    d.ellipse([m - r - 2, m - r - 2, m + r + 2, m + r + 2], fill=c[:3] + (70,))
    d.ellipse([m - r, m - r, m + r, m + r], fill=c)
    if core:
        d.ellipse([m - r / 2, m - r / 2, m + r / 2, m + r / 2], fill=(255, 255, 255, 255))
    return im


def gen_projectiles():
    rows = []
    for nm, c, r in (("espinho", col("player_gun"), 4), ("cuspe", col("flor_det"), 5), ("bolt", col("core"), 5), ("estilhaco", col("bio"), 3)):
        fr = []
        for i in range(2):
            im = glow_dot(16, c, r + i * .6)
            ImageDraw.Draw(im).line([0, 8, 5, 8], fill=c[:3] + (150,), width=2)
            fr.append(im)
        rows.append((nm, fr))
    save(sheet(rows, 16), "fx", "projectiles.png")
    register("fx", "projectiles.png", 16, 16, [(n, 2, 10, True) for n, _ in rows])


def ring_img(s, w=3, c=(255, 255, 255, 255)):
    im = new(s); d = ImageDraw.Draw(im)
    d.ellipse([1, 1, s - 2, s - 2], fill=c[:3] + (30,), outline=c, width=w)
    return im


def gen_fx():
    save(ring_img(128, 4), "fx", "ring.png")  # branco: tingir com modulate
    save(new(8) if False else Image.new("RGBA", (32, 16), (0, 0, 0, 0)), "fx", "_tmp.png")
    os.remove(os.path.join(OUT, "fx", "_tmp.png"))
    sh = new(32, 16); ImageDraw.Draw(sh).ellipse([2, 2, 29, 13], fill=(0, 0, 0, 90)); save(sh, "fx", "shadow.png")
    # faíscas (6 frames, branco)
    fr = []
    rnd = random.Random(7)
    dirs = [rnd.random() * TAU for _ in range(8)]
    for i in range(6):
        im = new(32); d = ImageDraw.Draw(im); k = i / 5
        for a in dirs:
            r0, r1 = 3 + 11 * k, 6 + 12 * k
            d.line([16 + math.cos(a) * r0, 16 + math.sin(a) * r0, 16 + math.cos(a) * r1, 16 + math.sin(a) * r1], fill=(255, 255, 255, int(255 * (1 - k))), width=2)
        fr.append(im)
    save(sheet([("burst", fr)], 32), "fx", "burst.png"); register("fx", "burst.png", 32, 32, [("burst", 6, 20, False)])
    # explosão (6 frames x 64)
    fr = []
    for i in range(6):
        im = new(64); d = ImageDraw.Draw(im); k = i / 5; r = 6 + 24 * k
        d.ellipse([32 - r, 32 - r, 32 + r, 32 + r], fill=(255, 150 + int(80 * k), 60, int(255 * (1 - k * .8))))
        d.ellipse([32 - r * .6, 32 - r * .6, 32 + r * .6, 32 + r * .6], fill=(255, 240, 160, int(255 * (1 - k))))
        d.ellipse([32 - r, 32 - r, 32 + r, 32 + r], outline=(255, 230, 180, int(255 * (1 - k))), width=2)
        fr.append(im)
    save(sheet([("explosion", fr)], 64), "fx", "explosion.png"); register("fx", "explosion.png", 64, 64, [("explosion", 6, 18, False)])
    # escudo (4 frames x 48)
    fr = []
    for i in range(4):
        im = new(48); d = ImageDraw.Draw(im); a = 110 + int(60 * math.sin(i / 4 * TAU))
        d.ellipse([4, 4, 43, 43], fill=(120, 230, 255, 35), outline=(150, 240, 255, a + 60), width=2)
        d.arc([9, 9, 38, 38], 200 + i * 40, 300 + i * 40, fill=(255, 255, 255, 200), width=2)
        fr.append(im)
    save(sheet([("shield", fr)], 48), "fx", "shield.png"); register("fx", "shield.png", 48, 48, [("shield", 4, 8, True)])
    # telégrafo do golpe (círculo vermelho; escala feita pela cena)
    im = new(128); d = ImageDraw.Draw(im)
    d.ellipse([2, 2, 125, 125], fill=(255, 50, 50, 60), outline=(255, 90, 80, 230), width=4)
    save(im, "fx", "slam.png")
    # isca (4 x 32)
    fr = []
    for i in range(4):
        im = new(32); d = ImageDraw.Draw(im); p = 1 + .15 * math.sin(i / 4 * TAU); r = 10 * p
        d.ellipse([16 - r, 16 - r, 16 + r, 16 + r], fill=(130, 255, 130, 40), outline=(130, 255, 140, 170), width=1)
        blob(im, 16, 18, 6, 5, (90, 205, 90, 255)); d.ellipse([13, 12, 19, 16], fill=(205, 255, 155, 255))
        fr.append(outline(im) if False else im)
    save(sheet([("decoy", fr)], 32), "fx", "decoy.png"); register("fx", "decoy.png", 32, 32, [("decoy", 4, 6, True)])
    # esporos: zona (4 x 96) + partícula
    fr = []
    for i in range(4):
        im = new(96); d = ImageDraw.Draw(im)
        d.ellipse([2, 2, 93, 93], fill=(140, 190, 40, 55), outline=(205, 255, 80, 180), width=2)
        for j in range(6):
            a = i * .5 + j * TAU / 6; r = 48 * (.35 + .4 * abs(math.sin(i * .7 + j)))
            d.ellipse([48 + math.cos(a) * r - 2, 48 + math.sin(a) * r - 2, 48 + math.cos(a) * r + 2, 48 + math.sin(a) * r + 2], fill=(240, 255, 130, 210))
        fr.append(im)
    save(sheet([("zone", fr)], 96), "fx", "spores.png"); register("fx", "spores.png", 96, 96, [("zone", 4, 6, True)])
    dot = new(8); ImageDraw.Draw(dot).ellipse([1, 1, 6, 6], fill=(240, 255, 130, 255)); save(dot, "fx", "particle.png")


def gen_pickups():
    rows = []
    fr = [glow_dot(32, col("bio"), 5 + (i % 2)) for i in range(4)]
    rows.append(("biomass", fr))
    fr = []
    for i in range(4):
        im = new(32); d = ImageDraw.Draw(im); s_ = 9 + (i % 2)
        pts = [(16, 16 - s_), (16 + s_ * .8, 16), (16, 16 + s_), (16 - s_ * .8, 16)]
        d.ellipse([16 - s_ - 4, 16 - s_ - 4, 16 + s_ + 4, 16 + s_ + 4], fill=col("bio")[:3] + (50,))
        d.polygon(pts, fill=col("bio")); d.polygon([pts[0], pts[1], (16, 16)], fill=shade(col("bio"), .5))
        fr.append(outline(im))
    rows.append(("cache", fr))
    fr = []
    for i in range(6):
        im = new(32); d = ImageDraw.Draw(im); k = i / 6
        c = col("nucleus") if i % 2 == 0 else col("nucleus_violet")
        d.ellipse([4, 4, 27, 27], fill=c[:3] + (45,))
        sq = 1 - abs(math.sin(k * math.pi)) * .5
        pts = [(16, 5), (16 + 8 * sq, 16), (16, 27), (16 - 8 * sq, 16)]
        d.polygon(pts, fill=col("nucleus")); d.polygon([pts[0], pts[1], (16, 16)], fill=col("nucleus_violet"))
        d.ellipse([13, 13, 19, 19], fill=(255, 255, 255, 255))
        fr.append(outline(im))
    rows.append(("nucleus", fr))
    save(sheet(rows, 32), "fx", "pickups.png"); register("fx", "pickups.png", 32, 32, [("biomass", 4, 6, True), ("cache", 4, 6, True), ("nucleus", 6, 8, True)])


# ------------------------------------------------------------ mundo
def tree_img(i, rnd):
    im = new(64, 72); d = ImageDraw.Draw(im)
    d.ellipse([14, 56, 50, 70], fill=(0, 0, 0, 70))
    d.rectangle([29, 40, 35, 64], fill=col("bark")); d.rectangle([29, 40, 31, 64], fill=shade(col("bark"), .2))
    for dx, dy, r, k in ((0, -4, 22, "leaf_dark"), (-8, -10, 16, "leaf_mid"), (8, -14, 12, "leaf_light")):
        blob(im, 32 + dx + (i - 1.5) * 1.5, 34 + dy, r, r * .9, col(k))
    return outline(im)


def crystal_img(i, rnd):
    im = new(48, 64); d = ImageDraw.Draw(im); d.ellipse([8, 52, 40, 62], fill=(0, 0, 0, 70))
    cs = [(70, 30, 110), (110, 50, 150), (150, 80, 200), (90, 40, 130)]
    for j in range(3):
        x = 14 + j * 10 + rnd.randint(-2, 2); h = 24 + rnd.randint(0, 22) - j * 4 + i * 2
        pts = [(x, 58), (x - 6, 58 - h * .55), (x, 58 - h), (x + 6, 58 - h * .55)]
        d.polygon(pts, fill=cs[(j + i) % 4]); d.polygon([pts[1], pts[2], (x, 58 - h * .5)], fill=(205, 140, 235))
    return outline(im)


def pillar_img(i, rnd):
    im = new(48, 64); d = ImageDraw.Draw(im); d.ellipse([6, 52, 42, 62], fill=(0, 0, 0, 70))
    d.rectangle([12, 14, 36, 58], fill=(87, 94, 92)); d.rectangle([12, 14, 20, 58], fill=(112, 120, 116))
    d.rectangle([10, 10, 38, 18], fill=(102, 140, 102)); d.rectangle([10, 54, 38, 58], fill=(70, 76, 74))
    for k in range(3 + i):
        x = rnd.randint(14, 34); d.line([x, 20, x + rnd.randint(-2, 2), rnd.randint(30, 54)], fill=(60, 100, 60), width=1)
    d.rectangle([22, 28, 26, 40], fill=(120, 230, 160) if i % 2 else (80, 90, 88))
    return outline(im)


def gen_world_props():
    for name, fn, w, h in (("trees.png", tree_img, 64, 72), ("crystals.png", crystal_img, 48, 64), ("pillars.png", pillar_img, 48, 64)):
        rnd = random.Random(hash(name) & 0xffff if False else sum(map(ord, name)))
        fr = [fn(i, rnd) for i in range(4)]
        save(sheet([("v", fr)], h, w), "world", name)
        register("world", name, w, h, [("variants", 4, 1, False)])
    # estação pressurizada: anel 256 x 4 frames
    fr = []
    for i in range(4):
        im = new(256); d = ImageDraw.Draw(im); a = 150 + int(70 * math.sin(i / 4 * TAU))
        d.ellipse([4, 4, 251, 251], fill=(80, 230, 255, 22), outline=(100, 240, 255, a), width=3)
        d.ellipse([16, 16, 239, 239], outline=(150, 250, 255, 70), width=1)
        for j in range(12):
            ang = j * TAU / 12 + i * .08
            d.rectangle([128 + math.cos(ang) * 120 - 2, 128 + math.sin(ang) * 120 - 2, 128 + math.cos(ang) * 120 + 2, 128 + math.sin(ang) * 120 + 2], fill=(180, 255, 255, 200))
        fr.append(im)
    save(sheet([("dome", fr)], 256), "world", "station.png"); register("world", "station.png", 256, 256, [("dome", 4, 4, True)])
    # terminal 32x40
    fr = []
    for i in range(4):
        im = new(32, 40); d = ImageDraw.Draw(im); d.ellipse([3, 32, 29, 39], fill=(0, 0, 0, 70))
        d.rectangle([6, 6, 26, 34], fill=(51, 66, 72)); d.rectangle([6, 6, 26, 34], outline=(102, 204, 204), width=1)
        g = 180 + int(60 * math.sin(i / 4 * TAU)); d.rectangle([9, 10, 23, 22], fill=(50, 230, 255, g))
        d.rectangle([9, 26, 14, 30], fill=(230, 150, 50)); d.rectangle([18, 26, 23, 30], fill=(100, 230, 125))
        fr.append(outline(im))
    save(sheet([("idle", fr)], 40, 32), "world", "terminal.png"); register("world", "terminal.png", 32, 40, [("idle", 4, 5, True)])
    # nave 128x64
    fr = []
    for i in range(4):
        im = new(128, 64); d = ImageDraw.Draw(im); d.ellipse([10, 50, 120, 62], fill=(0, 0, 0, 70))
        d.polygon([(8, 36), (30, 14), (96, 10), (124, 30), (100, 52), (24, 54)], fill=(128, 133, 140))
        d.polygon([(8, 36), (30, 14), (96, 10), (60, 30)], fill=(165, 170, 176))
        d.polygon([(34, 30), (64, 20), (98, 26), (82, 42), (44, 44)], fill=(242, 140, 51))
        d.rectangle([60, 24, 76, 32], fill=(140, 230, 255)); d.line([60, 14, 68, 50], fill=(60, 60, 66), width=1)
        d.ellipse([4 - i % 2, 40, 12, 48], fill=(255, 130, 50, 160 + 20 * (i % 2)))
        fr.append(outline(im))
    save(sheet([("idle", fr)], 64, 128), "world", "ship.png"); register("world", "ship.png", 128, 64, [("idle", 4, 5, True)])
    # ruína 48x64 e mecanismo 48x64 (idle / ativo)
    def ruin(i, active=False, mech=False):
        im = new(48, 64); d = ImageDraw.Draw(im); d.ellipse([6, 54, 42, 63], fill=(0, 0, 0, 70))
        c = (180, 120, 242) if not active else (120, 255, 170); g = .5 + .5 * math.sin(i / 4 * TAU)
        d.rectangle([14, 20, 34, 58], fill=(64, 69, 77)); d.rectangle([14, 20, 20, 58], fill=(85, 90, 100))
        d.rectangle([12, 16, 36, 22], fill=(95, 100, 110))
        d.ellipse([19, 28, 29, 38], fill=c + (int(110 + 130 * g),)); d.line([18, 44, 30, 44], fill=c, width=2); d.line([24, 44, 24, 52], fill=c, width=2)
        if mech:
            d.polygon([(8, 60), (24, 4), (40, 60)] if False else [(10, 20), (24, 6), (38, 20)], fill=(110, 118, 128))
        return outline(im)
    save(sheet([("idle", [ruin(i) for i in range(4)])], 64, 48), "world", "ruin.png"); register("world", "ruin.png", 48, 64, [("idle", 4, 4, True)])
    save(sheet([("idle", [ruin(i, False, True) for i in range(4)]), ("active", [ruin(i, True, True) for i in range(4)])], 64, 48), "world", "mechanism.png")
    register("world", "mechanism.png", 48, 64, [("idle", 4, 4, True), ("active", 4, 8, True)])
    # portão de raízes (224 x 64): fechada 4, abrindo 6, aberta 1
    def gate(open_k, ph):
        im = new(224, 64); d = ImageDraw.Draw(im); a = 1 - open_k
        if a <= 0.02:
            return im
        for i in range(11):
            x = 12 + i * 20; wob = math.sin(ph * TAU + i) * 3; h = int(40 * a)
            d.line([x, 50, x + wob, 50 - h], fill=(100, 51, 115, int(255 * a)), width=6)
            d.line([x, 50, x - wob, 50 - h - 4], fill=(180, 77, 180, int(255 * a)), width=2)
        d.rectangle([4, 44, 219, 56], outline=(180, 77, 180, int(200 * a)), width=2)
        return im
    rows = [("closed", [gate(0, i / 4) for i in range(4)]), ("opening", [gate(i / 5, 0.3) for i in range(6)]), ("open", [gate(1, 0)])]
    save(sheet(rows, 64, 224), "world", "gate.png"); register("world", "gate.png", 224, 64, [("closed", 4, 5, True), ("opening", 6, 8, False), ("open", 1, 1, False)])
    # arena do chefe 544 x 4 frames (anel + runas)
    fr = []
    for i in range(4):
        im = new(544); d = ImageDraw.Draw(im); a = 90 + int(50 * math.sin(i / 4 * TAU))
        d.ellipse([6, 6, 537, 537], outline=(180, 100, 230, a + 40), width=4); d.ellipse([30, 30, 513, 513], outline=(180, 100, 230, a // 2), width=1)
        for j in range(16):
            ang = j * TAU / 16 + i * .05; x, y = 272 + math.cos(ang) * 255, 272 + math.sin(ang) * 255
            d.rectangle([x - 4, y - 4, x + 4, y + 4], fill=(200, 140, 245, a + 60))
        fr.append(im)
    save(sheet([("ring", fr)], 544), "world", "arena.png"); register("world", "arena.png", 544, 544, [("ring", 4, 4, True)])
    # névoa contaminada tileável 64 x 4
    rnd = random.Random(3); fr = []
    for i in range(4):
        im = new(64); d = ImageDraw.Draw(im)
        for _ in range(22):
            x, y, r = rnd.randint(0, 63), rnd.randint(0, 63), rnd.randint(5, 12)
            for ox in (-64, 0, 64):
                for oy in (-64, 0, 64):
                    d.ellipse([x + ox - r, y + oy - r, x + ox + r, y + oy + r], fill=(180, 40, 170, 26))
        fr.append(im)
    save(fr[0], "world", "fog_tile.png"); save(sheet([("fog", fr)], 64), "world", "hostile_fx.png"); register("world", "hostile_fx.png", 64, 64, [("fog", 4, 3, True)])
    # decoração 32x32 (16 itens)
    rnd = random.Random(11); items = []
    for i in range(16):
        im = new(32); d = ImageDraw.Draw(im)
        kind = i % 4
        if kind == 0:
            for _ in range(6):
                x = rnd.randint(6, 26); d.line([x, 26, x + rnd.randint(-3, 3), rnd.randint(12, 20)], fill=col(("leaf_mid", "leaf_light")[rnd.randint(0, 1)]), width=1)
        elif kind == 1:
            for _ in range(3):
                x, y = rnd.randint(8, 24), rnd.randint(14, 26); d.line([x, y, x, y + 6], fill=col("leaf_mid")); d.ellipse([x - 2, y - 3, x + 2, y + 1], fill=[(255, 120, 230, 255), (150, 255, 220, 255), (255, 230, 120, 255)][rnd.randint(0, 2)])
        elif kind == 2:
            blob(im, 16, 22, 8 + rnd.randint(0, 3), 5, (96, 100, 98, 255))
        else:
            for _ in range(5):
                x, y = rnd.randint(6, 26), rnd.randint(8, 26); d.ellipse([x - 2, y - 1, x + 2, y + 1], fill=(120, 60, 100, 255))
        items.append(im)
    save(sheet([("decor", items)], 32), "world", "decor.png"); register("world", "decor.png", 32, 32, [("decor", 16, 1, False)])


# ------------------------------------------------------------ tilesets (tile 32 px)
def tile_noise(base, rnd, n=26, spread=.09):
    im = new(32); d = ImageDraw.Draw(im); d.rectangle([0, 0, 31, 31], fill=base)
    for _ in range(n):
        x, y = rnd.randint(0, 31), rnd.randint(0, 31); k = rnd.uniform(-spread, spread)
        d.rectangle([x, y, x + rnd.randint(0, 2), y + rnd.randint(0, 1)], fill=shade(base, k * 2))
    return im


def gen_tilesets():
    biomes = {"floresta": ("ground_floresta", (70, 52, 36, 255)), "bacia": ("ground_bacia", (60, 72, 90, 255)),
              "santuario": ("ground_santuario", (84, 92, 86, 255)), "jardim": ("ground_jardim", (66, 50, 90, 255))}
    for bn, (gk, alt) in biomes.items():
        rnd = random.Random(sum(map(ord, bn))); base = col(gk); T = []
        for i in range(4):  # chão base
            t = tile_noise(base, rnd)
            if i >= 2:
                d = ImageDraw.Draw(t)
                for _ in range(4):
                    x = rnd.randint(2, 28); d.line([x, 30, x + rnd.randint(-2, 2), 24], fill=shade(base, .3), width=1)
            T.append(t)
        for i in range(4):  # trilha
            T.append(tile_noise(alt, rnd, 22, .06))
        for i in range(4):  # pedra/lama
            t = tile_noise((90, 96, 96, 255) if bn != "bacia" else (40, 50, 70, 255), rnd, 18, .1); d = ImageDraw.Draw(t)
            d.line([rnd.randint(0, 31), 0, rnd.randint(0, 31), 31], fill=(0, 0, 0, 60), width=1); T.append(t)
        for i in range(4):  # contaminado
            t = tile_noise(col("contam")[:3] + (255,) if False else (92, 28, 88, 255), rnd, 30, .12); d = ImageDraw.Draw(t)
            for _ in range(2):
                x, y = rnd.randint(4, 27), rnd.randint(4, 27); d.ellipse([x - 3, y - 2, x + 3, y + 2], fill=(180, 50, 170, 120))
            T.append(t)
        for i in range(4):  # parede (muralha)
            t = tile_noise((72, 40, 86, 255), rnd, 14, .08); d = ImageDraw.Draw(t)
            d.line([0, 15, 31, 15], fill=(30, 12, 40, 255)); d.line([16 if i % 2 else 8, 0, 16 if i % 2 else 8, 15], fill=(30, 12, 40, 255)); d.line([24, 15, 24, 31], fill=(30, 12, 40, 255))
            T.append(t)
        img = new(32 * 4, 32 * 5)
        for i, t in enumerate(T):
            img.paste(t, ((i % 4) * 32, (i // 4) * 32))
        save(img, "world", f"tileset_{bn}.png")
        register("world", f"tileset_{bn}.png", 32, 32, [("grid", 4, 0, False)])
        MANIFEST[f"world/tileset_{bn}.png"]["rows"] = ["chao", "trilha", "pedra", "contaminado", "muralha"]


# ------------------------------------------------------------ UI
def panel9(c, border, name, size=48, rad=6):
    im = new(size); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=rad, fill=c, outline=border, width=2)
    d.rounded_rectangle([3, 3, size - 4, size - 4], radius=rad - 2, outline=border[:3] + (70,), width=1)
    save(im, "ui", name)


def gen_ui():
    panel9((13, 28, 31, 245), (56, 148, 133, 255), "panel_modal.png")
    panel9((23, 41, 43, 250), (56, 148, 133, 255), "panel_card.png")
    panel9((23, 41, 43, 250), (255, 209, 89, 255), "panel_card_evo.png")
    panel9((23, 41, 43, 250), (140, 242, 158, 255), "panel_card_owned.png")
    panel9((8, 18, 20, 200), (51, 128, 117, 200), "panel_hud.png", rad=5)
    panel9((20, 10, 20, 225), (204, 102, 230, 255), "panel_boss.png")
    for nm, bg, bd in (("normal", (20, 43, 43), (56, 148, 133)), ("hover", (31, 69, 66), (77, 217, 179)), ("pressed", (13, 31, 31), (77, 217, 179)), ("disabled", (15, 23, 23), (51, 71, 69))):
        panel9(bg + (255,), bd + (255,), f"button_{nm}.png", rad=5)
    # barras (fill 64x16) e fundo
    for nm, c in (("hp", (217, 64, 77)), ("o2", (77, 191, 242)), ("xp", (242, 204, 77)), ("boss", (179, 77, 217))):
        im = new(64, 16); d = ImageDraw.Draw(im); d.rectangle([0, 0, 63, 15], fill=c + (255,)); d.rectangle([0, 0, 63, 4], fill=shade(c + (255,), .35)); d.rectangle([0, 11, 63, 15], fill=shade(c + (255,), -.3))
        save(im, "ui", f"bar_{nm}.png")
    im = new(64, 16); ImageDraw.Draw(im).rectangle([0, 0, 63, 15], fill=(13, 20, 20, 230), outline=(77, 115, 107, 255)); save(im, "ui", "bar_bg.png")
    # vinhetas radiais 256
    for nm, c in (("o2", (89, 26, 128)), ("hurt", (230, 13, 13))):
        yy, xx = np.mgrid[0:256, 0:256]; r = np.hypot(xx - 127.5, yy - 127.5) / 128
        a = np.clip((r - .55) / .45, 0, 1) ** 1.5 * 230
        arr = np.zeros((256, 256, 4), "uint8"); arr[..., 0], arr[..., 1], arr[..., 2], arr[..., 3] = c[0], c[1], c[2], a.astype("uint8")
        save(Image.fromarray(arr, "RGBA"), "ui", f"vignette_{nm}.png")
    # ícones 32x32 (12)
    icons = ["pulse", "dash", "emergency", "weapon", "dose", "o2", "shield", "biomass", "nucleus", "scanner", "mutation", "suit"]
    fr = []
    for k, nm in enumerate(icons):
        im = new(32); d = ImageDraw.Draw(im); cc = [col("core"), col("accent"), col("warn"), col("player_gun"), col("bad"), col("nucleus"), col("core"), col("bio"), col("nucleus_violet"), col("core_violet"), col("good"), col("tech_orange")][k]
        d.rounded_rectangle([1, 1, 30, 30], radius=4, fill=(10, 24, 26, 255), outline=cc, width=1)
        if nm == "pulse":
            d.ellipse([7, 7, 24, 24], outline=cc, width=2); d.ellipse([12, 12, 19, 19], fill=cc)
        elif nm == "dash":
            d.polygon([(6, 16), (18, 8), (18, 13), (26, 13), (26, 19), (18, 19), (18, 24)], fill=cc)
        elif nm == "emergency":
            d.ellipse([6, 6, 25, 25], outline=cc, width=3); d.line([16, 8, 16, 18], fill=cc, width=3); d.rectangle([15, 21, 17, 23], fill=cc)
        elif nm == "weapon":
            d.polygon([(8, 22), (22, 9), (25, 12), (11, 25)], fill=cc); d.ellipse([22, 6, 27, 11], fill=(255, 255, 255, 255))
        elif nm == "dose":
            d.rectangle([12, 8, 19, 24], fill=cc); d.rectangle([9, 15, 22, 18], fill=(255, 255, 255, 255))
        elif nm == "o2":
            d.ellipse([9, 9, 22, 22], outline=cc, width=2); d.text((11, 11), "O", fill=cc)
        elif nm == "shield":
            d.polygon([(16, 6), (25, 10), (23, 21), (16, 26), (9, 21), (7, 10)], outline=cc, width=2)
        elif nm in ("biomass", "nucleus"):
            d.polygon([(16, 6), (24, 16), (16, 26), (8, 16)], fill=cc)
        elif nm == "scanner":
            d.arc([6, 6, 26, 26], 200, 340, fill=cc, width=2); d.arc([10, 10, 22, 22], 200, 340, fill=cc, width=2); d.ellipse([14, 18, 18, 22], fill=cc)
        elif nm == "mutation":
            d.line([10, 8, 22, 24], fill=cc, width=2); d.line([22, 8, 10, 24], fill=cc, width=2)
        else:
            d.rectangle([10, 8, 22, 24], outline=cc, width=2); d.rectangle([13, 11, 19, 15], fill=cc)
        fr.append(im)
    save(sheet([("icons", fr)], 32), "ui", "icons.png"); register("ui", "icons.png", 32, 32, [("icons:" + ",".join(icons), 12, 1, False)])
    # logo
    f1 = f2 = None
    for fp in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
        if os.path.exists(fp):
            f1, f2 = ImageFont.truetype(fp, 36), ImageFont.truetype(fp, 64)
            break
    if f1 is None:  # sem fonte TTF: o logo sai sem acento
        f1 = f2 = ImageFont.load_default()
    im = new(640, 150); d = ImageDraw.Draw(im)
    d.text((6, 4), "PROJETO", font=f1, fill=(148, 184, 173, 255)); d.text((6, 48), "ÚLTIMA SEMENTE", font=f2, fill=(77, 217, 179, 255))
    save(im, "ui", "logo.png")
    # fundo do menu em 3 camadas (1280x720)
    rnd = random.Random(21); W, H = 1280, 720
    far = new(W, H); d = ImageDraw.Draw(far)
    for y in range(H):
        k = y / H; d.line([0, y, W, y], fill=(int(4 + 8 * k), int(12 + 22 * k), int(12 + 20 * k), 255))
    d.ellipse([W * .78 - 300, H * .55 - 300, W * .78 + 300, H * .55 + 300], fill=(20, 51, 46, 120)); d.ellipse([W * .78 - 170, H * .55 - 170, W * .78 + 170, H * .55 + 170], fill=(25, 77, 66, 120))
    save(far, "ui", "menu_bg_far.png")
    mid = new(W, H); d = ImageDraw.Draw(mid)
    for i in range(10):
        x0 = rnd.randint(0, W); d.line([x0, H, x0 + rnd.randint(-120, 120), H - rnd.randint(200, 420)], fill=(40, 20, 55, 200), width=rnd.randint(8, 20))
    save(mid, "ui", "menu_bg_mid.png")
    near = new(W, H); d = ImageDraw.Draw(near); c = (W * .78, H * .55)
    for r, a in ((90, 40), (56, 90), (30, 230)):
        d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=(120, 240, 230, a))
    for i in range(8):
        ang = i * TAU / 8; d.line([c[0] + math.cos(ang) * 100, c[1] + math.sin(ang) * 100, c[0] + math.cos(ang) * 160, c[1] + math.sin(ang) * 160], fill=(190, 100, 230, 190), width=4)
    save(near, "ui", "menu_bg_near.png")
    # setas-guia e marcadores do mapa
    arrow = new(32); d = ImageDraw.Draw(arrow); d.polygon([(30, 16), (8, 6), (13, 16), (8, 26)], fill=(255, 255, 255, 255)); save(outline(arrow), "ui", "arrow.png")
    for nm, c in (("player", (255, 140, 51)), ("poi", (217, 140, 255)), ("nest", (242, 102, 166)), ("station", (77, 230, 255)), ("cache", (217, 245, 90))):
        im = new(16); d = ImageDraw.Draw(im); d.ellipse([3, 3, 12, 12], fill=c + (255,), outline=(255, 255, 255, 255)); save(im, "ui", f"mark_{nm}.png")


# ------------------------------------------------------------ preview e main
def preview():
    files = []
    for g in sorted(os.listdir(OUT)):
        p = os.path.join(OUT, g)
        if os.path.isdir(p):
            files += [os.path.join(p, f) for f in sorted(os.listdir(p)) if f.endswith(".png")]
    cell = 200; cols = 8; rows = (len(files) + cols - 1) // cols
    sheet_ = Image.new("RGBA", (cols * cell, rows * (cell + 14)), (28, 34, 36, 255)); d = ImageDraw.Draw(sheet_)
    for i, f in enumerate(files):
        im = Image.open(f).convert("RGBA"); im.thumbnail((cell - 8, cell - 8), Image.NEAREST)
        sc = max(1, min((cell - 8) // max(1, im.width), (cell - 8) // max(1, im.height)))
        if sc > 1:
            im = im.resize((im.width * sc, im.height * sc), Image.NEAREST)
        x, y = (i % cols) * cell, (i // cols) * (cell + 14)
        sheet_.paste(im, (x + 4, y + 14), im); d.text((x + 4, y + 1), os.path.basename(f)[:26], fill=(180, 220, 210, 255))
    sheet_.save(os.path.join(ROOT, "tools", "preview_sheets.png"))
    return len(files)


def main():
    os.makedirs(OUT, exist_ok=True)
    gen_creatures(); gen_enemy_extras(); gen_fx(); gen_pickups()
    import gen_player
    gen_player.generate(save, register, sheet)
    gen_world_props(); gen_tilesets(); gen_ui()
    json.dump(MANIFEST, open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    n = preview()
    print(f"OK: {n} PNGs em assets/art; manifest.json e tools/preview_sheets.png gerados")


if __name__ == "__main__":
    main()
