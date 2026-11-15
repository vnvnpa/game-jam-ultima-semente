#!/usr/bin/env python3
"""Valida o layout de world_map / garden_map / heart_map sem abrir a Godot.

Checa: obstáculos sobrepostos, obstáculos em cima de estações/interativos/caches/arena/muralhas/portão,
itens fora do mundo, regiões cobrindo o mapa e ALCANÇABILIDADE (flood-fill em grade de 20 px com a
colisão real: raio*0.8 + jogador) antes e depois de abrir o portão.
Uso: python3 tools/check_map_layout.py   (código de saída 1 se houver problema)
"""
import os, re, sys, math
from collections import deque

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
W, H, CELL, PLAYER_R = 3600, 2600, 20, 10.0
errs, warns = [], []


def parse(path):
    t = open(path, encoding="utf-8").read()
    ext = {m.group(2): m.group(1) for m in re.finditer(r'\[ext_resource [^\]]*path="([^"]+)" id="([^"]+)"\]', t)}
    subs = {}
    for m in re.finditer(r'\[sub_resource type="RectangleShape2D" id="([^"]+)"\]\nsize = Vector2\(([^,]+), ([^)]+)\)', t):
        subs[m.group(1)] = (float(m.group(2)), float(m.group(3)))
    nodes = []
    for m in re.finditer(r'\[node name="([^"]+)"([^\]]*)\]\n((?:(?!\[).*\n)*)', t):
        name, head, body = m.groups()
        par = re.search(r'parent="([^"]*)"', head)
        inst = re.search(r'instance=ExtResource\("([^"]+)"\)', head)
        props = {}
        for ln in body.strip().split("\n"):
            if " = " in ln:
                k, v = ln.split(" = ", 1)
                props[k] = v
        nodes.append(dict(name=name, parent=par.group(1) if par else None, inst=ext.get(inst.group(1)) if inst else None, props=props))
    return ext, subs, nodes


def vec(s):
    m = re.search(r"Vector2\(([^,]+), ([^)]+)\)", s)
    return (float(m.group(1)), float(m.group(2))) if m else (0.0, 0.0)


def load(name):
    ext, subs, nodes = parse(os.path.join(ROOT, "scenes", "world", name + ".tscn"))
    d = dict(obs=[], walls=[], caches=[], inter=[], stations=[], hostile=[], regions=[], gate=None, gate_open=False, arena=None, arena_trigger=480.0, arena_ring=260.0)
    for n in nodes:
        p, pr = n["parent"], n["props"]
        pos = vec(pr.get("position", "Vector2(0, 0)"))
        if p == "Obstacles":
            d["obs"].append((n["name"], pos[0], pos[1], float(pr.get("radius", "20"))))
        elif p == "Caches":
            d["caches"].append((n["name"], pos[0], pos[1]))
        elif p == "Interactables":
            d["inter"].append((n["name"], pos[0], pos[1], pr.get("kind", '"poi"').strip('"')))
        elif p == "Stations":
            d["stations"].append((n["name"], pos[0], pos[1], float(pr.get("radius", "120"))))
        elif p == "HostileZones":
            sx, sy = vec(pr.get("size", "Vector2(600, 400)"))
            d["hostile"].append((n["name"], pos[0] - sx / 2, pos[1] - sy / 2, pos[0] + sx / 2, pos[1] + sy / 2))
        elif p == "Regions":
            sx, sy = vec(pr["size"])
            d["regions"].append((pr["region_name"].strip('"'), pos[0] - sx / 2, pos[1] - sy / 2, pos[0] + sx / 2, pos[1] + sy / 2, pr.get("locked_until_gate") == "true"))
        elif p == "Walls" and n["inst"] is None:
            d["walls"].append([n["name"], pos[0], pos[1], None])
        elif p and p.startswith("Walls/") and n["name"] == "Shape":
            sid = re.search(r'SubResource\("([^"]+)"\)', pr["shape"]).group(1)
            for w in d["walls"]:
                if w[0] == p.split("/")[1]:
                    w[3] = subs[sid]
        elif n["name"] == "Gate" and p == ".":
            d["gate"] = pos if "position" in pr else (2600.0, 640.0)   # padrão herdado de root_gate.tscn
            d["gate_open"] = pr.get("start_open") == "true"
        elif n["name"] == "BossArena":
            d["arena"] = pos
            d["arena_trigger"] = float(pr.get("trigger_radius", "480"))
            d["arena_ring"] = float(pr.get("ring_radius", "260"))
    return d


def rect_of(w):
    return (w[1] - w[3][0] / 2, w[2] - w[3][1] / 2, w[1] + w[3][0] / 2, w[2] + w[3][1] / 2)


def blocked_grid(d, gate_closed):
    gw, gh = W // CELL, H // CELL
    g = [[False] * gw for _ in range(gh)]
    rects = [rect_of(w) for w in d["walls"]]
    if gate_closed and d["gate"] and not d["gate_open"]:
        rects.append((d["gate"][0] - 100, d["gate"][1] - 18, d["gate"][0] + 100, d["gate"][1] + 18))
    for gy in range(gh):
        for gx in range(gw):
            x, y = gx * CELL + CELL / 2, gy * CELL + CELL / 2
            if x < 14 or y < 14 or x > W - 14 or y > H - 14:
                g[gy][gx] = True
                continue
            for (x0, y0, x1, y1) in rects:
                if x0 - PLAYER_R < x < x1 + PLAYER_R and y0 - PLAYER_R < y < y1 + PLAYER_R:
                    g[gy][gx] = True
                    break
    for (_, ox, oy, r) in d["obs"]:
        rr = r * 0.8 + PLAYER_R
        for gy in range(max(0, int((oy - rr) // CELL)), min(gh, int((oy + rr) // CELL) + 1)):
            for gx in range(max(0, int((ox - rr) // CELL)), min(gw, int((ox + rr) // CELL) + 1)):
                if math.hypot(gx * CELL + CELL / 2 - ox, gy * CELL + CELL / 2 - oy) < rr:
                    g[gy][gx] = True
    return g


def flood(g, start):
    gh, gw = len(g), len(g[0])
    sx, sy = int(start[0] // CELL), int(start[1] // CELL)
    seen = [[False] * gw for _ in range(gh)]
    if g[sy][sx]:
        return seen
    q = deque([(sx, sy)])
    seen[sy][sx] = True
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < gw and 0 <= ny < gh and not seen[ny][nx] and not g[ny][nx]:
                seen[ny][nx] = True
                q.append((nx, ny))
    return seen


def reach(seen, x, y, slack=2):
    gx, gy = int(x // CELL), int(y // CELL)
    for dy in range(-slack, slack + 1):
        for dx in range(-slack, slack + 1):
            if 0 <= gy + dy < len(seen) and 0 <= gx + dx < len(seen[0]) and seen[gy + dy][gx + dx]:
                return True
    return False


def in_rect(x, y, r):
    return r[0] <= x <= r[2] and r[1] <= y <= r[3]


def check(name, start, locked_names=()):
    d = load(name)
    E = lambda m: errs.append("%s: %s" % (name, m))
    Wn = lambda m: warns.append("%s: %s" % (name, m))
    obs = d["obs"]
    # 1) dentro do mundo
    for (n, x, y, r) in obs:
        if x - r < 20 or y - r < 20 or x + r > W - 20 or y + r > H - 20:
            Wn("%s encosta na borda do mundo (%.0f, %.0f)" % (n, x, y))
    # 2) sobreposição entre obstáculos (colisão real = r*0.8)
    for i in range(len(obs)):
        for j in range(i + 1, len(obs)):
            a, b = obs[i], obs[j]
            if math.hypot(a[1] - b[1], a[2] - b[2]) < (a[3] + b[3]) * 0.8 - 1:
                E("obstáculos sobrepostos: %s e %s" % (a[0], b[0]))
    # 3) obstáculos contra estações, interativos, caches, arena e muralhas
    for (n, x, y, r) in obs:
        for (sn, sx, sy, sr) in d["stations"]:
            if math.hypot(x - sx, y - sy) < sr + r * 0.8:
                E("%s dentro da estação %s" % (n, sn))
        for (iname, ix, iy, _k) in d["inter"]:
            if math.hypot(x - ix, y - iy) < r * 0.8 + 40:
                E("%s bloqueia o interativo %s" % (n, iname))
        for (cn, cx, cy) in d["caches"]:
            if math.hypot(x - cx, y - cy) < r * 0.8 + 14:
                E("%s cobre %s" % (n, cn))
        if d["arena"] and math.hypot(x - d["arena"][0], y - d["arena"][1]) < d["arena_ring"] + 20 and name != "world_map":
            E("%s dentro da arena do chefe" % n)
        for w in d["walls"]:
            rr = rect_of(w)
            if rr[0] - r < x < rr[2] + r and rr[1] - r < y < rr[3] + r:
                E("%s dentro da muralha %s" % (n, w[0]))
        if d["gate"] and not d["gate_open"] and math.hypot(x - d["gate"][0], y - d["gate"][1]) < r + 110:
            E("%s perto demais do portão" % n)
    # 4) regiões cobrem todo o mundo? (amostra)
    holes = 0
    for gx in range(0, W, 100):
        for gy in range(0, H, 100):
            if not any(r[1] <= gx + 50 < r[3] and r[2] <= gy + 50 < r[4] for r in d["regions"]):
                holes += 1
    if holes:
        Wn("%d amostras de 100 px sem região (cairão em \"Terras desconhecidas\")" % holes)
    # 5) início + alcançabilidade
    targets = [("estação " + s[0], s[1], s[2]) for s in d["stations"]] + [("interativo " + i[0], i[1], i[2]) for i in d["inter"]] + \
              [("cache " + c[0], c[1], c[2]) for c in d["caches"]]
    if d["arena"]:
        targets.append(("arena", d["arena"][0], d["arena"][1] + (d["arena_ring"] * .8 if name != "world_map" else 0)))
    for (label, g_closed) in (("com portão fechado", True), ("com portão aberto", False)):
        g = blocked_grid(d, g_closed)
        seen = flood(g, start)
        if not reach(seen, *start):
            E("ponto inicial %s preso (%s)" % (start, label))
            continue
        for (tn, x, y) in targets:
            in_locked = any(in_rect(x, y, (r[1], r[2], r[3], r[4])) and r[5] for r in d["regions"])
            ok = reach(seen, x, y)
            if g_closed and in_locked:
                if ok and d["gate"] and not d["gate_open"]:
                    E("%s alcançável sem abrir o portão" % tn)
                continue
            if not ok:
                E("%s inalcançável (%s)" % (tn, label))
        free = sum(1 for row in seen for v in row if v)
        total = sum(1 for row in g for v in row if not v)
        if total - free > total * 0.03 and not g_closed:
            Wn("%.1f%% do chão livre está isolado (ilhas)" % (100.0 * (total - free) / total))
    print("%-12s obstáculos %3d | caches %2d | interativos %d | estações %d" % (name, len(obs), len(d["caches"]), len(d["inter"]), len(d["stations"])))


def main():
    check("world_map", (560, 1570))
    check("garden_map", (400, 1970))
    check("heart_map", (500, 1380))
    for w in warns:
        print("AVISO:", w)
    for e in errs:
        print("ERRO:", e)
    print("layout:", "OK" if not errs else "%d erro(s)" % len(errs))
    sys.exit(1 if errs else 0)



if __name__ == "__main__":
    main()
