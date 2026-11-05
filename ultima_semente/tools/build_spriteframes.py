#!/usr/bin/env python3
"""Lê assets/art/manifest.json e escreve um SpriteFrames (.tres) por sheet em
assets/art/frames/. Rode depois de tools/gen_art.py:  python3 tools/build_spriteframes.py"""
import json, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
man = json.load(open(os.path.join(ROOT, "assets/art/manifest.json"), encoding="utf-8"))
SKIP = {"trees.png", "crystals.png", "pillars.png", "decor.png", "mutation_spines.png"}
out_dir = os.path.join(ROOT, "assets/art/frames")
os.makedirs(out_dir, exist_ok=True)
n_files = 0
for key, info in man.items():
	group, name = key.split("/")
	if group == "ui" or name.startswith("tileset") or name in SKIP:
		continue
	fw, fh = info["frame"]
	subs, anims = [], []
	for a in info["anims"]:
		ids = []
		for i in range(a["frames"]):
			subs.append((i * fw, a["row"] * fh))
			ids.append(len(subs))
		anims.append((a, ids))
	L = ['[gd_resource type="SpriteFrames" load_steps=%d format=3]' % (len(subs) + 2), "",
		 '[ext_resource type="Texture2D" path="res://assets/art/%s/%s" id="1_tex"]' % (group, name), ""]
	for k, (x, y) in enumerate(subs, 1):
		L += ['[sub_resource type="AtlasTexture" id="AtlasTexture_%d"]' % k, 'atlas = ExtResource("1_tex")',
			  'region = Rect2(%d, %d, %d, %d)' % (x, y, fw, fh), ""]
	parts = []
	for a, ids in anims:
		fr = ", ".join('{\n"duration": 1.0,\n"texture": SubResource("AtlasTexture_%d")\n}' % i for i in ids)
		parts.append('{\n"frames": [%s],\n"loop": %s,\n"name": &"%s",\n"speed": %.1f\n}' % (fr, "true" if a["loop"] else "false", a["name"], max(1.0, float(a["fps"]))))
	L += ["[resource]", "animations = [" + ", ".join(parts) + "]", ""]
	open(os.path.join(out_dir, os.path.splitext(name)[0] + ".tres"), "w", encoding="utf-8").write("\n".join(L))
	n_files += 1
print("OK: %d SpriteFrames em assets/art/frames" % n_files)
