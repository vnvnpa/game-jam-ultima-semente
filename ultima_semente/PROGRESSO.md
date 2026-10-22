# PROGRESSO — Última Semente

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
