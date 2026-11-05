# PROGRESSO — Última Semente

## Controle (gamepad) — ligações completas
Mover: analógico esquerdo / D-pad · **Mirar: analógico direito (novo)** · A ou **RT** Pulso de Raízes · RB ou **R3** Ruptura · Y ou **LT** Nuvem de Esporos · X Pulso de Emergência · B interagir (segurar para extrair) · Back mapa · Start pausa.
- Novas ações `aim_left/right/up/down` (eixos 2 e 3) no Input Map; `player.gd` usa o analógico direito para a direção do Kael/arma.
- Textos do HUD, tela de preparação, mapa e prompts mostram os botões do controle (A, RB, Y, X, B, Back, Start) quando o último dispositivo usado foi o controle (`GameManager.using_pad`, `key_text`, `pause_text`). A tela de remapeamento continua mostrando o teclado.
- `smoke_test.gd` confere que todas as 15 ações têm evento de controle.
- Falta: remapear botões do controle na tela de configurações. NÃO testado com controle real.

## Correção: profundidade e rotação do Kael (pós-F8a)
**Causa:** a folha `player_sheet` já tinha frente/costas/perfil (`idle_down`, `walk_up`, `dash_side`...), mas o `player.gd` ainda pedia `idle/walk/hurt/dash`, que não existem; nenhuma animação tocava e o Kael nunca virava.
**Feito**
- `player.gd`: vista escolhida pela mira (com histerese): frente/costas/perfil (espelhado para a esquerda); animações `idle|walk|hurt|dash` + `_down|_up|_side`. Sem alvo e com o mouse parado, o Kael olha para onde anda (toque/gamepad). Nova arma (`Weapon`, `weapon.png`) que gira de verdade para a mira e passa atrás do corpo quando ele está de costas.
- `player.tscn`: nó `Weapon`, `autoplay = idle_down`, sombra com `z_index = -1`.
- Profundidade (Y-sort): `Run._setup_depth()` ordena Kael, inimigos, árvores/cristais/pilares, caches, ruínas/terminais, ninhos e biomassa pelo Y (quem está ao sul aparece na frente). Chão, regiões, zonas, estações, arena, muralhas e sombras ficam embaixo; projéteis, efeitos e setas em cima. A nave fica no chão. Vale para Floresta, Jardim e Coração.
- Corpo morto dos inimigos entra na mesma ordenação (`enemy.gd`).
- `smoke_test.gd`: 3 checagens novas (animações direcionais, arma, Y-sort).
**Assets conferidos:** 480 referências `res://` (1 falso positivo de texto), tamanhos de PNG coerentes com os `.tres`.
**NÃO testado na Godot.** Ajustes finos prováveis: `FOOT` em `obstacle.gd` e a posição do pé (sombra em y=12 no Kael) para o ponto de troca de frente/atrás; posição/offset da arma.


## Refatoração (docs/PROMPT_REFATORACAO_COMPLETA.md)

### F0 — Base e empacotamento: CONCLUÍDA (estática)
**Implementado**
- `project.godot`: seção `[input]` com as 10 ações (`move_*`, `skill_1`, `skill_2`, `use_pulse`, `interact`, `map`, `pause`) e `[layer_names]` das camadas de física 2D (1 mundo, 2 jogador, 3 inimigo, 4 projetil_jogador, 5 projetil_inimigo, 6 coletavel, 7 interativo, 8 zona).
- `game_manager.gd`: removido o dicionário `ACTIONS`; as teclas padrão são lidas do Input Map no `_ready` (`_read_defaults`). O remapeamento continua igual, mas agora salva **só as diferenças** (entradas iguais ao padrão são descartadas).
- `tools/validate_scenes.py`: novas checagens (ações do Input Map, nomes das camadas, autoloads, arquivos obrigatórios, ausência de `.godot/`).
- Checklist de empacotamento verificado: `ui/game_theme.tres`, `assets/world/*.png`, `icon.svg`, `.gitignore` presentes; sem `.godot/`.

**Testado:** `validate_scenes.py` no zip extraído em pasta limpa (45 cenas, 0 problemas).
**NÃO testado (Godot não roda aqui):** abertura no editor, `--import`, `smoke_test.gd`, `smoke_garden.gd`, remapeamento em jogo.
**Observação:** as camadas só foram *nomeadas*; os valores de `collision_layer/mask` das entidades (hoje 1/2/4) seguem iguais e já batem com os nomes (1 mundo, 2 jogador, 3 inimigo). Projéteis/zonas ganham suas camadas nas fases F3–F5.

**Para testar no editor:** abrir o projeto; conferir em Projeto > Configurações > Mapa de Entrada as 10 ações; em Camadas, os 8 nomes; rodar o jogo e remapear uma tecla em Configurações > Controles; rodar os dois smoke tests e colar o console aqui.

**Próxima fase:** F1 — pipeline de arte/áudio (`tools/gen_art.py`, `gen_audio.py`, `palette.json`, preview das folhas).

### F1 — Pipeline de arte e áudio: CONCLUÍDA (gerada e inspecionada; não importada na Godot)
**Implementado**
- `tools/palette.json` (paleta central), `tools/gen_art.py` (determinístico, Pillow+numpy), `tools/gen_audio.py` (numpy).
- 69 PNGs em `assets/art/{player,enemies,fx,world,ui}` seguindo a lista da seção 4 do prompt: Kael, espinhos de mutação, companheiro, 8 inimigos, Anomalia + auras (4 modificadores), Ninho, Guardião, Jardineiro, projéteis, anel/faíscas/explosão/escudo/telégrafo/isca/esporos, coletáveis, árvores/cristais/pilares, estação, terminal, nave, ruína, mecanismo, portão, arena, névoa contaminada, decoração, 4 tilesets (grade 4×5 de tiles 32 px: chão, trilha, pedra, contaminado, muralha), painéis 9-patch, botões, barras, vinhetas, ícones (12), logo, fundo do menu (3 camadas), setas e marcadores de mapa.
- `assets/art/manifest.json`: tamanho de frame e animações (linha, nº de frames, fps, loop) de cada sheet; base para montar os `SpriteFrames` (F4/F5).
- `tools/preview_sheets.png`: contact sheet de tudo.
- 25 SFX (os 20 originais + `step`, `gate_open`, `mechanism`, `shield`, `heal`) e 2 músicas em `assets/audio/{sfx,music}` (loops de 8 s, 8 kHz).
- Para trocar arte/áudio: substitua o arquivo mantendo nome, tamanho de frame e layout (uma animação por linha).

**Limitações assumidas (honestas)**
- Arte procedural: coerente e funcional, não arte de estúdio. Nada ainda usa esses arquivos: as cenas continuam com `_draw()` até F3–F6.
- Jogador só tem a vista lateral (direita; espelhar com `flip_h`). Cima/baixo ficam para depois, se você quiser.
- Os tilesets são grades de tiles; os *terrain sets* (autotile) e o `bake_tilemap.gd` entram na F3.
- Logo precisa de fonte TTF no sistema que gera (DejaVu/Liberation); sem ela sai sem acento.
- Música: arquivos .wav ainda sem marcação de loop; configurar na importação/F7.

**Para testar:** `python3 tools/gen_art.py && python3 tools/gen_audio.py`; abrir `tools/preview_sheets.png`; abrir o projeto na Godot e deixar importar (conferir que os PNGs ficam nítidos, filtro nearest).
**Próxima fase:** F3 — mundo (TileMap, props, estações, zonas, portão, arena, interativos e coletáveis como cenas), conforme a ordem de prioridade do prompt (F0 → F1 → F3 → F4 → F5 → F6 → F2 → F7 → F8 → F9).

### F3 — Mundo com a arte nova: IMPLEMENTADA (não executada na Godot)
**Feito**
- `tools/build_spriteframes.py` → 28 `SpriteFrames` em `assets/art/frames/` (a partir do manifest); `tools/build_tileset.py` → `assets/art/world/ground_tileset.tres` (4 fontes: floresta, bacia, santuário, jardim).
- Novo `scripts/world/ground_painter.gd` (nó `Ground`, `TileMapLayer`, nos dois mapas): pinta o chão ao iniciar (bioma por região, pedra por ruído, tile contaminado dentro das zonas hostis) e espalha decoração sem pisar em obstáculos, estações ou zonas hostis. O sprite `Terrain` antigo fica só como guia no editor e é escondido em jogo.
- Árvores, cristais e pilares (variante por posição, escala pelo raio), estações (anel animado), terminal/nave/ruína/mecanismo (`Interactable`, mecanismo troca para "active" ao ativar, ruína escurece depois de lida), portão (fechado → abrindo → aberto), arena do chefe, névoa nas zonas hostis e biomassa/caches agora usam sprites. `draw_placeholder = false` nas cenas; os desenhos de reserva continuam no código (ligue o flag para voltar).
- Dicas visuais mantidas (anel do Sentido Biológico, raio do mecanismo, rótulos das estações e das zonas).
- `smoke_test.gd`: 2 checagens novas (chão pintado, decoração).

**Não testado:** tudo que depende da Godot (importação dos PNGs, tiles aparecendo, escalas/posições dos pés, animação do portão). Prováveis ajustes finos: posição vertical dos sprites (`FOOT` em `obstacle.gd`, `_setup_sprite` em `interactable.gd`), tamanho das árvores, tom da névoa.
**Para testar:** abrir o projeto, deixar importar, `--import`, rodar `smoke_test.gd` e `smoke_garden.gd`, jogar uma expedição e olhar o mapa (tecla M) e o Santuário.
**Limitações:** bordas entre biomas são retas (sem transição); não há trilhas pintadas; paredes (muralhas) ainda usam o ColorRect antigo; ordenação em Y (árvore na frente do jogador) não foi feita.
**Próxima fase:** F4 — Kael e a arma/efeitos com sprites (player, espinhos, companheiro, pulso/ruptura, escudo).

### F4 — Kael, arma e efeitos com sprites: IMPLEMENTADA (não executada na Godot)
**Feito**
- `player.tscn`: nós `Shadow`, `Spines`, `Sprite` (idle/walk/hurt/dash), `ShieldFx`, `Companions`; `player.gd` ganhou `_process` só visual (animação por estado, espelhamento pela mira, pisca na invulnerabilidade, espinhos de mutação por contagem, escudo, companheiros como sprites com animação de ataque, pose de morte). Lógica de jogo (física, dano, habilidades) intocada.
- Projéteis (espinho / cuspe / estilhaço, rotacionados, veneno em verde-amarelo), anéis e faíscas (`Fx` com sprites tingidos pela cor pedida), isca, zona de esporos (escala pelo raio, some no fim) e telégrafo do golpe do Guardião (círculo + preenchimento crescente) usam a arte nova. O texto flutuante continua desenhado.
- `draw_placeholder = false` nas cenas; os desenhos antigos seguem no código como reserva.
- `smoke_test.gd`: checagem "Kael com sprite".

**Não testado (precisa da Godot):** alinhamento do pé do Kael com a colisão, tamanho dos projéteis, aparência dos anéis (textura branca tingida), `animation_finished` do companheiro.
**Limitações:** só vista lateral (espelhada); a arma é parte do desenho do Kael, então a mira vertical não gira o braço; sem animação de ruptura além do esticar do frame.
**Próxima fase:** F5 — inimigos e chefes com sprites (larva, cortarraiz, flor, casca, esporídeo, parasita, Anomalia + auras, Ninho, Guardião, Jardineiro).

### F5 — Inimigos e chefes com sprites: IMPLEMENTADA (não executada na Godot)
**Feito**
- `EnemyData.frames` (novo `@export SpriteFrames`) nos 10 `.tres` de `data/enemies/` (larva, cortarraiz, flor, casca, esporídeo, parasita, Anomalia, Ninho, Guardião, Jardineiro). `enemy.tscn` ganhou `Shadow`, `Sprite` e `Aura`; Guardião e Jardineiro herdam.
- `enemy.gd`: `_apply_frames()` (escala pelo raio, pé alinhado), `_process` só visual (anda/parado/investida do Cortarraiz por `mode`/hurt, espelha para o jogador, tingimento por dano, buff do Parasita, raiz e veneno), `play_event()` para tiro, esporos, pulso, invocação do Ninho, golpe e invocação do Guardião, fase 2, tiros e raízes do Jardineiro (`_base_anim` do Jardineiro alterna blindado/exposto) e `_spawn_death_visual()` (a animação de morte toca numa cópia visual, porque o inimigo some na hora). A Anomalia mostra a aura do modificador.
- Barras de vida, rótulo/anel de elite, status e textos da Consciência da Rede continuam desenhados; só o corpo foi trocado (`draw_placeholder = false`, reserva mantida).
- `smoke_test.gd`: confere que os ninhos têm sprite.

**Não testado (precisa da Godot):** escala/pé de cada criatura (regra: raio / (0,3 × largura do frame)), brilho de dano (modulate > 1 pode clampar no renderer Compatibility), duração das animações de evento, nitidez do Guardião (96 px) em escala 1,18.
**Limitações:** só vista lateral/espelho; sem animação de "andar" para Flor e Ninho (ficam em idle); a morte não herda o brilho de dano.
**Próxima fase:** F6 — interface: HUD, menus, loja, laboratório, mapa, pausa com painéis/botões/ícones/barras/vinhetas novos e fundo do menu em camadas. Depois F2, F7, F8, F9.

### F9 (parcial, sem Godot) — QA e Web
- `docs/QA_CHECKLIST.md` (testes manuais por área), `export_presets.cfg` (preset Web sem threads), README atualizado, `tools/run_checks.py` (validate_scenes + lint_gd + lint_syntax) e `tools/lint_syntax.py` (checagem estrutural via parser do Python; falso positivo conhecido: lambda com atribuição em `pause_menu.gd`).
- **Pendente:** executar tudo na Godot, medir FPS/memória no navegador, ajustar balanceamento com base nos testes.

### Erros de carga reportados (ShopManager / ShopMenu / BiomassPickup)
- Reconstruído `shop_manager.gd` (duplicata de `buy_item`); trocadas lambdas de várias linhas/com argumentos extras por métodos nomeados (`audio_manager.gd`, `player.gd`, `game_data.gd`, `main_menu_screen.gd`) para eliminar qualquer dúvida de sintaxe.
- `lint_gd.py` e `validate_scenes.py` passam, mas só a Godot confirma. Novo `tools/check_scripts.py` roda a Godot (`--check-only`) em cada script e imprime o erro com arquivo e linha.
- Se persistir: fechar a Godot, apagar a pasta `.godot/` do projeto (cache de classes) e abrir de novo; depois enviar as linhas completas do painel Saída (formato `res://...gd:LINHA - Parse Error: ...`).

### Correção F8a (erro "Could not parse global class ShopManager")
- Causa: ao migrar a loja para dados (F2) um `index()` pegou a ocorrência errada e deixou `buy_item` duplicado em `shop_manager.gd`. Corrigido (arquivo reconstruído e revisado).
- Novo `tools/lint_gd.py` (funções/variáveis duplicadas, parênteses, indentação, blocos vazios) para pegar esse tipo de falha antes da Godot; todos os `.gd` passam. Rode `python3 tools/lint_gd.py` junto com `validate_scenes.py`.

### F8 (parte 2) — Coração de Nymara: IMPLEMENTADA (não executada na Godot)
**Fluxo novo da campanha:** Guardião → Santuário do Último Jardim → **Coração de Nymara (final)**. Vencer o Jardineiro agora mostra a tela de fase concluída ("Descer ao Coração de Nymara") em vez de encerrar a campanha; a vitória final (epílogo + "PARABÉNS" + créditos) vem depois do Coração. Saves antigos com a campanha já concluída também liberam o Coração.
**Feito**
- Fase `heart_run.tscn` + `heart_map.tscn` (mapa gerado: Câmara de Acesso com estação, terminal e nave; 2 ecos de Nymara com registros novos `reg_coracao_a/b` e 1 Núcleo descoberto; ~56 obstáculos; 9 caches; arena central; barreira já aberta via novo `RootGate.start_open`). Perfil de ondas `data/waves/03_coracao.tres`.
- Chefe `HeartBoss` (`scripts/enemies/heart_boss.gd`, 2600 de vida, recompensa 3–5 Núcleos via novos `EnemyData.nucleos_min/max`): **Etapa 1 Defesa** (raízes + invocações, vulnerável até 66%); **Etapa 2 Exposição** (núcleo protegido, 4 `estrutura_raiz` ao redor que lançam raízes telegrafadas; "Estruturas restantes: N"); **Etapa 3 Decisão** (núcleo exposto com raízes, invocações e anel de projéteis; aos 12% a Rede se rende, os inimigos somem e abre a escolha). Nunca morre antes da decisão (`die()` bloqueado, veneno/DoT respeitam as etapas).
- Escolha final (`DecisionScreen`): **Plantar a Última Semente (restaurar Nymara)** ou **Entregar a Semente à Rede Raiz (coexistir)**; o epílogo muda pela escolha e pelos registros lidos (≥ 8); `last_ending` salvo. HUD mostra objetivo por etapa e "Fase N" na barra do chefe.
- Arte nova (`coracao.png`, `estrutura.png`), `EnemyData` novos (`11_coracao_rede`, `12_estrutura_raiz`), comportamento `estrutura` no `enemy.gd`, botão "Coração de Nymara" no menu (aparece ao liberar), `tools/smoke_heart.gd` (3 etapas + decisão + fim).
**Não testado na Godot:** toda a fase. Prováveis ajustes: dificuldade (vida 2600, ondas, volumes de raízes), posição/escala do sprite do Coração (128 px), estruturas posicionadas por `is_free_spot`, legibilidade da tela de decisão, tempo do smoke (`smoke_heart.gd` espera até 4000 quadros).
**Ainda falta do GDD:** sinergia "Micélio + Adaptabilidade" (sem mutação equivalente), remapeamento de botões do gamepad, "Revisitar o mundo" (pós-jogo, fora do MVP).
**Próximo:** testar tudo (`docs/QA_CHECKLIST.md`), balancear com os números reais e fechar F9 (exportação Web e medições).

### F8 (parte 1) — Nuvem de Esporos, Dardo, sinergia e gamepad: IMPLEMENTADA (não executada na Godot)
**Feito**
- **Nuvem de Esporos** (tecla **F**, gamepad **Y**): mutação temporária "Nuvem de Esporos" (Ressonância, 3 níveis, +25% de área por nível). Nuvem de 6 s que **retarda (−35%) e enfraquece (+25% de dano recebido)** os inimigos dentro; recarga 14 s (afetada por `skill_cd_mult`); até 4 ativas. Evolução **Nuvem em Cadeia** (precisa da Nuvem + Ressonância Profunda + 3 melhorias de Ressonância): inimigo enfraquecido que morre cria uma nuvem menor (40% de chance). Números em `data/abilities/01_nuvem_esporos.tres`. HUD mostra o botão só depois de escolher a mutação.
- **Dardo de Fotossíntese**: mutação temporária (Predação, 3 níveis, +25% de dano por nível) que liga uma segunda arma automática rápida (0,38 s, alcance 420). Marca o alvo (losango amarelo, 4 s); dardos seguintes causam +60% nele. Dados em `data/weapons/dardo_fotossintese.tres` (`WeaponData` ganhou `bonus_marcado`, `duracao_marca`, `escala_por_nivel`).
- **Sinergia Pulso de Raízes + Nuvem de Esporos** (GDD 6.3): com a Nuvem, o Pulso deixa os atingidos vulneráveis por 5 s. A sinergia Ruptura + Casca Regenerativa já existia; Espinho + Cadência/Núcleo Perfurante funcionam pelos atributos.
- **Gamepad**: Input Map com analógico esquerdo/D-pad (mover), A pulso, RB ruptura, X emergência, Y nuvem, B interagir (segurar para extrair), Back mapa, Start pausa; mira segue a direção do movimento quando o último dispositivo é o gamepad (volta ao mouse ao mexer o mouse); botões das telas ganham foco por D-pad quando há controle conectado (cartas de mutação já focam a primeira). O remapeamento de teclas preserva os eventos de gamepad.
- `StatRules` +2 atributos (`cloud_power`, `dart_level`); `UpgradeData.requer_upgrade`; `smoke_test.gd` usa a Nuvem e confere os dados novos.
**Não testado na Godot:** tudo acima; sobretudo o foco por gamepad nos menus, o equilíbrio (Nuvem +25% de dano em chefes, Dardo) e a sobreposição de 5 caixas de habilidade no HUD.
**Ainda falta do F8:** Coração de Nymara (chefe final em 3 etapas + escolha do final), a sinergia "Micélio + Adaptabilidade" (não há mutação "Adaptabilidade" no jogo), remapeamento de botões do gamepad na tela de configurações.
**Próximo passo sugerido:** F8 parte 2 — Coração de Nymara (nova fase/arena, chefe de 3 etapas, decisão final e epílogo) — ou F9 (QA/Web/README) se preferir fechar a versão atual antes.

### F7 — Áudio e integração: IMPLEMENTADA (não executada na Godot)
**Feito**
- Novos recursos `SfxEntry`/`SfxBank` e `MusicSet`; `data/audio/sfx_bank.tres` (25 sons: stream, volume, tom e intervalo mínimo por som) e `data/audio/music_set.tres` (trilhas, volumes, queda da trilha calma, abafar na pausa, entrada gradual, velocidade do crossfade). Gerados por `tools/build_audio_bank.py`.
- `AudioManager` enxuto (de ~250 para ~150 linhas): sem geração procedural, lê o banco/música; pool de 12 players; crossfade explorar↔combate; entrada gradual; música abaixa 9 dB na pausa; silencia o Master quando a janela/aba perde o foco e restaura ao voltar; trilhas recomeçam sozinhas se o loop falhar. API igual (`play_sfx`, `start_music`, `stop_music`, `set_combat_intensity`, `apply_volumes`, nova `has_sfx`).
- Músicas com marcador de loop dentro do WAV (chunk `smpl`, "Detect From WAV" da Godot); `default_bus_layout.tres` com Music e SFX.
- Sons que estavam só no banco agora tocam: `gate_open` (barreira abre), `mechanism` (mecanismo ativado), `shield` (Escudo de Campo recarrega), `heal` (Dose de Biomassa). `step` está no banco mas não é usado (evitei repetição chata).
- `smoke_test.gd`: confere o banco de sons.
**Não testado na Godot:** importação dos WAV (loop pelo `smpl`), crossfade, silêncio ao perder o foco no navegador, desbloqueio de áudio no Web (precisa de clique/tecla antes do primeiro som).
**Limitações:** entidades ainda não têm `AudioStreamPlayer2D` próprios (sons são globais, sem posição); sem remapeamento de volumes por categoria além de Música/SFX.
**Próxima fase:** F8 — conteúdo pendente do GDD (Coração de Nymara com 3 etapas e decisão, Nuvem de Esporos, Dardo de Fotossíntese, sinergias, gamepad). É a maior; posso começar por Nuvem de Esporos + gamepad + sinergias e deixar o chefe final para o passo seguinte.

### F2 — Recursos de dados: IMPLEMENTADA (não executada na Godot)
**Feito** (os valores foram extraídos do código real: o comportamento padrão não muda)
- Novas classes `Resource`: `WaveProfile` + `WaveStage`, `ThreatEventData`, `EliteModifier`, `BuffData`, `StatRules`; `ShopItemData` ganhou o efeito do item (`tipo`, `valor`, `valor_max`, `buff_id`, `mods_add/mul`, `sempre_oferecido`).
- Novos `.tres`: `data/waves/` (floresta e jardim: 6 etapas com pesos, lote, máx. de elites, tetos, intervalos, escala de vida, distâncias, pressão com chefe, elites), `data/events/` (2 enxames + crise), `data/elites/` (4 modificadores), `data/buffs/` (6, com nome no HUD e duração), `data/rules/stat_rules.tres` (base de vida/velocidade/O2, 29 atributos-base e 29 limites). Os 9 itens da loja têm o efeito em dados (a Mira passou a ser `mods_mul` do item).
- Constantes removidas do código: `SpawnDirector` (CAP, RAMP, HARD_CAP, MIN/MAX_DIST, pesos, etapas, elites), `WorldEvents` (horários, durações, recompensas), `RunState` (`BASE_*`, `STAT_LIMITS`, `BUFF_DEFS`), `Enemy.setup` (modificadores de elite) e explosão da Anomalia em `Run`, nomes de buffs do HUD, durações de buffs na loja/jogador, `match` de itens em `ShopManager` (agora por `tipo`).
- Escolha do perfil por fase: `SpawnDirector.profile_id` ("floresta" por padrão; `garden_run.tscn` usa "jardim"). `stage_name` virou `director.stage_name_at(t)`.
- `smoke_test.gd`: 5 checagens novas; `validate_scenes.py` agora entende `sub_resource` em `.tres` e exige `stat_rules.tres`/perfil.
**Não feito de propósito:** `SfxBank` entra na F7 (áudio); `PlayerStats` foi fundido no `StatRules`; vida/dano/limites dos chefes continuam nos `.tres` dos inimigos e `gardener.gd` (constantes de ciclo do Jardineiro ainda no script).
**Não testado na Godot:** carregamento dos `.tres` com sub-recursos, arrays/dicionários no Inspector, o `sort_custom` dos eventos, equivalência numérica (deve ser idêntica).
**Para testar:** abrir `data/waves/01_floresta.tres` e `data/rules/stat_rules.tres` no Inspector; rodar os smoke tests; jogar e conferir etapas no HUD, eventos aos 9/14/17 min e a loja (todos os 9 itens).
**Próxima fase:** F7 — áudio: `SfxBank`/`MusicSet`, `AudioManager` enxuto com crossfade, loop dos .wav, foco da janela.

### Ajustes pós-teste do usuário (F6.1)
- HUD: o ícone de Emergência cobria o "R"; agora o texto das 4 habilidades é alinhado à direita, o ícone fica centralizado à esquerda e as caixas ficaram mais largas (148/156 px).
- Dificuldade do Santuário do Último Jardim (inimigos continuam durante o chefe): Jardineiro com 1300 de vida (era 1500), tiros 10 e raízes 20 de dano (eram 12/24), janelas de exposição maiores (7 s e 5,5 s), blindagem 6 s, tiros menos frequentes, leque da fase 2 com 4 tiros, 4/6 raízes, invocação a cada 20 s; ondas dos mecanismos com 2 criaturas (eram 3). Em qualquer chefe, o limite de inimigos comuns caiu de 50% para 40% e o intervalo de surgimento ficou 30% maior.
- Projéteis (do jogador e dos inimigos) agora param nas muralhas e na barreira fechada (`WorldMap.is_inside_wall`), com uma faísca; árvores/cristais/pilares continuam não bloqueando tiros.
- Menu principal: botões menores (250×38), alinhados à esquerda, que crescem 18% ao serem selecionados (mouse por cima ou teclado: setas/Tab, Enter); "Nova Expedição" já começa selecionado.
**Não testado na Godot.** Se ainda estiver difícil, os números estão em `gardener.gd` (constantes no topo), `10_jardineiro_vazio.tres` e `garden_objectives.gd` (Inspector).

### F6 — Interface com a arte nova: IMPLEMENTADA (não executada na Godot)
**Feito**
- `ui/game_theme.tres`: painéis (modal, carta, carta de evolução, carta adquirida, detalhe, HUD, chefe, habilidade), botões (4 estados) e barras (fundo + HP/O2/XP/chefe) agora são `StyleBoxTexture` dos PNGs de `assets/art/ui/` (9-patch, margem 8; barras margem 0/2). O foco do botão continua o contorno dourado (StyleBoxFlat). Todas as telas herdam o novo visual sem mudar de cena.
- `hud.tscn`: vinhetas de oxigênio e de dano viram PNGs; ícones (arma, pulso, ruptura, emergência) ao lado do texto das habilidades (caixas mais largas: 132/140 px).
- Menu principal: fundo em 3 camadas (`BgFar/BgMid/BgNear`, atrás do desenho de esporos animados) e logo em PNG; `draw_backdrop = false` (o desenho procedural continua como reserva).

**Não testado (precisa da Godot):** legibilidade do texto sobre os painéis texturizados, cantos 9-patch, posição dos ícones no HUD (podem encostar no texto), logo (a fonte do logo depende do TTF do sistema que gerou), nitidez em escala.
**Limitações:** mapa (M), loja, laboratório, codex e tela de vitória usam o tema novo mas não ganharam ícones próprios; fonte do jogo segue a padrão da Godot; sem transições de tela.
**Próxima fase (ordem do prompt):** F2 — conteúdo/dificuldade (balanceamento em Resources, eventos); depois F7 (áudio na Godot: loops, barramentos, importação), F8, F9.

---

## Histórico anterior

> Revisão estática (a Godot não pôde ser executada no ambiente de edição). Só o `validate_scenes.py` rodou (45 cenas, 0 problemas).
> Após aplicar os lotes, rode: `godot --headless --path . --import` (importa o novo terreno) e depois
> `godot --headless --path . -s res://tools/smoke_test.gd` e `... -s res://tools/smoke_garden.gd`.

## Feito
- Base: loop completo, mapa em cena, oxigênio, 6 inimigos + elite + ninhos + Guardião, loja, 15 melhorias + 3 evoluções, 15 mutações permanentes, save validado.
- Lote 1 (robustez): backup de save só se íntegro, gravação agrupada de configurações, bestiário salvo na hora, elite sem retry por quadro, evento interrompido quando o chefe desperta.
- Lote 2 (GDD 5.2): remapeamento de teclas (Configurações > Controles) e textos de controle dinâmicos.
- Lote 3 (GDD 14.1): **Santuário do Último Jardim**.
  - Fluxo: Guardião derrotado → tela "Guardião derrotado" (`LevelCompleteScreen`) → entrar no Jardim ou menu. O menu ganha o botão "Santuário do Último Jardim" (`garden_unlocked` no save). "Nova expedição" na morte reinicia o mesmo nível.
  - Missão dedicada com estado novo (só mutações permanentes), 2 terminais de loja, 2 bolsões de ar, 2 zonas contaminadas, 3 registros (um com Núcleo), 14 caches, 112 obstáculos.
  - `GardenObjectives`: 3 mecanismos (30 s cada, ondas crescentes, só avança perto do mecanismo); ao concluir abre a passagem.
  - `Gardener` (Jardineiro Vazio): blindado por padrão, janelas de vulnerabilidade (5,5 s / 4 s na fase 2), leque de disparos, raízes telegrafadas em linha, invocações na fase 2; veneno também respeita a blindagem.
  - `Run` parametrizado (`level_id`, `boss_id`, `starting_record`, `intro_text`, `objective_text()`); `SpawnDirector` com `time_offset`/`first_elite_time`; `WorldEvents.enabled`.
  - Epílogo/vitória agora ocorrem após o Jardineiro Vazio (provisório: `campaign_completed`).
  - Testes: `tools/smoke_garden.gd` (novo) e ajustes em `smoke_test.gd`.

## Em andamento
- Nada pela metade.

## Falta (GDD)
1. Coração de Nymara (3 etapas + decisão) e escolha de final; mover o `campaign_completed` para ele.
2. Nuvem de Esporos e Dardo de Fotossíntese; sinergias extras.
3. Gamepad; localização.
4. Arte/áudio reais (hoje tudo é `_draw()` e áudio procedural); terreno do Jardim é gerado por script (substituível).
5. Balanceamento por teste real (vida do Jardineiro 1500, ondas, dificuldade inicial `time_offset = 600`).

## Próximo passo
Coração de Nymara: nível final com chefe em 3 etapas (defesa, exposição, decisão) reaproveitando `Run`/`GardenObjectives`/`Gardener`, e fechar a campanha lá.

## Problemas conhecidos / riscos
- Nada foi executado na Godot; testes automatizados novos não foram rodados.
- Eventos e ondas de mecanismo criam inimigos acima do teto normal (limite duro 70); medir FPS no navegador.
- Jardineiro e ondas sem playtest: valores são palpites iniciais.
- O arquivo `.import` do `garden_terrain.png` será criado pela Godot na primeira abertura.
- `smoke_test` não restaura o `.bak` do seu save.
- Em layouts não QWERTY o nome de tecla exibido pode divergir.
