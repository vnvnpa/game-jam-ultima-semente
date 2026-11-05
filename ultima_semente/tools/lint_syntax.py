#!/usr/bin/env python3
"""Checagem de sintaxe APROXIMADA dos .gd: converte cada script em Python (mesmas linhas) e usa o
parser do Python para achar erro estrutural (blocos, parênteses, if/else). Não substitui a Godot.
Falso positivo conhecido: lambda com atribuição (pause_menu.gd)."""
import re,os,sys,ast
KW={'from':'_from','with':'_with','global':'_global','del':'_del','try':'_try','except':'_exc','finally':'_fin','nonlocal':'_nl','raise':'_raise','import':'_imp','async':'_async','yield':'_yield','is_':'is_'}
def strip_comment(l):
    out=[];i=0;ins=False
    while i<len(l):
        c=l[i]
        if ins:
            out.append(c)
            if c=='\\' and i+1<len(l): out.append(l[i+1]); i+=1
            elif c=='"': ins=False
        else:
            if c=='"': ins=True; out.append(c)
            elif c=='#': break
            else: out.append(c)
        i+=1
    return ''.join(out).rstrip()
def conv(src):
    out=[]; match_stack=[]  # indent levels of match blocks
    lines=src.split('\n')
    in_enum=False
    for raw in lines:
        l=strip_comment(raw)
        s=l.strip()
        ind=len(l)-len(l.lstrip('\t'))
        # fechar match
        while match_stack and s and ind<=match_stack[-1][0]:
            match_stack.pop()
        if in_enum:
            if '}' in l: in_enum=False
            out.append(''); continue
        if s.startswith('#') or not s: out.append(''); continue
        if re.match(r'^(class_name|extends|signal|@tool|@icon)\b',s): out.append(''); continue
        if s.startswith('enum '):
            if '}' not in s: in_enum=True
            out.append(''); continue
        # remove strings for safe regex work but keep them: operate on code outside strings
        parts=re.split(r'("(?:\\.|[^"\\])*")',l)
        code=[]
        for i,pt in enumerate(parts):
            if i%2==1: code.append(pt); continue
            t=pt
            t=re.sub(r'&(?=$|\s)','',t)
            code.append(t)
        # reconstituir tratando &"..." e ^"..."
        l=''.join(code)
        l=re.sub(r'(?<![\w)\]])&"','"',l); l=re.sub(r'\^"','"',l)
        s=l.strip()
        if not s: out.append(''); continue
        ind=len(l)-len(l.lstrip('\t'))
        # anotações
        s=re.sub(r'^(@[\w]+(\([^)]*\))?\s+)+','',s)
        if s.startswith('@'): out.append(''); continue
        s=re.sub(r'^static\s+func\s','func ',s)
        s=re.sub(r'^static\s+var\s','var ',s)
        # func -> def
        m=re.match(r'^func\s+(\w+)\s*\((.*)\)\s*(->\s*[\w\[\]\.]+)?\s*:\s*(.*)$',s)
        if m: s='def %s(%s)%s: %s'%(m.group(1),m.group(2),(' '+m.group(3)) if m.group(3) else '',m.group(4) or '')
        # var/const
        if re.match(r'^(var|const)\s',s):
            s=re.sub(r'^(var|const)\s+','',s)
            if s.rstrip().endswith(':') and '=' in s or re.match(r'^\w+\s*:\s*\w+\s*:$',s.rstrip()):
                s=s.rstrip()[:-1]+'\nif True:' if False else s  # setter
            if s.rstrip().endswith(':') : s='if True:' if False else s
        # lambdas inline
        def lam(mm):
            params=re.sub(r':\s*[\w\.\[\]]+','',mm.group(1))
            return 'lambda %s:'%params
        s=re.sub(r'\bfunc\s*\(([^)]*)\)\s*(?:->\s*[\w\.]+)?\s*:',lam,s)
        s=re.sub(r'\bawait\s+','',s)
        s=re.sub(r'\$[\w/%"]+','None',s)
        s=re.sub(r'(=\s*|\(\s*|,\s*)%(\w+)',r'\1None',s)
        s=re.sub(r'\s+as\s+[A-Z]\w*(\[\w+\])?','',s)
        s=re.sub(r'\b(true)\b','True',s); s=re.sub(r'\b(false)\b','False',s); s=re.sub(r'\bnull\b','None',s)
        s=re.sub(r'(?<![\w"])!(?!=)',' not ',s); s=s.replace('&&',' and ').replace('||',' or ')
        for k,v in KW.items():
            s=re.sub(r'(?<![\w"\.])'+k+r'(?![\w"])',v,s) if k not in ('is_',) else s
        s=re.sub(r'^(set|get)\((\w*)\):',r'def \1(\2):',s)
        # match
        if s.startswith('match '):
            match_stack.append((ind,)); out.append('\t'*ind+s); continue
        if match_stack and ind==match_stack[-1][0]+1 and s.endswith(':') and not s.startswith(('if ','elif ','else','for ','while ','def ')):
            pat=s[:-1]
            s='case %s:'%('_' if pat.strip()=='_' else pat)
        # var setter: "x: T = v:" -> bloco
        if re.match(r'^\w+(\s*:\s*[\w\[\]\.]+)?(\s*=.*)?\s*:$',s) and not s.startswith(('else','if','elif','while','for','case','def','match')) and not s.startswith('case'):
            # propriedade com set/get
            s=s[:-1].rstrip()
            s=(s if '=' in s else s+' = None')
            out.append('\t'*ind+s)
            out.append('\t'*ind+'if True:')   # mantém a numeração? adiciona linha extra
            continue
        out.append('\t'*ind+s)
    return out
bad=0
for d,_,fs in os.walk('scripts'):
    for f in sorted(fs):
        if not f.endswith('.gd'): continue
        p=os.path.join(d,f)
        src=open(p,encoding='utf-8').read()
        lines=conv(src)
        # mapa de linha: linhas extras 'if True:' deslocam; guardar mapa
        code='\n'.join(lines)+'\n'
        try:
            ast.parse(code)
        except SyntaxError as e:
            bad+=1
            ln=e.lineno or 0
            print(p,'py-linha',ln,e.msg,'->',(lines[ln-1].strip() if 0<ln<=len(lines) else ''))
print('com erro de sintaxe (aprox.):',bad)
