# Projeto: Última Semente — build MVP (Godot 4.7.x, GDScript)
---
## Atualização (versão pós-F8a) — leia isto primeiro
**Estado honesto:** o conteúdo abaixo foi escrito para a primeira build; várias partes mudaram. Nada desta versão foi executado na Godot pelo autor do código (o ambiente de geração não tem Godot): use `docs/QA_CHECKLIST.md`.

**Novidades:** arte e áudio gerados por script (`tools/gen_art.py`, `gen_audio.py`), chão em TileMapLayer, sprites animados (Kael, inimigos, chefes, mundo), interface texturizada, balanceamento em Resources (`data/waves`, `events`, `elites`, `buffs`, `rules`, `abilities`, `audio`), Nuvem de Esporos (F), Dardo de Fotossíntese, Santuário do Último Jardim (fase 2) e Coração de Nymara (fase final, chefe em 3 etapas + escolha do final), gamepad, menu com botões que crescem.

**Controles:** WASD/Setas · mouse · Espaço Pulso · Q Ruptura · R Emergência · F Nuvem · E interagir · M mapa · Esc pausa. Gamepad: analógico/D-pad, A, RB, X, Y, B, Back, Start.

**Comandos úteis (raiz do projeto):**
```
python3 tools/run_checks.py            # validação estática (sem Godot)
python3 tools/gen_art.py && python3 tools/build_spriteframes.py && python3 tools/build_tileset.py
python3 tools/gen_audio.py && python3 tools/build_audio_bank.py
python3 tools/check_scripts.py <Godot>  # erros de script com linha (usa a Godot)
godot --headless --path . --import
godot --headless --path . -s res://tools/smoke_test.gd
godot --headless --path . -s res://tools/smoke_garden.gd
godot --headless --path . -s res://tools/smoke_heart.gd
```
**Dados editáveis no Inspetor:** `data/waves` (dificuldade por tempo), `events`, `elites`, `buffs`, `rules/stat_rules.tres`, `abilities`, `audio/sfx_bank.tres` + `music_set.tres`, além de `enemies`, `mutations`, `upgrades`, `shop`, `equipment`, `weapons`.

**Exportar para Web:** preset "Web" já em `export_presets.cfg` (sem threads, para o itch.io). Em *Projeto → Exportar* instale os templates 4.7.x e exporte para `export/web/index.html`; compacte a pasta em `.zip` e marque "play in browser". `ITCH_URL` em `scripts/core/game_config.gd` continua vazio de propósito.

**Se aparecerem erros ao abrir:** apague `.godot/`, reabra, e envie as linhas completas do painel Saída.
---


Jogo 2D top-down de ação, sobrevivência e evolução biológica, implementado a partir de
`docs/GDD_Projeto_Ultima_Semente.md`. Toda a arte, os sons e a música são **gerados por código**
(nenhum asset de terceiros). Renderizador: **Compatibility** (compatível com Web/itch.io).

## Como abrir e jogar
1. Instale a **Godot 4.7.2** (versão estável mais recente na data da criação) — versão padrão, **não** .NET.
2. Abra o Godot → *Import* → selecione `project.godot` → aguarde a importação inicial → **F5**.

## Controles
WASD/Setas mover · Mouse mirar · a arma (Espinho Simbiótico) dispara sozinha · **Espaço** Pulso de Raízes ·
**Q** Ruptura Celular (arrancada) · **R** Pulso de Emergência (comprado na loja) · **E** interagir
(segurar na nave para extrair) · **M** mapa · **Esc** pausa.

## O que está implementado
- Menu principal, preparação, HUD, pausa, configurações (volumes separados, reduzir efeitos, números de dano),
  mapa, créditos, arquivo biológico (criaturas, mutações, registros), game over e vitória/epílogo.
- Mapa aberto montado no editor: 3 regiões (Floresta do Despertar, Bacia dos Ecos, Santuário das Raízes),
  130 obstáculos com colisão, 3 ninhos, 4 pontos de interesse com registros, 16 caches de Biomassa.
- Oxigênio: consumo só em zonas contaminadas, recarga em estações/bolsões, falta de ar causa dano gradual,
  alertas, seta de retorno e vinheta.
- 6 inimigos comuns + Anomalia (elite, 4 modificadores) + Ninho + chefe **Guardião de Raízes** (2 fases,
  2 padrões: Raízes Esmagadoras telegrafadas e Invocação).
- Diretor de surgimento por etapas (teto de pressão aos 22 min), elites, eventos de ameaça (Enxame/Crise).
- 15 mutações temporárias + 3 evoluções especiais; 15 mutações **permanentes** em 3 linhas com
  pré-requisitos, incompatibilidade, vantagens e efeitos colaterais; compra e reversão (custo = valor pago,
  sem reembolso) com confirmação e antes/depois dos atributos.
- Loja (9 consumíveis + 6 equipamentos), com confirmação explícita, limite por visita e ofertas rotativas.
- Núcleos Primordiais: salvos imediatamente, recompensa de chefe e descobertas creditadas **uma única vez**.
- Save em `user://` com validação, backup e transação (compra/reversão desfeitas se a gravação falhar).
- Pausa automática ao perder o foco da janela/aba.
- **Santuário do Último Jardim** (GDD 14.1), missão dedicada liberada ao derrotar o Guardião de Raízes (menu principal):
  3 mecanismos para ativar resistindo a ondas, passagem para a Câmara e chefe **Jardineiro Vazio** (blindado, só recebe
  dano nas janelas de vulnerabilidade; disparos em leque, raízes telegrafadas e invocações na fase 2). Começa só com as
  mutações permanentes; derrotar o Guardião na expedição principal agora abre uma tela de transição em vez dos créditos.
- Remapeamento de teclas (Configurações > Controles): tecla principal de cada ação, com troca automática em conflito; Esc, setas e 1–3 reservadas.

## Fora desta build (pendente, conforme GDD)
- Nível final **Coração de Nymara** e a escolha do final: nesta build, derrotar o Jardineiro Vazio (Santuário do
  Último Jardim) encerra a campanha (epílogo + créditos), de forma provisória.
- Gamepad, localização, Nuvem de Esporos/Dardo de Fotossíntese e outras sinergias extras.
- Modo "revisitar o mundo" (previsto só como pós-lançamento no GDD).
- `ITCH_URL` em `scripts/core/game_config.gd` está **vazio de propósito**: preencha com o endereço real do
  jogo para o botão "Apoiar o projeto" aparecer nos créditos.

## Como editar cada parte no editor do Godot (tudo é cena ou recurso)
| O quê | Onde editar |
|---|---|
| Jogador (colisão, câmera, zoom, habilidades: raio/dano/recarga do Pulso, arrancada) | `scenes/entities/player.tscn` (Inspector do nó raiz → grupos "Pulso", "Ruptura"...) |
| Inimigos / chefe | `scenes/entities/enemy.tscn`, `boss.tscn` (herda de enemy). Cada inimigo aponta para a sua cena no campo **Cena** do `.tres` |
| Números de cada inimigo, mutação, melhoria, item, equipamento, registro, arma | `.tres` em `data/enemies`, `mutations`, `upgrades`, `shop`, `equipment`, `records`, `weapons`. Para criar um novo, **duplique um `.tres`** (o prefixo `01_`, `02_` define a ordem) e edite no Inspector |
| Projéteis, coletáveis, zonas de esporos, golpe do chefe, isca, efeitos, interativos | `scenes/entities/*.tscn` |
| **Cenário inteiro** (terreno, regiões, zonas contaminadas, estações, muralhas, barreira, obstáculos, caches, nave, terminais, ruínas, ninhos, arena do chefe) | `scenes/world/world_map.tscn`: abra e mova/duplique/apague os nós no editor (grupos `Regions`, `HostileZones`, `Stations`, `Walls`, `Obstacles`, `Caches`, `Interactables`, `Nests`, `BossArena`) |
| Imagem do terreno | `assets/world/terrain.png` (pinte/substitua no editor de imagens; 1 pixel = 4 px do mundo) |
| Cada tipo de elemento | `scenes/world/station.tscn`, `hostile_zone.tscn`, `region_zone.tscn`, `boss_arena.tscn`, `tree/crystal/pillar.tscn`, `root_gate.tscn` e `scenes/entities/interactable.tscn`, `biomass_pickup.tscn` |
| Nível do Jardim | `scenes/world/garden_map.tscn` (mapa), `scenes/world/garden_run.tscn` (regras: `Level Id`, `Boss Id`, dificuldade inicial no `SpawnDirector`, `Objectives`), `data/enemies/10_jardineiro_vazio.tres` |
| Estrutura da expedição (mundo, sistemas, HUD, quais cenas são usadas) | `scenes/world/run.tscn` |
| HUD, mapa, menus, loja, laboratório, créditos etc. | `scenes/ui/*.tscn` |
| Cores, botões, painéis, fontes da interface | `ui/game_theme.tres` (Theme; veja as "Type Variations") |
| Cena inicial e cenas de cada tela | `scenes/main/main.tscn` |

**Visual:** como o projeto não usa imagens de terceiros, o desenho de personagens e do mundo ainda é feito por
`_draw()` (formas simples). Para usar sprites: adicione um `Sprite2D`/`AnimatedSprite2D` à cena da entidade e
desmarque **Draw Placeholder** no Inspector do nó raiz.

**Como o cenário funciona:** os nós do mapa se registram sozinhos ao iniciar a expedição; `world_layout.gd` não
guarda mais dados de nível (só o tamanho do mundo, 3600×2600, que deve combinar com os limites da câmera em
`player.tscn` e com as bordas em `world_map.tscn`). Nas **ruínas** (`Interactable` tipo *poi*) você define o registro
e a recompensa única de Núcleo no Inspector; nos **ninhos** (instâncias de `enemy.tscn` com *Preset Data*) você
escolhe o `.tres`; quantos ninhos abrem a barreira é `Nests Required` em `run.tscn`. Os objetos do cenário usam
`@tool`, então aparecem desenhados no editor.

Só é criado por código o que nasce **durante** o jogo: inimigos comuns e chefe, projéteis, efeitos, coletáveis
dropados, zonas de esporo, golpes do chefe, isca e as janelas/menus que abrem sob demanda — sempre a partir
das cenas configuradas em `run.tscn`.

## Exportar para Web / itch.io
*Project → Export → Add… → Web*, instale os templates de exportação 4.7.x, exporte como `index.html`,
compacte tudo em um `.zip` e envie ao itch.io marcando "This file will be played in the browser".

## Teste automatizado
`godot --headless --path . --import   # só na primeira vez (importa o PNG do terreno)
godot --headless --path . -s res://tools/smoke_test.gd`
Carrega e instancia **todas** as cenas e `.tres`, e exercita mundo, oxigênio, inimigos, chefe, mutações, loja, menus e
salvamento (faz backup/restauração do seu save). Qualquer erro aparece no console.

`godot --headless --path . -s res://tools/smoke_garden.gd` testa o Santuário do Último Jardim (mecanismos, chefe, vitória).

`python3 tools/validate_scenes.py` (opcional, fora do Godot) confere referências, nomes únicos `%Nome`, variações
de tema e propriedades das cenas/`.tres`.

## Estrutura
`scenes/` (entities, world, ui, main) · `data/` (.tres) · `ui/` (tema) · `scripts/core` (autoloads, main, config) · `scripts/data` (classes Resource) · `scripts/player` · `scripts/enemies` ·
`scripts/combat` · `scripts/progression` · `scripts/economy` · `scripts/oxygen` · `scripts/world` · `scripts/ui`.
