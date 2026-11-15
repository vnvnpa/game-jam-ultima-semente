#!/usr/bin/env python3
"""Gera docs/previews/mapa_<nome>.png: aproximação fiel do que o GroundPainter + cenas desenham
(chão por região, zonas contaminadas, trilhas, props escalados pelo raio, muralhas, estações, arena).
Uso: python3 tools/render_map_preview.py [escala=0.5]"""
import os, sys, math, random, re
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_map_layout as cm  # reutiliza o parser (roda as checagens ao importar; saída ignorada)

ROOT = cm.ROOT
WD = os.path.join(ROOT, "assets", "art", "world")
SCALE = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
SHEET = {"Tree": "trees.png", "Crystal": "crystals.png", "Pillar": "pillars.png", "Planter": "planters.png", "Capsule": "capsules.png", "Root": "roots.png", "Bulb": "bulbs.png"}
FOOT = {"Tree": 28, "Planter": 28, "Root": 28, "Crystal": 26, "Capsule": 26, "Pillar": 26, "Bulb": 26}
BIOME = {"floresta": 0, "bacia": 1, "santuario": 2, "jardim": 3, "estufa": 4, "nucleo": 5}
NAMES = list(BIOME)


def scene_cfg(name):
    t = open(os.path.join(ROOT, "scenes", "world", name + ".tscn"), encoding="utf-8").read()
    bs = dict(re.findall(r'"([^"]+)": (\d+)', re.search(r"biome_sources = \{(.*?)\}", t, re.S).group(1))) if "biome_sources" in t else {}
    default = int(re.search(r"default_source = (\d+)", t).group(1)) if "default_source = " in t else 0
    decor = re.search(r'assets/art/world/(decor\w*\.png)', t).group(1)
    dk = dict(re.findall(r'"([^"]+)": \[([^\]]*)\]', re.search(r"decor_kinds = \{(.*?)\}", t, re.S).group(1))) if "decor_kinds" in t else {}
    return {k: int(v) for k, v in bs.items()}, default, decor, {k: [int(x) for x in v.split(",") if x.strip()] for k, v in dk.items()}


def region_at(d, x, y):
    found = None
    for r in d["regions"]:
        if r[1] <= x < r[3] and r[2] <= y < r[4]:
            found = r
    return found


def render(name):
    d = cm.load(name)
    biomes, default, decor_file, dkinds = scene_cfg(name)
    if name == "world_map":
        biomes = {"Floresta do Despertar": 0, "Bacia dos Ecos": 1, "Santuário das Raízes": 2}
        dkinds = {"Floresta do Despertar": [0, 0, 1, 1, 2], "Bacia dos Ecos": [2, 3, 3], "Santuário das Raízes": [2, 2, 3]}
        decor_file = "decor.png"
    tsets = {i: Image.open(os.path.join(WD, "tileset_%s.png" % n)).convert("RGBA") for i, n in enumerate(NAMES)}
    img = Image.new("RGBA", (cm.W, cm.H), (8, 12, 12, 255))
    rnd = random.Random(1337)
    stations = d["stations"]
    # chão
    for ty in range(cm.H // 32 + 1):
        for tx in range(cm.W // 32 + 1):
            x, y = tx * 32 + 16, ty * 32 + 16
            rg = region_at(d, x, y)
            src = biomes.get(rg[0], default) if rg else default
            hostile = any(h[1] <= x <= h[3] and h[2] <= y <= h[4] for h in d["hostile"]) and not any(math.hypot(x - s[1], y - s[2]) <= s[3] for s in stations)
            row = 3 if hostile else 0
            col = [0, 0, 0, 0, 0, 1, 1, 1, 2, 3][rnd.randint(0, 9)]
            img.paste(tsets[src].crop((col * 32, row * 32, col * 32 + 32, row * 32 + 32)), (tx * 32, ty * 32))
    # trilhas (mesma lógica do GroundPainter: vizinho mais próximo)
    pts = [(s[1], s[2]) for s in stations] + [(i[1], i[2]) for i in d["inter"]] + ([d["arena"]] if d["arena"] else [])
    left = pts[1:]
    cur = pts[0]
    trail = Image.new("RGBA", (cm.W, cm.H), (0, 0, 0, 0))
    while left:
        left.sort(key=lambda p: math.hypot(p[0] - cur[0], p[1] - cur[1]))
        nxt = left.pop(0)
        steps = max(2, int(math.hypot(nxt[0] - cur[0], nxt[1] - cur[1]) / 16))
        px, py = (nxt[1] - cur[1]), -(nxt[0] - cur[0]); ln = math.hypot(px, py) or 1
        ph = rnd.random() * math.tau
        for i in range(steps + 1):
            t = i / steps; f = math.sin(t * math.pi)
            x = cur[0] + (nxt[0] - cur[0]) * t + px / ln * math.sin(t * 9 + ph) * 26 * f
            y = cur[1] + (nxt[1] - cur[1]) * t + py / ln * math.sin(t * 9 + ph) * 26 * f
            cx, cy = int(x // 32), int(y // 32)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if abs(dx) + abs(dy) > 1 + rnd.randint(0, 1):
                        continue
                    wx, wy = (cx + dx) * 32 + 16, (cy + dy) * 32 + 16
                    if any(h[1] <= wx <= h[3] and h[2] <= wy <= h[4] for h in d["hostile"]) or any(math.hypot(wx - s[1], wy - s[2]) <= s[3] for s in stations):
                        continue
                    rg = region_at(d, wx, wy)
                    src = biomes.get(rg[0], default) if rg else default
                    tc = rnd.randint(0, 3) * 32
                    trail.paste(tsets[src].crop((tc, 32, tc + 32, 64)), ((cx + dx) * 32, (cy + dy) * 32))
        cur = nxt
    img.alpha_composite(trail)
    # decoração
    dec = Image.open(os.path.join(WD, decor_file)).convert("RGBA")
    for r in d["regions"]:
        kinds = dkinds.get(r[0], [])
        if not kinds:
            continue
        for _ in range(60):
            x, y = rnd.uniform(r[1], r[3]), rnd.uniform(r[2], r[4])
            if any(math.hypot(x - o[1], y - o[2]) < o[3] + 16 for o in d["obs"]):
                continue
            idx = kinds[rnd.randint(0, len(kinds) - 1)] + 4 * rnd.randint(0, 3)
            sp = dec.crop((idx * 32, 0, idx * 32 + 32, 32))
            img.alpha_composite(sp, (int(x - 16), int(y - 16)))
    # muralhas
    wh = Image.open(os.path.join(WD, "wall_raizes.png")).convert("RGBA")
    for w in d["walls"]:
        x0, y0, x1, y1 = cm.rect_of(w)
        for xx in range(int(x0), int(x1), 32):
            img.alpha_composite(wh.crop((0, 0, min(32, int(x1) - xx), 36)), (xx, int(y0)))
    # estações (anel)
    dr = ImageDraw.Draw(img)
    for s in stations:
        dr.ellipse([s[1] - s[3], s[2] - s[3], s[1] + s[3], s[2] + s[3]], outline=(100, 240, 255, 255), width=3)
    # portão
    if d["gate"] and not d["gate_open"]:
        gx, gy = d["gate"]
        dr.rectangle([gx - 100, gy - 18, gx + 100, gy + 18], outline=(180, 77, 180, 255), width=4)
    # arena
    if d["arena"]:
        ax, ay = d["arena"]
        dr.ellipse([ax - d["arena_ring"], ay - d["arena_ring"], ax + d["arena_ring"], ay + d["arena_ring"]], outline=(200, 140, 245, 255), width=4)
    # props (ordenados por y)
    cache = {}
    for (n, x, y, r) in sorted(d["obs"], key=lambda o: o[2]):
        kind = re.sub(r"\d+$", "", n)
        sh = cache.get(kind) or Image.open(os.path.join(WD, SHEET[kind])).convert("RGBA")
        cache[kind] = sh
        fw = sh.width // 4
        v = abs(int(x * 7.0 + y * 13.0)) % 4
        sp = sh.crop((v * fw, 0, v * fw + fw, sh.height))
        k = r / 20.0
        sp = sp.resize((max(1, int(sp.width * k)), max(1, int(sp.height * k))), Image.NEAREST)
        img.alpha_composite(sp, (int(x - sp.width / 2), int(y - (FOOT[kind] - 10) * k - sp.height / 2)))
    # interativos e caches
    for (n, x, y, k) in d["inter"]:
        col = {"shop": (60, 220, 230), "ship": (240, 150, 60), "mechanism": (255, 210, 80)}.get(k, (190, 120, 245))
        dr.rectangle([x - 8, y - 14, x + 8, y + 10], fill=col + (255,), outline=(0, 0, 0, 255))
    for (n, x, y) in d["caches"]:
        dr.polygon([(x, y - 9), (x + 7, y), (x, y + 9), (x - 7, y)], fill=(217, 245, 90, 255))
    dr.ellipse([cm_start(name)[0] - 7, cm_start(name)[1] - 7, cm_start(name)[0] + 7, cm_start(name)[1] + 7], fill=(255, 140, 40, 255), outline=(0, 0, 0, 255))
    out = img.resize((int(cm.W * SCALE), int(cm.H * SCALE)), Image.LANCZOS)
    os.makedirs(os.path.join(ROOT, "docs", "previews"), exist_ok=True)
    out.save(os.path.join(ROOT, "docs", "previews", "mapa_%s.png" % name.replace("_map", "")))
    print("ok:", name)


def cm_start(name):
    return {"world_map": (560, 1570), "garden_map": (400, 1970), "heart_map": (500, 1380)}[name]


if __name__ == "__main__":
    for n in ("world_map", "garden_map", "heart_map"):
        render(n)
