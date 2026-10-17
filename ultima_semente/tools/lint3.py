import re, os
root='/home/claude/ultima_semente/scripts'
sigs={}
texts={}
for d,_,fs in os.walk(root):
    for f in fs:
        if f.endswith('.gd'):
            p=os.path.join(d,f); t=open(p,encoding='utf-8').read(); texts[p]=t
            for m in re.finditer(r'^(?:static\s+)?func\s+(\w+)\((.*?)\)\s*(?:->\s*[\w\[\]\.]+)?\s*:\s*$',t,re.M):
                name,params=m.group(1),m.group(2)
                ps=[x for x in re.split(r',\s*(?![^()]*\))',params) if x.strip()]
                sigs.setdefault(name,set()).add((len([x for x in ps if '=' not in x]),len(ps)))
def split_args(s):
    depth=0;cur='';out=[];instr=False
    for ch in s:
        if ch=='"': instr=not instr
        if not instr:
            if ch in '([{': depth+=1
            elif ch in ')]}': depth-=1
            elif ch==',' and depth==0: out.append(cur);cur='';continue
        cur+=ch
    if cur.strip(): out.append(cur)
    return out
errs=[]
skip={'_ready','_process','_physics_process','_draw','new','connect','emit','append','get','has'}
for p,t in texts.items():
    rel=os.path.relpath(p,root)
    for i,l in enumerate(t.split('\n'),1):
        if l.strip().startswith(('func ','static func ','#')): continue
        for m in re.finditer(r'\b(\w+)\(',l):
            n=m.group(1)
            if n not in sigs or n in skip or len(sigs[n])!=1: continue
            # extrair args com parênteses balanceados
            start=m.end(); depth=1; j=start; instr=False
            while j<len(l) and depth>0:
                ch=l[j]
                if ch=='"': instr=not instr
                if not instr:
                    if ch=='(': depth+=1
                    elif ch==')': depth-=1
                j+=1
            if depth!=0: continue
            args=split_args(l[start:j-1])
            mn,mx=list(sigs[n])[0]
            if not (mn<=len(args)<=mx):
                errs.append(f'{rel}:{i}: {n}() recebe {len(args)} args, esperado {mn}-{mx}: {l.strip()[:90]}')
print('\n'.join(errs) if errs else 'chamadas ok'); print(len(errs))
