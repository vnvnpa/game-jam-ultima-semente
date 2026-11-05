#!/usr/bin/env python3
"""Roda a própria Godot em modo de checagem em cada .gd e mostra os erros COM linha.
Uso (raiz do projeto):  python3 tools/check_scripts.py [caminho/do/godot]
Se o executável não for informado, tenta 'godot' / 'godot4' no PATH."""
import os, shutil, subprocess, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
exe = sys.argv[1] if len(sys.argv) > 1 else (shutil.which("godot") or shutil.which("godot4"))
if not exe:
    sys.exit("Informe o caminho da Godot: python3 tools/check_scripts.py C:/caminho/Godot.exe")
bad = 0
for d, _, fs in os.walk(os.path.join(ROOT, "scripts")):
    for f in sorted(fs):
        if f.endswith(".gd"):
            res = "res://" + os.path.relpath(os.path.join(d, f), ROOT).replace(os.sep, "/")
            r = subprocess.run([exe, "--headless", "--path", ROOT, "--check-only", "--script", res], capture_output=True, text=True, timeout=120)
            out = (r.stdout + r.stderr).strip()
            if r.returncode != 0 or "rror" in out:
                bad += 1
                print("=== " + res + "\n" + out + "\n")
print("scripts com erro:", bad)
