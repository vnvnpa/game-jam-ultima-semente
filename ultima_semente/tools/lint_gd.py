#!/usr/bin/env python3
"""Lint estático rápido dos .gd (não substitui a Godot): funções/variáveis/constantes
duplicadas, parênteses desbalanceados, indentação com espaços e blocos sem corpo.
Uso (raiz do projeto):  python3 tools/lint_gd.py   -> código 1 se achar problemas."""
import collections, os, re, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
def strip(l):
    l = re.sub(r'"(?:\\.|[^"\\])*"', '""', l)
    return '' if l.lstrip().startswith('#') else re.sub(r'\s#.*$', '', l.rstrip())
n_bad = 0
for d, _, fs in os.walk(os.path.join(ROOT, "scripts")):
    for f in sorted(fs):
        if not f.endswith(".gd"):
            continue
        p = os.path.join(d, f); rel = os.path.relpath(p, ROOT)
        t = open(p, encoding="utf-8").read(); lines = t.split("\n"); msgs = []
        for kind, rx in (("função", r'^(?:static )?func (\w+)'), ("variável", r'^(?:@onready |@export[^\n]* )?var (\w+)'), ("constante", r'^const (\w+)')):
            for k, v in collections.Counter(re.findall(rx, t, re.M)).items():
                if v > 1: msgs.append(f"{kind} duplicada: {k}")
        s = "\n".join(strip(l) for l in lines)
        for a, b, nm in (("(", ")", "parênteses"), ("[", "]", "colchetes"), ("{", "}", "chaves")):
            if s.count(a) != s.count(b): msgs.append(f"{nm} desbalanceados")
        for i, l in enumerate(lines, 1):
            if re.match(r'^ +\S', l): msgs.append(f"linha {i}: indentação com espaços"); break
        for n, l in enumerate(lines):
            sl = strip(l)
            if sl.strip().endswith(":") and not sl.lstrip().startswith("@"):
                m = n + 1
                while m < len(lines) and not strip(lines[m]).strip(): m += 1
                ind = len(l) - len(l.lstrip("\t"))
                if m >= len(lines) or len(lines[m]) - len(lines[m].lstrip("\t")) <= ind:
                    msgs.append(f"linha {n+1}: bloco sem corpo"); break
        if msgs:
            n_bad += 1; print(rel, "->", "; ".join(msgs))
print("lint_gd:", "OK" if not n_bad else f"{n_bad} arquivo(s) com problema")
sys.exit(1 if n_bad else 0)
