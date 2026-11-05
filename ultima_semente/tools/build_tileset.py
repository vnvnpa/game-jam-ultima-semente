#!/usr/bin/env python3
"""Escreve assets/art/world/ground_tileset.tres: um TileSet 32x32 com 4 fontes
(0 floresta, 1 bacia, 2 santuário, 3 jardim); cada fonte é uma grade 4x5
(linhas: chão, trilha, pedra, contaminado, muralha)."""
import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
biomes = ["floresta", "bacia", "santuario", "jardim"]
L = ['[gd_resource type="TileSet" load_steps=%d format=3]' % (len(biomes) * 2 + 1), ""]
for i, b in enumerate(biomes):
	L.append('[ext_resource type="Texture2D" path="res://assets/art/world/tileset_%s.png" id="%d_tex"]' % (b, i + 1))
L.append("")
for i, b in enumerate(biomes):
	L += ['[sub_resource type="TileSetAtlasSource" id="TileSetAtlasSource_%d"]' % (i + 1), 'texture = ExtResource("%d_tex")' % (i + 1),
		  "texture_region_size = Vector2i(32, 32)"]
	for y in range(5):
		for x in range(4):
			L.append("%d:%d/0 = 0" % (x, y))
	L.append("")
L += ["[resource]", "tile_size = Vector2i(32, 32)"]
for i in range(len(biomes)):
	L.append('sources/%d = SubResource("TileSetAtlasSource_%d")' % (i, i + 1))
open(os.path.join(ROOT, "assets/art/world/ground_tileset.tres"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("OK: ground_tileset.tres")
