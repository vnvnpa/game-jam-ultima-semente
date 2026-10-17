import re, os
root='/home/claude/ultima_semente/scripts'
errs=[]
def check(p):
    rel=os.path.relpath(p,root)
    stack=None
    for i,l in enumerate(open(p,encoding='utf-8').read().split('\n'),1):
        if not l.strip() or l.strip().startswith('#'): continue
        ind=len(l)-len(l.lstrip('\t')); s=l.strip()
        if ind==0:
            if re.match(r'(static\s+)?func\s',s):
                stack=[(0,set(re.findall(r'[(,]\s*(\w+)\s*:',s)))]
            else: stack=None
            continue
        if stack is None: continue
        while len(stack)>1 and stack[-1][0]>=ind: stack.pop()
        m=re.match(r'(?:var|for)\s+(\w+)',s)
        if m:
            n=m.group(1)
            if s.startswith('var'):
                for (_,ss) in stack:
                    if n in ss: errs.append(f'{rel}:{i}: redeclaração de {n}')
                stack[-1][1].add(n)
        if s.endswith(':') and re.match(r'(if|elif|else|for|while|match|[^\s"]+:?)',s):
            sc=set()
            m2=re.match(r'for\s+(\w+)\s+in',s)
            if m2:
                n=m2.group(1)
                for (_,ss) in stack:
                    if n in ss: errs.append(f'{rel}:{i}: variável de for {n} já declarada')
                sc.add(n)
            stack.append((ind,sc))
for d,_,fs in os.walk(root):
    for f in fs:
        if f.endswith('.gd'): check(os.path.join(d,f))
print('\n'.join(errs) if errs else 'sem redeclarações')
