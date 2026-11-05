#!/usr/bin/env python3
"""Escreve data/audio/sfx_bank.tres (um SfxEntry por .wav de assets/audio/sfx) e
data/audio/music_set.tres. Rode depois de tools/gen_audio.py."""
import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sfx = sorted(f[:-4] for f in os.listdir(os.path.join(ROOT, "assets/audio/sfx")) if f.endswith(".wav"))
L = ['[gd_resource type="Resource" script_class="SfxBank" load_steps=%d format=3]' % (2 * len(sfx) + 2), "",
	 '[ext_resource type="Script" path="res://scripts/data/sfx_bank.gd" id="1_script"]',
	 '[ext_resource type="Script" path="res://scripts/data/sfx_entry.gd" id="2_entry"]']
for i, n in enumerate(sfx):
	L.append('[ext_resource type="AudioStream" path="res://assets/audio/sfx/%s.wav" id="s%d"]' % (n, i))
L.append("")
for i, n in enumerate(sfx):
	L += ['[sub_resource type="Resource" id="Entry_%d"]' % i, 'script = ExtResource("2_entry")', 'id = "%s"' % n, 'stream = ExtResource("s%d")' % i,
		  "volume_db = 0.0", "pitch = 1.0", "cooldown_ms = 35", ""]
L += ["[resource]", 'script = ExtResource("1_script")', "entries = [%s]" % ", ".join('SubResource("Entry_%d")' % i for i in range(len(sfx))), ""]
open(os.path.join(ROOT, "data/audio/sfx_bank.tres"), "w", encoding="utf-8").write("\n".join(L))
M = ['[gd_resource type="Resource" script_class="MusicSet" load_steps=4 format=3]', "",
	 '[ext_resource type="Script" path="res://scripts/data/music_set.gd" id="1_script"]',
	 '[ext_resource type="AudioStream" path="res://assets/audio/music/explore_loop.wav" id="2_exp"]',
	 '[ext_resource type="AudioStream" path="res://assets/audio/music/combat_loop.wav" id="3_com"]', "",
	 "[resource]", 'script = ExtResource("1_script")', 'explorar = ExtResource("2_exp")', 'combate = ExtResource("3_com")',
	 "explorar_db = -6.0", "combate_db = -9.0", "explorar_queda_db = -10.0", "duck_pausa_db = -9.0", "entrada_s = 1.5", "velocidade_mistura = 0.4", ""]
open(os.path.join(ROOT, "data/audio/music_set.tres"), "w", encoding="utf-8").write("\n".join(M))
print("OK: sfx_bank.tres (%d sons) e music_set.tres" % len(sfx))
