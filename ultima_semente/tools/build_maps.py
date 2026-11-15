#!/usr/bin/env python3
"""Escreve scenes/world/garden_map.tscn e heart_map.tscn com layouts PRÓPRIOS de cada fase.

Santuário do Último Jardim (garden): Eclusa a sudoeste -> Estufas Esquecidas (fileiras de vasos e
  cápsulas) -> Jardim Suspenso (colunata dos Arquitetos, 2 zonas contaminadas com mecanismos) ->
  muralha + Barreira de Raízes -> Câmara do Jardineiro (faixa norte inteira).
Coração de Nymara (heart): Câmara de Acesso a oeste -> Raízes Profundas (3 cortinas de raízes
  com passagens em zigue-zague) -> Câmara do Núcleo (arena a leste, cercada de cristais/bulbos).

Os obstáculos são sorteados com semente fixa e regras de exclusão (estações, interativos, caminhos,
arena, muralhas). Depois rode tools/check_map_layout.py para validar colisões e alcançabilidade.
"""
import os, re, math, random

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SC = os.path.join(ROOT, "scenes", "world")
W_, H_ = 3600, 2600

KINDS = {  # chave -> (id do ext_resource, cena, prefixo do nome, faixa de raio)
    "tree": ("16_tree", "tree.tscn", "Tree", (17, 27)),
    "crystal": ("14_crystal", "crystal.tscn", "Crystal", (15, 26)),
    "pillar": ("15_pillar", "pillar.tscn", "Pillar", (17, 25)),
    "planter": ("30_planter", "planter.tscn", "Planter", (22, 26)),
    "capsule": ("31_capsule", "capsule.tscn", "Capsule", (17, 21)),
    "root": ("32_root", "root_mass.tscn", "Root", (24, 32)),
    "bulb": ("33_bulb", "bulb.tscn", "Bulb", (14, 18)),
}


class Layout:
    """Acumula elementos e valida posições durante a geração."""

    def __init__(self, seed):
        self.rnd = random.Random(seed)
        self.obs = []          # (kind, x, y, r)
        self.fixed = []        # (x, y, raio_livre): pontos que precisam ficar livres
        self.rects = []        # (x0, y0, x1, y1): retângulos proibidos (muralhas, portão)

    def keep_free(self, x, y, r):
        self.fixed.append((x, y, r))

    def ok(self, x, y, r, gap=16):
        if x < 70 or y < 70 or x > W_ - 70 or y > H_ - 70:
            return False
        for (fx, fy, fr) in self.fixed:
            if math.hypot(x - fx, y - fy) < fr + r:
                return False
        for (x0, y0, x1, y1) in self.rects:
            if x0 - r < x < x1 + r and y0 - r < y < y1 + r:
                return False
        for (_, ox, oy, orr) in self.obs:
            if math.hypot(x - ox, y - oy) < orr + r + gap:
                return False
        return True

    def add(self, kind, x, y, r=None, gap=16):
        lo, hi = KINDS[kind][3]
        r = r if r is not None else round(self.rnd.uniform(lo, hi), 1)
        if self.ok(x, y, r, gap):
            self.obs.append((kind, round(x, 1), round(y, 1), r))
            return True
        return False

    def scatter(self, kind, n, rect, tries=40, gap=22, avoid=None):
        done = 0
        x0, y0, x1, y1 = rect
        for _ in range(n * tries):
            if done >= n:
                break
            x, y = self.rnd.uniform(x0, x1), self.rnd.uniform(y0, y1)
            if avoid and avoid(x, y):
                continue
            if self.add(kind, x, y, gap=gap):
                done += 1
        return done

    def cluster(self, kind, cx, cy, n, spread, gap=10):
        done = 0
        for _ in range(n * 30):
            if done >= n:
                break
            a, d = self.rnd.random() * math.tau, self.rnd.uniform(0, spread)
            if self.add(kind, cx + math.cos(a) * d, cy + math.sin(a) * d, gap=gap):
                done += 1
        return done

    def line(self, kind, x0, y0, x1, y1, step, jitter=6, gaps=()):
        """Fileira de obstáculos; `gaps` = lista de (centro, meia-largura) ao longo do eixo maior."""
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        for i in range(n + 1):
            t = i / n
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            axis = y if abs(y1 - y0) > abs(x1 - x0) else x
            if any(abs(axis - c) < hw for c, hw in gaps):
                continue
            self.add(kind, x + self.rnd.uniform(-jitter, jitter), y + self.rnd.uniform(-jitter, jitter), gap=4)


def wavy_curtain(lay, x0, gaps, amp=34, period=170, step=60, rmin=28, rmax=34):
    """Cortina orgânica de raízes: duas fileiras ondulantes defasadas, com passagens em `gaps`."""
    y = 90
    i = 0
    while y < H_ - 80:
        if not any(abs(y - c) < hw for c, hw in gaps):
            for off in (0, 40):
                x = x0 + off + amp * math.sin(y / period * math.tau / 2) + lay.rnd.uniform(-6, 6)
                lay.add("root", x, y + off * 0.45, r=round(lay.rnd.uniform(rmin, rmax), 1), gap=-6)
        y += step
        i += 1


def fmt(v):
    return "%.1f" % v


def read_blocks(path, parent):
    """Blocos [node ...] cujo parent é `parent` (para reaproveitar Interactables/Caches)."""
    t = open(path, encoding="utf-8").read()
    out = []
    for m in re.finditer(r'\[node name="(\w+)" parent="%s" instance=ExtResource\("([^"]+)"\)\]\n((?:(?!\[).*\n)*)' % re.escape(parent), t):
        props = {}
        for ln in m.group(3).strip().split("\n"):
            if " = " in ln:
                k, v = ln.split(" = ", 1)
                props[k] = v
        out.append((m.group(1), props))
    return out


def emit(spec, path):
    ext = [
        ("Script", "res://scripts/world/world_map.gd", "1_world_map"),
        ("Texture2D", "res://assets/world/garden_terrain.png", "2_terrain"),
        ("PackedScene", "res://scenes/world/region_zone.tscn", "3_region_zon"),
        ("PackedScene", "res://scenes/world/hostile_zone.tscn", "4_hostile_zo"),
        ("PackedScene", "res://scenes/world/station.tscn", "5_station"),
        ("PackedScene", "res://scenes/world/root_gate.tscn", "13_root_gate"),
        ("PackedScene", "res://scenes/entities/biomass_pickup.tscn", "17_biomass_pi"),
        ("PackedScene", "res://scenes/entities/interactable.tscn", "18_interactab"),
        ("PackedScene", "res://scenes/world/boss_arena.tscn", "21_boss_arena"),
        ("Script", "res://scripts/world/ground_painter.gd", "90_painter"),
        ("TileSet", "res://assets/art/world/ground_tileset.tres", "91_tileset"),
        ("Texture2D", "res://assets/art/world/%s" % spec["decor"], "92_decor"),
        ("Texture2D", "res://assets/art/world/wall_raizes.png", "93_wall_h"),
        ("Texture2D", "res://assets/art/world/wall_raizes_v.png", "94_wall_v"),
    ]
    used = sorted({k for (k, *_r) in spec["obs"]})
    for k in used:
        ext.append(("PackedScene", "res://scenes/world/%s" % KINDS[k][1], KINDS[k][0]))
    subs = [("RectangleShape2D_6", (3800, 100)), ("RectangleShape2D_7", (3800, 100)), ("RectangleShape2D_8", (100, 2600)), ("RectangleShape2D_9", (100, 2600))]
    for i, w in enumerate(spec["walls"]):
        subs.append(("RectangleShape2D_%d" % (10 + i), (w["w"], w["h"])))
    L = ["[gd_scene load_steps=%d format=3]\n" % (len(ext) + len(subs) + 1)]
    for (tp, p, i) in ext:
        L.append('[ext_resource type="%s" path="%s" id="%s"]' % (tp, p, i))
    L.append("")
    for (i, (w, h)) in subs:
        L.append('[sub_resource type="RectangleShape2D" id="%s"]\nsize = Vector2(%s, %s)\n' % (i, fmt(w), fmt(h)))
    L.append('[node name="WorldMap" type="Node2D"]\nscript = ExtResource("1_world_map")\n')
    L.append('[node name="Terrain" type="Sprite2D" parent="."]\ntexture = ExtResource("2_terrain")\ncentered = false\nscale = Vector2(4.0, 4.0)\n')
    bs = ",\n".join('"%s": %d' % (k, v) for k, v in spec["biomes"].items())
    dk = ",\n".join('"%s": %s' % (k, v) for k, v in spec["decor_kinds"].items())
    L.append('[node name="Ground" type="TileMapLayer" parent="."]\ntile_set = ExtResource("91_tileset")\nscript = ExtResource("90_painter")\nbiome_sources = {\n%s\n}\ndefault_source = %d\ndecor_kinds = {\n%s\n}\ndecor_texture = ExtResource("92_decor")\ndecor_per_region = %d\n' % (bs, spec["default_source"], dk, spec["decor_count"]))
    L.append('[node name="Regions" type="Node2D" parent="."]\n')
    for r in spec["regions"]:
        x0, y0, x1, y1 = r["rect"]
        L.append('[node name="%s" parent="Regions" instance=ExtResource("3_region_zon")]\nposition = Vector2(%s, %s)\nregion_name = "%s"\nsize = Vector2(%s, %s)\nmap_color = Color(%s)\n%s' % (
            r["node"], fmt((x0 + x1) / 2), fmt((y0 + y1) / 2), r["name"], fmt(x1 - x0), fmt(y1 - y0), r["color"], "locked_until_gate = true\n" if r.get("locked") else ""))
    L.append('[node name="HostileZones" type="Node2D" parent="."]\n')
    for z in spec["hostile"]:
        L.append('[node name="%s" parent="HostileZones" instance=ExtResource("4_hostile_zo")]\nposition = Vector2(%s, %s)\nsize = Vector2(%s, %s)\n' % (z[0], fmt(z[1]), fmt(z[2]), fmt(z[3]), fmt(z[4])))
    L.append('[node name="Stations" type="Node2D" parent="."]\n')
    for s in spec["stations"]:
        L.append('[node name="%s" parent="Stations" instance=ExtResource("5_station")]\nposition = Vector2(%s, %s)\nstation_id = "%s"\ndisplay_name = "%s"\nradius = %s\n' % (s[0], fmt(s[1]), fmt(s[2]), s[3], s[4], fmt(s[5])))
    L.append('[node name="Borders" type="Node2D" parent="."]\n')
    for nm, (px, py), sid in (("Top", (1800, -50), 6), ("Bottom", (1800, 2650), 7), ("Left", (-50, 1300), 8), ("Right", (3650, 1300), 9)):
        L.append('[node name="%s" type="StaticBody2D" parent="Borders"]\nposition = Vector2(%s, %s)\ncollision_layer = 1\ncollision_mask = 0\n\n[node name="Shape" type="CollisionShape2D" parent="Borders/%s"]\nshape = SubResource("RectangleShape2D_%d")\n' % (nm, fmt(px), fmt(py), nm, sid))
    L.append('[node name="Walls" type="Node2D" parent="."]\n')
    for i, w in enumerate(spec["walls"]):
        tex = "93_wall_h" if w["w"] >= w["h"] else "94_wall_v"
        L.append('[node name="%s" type="StaticBody2D" parent="Walls"]\nposition = Vector2(%s, %s)\ncollision_layer = 1\ncollision_mask = 0\n\n[node name="Shape" type="CollisionShape2D" parent="Walls/%s"]\nshape = SubResource("RectangleShape2D_%d")\n\n[node name="Visual" type="TextureRect" parent="Walls/%s"]\nlayout_mode = 0\noffset_left = %s\noffset_top = %s\noffset_right = %s\noffset_bottom = %s\nmouse_filter = 2\ntexture = ExtResource("%s")\nexpand_mode = 1\nstretch_mode = 1\n' % (
            w["name"], fmt(w["x"]), fmt(w["y"]), w["name"], 10 + i, w["name"], fmt(-w["w"] / 2), fmt(-w["h"] / 2), fmt(w["w"] / 2), fmt(w["h"] / 2), tex))
    g = spec["gate"]
    L.append('[node name="Gate" parent="." instance=ExtResource("13_root_gate")]\nposition = Vector2(%s, %s)\n%s' % (fmt(g[0]), fmt(g[1]), "start_open = true\n" if g[2] else ""))
    L.append('[node name="Obstacles" type="Node2D" parent="."]\n')
    counts = {}
    for (k, x, y, r) in spec["obs"]:
        counts[k] = counts.get(k, 0) + 1
        L.append('[node name="%s%02d" parent="Obstacles" instance=ExtResource("%s")]\nposition = Vector2(%s, %s)\nradius = %s\n' % (KINDS[k][2], counts[k], KINDS[k][0], fmt(x), fmt(y), fmt(r)))
    L.append('[node name="Caches" type="Node2D" parent="."]\n')
    for i, (x, y, v) in enumerate(spec["caches"]):
        L.append('[node name="Cache%02d" parent="Caches" instance=ExtResource("17_biomass_pi")]\nposition = Vector2(%s, %s)\nvalue = %d\npersistent = true\n' % (i + 1, fmt(x), fmt(y), v))
    L.append('[node name="Interactables" type="Node2D" parent="."]\n')
    for (nm, props, (x, y)) in spec["inter"]:
        body = "\n".join("%s = %s" % (k, v) for k, v in props.items() if k != "position")
        L.append('[node name="%s" parent="Interactables" instance=ExtResource("18_interactab")]\nposition = Vector2(%s, %s)\n%s\n' % (nm, fmt(x), fmt(y), body))
    a = spec["arena"]
    L.append('[node name="BossArena" parent="." instance=ExtResource("21_boss_arena")]\nposition = Vector2(%s, %s)\n%s' % (fmt(a[0]), fmt(a[1]), "".join("%s = %s\n" % kv for kv in a[2].items())))
    open(path, "w", encoding="utf-8").write("\n".join(L))


def place_caches(lay, spots, values, rnd):
    out = []
    for (cx, cy, spread), v in zip(spots, values):
        for _ in range(80):
            x, y = cx + rnd.uniform(-spread, spread), cy + rnd.uniform(-spread, spread)
            if lay.ok(x, y, 14, gap=10):
                out.append((round(x, 1), round(y, 1), v))
                lay.obs.append(("cache_mark", x, y, 14))   # reserva o lugar (removido depois)
                break
    lay.obs = [o for o in lay.obs if o[0] != "cache_mark"]
    return out


def inter_blocks(path, positions):
    blocks = {n: p for n, p in read_blocks(path, "Interactables")}
    return [(n, blocks[n], pos) for n, pos in positions.items()]


# ====================================================================== SANTUÁRIO DO ÚLTIMO JARDIM
def build_garden():
    lay = Layout(2026)
    path = os.path.join(SC, "garden_map.tscn")
    inter_pos = {
        "TerminalEclusa": (490, 1900), "TerminalEstufa": (1420, 1500),
        "Mecanismo1": (650, 1000), "Mecanismo2": (2300, 2150), "Mecanismo3": (3100, 1250),
        "RuinaJardimA": (1000, 1850), "VozDaRede": (2250, 1000), "TerminalInterior": (3000, 250),
    }
    inter = inter_blocks(path, inter_pos)
    stations = [("Eclusa", 400, 1900, "eclusa", "Eclusa de Entrada", 170), ("Estufa", 1350, 1500, "estufa", "Estufa Segura", 120),
                ("Bolsao1", 2650, 1500, "bolsao1", "Bolsão de Ar", 100), ("Bolsao2", 1950, 2050, "bolsao2", "Bolsão de Ar", 100)]
    arena = (1800, 290, {})
    # pontos livres
    lay.keep_free(400, 1970, 120)
    for (_, x, y, _i, _n, r) in stations:
        lay.keep_free(x, y, r + 45)
    for pos in inter_pos.values():
        lay.keep_free(pos[0], pos[1], 80)
    lay.keep_free(arena[0], arena[1], 330)
    lay.rects += [(0, 618, 1700, 662), (1900, 618, 3600, 662), (1650, 560, 1950, 780)]   # muralha, portão e antecâmara
    lay.keep_free(1800, 720, 100)
    # corredor central (Estufa -> Bolsão 1) e trilha da Eclusa à Estufa deixados livres
    for t in range(0, 11):
        lay.keep_free(1350 + (2650 - 1350) * t / 10, 1500, 70)
        lay.keep_free(400 + (1350 - 400) * t / 10, 1900 + (1500 - 1900) * t / 10, 60)

    # --- Estufas Esquecidas: blocos de vasos em fileiras (2 x 5) e cápsulas
    for (bx, by) in ((260, 1180), (780, 1180), (260, 2280), (900, 2330)):
        for row in range(2):
            for col in range(4):
                lay.add("planter", bx + col * 74, by + row * 70, r=22 + (col + row) % 3, gap=6)
    lay.line("capsule", 120, 760, 120, 1700, 74, jitter=3)           # parede de cápsulas no oeste
    lay.line("capsule", 1230, 1900, 1230, 2450, 74, jitter=3, gaps=[(2150, 90)])
    lay.cluster("capsule", 1350, 1330, 4, 60)
    lay.scatter("tree", 9, (80, 700, 1450, 2500), avoid=lambda x, y: x > 1200 and 1350 < y < 1650)
    lay.scatter("crystal", 4, (80, 700, 1450, 2500))
    # --- Jardim Suspenso: colunata dos Arquitetos
    for i in range(7):
        x = 1620 + i * 150
        if not (2560 < x < 2740):
            lay.add("pillar", x, 1360, gap=4)
            lay.add("pillar", x, 1640, gap=4)
    for (mx, my) in ((650, 1000), (2300, 2150), (3100, 1250)):   # círculo de pilares em volta de cada mecanismo
        for k in range(5):
            a = k * math.tau / 5 + 0.4
            lay.add("pillar", mx + math.cos(a) * 170, my + math.sin(a) * 170, gap=4)
    lay.cluster("crystal", 3050, 1050, 5, 90); lay.cluster("crystal", 3350, 1480, 5, 90); lay.cluster("crystal", 1900, 2330, 4, 80)
    lay.cluster("crystal", 2600, 2420, 4, 90); lay.cluster("crystal", 3350, 2350, 4, 90)
    lay.scatter("pillar", 8, (1550, 700, 3500, 2500))
    lay.scatter("crystal", 10, (1550, 700, 3500, 2500))
    lay.scatter("capsule", 6, (1550, 700, 3500, 2500))
    lay.scatter("planter", 6, (1550, 700, 3500, 2500))
    # --- Câmara do Jardineiro
    for x in (1100, 1450, 2150, 2500, 2850):
        lay.add("pillar", x, 520, r=24, gap=4)
    for (x, y) in ((420, 300), (900, 150), (2700, 150), (3200, 360), (3350, 160)):
        lay.add("crystal", x, y, gap=4)
    lay.scatter("pillar", 5, (150, 120, 3450, 520))
    lay.scatter("crystal", 6, (150, 120, 3450, 520))
    lay.scatter("planter", 3, (150, 120, 3450, 520))
    caches = place_caches(lay, [(620, 1500, 80), (1000, 2150, 90), (300, 900, 70), (800, 700, 60), (1450, 1000, 80), (1800, 1750, 80), (2150, 1500, 80),
                                (2400, 800, 70), (3350, 900, 60), (3000, 1550, 70), (2000, 2420, 70), (3150, 2150, 80), (700, 300, 70), (3300, 330, 70)],
                          [7, 8, 6, 11, 10, 8, 9, 9, 7, 6, 7, 9, 8, 7], lay.rnd)
    spec = dict(decor="decor_estufa.png", default_source=4, decor_count=60,
                biomes={"Estufas Esquecidas": 4, "Jardim Suspenso": 3, "Câmara do Jardineiro": 2},
                decor_kinds={"Estufas Esquecidas": "[0, 1, 2, 3]", "Jardim Suspenso": "[0, 1, 3, 3]", "Câmara do Jardineiro": "[2, 2, 3]"},
                regions=[dict(node="Estufas", name="Estufas Esquecidas", rect=(0, 650, 1500, 2600), color="0.1, 0.25, 0.22, 1.0"),
                         dict(node="Jardim", name="Jardim Suspenso", rect=(1500, 650, 3600, 2600), color="0.13, 0.15, 0.3, 1.0"),
                         dict(node="Camara", name="Câmara do Jardineiro", rect=(0, 0, 3600, 650), color="0.22, 0.17, 0.3, 1.0", locked=True)],
                hostile=[("Zona1", 3000, 1350, 700, 600), ("Zona2", 2150, 2150, 800, 500)],
                stations=stations,
                walls=[dict(name="WallWest", x=850, y=640, w=1700, h=36), dict(name="WallEast", x=2750, y=640, w=1700, h=36)],
                gate=(1800, 640, False), obs=lay.obs, caches=caches, inter=inter, arena=arena)
    emit(spec, path)
    print("garden:", len(lay.obs), "obstáculos,", len(caches), "caches")


# ====================================================================== CORAÇÃO DE NYMARA
def build_heart():
    lay = Layout(7077)
    path = os.path.join(SC, "heart_map.tscn")
    inter_pos = {"Ship": (360, 1220), "TerminalBase": (540, 1330), "RuinaCoracaoA": (1550, 650), "RuinaCoracaoB": (1550, 1950)}
    inter = inter_blocks(path, inter_pos)
    stations = [("Base", 420, 1300, "base_coracao", "Câmara de Acesso", 170)]
    arena = (2750, 1300, {"ring_radius": "380.0", "trigger_radius": "620.0"})
    lay.keep_free(500, 1380, 120)
    lay.keep_free(420, 1300, 215)
    for pos in inter_pos.values():
        lay.keep_free(pos[0], pos[1], 90)
    lay.keep_free(arena[0], arena[1], 450)
    # corredor do início até a arena (3 passagens principais, ver cortinas)
    # --- Câmara de Acesso: ruínas dos Arquitetos ao redor (colunas quebradas e cristais)
    for (x, y) in ((220, 760), (520, 700), (820, 790), (230, 1840), (540, 1900), (840, 1810)):
        lay.add("pillar", x, y, gap=4)
    lay.cluster("crystal", 160, 1000, 3, 70); lay.cluster("crystal", 170, 1600, 3, 70)
    lay.cluster("capsule", 250, 560, 5, 90); lay.cluster("capsule", 760, 2120, 5, 90); lay.cluster("planter", 880, 520, 3, 70); lay.cluster("planter", 140, 2200, 3, 70)
    lay.cluster("root", 900, 1010, 2, 60); lay.cluster("root", 900, 1600, 2, 60)
    lay.scatter("crystal", 4, (80, 300, 950, 2400)); lay.scatter("root", 5, (80, 150, 950, 2450))
    # --- Raízes Profundas: 3 cortinas de raízes com passagens em zigue-zague
    gaps1 = [(780, 130), (1830, 130)]
    gaps2 = [(1300, 150)]
    gaps3 = [(560, 130), (1100, 90), (2050, 130)]
    wavy_curtain(lay, 1130, gaps1); wavy_curtain(lay, 1640, gaps2, amp=40); wavy_curtain(lay, 2130, gaps3)
    for (cx, gs) in ((1150, gaps1), (1660, gaps2), (2150, gaps3)):   # bulbos luminosos marcam cada passagem
        for (gy, hw) in gs:
            for sgn in (-1, 1):
                lay.add("bulb", cx + 20, gy + sgn * (hw + 40), gap=2)
                lay.add("bulb", cx + 70, gy + sgn * (hw + 70), gap=2)
    for (x, y) in ((1400, 520), (1400, 1100), (1400, 1560), (1400, 2150), (1900, 900), (1900, 1700), (1900, 2200), (1900, 450)):
        lay.add("pillar", x, y, gap=4)
    lay.scatter("bulb", 14, (1200, 150, 2100, 2450))
    lay.scatter("crystal", 8, (1200, 150, 2100, 2450))
    lay.scatter("root", 10, (1200, 150, 2100, 2450))
    # --- Câmara do Núcleo: anel de cristais e bulbos fora da arena
    for k in range(34):
        a = k * math.tau / 34
        rr = 470 + (k % 3) * 34
        lay.add("crystal" if k % 3 != 1 else "bulb", arena[0] + math.cos(a) * rr, arena[1] + math.sin(a) * rr, gap=2)
    for k in range(14):
        a = k * math.tau / 14 + 0.2
        lay.add("root", arena[0] + math.cos(a) * 640, arena[1] + math.sin(a) * 640, gap=2)
    lay.scatter("root", 8, (2250, 150, 3500, 2450)); lay.scatter("bulb", 10, (2250, 150, 3500, 2450)); lay.scatter("crystal", 6, (2250, 150, 3500, 2450))
    caches = place_caches(lay, [(250, 400, 80), (250, 2200, 80), (1400, 330, 70), (1400, 2330, 70), (1900, 1300, 90), (1650, 1000, 60), (2400, 450, 80), (2400, 2150, 80), (3250, 1300, 120)],
                          [7, 7, 8, 8, 10, 9, 9, 9, 12], lay.rnd)
    spec = dict(decor="decor_nucleo.png", default_source=5, decor_count=60,
                biomes={"Câmara de Acesso": 4, "Raízes Profundas": 5, "Núcleo das Raízes": 5},
                decor_kinds={"Câmara de Acesso": "[0, 2, 3]", "Raízes Profundas": "[0, 1, 1, 3]", "Núcleo das Raízes": "[1, 1, 3, 3]"},
                regions=[dict(node="Acesso", name="Câmara de Acesso", rect=(0, 0, 1000, 2600), color="0.14, 0.2, 0.22, 1.0"),
                         dict(node="Raizes", name="Raízes Profundas", rect=(1000, 0, 2300, 2600), color="0.24, 0.1, 0.2, 1.0"),
                         dict(node="Nucleo", name="Núcleo das Raízes", rect=(2300, 0, 3600, 2600), color="0.2, 0.1, 0.3, 1.0")],
                hostile=[], stations=stations, walls=[], gate=(1800, -300, True), obs=lay.obs, caches=caches, inter=inter, arena=arena)
    emit(spec, path)
    print("heart:", len(lay.obs), "obstáculos,", len(caches), "caches")


if __name__ == "__main__":
    build_garden()
    build_heart()
