#!/usr/bin/env python3
"""Roda todas as checagens estáticas (sem Godot): validate_scenes, lint_gd e lint_syntax.
Uso (raiz do projeto):  python3 tools/run_checks.py"""
import os, subprocess, sys
T = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(T); ok = True
for s in ("validate_scenes.py", "lint_gd.py", "lint_syntax.py"):
    r = subprocess.run([sys.executable, os.path.join(T, s)], cwd=ROOT, capture_output=True, text=True)
    tail = (r.stdout.strip().splitlines() or [""])[-1]
    print(f"{s}: {tail}")
    ok = ok and (r.returncode == 0 or s == "lint_syntax.py")
print("TUDO OK" if ok else "HÁ PROBLEMAS (veja a saída de cada script)")
sys.exit(0 if ok else 1)
