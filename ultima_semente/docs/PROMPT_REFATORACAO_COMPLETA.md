# PROMPT MESTRE — Refatoração completa de "Última Semente"
### Objetivo: arte real em sprites/cenários e TUDO configurável no Inspetor (código só para lógica)

> **Como usar:** abra uma conversa nova, anexe o **zip completo do projeto** e cole o bloco da seção 0.
> Este arquivo (`docs/PROMPT_REFATORACAO_COMPLETA.md`) é a especificação; o GDD (`docs/GDD_Projeto_Ultima_Semente.md`)
> continua sendo a fonte das regras de jogo. Se os dois divergirem sobre *regras de jogo*, vale o GDD; sobre
> *arquitetura e arte*, vale este documento.

---

## 0. Bloco para colar na conversa

```
Você é o desenvolvedor líder do jogo "Última Semente" (Godot 4.7.x, GDScript, renderer Compatibility, exportação Web).
Leia docs/PROMPT_REFATORACAO_COMPLETA.md e docs/GDD_Projeto_Ultima_Semente.md inteiros antes de qualquer coisa.
Missão: refazer o projeto para que TODO elemento visual e de configuração viva em cenas (.tscn) e recursos (.tres),
editável no Inspetor da Godot, sem arte desenhada por _draw(). Código só para lógica.
Trabalhe por fases (seção 9). Em cada resposta: (1) avalie o estado, (2) execute UMA fase (ou parte dela),
(3) entregue o PROJETO COMPLETO em .zip (nunca só os arquivos alterados), (4) diga o que abrir/testar no editor,
(5) atualize PROGRESSO.md. Não invente nós, APIs ou arquivos; se faltar informação, assuma, avise e siga.
Responda em português. Comece pela Fase 0.
```

---

## 1. Por que refazer (diagnóstico real do projeto atual)

O jogo funciona por código, mas **não é editável no editor**:

| Problema | Onde está |
|---|---|
| Quase toda a arte é desenhada por `_draw()` (círculos, linhas, polígonos) | `player.gd`, `enemy.gd`, `boss.gd`, `gardener.gd`, `projectile.gd`, `fx.gd`, `biomass_pickup.gd`, `decoy.gd`, `spore_zone.gd`, `root_slam.gd`, `obstacle.gd`, `station.gd`, `hostile_zone.gd`, `region_zone.gd`, `boss_arena.gd`, `root_gate.gd`, `interactable.gd`, `guide_arrows.gd`, `map_overlay.gd`, `main_menu_screen.gd` |
| O "sprite" de cada coisa é só um export `draw_placeholder` | todas as cenas de `scenes/entities` e `scenes/world` |
| Chão = uma única imagem gerada (`terrain.png`/`garden_terrain.png`) esticada ×4, sem tiles, sem camadas | `world_map.tscn`, `garden_map.tscn` |
| Sem animações (só `sin(anim_t)` no código) | inimigos, jogador, chefes |
| Áudio 100% procedural em código (`audio_manager.gd`), sem arquivos nem players na cena | `audio_manager.gd` |
| Balanceamento escondido em código: tabelas de spawn, limites de atributos, efeitos de loja, buffs, timers de chefe, cronograma de eventos | `spawn_director.gd`, `run_state.gd`, `shop_manager.gd`, `world_events.gd`, `boss.gd`, `gardener.gd`, `player.gd` |
| Teclas criadas por código | `game_manager.gd` (`ACTIONS`) |
| Tema de reserva construído em código | `ui_kit.gd` |
| Pacote entregue sem `ui/` e `terrain.png` quebrou a abertura do projeto | (erro de empacotamento — ver seção 10) |

**Resultado desejado:** abrir `world_map.tscn` e ver o mapa pintado com TileMap; abrir `enemy_larva.tscn` e ver o
sprite animado, a colisão, os sons e as partículas como nós; mudar vida, velocidade, cores, sons e frames **sem
tocar em script**.

---

## 2. Regras de ouro (valem para todas as fases)

1. **Visual = nós.** `Sprite2D`, `AnimatedSprite2D`, `TileMapLayer`, `Polygon2D`, `Line2D`, `CPUParticles2D`,
   `GPUParticles2D` (**não** usar GPU em export Web/Compatibility sem testar; preferir `CPUParticles2D`),
   `AnimationPlayer`, `Label`, `TextureRect`, `NinePatchRect`. **Proibido** `_draw()` para arte final.
   `_draw()` só é aceitável em ferramentas de debug (ex.: círculo de alcance, desligado por padrão).
2. **Configuração = Inspetor.** Todo número de design (vida, dano, velocidade, tempos, raios, custos, probabilidades,
   cores, curvas) é `@export` ou campo de `Resource` (`.tres`). Constante no código só se for **regra fixa do motor**
   (ex.: `TAU`, tamanho do mundo se não puder vir de cena).
3. **Lógica = scripts.** Scripts pequenos, tipados, sem `draw_placeholder`, sem `@tool` desnecessário
   (com nós reais o editor já mostra tudo). Remover `@tool` de scripts que só existiam para desenhar no editor.
4. **Uma cena por coisa.** Cada inimigo, chefe, projétil, efeito, objeto de mundo, tela e tipo de interativo tem a
   **sua** `.tscn`, com herança de cena (`enemy_base.tscn` → `enemy_larva.tscn`). Nada é montado por `Node.new()` em código,
   exceto listas dinâmicas (ex.: linhas de um menu) e instâncias de cenas já configuradas.
5. **Referências por `@export`** (`@export var sprite: AnimatedSprite2D`, `@export var scene: PackedScene`), não por
   caminhos de string. `%NomeUnico` aceitável dentro da própria cena.
6. **Entradas** (`Input Map`) definidas em `project.godot` (Projeto → Configurações → Mapa de Entrada). O remapeamento
   em jogo (já existe) passa a guardar **somente as diferenças** em save.
7. **Camadas de colisão com nome** em `project.godot` (`layer_names`): 1 `mundo`, 2 `jogador`, 3 `inimigo`,
   4 `projetil_jogador`, 5 `projetil_inimigo`, 6 `coletavel`, 7 `interativo`, 8 `zona`.
8. **Textos de interface** ficam em cenas/temas; números formatados em código com `%`.
9. **Nada de assets de terceiros** sem licença registrada (GDD 21.10). Arte e áudio do projeto são gerados por
   scripts em `tools/` (seção 5) e **substituíveis** pelo usuário mantendo os mesmos nomes/tamanhos.
10. **Compatibilidade Web:** Renderer Compatibility, texturas `nearest`, sem shaders pesados, partículas limitadas,
    áudio só após interação.
11. **Não regredir o jogo:** todo comportamento do GDD/README atual continua valendo (oxigênio, loja, mutações,
    save, chefes, Jardim, remapeamento, acessibilidade "reduzir efeitos").

---

## 3. Arquitetura alvo

### 3.1 Estrutura de pastas

```
ultima_semente/
├── project.godot                (Input Map, layer_names, autoloads)
├── assets/
│   ├── art/
│   │   ├── player/        player_sheet.png, mutation_spines.png, companion.png
│   │   ├── enemies/       larva.png, cortarraiz.png, flor.png, casca.png, esporideo.png, parasita.png,
│   │   │                  anomalia.png, ninho.png, guardiao.png, jardineiro.png
│   │   ├── world/         tileset_floresta.png, tileset_bacia.png, tileset_santuario.png, tileset_jardim.png,
│   │   │                  decor.png, trees.png, crystals.png, pillars.png, station.png, terminal.png, ship.png,
│   │   │                  ruin.png, mechanism.png, gate.png, arena.png, hostile_fx.png
│   │   ├── fx/            projectiles.png, ring.png, burst.png, explosion.png, shield.png, slam.png, decoy.png,
│   │   │                  pickups.png, spores.png
│   │   └── ui/            panel_*.png (9-patch), button_*.png, icons.png, bars.png, vignette_*.png, logo.png,
│   │                      menu_bg_*.png
│   ├── audio/
│   │   ├── sfx/           shoot.wav, hit.wav, ... (um arquivo por efeito)
│   │   └── music/         explore_loop.wav, combat_loop.wav
│   └── fonts/             (opcional; fonte pixel com licença registrada)
├── data/                  (.tres de dados — já existe; ver 3.3 para os novos)
├── scenes/
│   ├── player/            player.tscn, companion.tscn
│   ├── enemies/           enemy_base.tscn + 1 cena por inimigo/chefe
│   ├── combat/            projectile_*.tscn, slam.tscn, spore_zone.tscn, decoy.tscn, explosion.tscn
│   ├── fx/                fx_ring.tscn, fx_burst.tscn, fx_float_text.tscn, fx_hit.tscn ...
│   ├── pickups/           biomass.tscn, biomass_cache.tscn, nucleus.tscn
│   ├── world/             worlds/world_floresta.tscn, world_jardim.tscn; props/; zones/; interactables/
│   ├── ui/                (já existe; ganhar texturas, ícones, 9-patch)
│   └── main/
├── scripts/               (somente lógica)
├── tools/                 gen_art.py, gen_audio.py, bake_tilemap.gd, smoke_test.gd, smoke_garden.gd,
│                          validate_scenes.py, lint*.py
└── docs/
```

### 3.2 Padrão de cada entidade (exemplo: inimigo)

```
EnemyLarva (CharacterBody2D)               ← enemy_larva.tscn, herda enemy_base.tscn, script enemy.gd
├── Sprite (AnimatedSprite2D)              ← SpriteFrames: idle, walk, hurt, death
├── Shadow (Sprite2D)                      ← sombra oval
├── Shape (CollisionShape2D)               ← o RAIO vem daqui (script lê o shape; some o campo "raio" duplicado)
├── HurtFlash (AnimationPlayer)            ← pisca ao levar dano (modulate), editável
├── StatusFx (Node2D)                      ← filhos: AuraEmpower, RootedFx, PoisonFx (visíveis por script)
├── HpBar (TextureProgressBar)             ← barra de vida
├── Audio (AudioStreamPlayer2D x N)        ← streams atribuídos no Inspetor (ou SfxBank)
└── Hit/Hurtbox (Area2D, opcional)
```
O script só decide *quando* tocar `Sprite.play("walk")`, mostrar `AuraEmpower` etc. **Cor, frames, velocidade de animação,
tamanho e sons são do Inspetor.**

### 3.3 Dados que saem do código para `Resource`

| Hoje (em código) | Novo Resource (`.tres`) | Campos |
|---|---|---|
| `SpawnDirector.weights()`, `CAP_*`, `RAMP_TIME`, intervalos, `max_elites` | `WaveProfile` + `WaveStage` | por etapa: `inicio_s`, nome, lista `(EnemyData, peso)`, `lote`, `teto`, `intervalo` |
| `WorldEvents.schedule`, durações, tamanhos | `ThreatEventData` | `tempo_s`, `tipo`, `duracao_s`, `inimigos_por_onda`, `recompensa` |
| `RunState.STAT_LIMITS`, `BASE_*`, `BUFF_DEFS` | `StatRules` / `BuffData` | limites min/máx por atributo; buffs com `mods`, duração, ícone |
| `ShopManager.buy_item` (`match` de efeitos) | `ShopItemData` ganha `efeito_tipo` (enum), `valor`, `duracao`, `max_cargas`, `icone` | loja deixa de ter `match` por id |
| Timers/dano de `Boss`/`Gardener` | `@export` na cena do chefe ou `BossPatternData` | intervalos, contagens, raios, dano |
| `GameManager.ACTIONS` | Input Map do `project.godot` | só o remapeamento fica em código |
| `AudioManager._build_sfx()` | `SfxBank` (Resource: nome → `AudioStream`, volume, variação de pitch) | arquivos `.wav` em `assets/audio` |
| `Run.EXTRACT_*`, limites de projéteis/drops | `@export` no `Run` ou `GameBalance.tres` | |
| `Player` (vida base, velocidade base, etc.) | `PlayerStats.tres` | `BASE_HP`, `BASE_SPEED`, `BASE_O2`, raio de coleta |

---

## 4. Direção de arte (do GDD, seção 4)

- Pixel art top-down, silhuetas claras, `texture_filter = nearest`.
- **Tile 32×32 px** (arte base em 16×16 ampliada 2× na criação; um tile = 32 px de mundo). Mundo atual 3600×2600
  → **113×82 tiles** (o `WORLD_RECT` pode virar `@export` do mapa).
- Paleta: vegetação saudável verdes/turquesas; contaminação roxos/magentas/vermelhos; tecnologia humana
  laranja/cinza/branco; Biomassa dourado-esverdeado; Núcleos ciano/violeta.
- Personagens: **frame 32×32** (jogador, comuns); **48×48** (Casca-Túmulo, Anomalia); **64×64** (Ninho);
  **96×96** (Guardião, Jardineiro). Pivô nos pés (offset da `AnimatedSprite2D`).
- Mutações alteram a silhueta do jogador: camadas de espinhos como `Sprite2D` filhos ligados/desligados por contagem.

### 4.1 Lista completa de sprites (com frames)

| Arte | Folha | Animações (frames) |
|---|---|---|
| Jogador Kael | `player_sheet.png` 32×32 | idle (4), walk (6), hurt (2), dash (3), death (6); direções: baixo/cima/lado (+`flip_h`) |
| Espinhos de mutação | `mutation_spines.png` | 8 variações (sobreposições) |
| Companheiro Micélio | `companion.png` | idle (4), attack (3) |
| Larva-Fértil | `larva.png` | idle (4), walk (6), hurt (2), death (5) |
| Cortarraiz | `cortarraiz.png` | walk (6), windup (3), charge (3), recover (2), death (5) |
| Flor de Ruptura | `flor.png` | idle (4), shoot (4), death (5) |
| Casca-Túmulo | `casca.png` 48×48 | walk (6), hurt (2), death (6) |
| Esporídeo | `esporideo.png` | walk (6), spore (3), death (5) |
| Parasita de Sinal | `parasita.png` | float (4), pulse (4), death (5) |
| Anomalia (elite) | `anomalia.png` 48×48 | walk (6), hurt (2), death (6) + 4 tints/auras (blindada/veloz/explosiva/regenerante) |
| Ninho | `ninho.png` 64×64 | idle (4), spawn (4), death (6) |
| Guardião de Raízes | `guardiao.png` 96×96 | idle (4), slam (6), summon (6), phase2 (4), death (8) |
| Jardineiro Vazio | `jardineiro.png` 96×96 | shielded (4), exposed (4), shoot (4), roots (6), death (8) |
| Projéteis | `projectiles.png` 16×16 | espinho (2), cuspe (2), bolt do Jardineiro (2), estilhaço (2) |
| Efeitos | `ring.png`, `burst.png`, `explosion.png` (6), `shield.png`, `slam.png` (telégrafo), `decoy.png` (4) | |
| Coletáveis | `pickups.png` | biomassa (4), cache (4), núcleo (6) |
| Esporos | `spores.png` | zona (4) + partículas |
| Árvores, cristais, pilares | `trees.png`, `crystals.png`, `pillars.png` | 3–4 variações cada, com sombra |
| Estação pressurizada | `station.png` | cúpula/anel (4) |
| Terminal, nave, ruína, mecanismo | `terminal.png`, `ship.png`, `ruin.png`, `mechanism.png` | idle (4); mecanismo ainda: ativo (4) |
| Barreira de Raízes | `gate.png` | fechada (4), abrindo (6), aberta (1) |
| Arena do chefe | `arena.png` | anel/runas (4) |
| Zona contaminada | `hostile_fx.png` | névoa tileável (4) |
| Tilesets | 4 arquivos | ver 5.2 |
| UI | painéis 9-patch, botões (normal/hover/pressed/disabled), ícones 32×32 (habilidades, buffs, itens, equipamentos), barras, vinhetas, logo, fundo do menu | |

---

## 5. Pipeline de assets

### 5.1 Geração
- `tools/gen_art.py` (Python + Pillow) gera **todos** os PNGs acima de forma determinística (`seed` fixa), com
  paleta central em `tools/palette.json`. Cada sprite é desenhado com primitivas de pixel art (contorno, sombreamento
  em 2–3 tons, luz vinda de cima-esquerda) e salvo como **spritesheet horizontal** (um frame por coluna, uma
  animação por linha).
- `tools/gen_audio.py` gera os `.wav` (mesmas receitas hoje em `audio_manager.gd`) e os loops de música.
- **Honestidade sobre qualidade:** arte gerada por script é *funcional e coerente*, não arte final de estúdio. O
  projeto deve ser montado para que o usuário **troque qualquer PNG** (mesmo nome, mesmas colunas/linhas) e tudo
  continue funcionando, ou ajuste os frames no Inspetor (`SpriteFrames`).
- Importação: preset `2D Pixel` (filter nearest, sem mipmaps); gerar os `.import` não é necessário (a Godot cria).

### 5.2 Mapa em TileMap (resolve "sem chão")
- Cada mundo (`world_floresta.tscn`, `world_jardim.tscn`) tem:
  `Ground (TileMapLayer)` → `GroundDetail (TileMapLayer)` → `Props (Node2D com cenas de obstáculo)` →
  `Decor (TileMapLayer ou Node2D de Sprite2D)` → `Overlay (zonas, estações, portões)`.
- `TileSet` por bioma com *terrain sets* (grama/terra/pedra/lama/contaminado/violeta) e **colisão/ruído** no tile
  quando aplicável (paredes, água).
- `tools/bake_tilemap.gd` (EditorScript): lê as `RegionZone`/`HostileZone` do mapa e **pinta o chão inicial**
  automaticamente (cada região com seu bioma, trilhas entre pontos de interesse, bordas das zonas contaminadas),
  para que o usuário só retoque à mão.
- Muralhas passam a ser `TileMapLayer` com colisão **ou** `StaticBody2D` com `Sprite2D`/`NinePatchRect`
  (sem `ColorRect` roxo).

---

## 6. Especificação por sistema (o que cada cena terá no Inspetor)

### 6.1 Jogador (`scenes/player/player.tscn`)
Nós: `Sprite (AnimatedSprite2D)`, `Spines (Node2D → 8 Sprite2D)`, `Shadow`, `Arm/Muzzle (Marker2D)`,
`ShieldFx (Sprite2D)`, `Companions (Node2D, instancia companion.tscn)`, `Shape`, `Camera (Camera2D)`,
`HurtFx (AnimationPlayer)`, `DashFx (CPUParticles2D)`, `PickupArea (Area2D)`, `Audio*`.
Inspetor: raio de pulso/emergência, tempos, invulnerabilidade, zoom, suavização, limites da câmera (vindos do mapa),
`PlayerStats.tres`, cena do projétil (`@export var projectile_scene`).
Código: movimento, mira, disparo, habilidades, dano/cura, escudo.

### 6.2 Inimigos e chefes
- `enemy_base.tscn` com o esqueleto da seção 3.2; cada inimigo herda e preenche sprite/colisão/sons.
- `EnemyData.tres` mantém **números** (vida, dano, velocidade, XP, drops, intervalos, parâmetros) e passa a ter
  `cena` obrigatória; **remover** `raio`, `cor`, `cor_detalhe` (vêm da cena).
- Comportamentos continuam em script, **um script por comportamento** (`behavior_chase.gd`, `behavior_charger.gd`,
  `behavior_ranged.gd`, `behavior_spore.gd`, `behavior_parasite.gd`, `behavior_nest.gd`, `behavior_boss_*.gd`) como
  `Node` filho configurável no Inspetor (composição em vez de `if comportamento == "..."`).
- Chefes: padrões (`slam`, `summon`, `shots`, `roots`) como nós filhos `BossPattern` com `@export` de intervalo,
  contagem, raio, dano, telégrafo (cena), som. Janela de vulnerabilidade do Jardineiro = `AnimationPlayer`/`Timer`.
- Elites (Anomalia): 4 modificadores como `Resource` (`EliteModifier`: tint, vida×, velocidade×, explosão, regen).

### 6.3 Combate e efeitos
- `projectile_*.tscn`: `Sprite/AnimatedSprite2D`, `Trail (Line2D ou CPUParticles2D)`, `Hit (cena de FX)`; dano, velocidade,
  vida e perfuração vêm do `WeaponData`/Inspetor.
- `fx_*.tscn`: anel (`Sprite2D` + `AnimationPlayer` escala/alpha), faíscas (`CPUParticles2D one_shot`), explosão
  (`AnimatedSprite2D`), texto flutuante (`Label` + `Tween`/`AnimationPlayer`, fonte do tema).
  Um `FxPool`/`Marker` opcional para limitar instâncias (já existe limite de 100).
- `slam.tscn` (telégrafo): círculo com `Sprite2D` + `AnimationPlayer` (cresce e muda de cor); raio via `@export`.
- `spore_zone.tscn`, `decoy.tscn`, `explosion.tscn` idem: tudo em nós.

### 6.4 Mundo
- **Obstáculo**: `tree_*.tscn`, `crystal_*.tscn`, `pillar_*.tscn` = `StaticBody2D` + `Sprite2D` + `Shadow` + `Shape`.
  O script `Obstacle` expõe `radius` **lendo a `CollisionShape2D`** (sem `radius` duplicado).
- **Estação**: `Sprite2D` da cúpula + `Area2D` circular + `AnimationPlayer` do pulso; raio = shape.
- **Zona contaminada**: `Polygon2D`/`TextureRect` com textura tileável + `CPUParticles2D` + `CollisionShape2D`
  retangular; `size` vem do shape.
- **Região**: nó só de dados (nome, cor do mapa, flag de bloqueio) com retângulo (shape).
- **Portão de Raízes**: `AnimatedSprite2D` (fechada/abrindo/aberta) + `StaticBody2D`.
- **Arena do chefe**: `Sprite2D`/anel + `Area2D` de gatilho (raio = shape).
- **Interativos**: uma cena por tipo (`terminal.tscn`, `ship.tscn`, `ruin.tscn`, `mechanism.tscn`), cada uma com
  sprite, brilho (`PointLight2D` opcional ou sprite aditivo), `Area2D` de alcance e prompt (`Label`).
  Script único `Interactable` genérico + `kind` como enum **ou** um script mínimo por tipo.
- **Coletáveis**: `biomass.tscn`, `biomass_cache.tscn`, `nucleus.tscn` com `AnimatedSprite2D` e `Area2D` de ímã.

### 6.5 Interface
- `game_theme.tres` com **`StyleBoxTexture`** (9-patch) para painéis/botões/barras, fonte pixel e tamanhos; remover o
  tema de reserva em código (`UIKit._build_fallback_theme`) e as cores duplicadas em `UIKit` (virar `Theme`/`Resource`
  `UiPalette`).
- HUD com ícones de habilidade (`TextureRect` + `TextureProgressBar` radial de recarga) em vez de apenas texto.
- Menu principal: cena com `ParallaxBackground`/`TextureRect` em camadas + `CPUParticles2D` de esporos + logo
  (substitui o `_draw` do `main_menu_screen.gd`).
- Mapa (`M`): `SubViewport`/`TextureRect` com ícones como `Sprite2D` (substitui `map_overlay._draw`); setas-guia
  (`guide_arrows`) como `Sprite2D`/`Line2D` por cena.
- Telas: lojas/laboratório/códice com ícones de item/mutação/inimigo (campo `icone` nos `.tres`).

### 6.6 Áudio
- `AudioManager` mantém só: barramentos, pool de players, crossfade de música, volumes salvos.
- `SfxBank.tres` (nome → stream/volume/pitch) e `MusicSet.tres` (explorar/combate) editáveis no Inspetor.
  Entidades podem ter `AudioStreamPlayer2D` próprios (passos, ataques) com stream no Inspetor.

### 6.7 O que PODE ficar em código
Movimento/IA, regras de dano e economia, validação/salvamento, remapeamento, fluxo de telas, aplicação de mods de
atributos, geração de ofertas da loja, sorteio de mutações, spawns (lendo `WaveProfile`). Tudo o resto → Inspetor.

---

## 7. Qualidade e testes (a cada fase)

- `python3 tools/validate_scenes.py` → 0 problemas (estender para checar `SpriteFrames`/texturas referenciadas).
- `godot --headless --path . --import` sem erros; `smoke_test.gd` e `smoke_garden.gd` passando (atualizar para os
  novos nós; os testes devem continuar cobrindo mundo, oxigênio, loja, chefes, save, Jardim, remapeamento).
- Teste manual por fase (lista no `PROGRESSO.md`): abrir cada cena nova no editor e conferir que **sprite, colisão e
  sons aparecem no Inspetor**.
- Desempenho Web: medir FPS com ~70 inimigos; limitar partículas/FX; sem erros no console.

---

## 8. Critérios de aceite do projeto refeito

1. Nenhum `_draw()` de arte restante (grep `_draw(` só em debug opcional).
2. Nenhum `draw_placeholder`.
3. Abrir `world_floresta.tscn` e `world_jardim.tscn` mostra **chão, decoração, obstáculos, estações, zonas e portão** como nós visíveis e editáveis.
4. Cada inimigo/chefe/projétil/efeito/objeto tem cena própria com sprite animado, colisão e sons configuráveis.
5. Trocar um PNG em `assets/art` por outro de mesmo layout atualiza o jogo sem editar código.
6. Balanceamento (spawn, eventos, buffs, limites, loja, chefes) só em `.tres`/Inspetor.
7. Teclas padrão no Input Map; remapeamento preservado.
8. Jogo roda do início ao fim (menu → expedição → Guardião → Jardim → vitória) sem erros no console.
9. Exportação Web testada (carregamento, áudio, save, foco).
10. README e PROGRESSO atualizados; zip completo entregue.

---

## 9. Plano de execução por fases

> Cada fase termina com **zip completo**, testes executados (ou declarados como não executados) e `PROGRESSO.md`.

| Fase | Entrega | Conteúdo |
|---|---|---|
| **F0 — Base e empacotamento** | projeto abre sem erros | `project.godot` com Input Map e `layer_names`; verificar todas as dependências; checklist de empacotamento; mover `ACTIONS` para o Input Map |
| **F1 — Pipeline de arte/áudio** | `tools/gen_art.py`, `gen_audio.py`, paleta, todos os PNG/WAV | sprites e sons completos de todas as listas da seção 4 e 6.6, com preview (`tools/preview_sheets.png`) |
| **F2 — Recursos de dados** | novos `.tres` | `WaveProfile`, `ThreatEventData`, `StatRules`, `BuffData`, `ShopItemData` com efeitos, `SfxBank`, `PlayerStats`, `EliteModifier`; remover constantes do código |
| **F3 — Mundo** | `world_floresta.tscn`, `world_jardim.tscn` | TileSets, `bake_tilemap.gd`, props com sprites, estações, zonas, portão, arena, interativos, coletáveis como cenas |
| **F4 — Jogador, combate e FX** | `player.tscn`, projéteis, FX, zonas | sem `_draw`; animações e partículas; câmera; sons nos nós |
| **F5 — Inimigos e chefes** | 10 cenas de inimigos + base | comportamentos como nós; chefes com `BossPattern`; ninhos |
| **F6 — Interface** | tema com texturas, HUD com ícones, menu animado, mapa e guias em nós | ícones nos `.tres` |
| **F7 — Áudio e integração** | `AudioManager` enxuto, `SfxBank`, músicas | crossfade, volumes, foco da janela |
| **F8 — Conteúdo pendente do GDD** | Coração de Nymara (3 etapas + decisão), Nuvem de Esporos, Dardo de Fotossíntese, sinergias, gamepad | já usando a nova arquitetura |
| **F9 — QA e Web** | exportação, desempenho, balanceamento, README | critérios da seção 8 |

Ordem de prioridade se o tempo for curto: **F0 → F1 → F3 → F4 → F5 → F6 → F2 → F7 → F8 → F9.**
(Primeiro o que o jogador vê e consegue editar: chão, personagens, inimigos, interface.)

---

## 10. Regras de entrega (lição aprendida)

1. **Sempre entregar o projeto COMPLETO em um .zip** (com `project.godot`, `ui/`, `assets/`, `docs/`, `data/`,
   `scenes/`, `scripts/`, `tools/`, `icon.svg`, `.gitignore`), **sem** a pasta `.godot/`. Nunca "só os arquivos alterados".
2. Antes de entregar: rodar `validate_scenes.py` **no zip extraído numa pasta limpa** para provar que não faltam
   dependências.
3. Listar no fim: arquivos novos/alterados, como testar no editor, testes rodados e **não** rodados, problemas
   conhecidos.
4. Declarar com clareza o que é **implementado**, **testado** e **pendente de validação** (GDD 24).
5. O assistente não consegue executar a Godot nem enviar ao GitHub: o usuário abre o projeto, roda os testes e
   cola o console de volta; o próximo lote corrige com base nisso.

---

## 11. Decisões assumidas (podem ser mudadas antes da F1)

- Tile de 32 px e frames de 32/48/64/96 px (seção 4).
- Arte e áudio gerados por script, substituíveis; sem fonte externa (usar a fonte padrão até haver uma fonte livre registrada).
- Partículas com `CPUParticles2D` por compatibilidade Web.
- Manter `WORLD_RECT` 3600×2600 até a F3; depois ele vem do mapa.
- Manter o GDD como regra de jogo; mudanças de design entram só como proposta separada.
