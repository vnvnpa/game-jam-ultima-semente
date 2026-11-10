"""Painéis, botões, barras e controles da interface em pixel art (sem suavização)."""
import os, math
from pix import C, hx, mix, BAYER4, contact
from ui_pal import T, V, G, R, B, L, O, W, glow, orb, edge_color

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "assets", "art", "ui")
os.makedirs(OUT, exist_ok=True)


def chamfer(c, w, h, n=2):
    for k in range(n):
        for i in range(n - k):
            for (x, y) in ((i, k), (w - 1 - i, k), (i, h - 1 - k), (w - 1 - i, h - 1 - k)):
                c.a[y, x] = (0, 0, 0, 0)


def stud(c, cx, cy, ramp_gem, rim):
    """Joia em losango 7x7 que fica no canto da moldura."""
    art = ["...o...",
           "..oago..".replace("o", "o")[:7] if False else "..ogo..",
           ".ogHgo.",
           "ogHhHgo",
           ".ogHgo.",
           "..ogo..",
           "...o..."]
    pal = {"o": edge_color(ramp_gem[3]), "g": ramp_gem[3], "H": ramp_gem[4], "h": ramp_gem[-1]}
    c.art(cx - 3, cy - 3, art, pal)
    c.px(cx - 1, cy - 1, rim)


def panel(name, ramp, gem, fill_a=250, thick=True, fill=None, brackets=False, alpha_rim=255):
    s = 48
    c = C(s, s)
    ramp = list(ramp)
    outl, rim, mid, gap, inner = ramp[0], ramp[5], ramp[3], ramp[1], ramp[4]
    fillc = fill or ramp[1]
    fillc = (*fillc[:3], fill_a)
    # fundo
    c.rect(1, 1, s - 2, s - 2, fillc)
    # sombra interna (dither) nas bordas
    shadow = (*ramp[0][:3], fill_a)
    for j in range(s):
        for i in range(s):
            d = min(i, j, s - 1 - i, s - 1 - j)
            if 4 <= d <= 9:
                t = (10 - d) / 7.0 * 0.85
                if t > BAYER4[j % 4, i % 4]:
                    c.px(i, j, shadow)
    # perfil da borda: d0 contorno, d1 rim, d2 mid, d3 vão, d4 linha interna
    prof = {0: outl, 1: rim, 2: mid, 3: gap}
    if not thick:
        prof = {0: outl, 1: mid, 2: gap}
    for d, col in prof.items():
        c.frame(d, d, s - 2 * d, s - 2 * d, (*col[:3], alpha_rim if d < 3 else fill_a))
    if thick:
        c.frame(4, 4, s - 8, s - 8, (*inner[:3], fill_a))
    # luz superior-esquerda: rim brilhante só nas bordas de cima e esquerda
    for i in range(6, s - 6):
        c.px(i, 1, ramp[6] if i % 6 else rim)
    for j in range(6, s - 6):
        c.px(1, j, rim)
    # base escura
    for i in range(3, s - 3):
        c.px(i, s - 2, ramp[2])
    chamfer(c, s, s, 2)
    if brackets:
        return c
    for (cx, cy) in ((5, 5), (s - 6, 5), (5, s - 6), (s - 6, s - 6)):
        stud(c, cx, cy, gem, rim)
    chamfer(c, s, s, 1)
    c.save(os.path.join(OUT, name))
    return c


def panel_hud(name, ramp, a=200):
    """Painel do HUD: translúcido, com colchetes nos cantos (não compete com o jogo)."""
    s = 48
    c = C(s, s)
    fillc = (*ramp[0][:3], a)
    c.rect(1, 1, s - 2, s - 2, fillc)
    c.frame(0, 0, s, s, (*ramp[2][:3], 230))
    c.frame(1, 1, s - 2, s - 2, (*ramp[1][:3], a))
    for (x0, y0, dx, dy) in ((0, 0, 1, 1), (s - 1, 0, -1, 1), (0, s - 1, 1, -1), (s - 1, s - 1, -1, -1)):
        for k in range(7):
            c.px(x0 + dx * k, y0, ramp[5])
            c.px(x0, y0 + dy * k, ramp[5])
        c.px(x0 + dx, y0 + dy, ramp[6])
        c.px(x0 + dx * 2, y0 + dy * 2, ramp[4])
    for i in range(10, s - 10):
        c.px(i, 1, (*ramp[3][:3], 255))
    chamfer(c, s, s, 1)
    c.save(os.path.join(OUT, name))


def button(name, state):
    s = 48
    c = C(s, s)
    P = {
        "normal": dict(rim=T[5], lit=T[6], b1=T[3], b2=T[2], low=T[1], gem=V[4], gem_h=V[5], inner=T[4]),
        "hover": dict(rim=T[7], lit=T[8], b1=T[4], b2=T[3], low=T[2], gem=T[7], gem_h=T[8], inner=T[6]),
        "pressed": dict(rim=T[4], lit=T[5], b1=T[1], b2=T[1], low=T[2], gem=V[3], gem_h=V[4], inner=T[3]),
        "disabled": dict(rim=T[3], lit=T[3], b1=T[2], b2=T[1], low=T[1], gem=T[3], gem_h=T[3], inner=T[2]),
    }[state]
    c.rect(0, 0, s, s, T[0])
    for j in range(1, s - 1):
        t = (j - 1) / (s - 3)
        col = P["b1"] if t < 0.42 else P["b2"]
        for i in range(1, s - 1):
            c.px(i, j, col)
    # transição em xadrez entre as duas bandas
    j0 = int(s * 0.42)
    for j in (j0, j0 + 1):
        for i in range(1, s - 1):
            if (i + j) % 2 == 0:
                c.px(i, j, P["b2"] if j == j0 else P["b1"])
    # base (sombra) e linha inferior
    for j in range(s - 6, s - 1):
        for i in range(1, s - 1):
            c.px(i, j, P["low"])
    # moldura interna fina (linha T4) para dar profundidade
    for i in range(3, s - 3):
        c.px(i, 3, P["inner"] if state != "pressed" else T[0])
        c.px(i, s - 7, T[0] if state != "pressed" else P["inner"])
    for j in range(3, s - 6):
        c.px(3, j, P["inner"] if state != "pressed" else T[0])
        c.px(s - 4, j, T[1] if state != "pressed" else P["inner"])
    # luz do topo e da esquerda
    for i in range(2, s - 2):
        c.px(i, 1, P["lit"] if i % 5 else P["rim"])
        c.px(i, 2, P["rim"])
    for j in range(2, s - 6):
        c.px(1, j, P["rim"])
    for i in range(1, s - 1):
        c.px(i, s - 2, T[0])
    chamfer(c, s, s, 2)
    # joias pequenas nos cantos superiores (3x3)
    for (cx, cy) in ((5, 5), (s - 6, 5), (5, s - 8), (s - 6, s - 8)):
        c.px(cx, cy, P["gem_h"]); c.px(cx - 1, cy, P["gem"]); c.px(cx + 1, cy, P["gem"])
        c.px(cx, cy - 1, P["gem"]); c.px(cx, cy + 1, P["gem"])
    if state == "disabled":
        for j in range(4, s - 4):
            for i in range(4, s - 4):
                if (i * 3 + j * 5) % 9 == 0:
                    c.px(i, j, T[1])
    c.save(os.path.join(OUT, name))


def button_focus():
    s = 48
    c = C(s, s)
    g1, g2 = G[5], G[3]
    for (x0, y0, dx, dy) in ((1, 1, 1, 1), (s - 2, 1, -1, 1), (1, s - 2, 1, -1), (s - 2, s - 2, -1, -1)):
        for k in range(8):
            c.px(x0 + dx * k, y0, g1)
            c.px(x0, y0 + dy * k, g1)
        c.px(x0 + dx, y0 + dy, g2)
    chamfer(c, s, s, 1)
    c.save(os.path.join(OUT, "button_focus.png"))


def bar(name, ramp, bg=False):
    w, h = 64, 16
    c = C(w, h)
    if bg:
        c.rect(0, 0, w, h, T[0])
        c.rect(1, 1, w - 2, h - 2, (8, 18, 21, 255))
        c.rect(1, 1, w - 2, 3, (5, 11, 13, 255))                 # sombra interna
        c.rect(1, h - 3, w - 2, 1, T[2])                         # reflexo inferior
        c.frame(0, 0, w, h, T[0])
        for i in range(1, w - 1):
            c.px(i, h - 2, T[3] if i % 2 else T[2])
        chamfer(c, w, h, 1)
        c.px(0, 0, (0, 0, 0, 0))
        c.save(os.path.join(OUT, name))
        return
    base = ramp[3]
    rows = [ramp[0], ramp[5], ramp[4], ramp[4], ramp[4], ramp[3], ramp[3], ramp[3], ramp[3], ramp[3], ramp[2], ramp[2], ramp[2], ramp[1], ramp[1], ramp[0]]
    for j in range(h):
        for i in range(w):
            c.px(i, j, rows[j])
    # dither de textura (grãos de luz), só horizontal para esticar bem
    for j in (5, 6):
        for i in range(0, w):
            if (i + j) % 4 == 0:
                c.px(i, j, ramp[4])
    for i in range(0, w):
        if i % 8 in (0, 1):
            c.px(i, 1, ramp[6])
    # capas laterais: esquerda escura, direita brilhante (ponta da barra)
    for j in range(h):
        c.px(0, j, ramp[0] if j in (0, h - 1) else ramp[1])
        c.px(w - 1, j, ramp[0] if j in (0, h - 1) else ramp[5])
        c.px(w - 2, j, ramp[4] if 1 < j < h - 2 else ramp[2])
    c.save(os.path.join(OUT, name))


def slider_parts():
    # trilha: mesma linguagem das barras de vida (moldura escura, sombra interna, reflexo embaixo)
    g = C(16, 10)
    g.rect(0, 0, 16, 10, T[0])
    g.rect(1, 1, 14, 8, (8, 18, 21, 255))
    g.rect(1, 1, 14, 3, (5, 11, 13, 255))
    for i in range(1, 15):
        g.px(i, 8, T[3] if i % 2 else T[2])
    g.frame(0, 0, 16, 10, T[0])
    chamfer(g, 16, 10, 1)
    g.save(os.path.join(OUT, "slider_groove.png"))
    # preenchimento: bandas de luz como na barra de vida; ponta direita brilhante marca o nível
    f = C(16, 10)
    rows = [T[0], T[7], T[6], T[6], T[5], T[5], T[4], T[4], T[3], T[0]]
    for j in range(10):
        for i in range(16):
            f.px(i, j, rows[j])
    for i in range(0, 16):
        if i % 4 == 0:
            f.px(i, 2, T[8])
    for j in range(10):
        f.px(0, j, T[0] if j in (0, 9) else T[2])
        f.px(15, j, T[0] if j in (0, 9) else T[8])
        f.px(14, j, T[6] if 0 < j < 8 else T[3])
    f.save(os.path.join(OUT, "slider_fill.png"))
    # marca de graduação (início, 25%, 50%, 75%, fim): sai um pouco da trilha em cima e embaixo
    tk = C(3, 16)
    for j in range(16):
        edge = j < 2 or j >= 14
        tk.px(1, j, T[6] if edge else T[0])
        if edge:
            tk.px(0, j, T[4]); tk.px(2, j, T[4])
        elif j % 2 == 0:
            tk.px(0, j, T[1]); tk.px(2, j, T[1])
    tk.save(os.path.join(OUT, "slider_tick.png"))
    for nm, hi in (("slider_grabber.png", False), ("slider_grabber_hi.png", True)):
        s = C(14, 22)
        body = (T[7] if hi else T[6], T[8] if hi else T[7], T[5])
        art = ["....oooooo....",
               "...oHHHHHHo...",
               "..oHhhhhhhHo..",
               "..oHhggggHHo..",
               "..oHhggggHHo..",
               "..oHhggggHHo..",
               "..oHhggggHHo..",
               "..oHhggggHHo..",
               "..oHhggggHHo..",
               "..oHhggggHHo..",
               "..oHhggggHHo..",
               "..oHhggggHHo..",
               "..oHhggggHHo..",
               "..oHHggggHbo..",
               "..oHHHHHHbbo..",
               "..oHbbbbbbbo..",
               "...obbbbbbo...",
               "....oooooo...."]
        s2 = C(14, 18)
        pal = {"o": T[0], "H": body[0], "h": body[1], "g": T[3], "b": body[2]}
        s2.art(0, 0, art, pal)
        for j in range(3, 13):
            s2.px(6, j, V[5] if hi else V[4])
            s2.px(7, j, V[4] if hi else V[3])
        s2.save(os.path.join(OUT, nm))


def checkboxes():
    def box(on, hi=False):
        c = C(18, 18)
        c.rect(0, 0, 18, 18, T[0])
        c.rect(1, 1, 16, 16, T[5] if hi else T[4])
        c.rect(2, 2, 14, 14, T[1])
        c.rect(2, 2, 14, 2, (5, 11, 13, 255))
        for i in range(2, 16):
            c.px(i, 15, T[2])
        chamfer(c, 18, 18, 1)
        if on:
            art = ["........o...",
                   ".......oLo..",
                   "......oLLo..",
                   "o....oLLo...",
                   "oL..oLLo....",
                   "oLLoLLo.....",
                   ".oLLLo......",
                   "..oLo.......",
                   "...o........"]
            pal = {"o": L[1], "L": L[4]}
            c.art(4, 4, art, pal)
            c.px(11, 5, L[6]); c.px(10, 6, L[6]); c.px(5, 8, L[5]); c.px(6, 9, L[5])
        return c
    box(False).save(os.path.join(OUT, "check_off.png"))
    box(True).save(os.path.join(OUT, "check_on.png"))
    box(False, True).save(os.path.join(OUT, "check_off_hi.png"))
    box(True, True).save(os.path.join(OUT, "check_on_hi.png"))


def scrollbar():
    c = C(10, 10)
    c.rect(0, 0, 10, 10, T[0]); c.rect(1, 1, 8, 8, T[1]); c.rect(1, 1, 8, 1, (5, 11, 13, 255))
    chamfer(c, 10, 10, 1)
    c.save(os.path.join(OUT, "scroll_bg.png"))
    g = C(10, 14)
    g.rect(0, 0, 10, 14, T[0]); g.rect(1, 1, 8, 12, T[4]); g.rect(1, 1, 8, 1, T[6]); g.rect(1, 1, 1, 12, T[5]); g.rect(1, 11, 8, 2, T[3])
    for j in (5, 6, 7):
        g.px(4, j, T[7]); g.px(5, j, T[3])
    chamfer(g, 10, 14, 1)
    g.save(os.path.join(OUT, "scroll_grabber.png"))


def tabs():
    for nm, sel, hov in (("tab_selected.png", True, False), ("tab_unselected.png", False, False), ("tab_hover.png", False, True)):
        c = C(24, 28)
        base = T[3] if sel else (T[2] if hov else T[1])
        rim = T[7] if sel else (T[5] if hov else T[3])
        c.rect(0, 0, 24, 28, T[0])
        c.rect(1, 1, 22, 27, base)
        for i in range(1, 23):
            c.px(i, 1, rim)
        c.rect(1, 2, 22, 2, T[4] if sel else base)
        if sel:
            c.rect(1, 25, 22, 3, base)
        else:
            c.rect(1, 25, 22, 3, T[0])
        chamfer(c, 24, 28, 2)
        c.save(os.path.join(OUT, nm))
    c = C(24, 24)
    c.rect(0, 0, 24, 24, T[0]); c.rect(1, 1, 22, 22, T[1]); c.frame(1, 1, 22, 22, T[3])
    c.save(os.path.join(OUT, "tab_panel.png"))


def separator():
    c = C(48, 7)
    for i in range(7, 41):
        c.px(i, 3, T[4]); c.px(i, 4, T[1])
        if i % 4 == 0:
            c.px(i, 3, T[6])
    for cx in (3, 44):
        art = ["...o...", "..ovo..", ".ovhvo.", "ovhHhvo", ".ovhvo.", "..ovo..", "...o..."]
        c.art(cx - 3, 0, art, {"o": V[0], "v": V[3], "h": V[5], "H": T[8]})
    c.save(os.path.join(OUT, "separator.png"))


if __name__ == "__main__":
    panel("panel_modal.png", T, V)
    panel("panel_card.png", [T[0], T[1], T[2], T[3], T[4], T[5], T[7]], V, fill=T[2])
    panel("panel_card_evo.png", G, G, fill=(34, 24, 12, 255))
    panel("panel_card_owned.png", L, L, fill=(14, 32, 20, 255))
    panel("panel_boss.png", V, V, fill=(20, 12, 36, 255))
    panel_hud("panel_hud.png", T, 205)
    button("button_normal.png", "normal"); button("button_hover.png", "hover")
    button("button_pressed.png", "pressed"); button("button_disabled.png", "disabled")
    button_focus()
    bar("bar_bg.png", None, bg=True)
    bar("bar_hp.png", R); bar("bar_o2.png", B); bar("bar_xp.png", G); bar("bar_boss.png", V)
    slider_parts(); checkboxes(); scrollbar(); tabs(); separator()
    files = [os.path.join(OUT, f) for f in ["panel_modal.png", "panel_card.png", "panel_card_evo.png", "panel_card_owned.png", "panel_boss.png", "panel_hud.png",
                                            "button_normal.png", "button_hover.png", "button_pressed.png", "button_disabled.png", "button_focus.png",
                                            "bar_bg.png", "bar_hp.png", "bar_o2.png", "bar_xp.png", "bar_boss.png",
                                            "slider_groove.png", "slider_fill.png", "slider_grabber.png", "check_off.png", "check_on.png", "scroll_grabber.png", "tab_selected.png", "tab_unselected.png", "separator.png"]]
    contact(files, 4, 6, "/tmp/ui_kit.png", pad=10)
