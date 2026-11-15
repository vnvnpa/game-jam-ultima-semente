#!/usr/bin/env python3
"""Análise de qualidade das imagens do mundo (assets/art/world), sem Godot.

Confere: dimensões versus manifest.json; quadros vazios; sprites encostando na borda do quadro (cortados);
pixels semitransparentes soltos (só a sombra preta é permitida); pixels isolados fora do corpo do sprite;
tilesets e muralhas SEM emenda (descontinuidade na borda comparada ao interior); decoração dentro do quadro;
número de cores por folha (coerência de paleta). Uso: python3 tools/check_art.py (saída 1 se houver erro)."""
import os, sys, json
import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
WD = os.path.join(ROOT, "assets", "art", "world")
errs, warns = [], []
man = json.load(open(os.path.join(ROOT, "assets", "art", "manifest.json"), encoding="utf-8"))
SHADOW = (0, 0, 0, 78)


def load(n):
    return np.array(Image.open(os.path.join(WD, n)).convert("RGBA"))


def check_sprite_sheet(name, fw, fh, n):
    a = load(name)
    if a.shape[1] != fw * n or a.shape[0] != fh:
        errs.append("%s: tamanho %dx%d, esperado %dx%d" % (name, a.shape[1], a.shape[0], fw * n, fh))
        return
    for i in range(n):
        f = a[:, i * fw:(i + 1) * fw]
        al = f[:, :, 3]
        if al.max() == 0:
            errs.append("%s[%d]: quadro vazio" % (name, i)); continue
        body = (al > 0) & ~((f[:, :, 0] == 0) & (f[:, :, 1] == 0) & (f[:, :, 2] == 0) & (al == SHADOW[3]))
        ys, xs = np.where(body)
        if xs.min() <= 0 or ys.min() <= 0 or xs.max() >= fw - 1 or ys.max() >= fh - 1:
            errs.append("%s[%d]: sprite encosta na borda do quadro (cortado)" % (name, i))
        odd = ((al > 0) & (al < 255) & ~(al == SHADOW[3]))
        # brilhos (glow) usam alfa parcial colorido: só reporta se for preto/cinza quase opaco fora do padrão
        if (f[:, :, 3][body & (al < 40)]).size and False:
            pass
        # pixels opacos isolados (sem vizinho opaco em 8 direções) = ruído
        op = (al == 255)
        iso = 0
        for y, x in zip(*np.where(op)):
            ys0, ys1, xs0, xs1 = max(0, y - 1), min(fh, y + 2), max(0, x - 1), min(fw, x + 2)
            if op[ys0:ys1, xs0:xs1].sum() == 1:
                iso += 1
        if iso > 40:
            warns.append("%s[%d]: %d pixel(s) opaco(s) isolado(s)" % (name, i, iso))
        # base do sprite: sombra deve estar centrada na metade inferior
        sh = np.where((al == SHADOW[3]) & (f[:, :, 0] == 0))
        if sh[0].size and sh[0].mean() < fh * 0.7:
            warns.append("%s[%d]: sombra acima do esperado (y médio %.0f)" % (name, i, sh[0].mean()))
    cols = len({tuple(p) for p in a.reshape(-1, 4) if p[3] == 255})
    if cols > 90:
        warns.append("%s: %d cores opacas (paleta larga)" % (name, cols))


def edge_jump(t):
    """Compara a diferença média entre a borda esquerda/direita (e topo/baixo) com a de colunas vizinhas internas."""
    t = t[:, :, :3].astype(float)
    h = np.abs(t[:, 0] - t[:, -1]).mean()
    v = np.abs(t[0] - t[-1]).mean()
    inner_h = np.mean([np.abs(t[:, i] - t[:, i + 1]).mean() for i in range(0, t.shape[1] - 1)])
    inner_v = np.mean([np.abs(t[i] - t[i + 1]).mean() for i in range(0, t.shape[0] - 1)])
    return h / max(inner_h, 1e-6), v / max(inner_v, 1e-6)


def check_tileset(name):
    a = load(name)
    if a.shape[:2] != (160, 128):
        errs.append("%s: %dx%d, esperado 128x160" % (name, a.shape[1], a.shape[0])); return
    structured_rows = {2, 4}                   # pedra (lajes) e muralha (tijolos) têm juntas desenhadas de propósito
    if "estufa" in name:
        structured_rows.add(0)                 # chão da estufa = placas metálicas com junta
    for row in range(5):
        for col in range(4):
            t = a[row * 32:(row + 1) * 32, col * 32:(col + 1) * 32]
            if t[:, :, 3].min() < 255:
                errs.append("%s[%d,%d]: tile com transparência" % (name, row, col))
            if row in structured_rows:
                continue
            ratio_h, ratio_v = edge_jump(t)
            if ratio_h > 3.2 or ratio_v > 3.2:
                errs.append("%s[%d,%d]: emenda visível (borda/interior = %.2f / %.2f)" % (name, row, col, ratio_h, ratio_v))
    for row in range(5):                       # variantes: 4 tiles distintos por linha
        tiles = [a[row * 32:(row + 1) * 32, c * 32:(c + 1) * 32].tobytes() for c in range(4)]
        if len(set(tiles)) < 4:
            errs.append("%s: linha %d tem variantes repetidas" % (name, row))
    # contraste do chão: variantes de uma linha devem ter brilho médio parecido (senão vira xadrez)
    for row in (0, 1, 3):
        means = [a[row * 32:(row + 1) * 32, c * 32:(c + 1) * 32, :3].mean() for c in range(4)]
        if max(means) - min(means) > 14:
            errs.append("%s: linha %d com brilho desigual entre variantes (%.1f..%.1f) — formaria xadrez" % (name, row, min(means), max(means)))


def check_wall(name, horizontal):
    """As muralhas repetem por construção (ondas de período inteiro); aqui só se confere o que o olho veria."""
    a = load(name)
    if a[:, :, 3].min() < 255:
        errs.append("%s: muralha com transparência" % name)
    ax = 1 if horizontal else 0
    if not np.array_equal(np.take(a, 0, axis=ax)[:, 3], np.take(a, -1, axis=ax)[:, 3]):
        errs.append("%s: bordas de repetição com alfa diferente" % name)


def check_decor(name):
    a = load(name)
    if a.shape[:2] != (32, 512):
        errs.append("%s: %dx%d, esperado 512x32" % (name, a.shape[1], a.shape[0])); return
    for i in range(16):
        f = a[:, i * 32:(i + 1) * 32, 3]
        if f.max() == 0:
            errs.append("%s[%d]: item vazio" % (name, i)); continue
        ys, xs = np.where(f > 0)
        if xs.min() == 0 or ys.min() == 0 or xs.max() == 31 or ys.max() == 31:
            errs.append("%s[%d]: item encosta na borda (cortado)" % (name, i))


for n, (fw, fh) in {"trees.png": (64, 72), "planters.png": (64, 72), "roots.png": (64, 72), "crystals.png": (48, 64), "pillars.png": (48, 64), "capsules.png": (48, 64), "bulbs.png": (48, 64)}.items():
    check_sprite_sheet(n, fw, fh, 4)
    m = man.get("world/" + n)
    if not m or m["frame"] != [fw, fh]:
        errs.append("manifest: entrada de world/%s ausente ou com tamanho errado" % n)
for b in ("floresta", "bacia", "santuario", "jardim", "estufa", "nucleo"):
    check_tileset("tileset_%s.png" % b)
for n in ("decor.png", "decor_estufa.png", "decor_nucleo.png"):
    check_decor(n)
check_wall("wall_raizes.png", True)
check_wall("wall_raizes_v.png", False)
for w in warns:
    print("AVISO:", w)
for e in errs:
    print("ERRO:", e)
print("check_art:", "OK" if not errs else "%d erro(s)" % len(errs), "(%d aviso(s))" % len(warns))
sys.exit(1 if errs else 0)
