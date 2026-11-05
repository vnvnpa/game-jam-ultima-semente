#!/usr/bin/env python3
"""Validador estático de .tscn/.tres do projeto (não substitui abrir no Godot)."""
import re, os, sys
ROOT=os.path.abspath(sys.argv[1]) if len(sys.argv)>1 else os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
errs=[]; warns=[]
def err(m): errs.append(m)
def disk(p): return os.path.join(ROOT,p.replace('res://',''))
# --- índices de scripts
script_info={}
for d,_,fs in os.walk(ROOT+'/scripts'):
    for f in fs:
        if f.endswith('.gd'):
            p=os.path.join(d,f); t=open(p,encoding='utf-8').read()
            props=set(re.findall(r'^(?:@export[^\n]*?\s)?var\s+(\w+)',t,re.M))|set(re.findall(r'^@export\w*(?:\([^)]*\))?\s+var\s+(\w+)',t,re.M))
            props|=set(re.findall(r'^@onready var (\w+)',t,re.M))
            onready=re.findall(r'^@onready var (\w+)\s*:\s*(\w+)\s*=\s*(%\w+|\$[\w/%]+)',t,re.M)
            exports=re.findall(r'^@export\s+var\s+(\w+)\s*:\s*(\w+)',t,re.M)
            ext=re.search(r'^extends\s+(\w+)',t,re.M)
            script_info['res://'+os.path.relpath(p,ROOT).replace(os.sep,'/')]={'props':props,'onready':onready,'exports':exports,'text':t,'extends':ext.group(1) if ext else None}
# --- tema
theme_types=set()
tt=open(ROOT+'/ui/game_theme.tres',encoding='utf-8').read()
theme_types=set(re.findall(r'^(\w+)/base_type',tt,re.M))
# --- inherit props (para extends de classes do projeto)
cls_by_name={}
for p,i in script_info.items():
    m=re.search(r'^class_name\s+(\w+)',i['text'],re.M)
    if m: cls_by_name[m.group(1)]=p
def allprops(p):
    out=set(); seen=0
    while p and seen<10:
        i=script_info.get(p); 
        if not i: break
        out|=i['props']; p=cls_by_name.get(i['extends']); seen+=1
    return out
def parse(path):
    t=open(disk(path),encoding='utf-8').read()
    ext={}; subs={}; nodes=[]; cur=None
    for line in t.split('\n'):
        m=re.match(r'\[ext_resource ([^\]]*)\]',line)
        if m:
            a=dict(re.findall(r'(\w+)="([^"]*)"',m.group(1))); ext[a['id']]=a
            if not os.path.exists(disk(a['path'])): err(f'{path}: ext_resource inexistente {a["path"]}')
            continue
        m=re.match(r'\[sub_resource type="(\w+)" id="([^"]+)"\]',line)
        if m: subs[m.group(2)]=m.group(1); cur=None; continue
        m=re.match(r'\[node name="([^"]*)"([^\]]*)\]',line)
        if m:
            rest=m.group(2)
            n={'name':m.group(1),'type':(re.search(r'type="(\w+)"',rest) or [None,None])[1],'parent':(re.search(r'parent="([^"]*)"',rest) or [None,None])[1],
               'instance':(re.search(r'instance=ExtResource\("([^"]+)"\)',rest) or [None,None])[1],'props':{}}
            nodes.append(n); cur=n; continue
        if line.startswith('['): cur=None; continue
        m=re.match(r'([\w/]+) = (.*)',line)
        if m and cur is not None: cur['props'][m.group(1)]=m.group(2)
    return t,ext,subs,nodes
def check_refs(path,t,ext,subs):
    for i in re.findall(r'ExtResource\("([^"]+)"\)',t):
        if i not in ext: err(f'{path}: ExtResource("{i}") sem declaração')
    for i in re.findall(r'SubResource\("([^"]+)"\)',t):
        if i not in subs: err(f'{path}: SubResource("{i}") sem declaração')
scenes=[]
for d,_,fs in os.walk(ROOT):
    if '/.godot' in d: continue
    for f in fs:
        if f.endswith('.tscn'): scenes.append('res://'+os.path.relpath(os.path.join(d,f),ROOT).replace(os.sep,'/'))
for sp in scenes:
    t,ext,subs,nodes=parse(sp); check_refs(sp,t,ext,subs)
    if not nodes: err(f'{sp}: sem nós'); continue
    if nodes[0]['parent'] is not None: err(f'{sp}: raiz com parent')
    paths={'.':nodes[0]}; seen=set()
    for n in nodes[1:]:
        par=n['parent']
        if par is None: err(f'{sp}: nó {n["name"]} sem parent'); continue
        if par not in paths: err(f'{sp}: parent "{par}" de {n["name"]} não existe (ordem?)'); continue
        full=n['name'] if par=='.' else par+'/'+n['name']
        if full in paths: err(f'{sp}: nó duplicado {full}')
        paths[full]=n
    # tipos
    for n in nodes:
        if n['type'] is None and n['instance'] is None and n is not nodes[0]: err(f'{sp}: nó {n["name"]} sem type nem instance')
    # únicos
    uniq={}
    for full,n in paths.items():
        if n['props'].get('unique_name_in_owner')=='true':
            if n['name'] in uniq: err(f'{sp}: nome único repetido {n["name"]}')
            uniq[n['name']]=full
    # variações de tema
    for n in nodes:
        v=n['props'].get('theme_type_variation')
        if v:
            name=re.search(r'&"(\w+)"',v).group(1)
            if name not in theme_types: err(f'{sp}: variação de tema inexistente {name} (nó {n["name"]})')
    # script da raiz
    rs=nodes[0]['props'].get('script')
    if rs:
        sid=re.search(r'"([^"]+)"',rs).group(1); spath=ext[sid]['path']; info=script_info.get(spath)
        if info:
            for var,typ,ref in info['onready']:
                if ref.startswith('%'):
                    if ref[1:] not in uniq: err(f'{sp}: script {os.path.basename(spath)} usa {ref} mas a cena não tem esse nome único')
                else:
                    pth=ref[1:].lstrip('/')
                    if pth not in paths: err(f'{sp}: script usa {ref} inexistente')
            for k in nodes[0]['props']:
                if k in ('script','process_mode','layout_mode','anchors_preset','anchor_right','anchor_bottom','grow_horizontal','grow_vertical','theme','theme_type_variation','mouse_filter','position','collision_layer','collision_mask','motion_mode','size_flags_horizontal','visible','offset_left','offset_top','offset_right','offset_bottom','custom_minimum_size'): continue
                if k not in allprops(spath): err(f'{sp}: propriedade "{k}" definida na cena não existe no script {os.path.basename(spath)}')
            for var,typ in info['exports']:
                if typ=='PackedScene' and var not in nodes[0]['props']: err(f'{sp}: export PackedScene "{var}" não atribuído na cena')
    # scripts em nós não-raiz: propriedades
    for n in nodes[1:]:
        s=n['props'].get('script')
        if s and n['instance'] is None:
            sid=re.search(r'"([^"]+)"',s).group(1); sp2=ext[sid]['path']
    # instâncias: propriedades sobrescritas devem existir no script da cena instanciada
    STD={'position','visible','rotation','scale','modulate','process_mode','unique_name_in_owner','z_index','name','offset_left','offset_top','offset_right','offset_bottom','custom_minimum_size','theme','size_flags_horizontal','size_flags_vertical','layout_mode','anchors_preset','anchor_left','anchor_right','anchor_top','anchor_bottom','grow_horizontal','grow_vertical','mouse_filter','script','text','theme_type_variation'}
    for n in nodes:
        if n['instance']:
            target=ext[n['instance']]['path']
            if not os.path.exists(disk(target)): continue
            tt2,text2,subs2,nodes2=parse(target)
            sc_script=nodes2[0]['props'].get('script') if nodes2 else None
            if nodes2 and nodes2[0]['instance'] and not sc_script:
                # cena herdada: procura o script na cena-base
                continue
            if sc_script:
                sid2=re.search(r'"([^"]+)"',sc_script).group(1)
                ext2={}
                for m2 in re.finditer(r'\[ext_resource ([^\]]*)\]',tt2):
                    a2=dict(re.findall(r'(\w+)="([^"]*)"',m2.group(1))); ext2[a2['id']]=a2
                p2=ext2[sid2]['path']
                for k in n['props']:
                    if k in STD: continue
                    if k not in allprops(p2): err(f'{sp}: instância {n["name"]} sobrescreve "{k}", que não existe em {os.path.basename(p2)}')
    # instâncias: ids de ext devem ser PackedScene
    for n in nodes:
        if n['instance'] and ext[n['instance']]['type']!='PackedScene': err(f'{sp}: instance não é PackedScene')
# .tres de dados
for d,_,fs in os.walk(ROOT+'/data'):
    for f in fs:
        if f.endswith('.tres'):
            p='res://'+os.path.relpath(os.path.join(d,f),ROOT).replace(os.sep,'/')
            t=open(disk(p),encoding='utf-8').read()
            ext={}
            for m in re.finditer(r'\[ext_resource ([^\]]*)\]',t):
                a=dict(re.findall(r'(\w+)="([^"]*)"',m.group(1))); ext[a['id']]=a
                if not os.path.exists(disk(a['path'])): err(f'{p}: ext inexistente {a["path"]}')
            check_refs(p,t,ext,{i:'Resource' for i in re.findall(r'\[sub_resource type="\w+" id="([^"]+)"\]',t)})
            sid=ext['1_script']['path']; props=allprops(sid)
            body=t.split('[resource]')[1]
            for k in re.findall(r'^(\w+) = ',body,re.M):
                if k!='script' and k not in props: err(f'{p}: propriedade {k} não existe em {os.path.basename(sid)}')
# project.godot -> main scene
pg=open(ROOT+'/project.godot',encoding='utf-8').read()
ms=re.search(r'run/main_scene="([^"]+)"',pg).group(1)
if not os.path.exists(disk(ms)): err('main_scene inexistente')
# F0: Input Map, camadas nomeadas, autoloads e ACTION_NAMES coerentes
gm=open(ROOT+'/scripts/core/game_manager.gd',encoding='utf-8').read()
m=re.search(r'const ACTION_NAMES: Array = \[(.*?)\]',gm)
names=re.findall(r'"(\w+)"',m.group(1)) if m else []
if not names: err('game_manager.gd: ACTION_NAMES ausente')
inp=pg.split('[input]')[1].split('\n[')[0] if '[input]' in pg else ''
for a in names:
    if not re.search(r'^'+a+r'=\{',inp,re.M): err(f'project.godot: ação {a} ausente do [input]')
exp=['mundo','jogador','inimigo','projetil_jogador','projetil_inimigo','coletavel','interativo','zona']
for i,n in enumerate(exp,1):
    if f'2d_physics/layer_{i}="{n}"' not in pg: err(f'project.godot: layer_{i} deveria se chamar {n}')
for a,pth in re.findall(r'^(\w+)="\*(res://[^"]+)"',pg,re.M):
    if not os.path.exists(disk(pth)): err(f'autoload {a}: {pth} inexistente')
for req in ['data/abilities/01_nuvem_esporos.tres','data/weapons/dardo_fotossintese.tres','data/audio/sfx_bank.tres','data/audio/music_set.tres','default_bus_layout.tres','data/rules/stat_rules.tres','data/waves/01_floresta.tres','icon.svg','ui/game_theme.tres','assets/art/world/ground_tileset.tres','assets/art/frames/station.tres','assets/art/frames/gate.tres','assets/art/frames/pickups.tres','assets/art/world/fog_tile.png','assets/world/terrain.png','assets/world/garden_terrain.png','.gitignore']:
    if not os.path.exists(os.path.join(ROOT,req)): err(f'arquivo obrigatório ausente: {req}')
if os.path.isdir(os.path.join(ROOT,'.godot')): err('pasta .godot não deve ir no pacote')
print('cenas:',len(scenes)); print('\n'.join(errs) if errs else 'VALIDAÇÃO OK'); print(len(errs),'problemas')
sys.exit(1 if errs else 0)
