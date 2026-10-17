import re, os, sys, collections
root='/home/claude/ultima_semente/scripts'
files=[]
for d,_,fs in os.walk(root):
    for f in fs:
        if f.endswith('.gd'): files.append(os.path.join(d,f))
classes={}  # class_name -> {members:set, consts:set}
autoloads={'GameData':'core/game_data.gd','SaveManager':'core/save_manager.gd','AudioManager':'core/audio_manager.gd','GameManager':'core/game_manager.gd'}
src={}
for p in files:
    t=open(p,encoding='utf-8').read(); src[p]=t
def members(t):
    m=set()
    for r in [r'^(?:static\s+)?func\s+(\w+)', r'^(?:static\s+)?var\s+(\w+)', r'^const\s+(\w+)', r'^signal\s+(\w+)', r'^@export[^\n]*var\s+(\w+)',r'^static var\s+(\w+)',r'^enum\s+(\w+)']:
        m|=set(re.findall(r,t,re.M))
    return m
cls={}
for p,t in src.items():
    m=re.search(r'^class_name\s+(\w+)',t,re.M)
    name=m.group(1) if m else None
    if not name:
        for a,rel in autoloads.items():
            if p.endswith(rel): name=a
    ext=re.search(r'^extends\s+(\w+)',t,re.M)
    cls[name or p]={'members':members(t),'ext':ext.group(1) if ext else None,'path':p}
def allmembers(n):
    out=set(); seen=0
    while n in cls and seen<10:
        out|=cls[n]['members']; n=cls[n]['ext']; seen+=1
    return out
errors=[]
varmap={ # variable name -> class
 'run':'Run','state':'RunState','st':'RunState','player':'Player','pl':'Player','oxygen':'OxygenManager','ox':'OxygenManager',
 'director':'SpawnDirector','events':'WorldEvents','shop':'ShopManager','hud':'HUD','map':'WorldMap','gate':'RootGate',
}
ENGINE_OK={'global_position','position','visible','queue_free','add_child','get_children','rotation','modulate','paused','velocity','z_index','get_child_count','name','process_mode','call_deferred'}
for p,t in src.items():
    rel=os.path.relpath(p,root)
    lines=t.split('\n')
    in_ml=False
    for i,l in enumerate(lines,1):
        if re.match(r'^ +\S',l): errors.append(f'{rel}:{i}: indentação com espaços')
        if re.match(r'^\t* +\t',l): errors.append(f'{rel}:{i}: mistura')
        if re.search(r':=\s*(clamp|min|max|lerp|abs|sign|round|floor|ceil|snapped|wrap|pow)\(',l): errors.append(f'{rel}:{i}: := com função Variant: {l.strip()}')
        if re.search(r'\bclamp\(|[^a-z_.]min\(|[^a-z_.]max\(|[^a-z_.]abs\(|[^a-z_.]round\(|[^a-z_.]floor\(',l) and 'func ' not in l: errors.append(f'{rel}:{i}: função Variant (aviso): {l.strip()}')
        if len(l.rstrip())>0 and l.count('"')%2==1 and '\\"' not in l and "'" not in l and '#' not in l: errors.append(f'{rel}:{i}: aspas ímpares? {l.strip()[:70]}')
        # membros
        for m in re.finditer(r'\b(GameData|SaveManager|AudioManager|GameManager|UIKit|WorldLayout|RunState|MutationManager|SpawnDirector|Player|GameConfig|WorldMap|Run)\.(\w+)',l):
            c,mem=m.group(1),m.group(2)
            if c in cls and mem not in allmembers(c) and mem not in ('new',) and mem not in ENGINE_OK:
                errors.append(f'{rel}:{i}: {c}.{mem} não existe')
        for m in re.finditer(r'\b(run|state|player|pl|oxygen|ox|director|events|shop|hud|map|gate)\.(\w+)',l):
            v,mem=m.group(1),m.group(2)
            c=varmap.get(v)
            if c=='RunState' and v=='st' and ('Dictionary' in l or 'settings' in l): continue
            if c and c in cls and mem not in allmembers(c) and mem not in ('new',) and mem not in ENGINE_OK:
                # evitar falso positivo: variáveis locais com mesmo nome
                errors.append(f'{rel}:{i}: {v}.{mem} (classe {c}) não existe')
print('\n'.join(errors[:200]) if errors else 'sem erros')
print(len(errors),'achados')
