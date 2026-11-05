# QA — Última Semente (checklist de testes manuais)

Marque cada item ao testar. Tudo aqui exige abrir o projeto na Godot 4.7.x; as checagens estáticas
(`python3 tools/run_checks.py`) não substituem estes testes.

## 0. Antes de jogar
- [ ] Apagar `.godot/`, abrir o projeto, aguardar a importação; painel **Saída** sem erros vermelhos.
- [ ] `godot --headless --path . --import` e depois `-s res://tools/smoke_test.gd` e `-s res://tools/smoke_garden.gd` terminam com "Falhas: 0".
- [ ] `python3 tools/check_scripts.py <caminho da Godot>` sem scripts com erro.

## 1. Expedição (Floresta / Bacia / Santuário das Raízes)
- [ ] Menu → Nova Expedição; Kael anda, mira com o mouse, a arma dispara sozinha.
- [ ] Primeira mutação em até ~2 min; cartas legíveis; teclas 1/2/3 e clique funcionam.
- [ ] Espaço (Pulso), Q (Ruptura), R (Emergência, comprado), F (Nuvem, depois de escolher a mutação).
- [ ] Oxigênio só cai nas zonas magenta; recarrega nas estações; alertas e vinheta aparecem.
- [ ] Loja: os 9 itens + 6 equipamentos; recusas ("vida cheia", limite por visita) funcionam.
- [ ] Ninhos: 2 destruídos abrem a barreira; tiros não atravessam muralhas nem a barreira fechada.
- [ ] Guardião de Raízes: golpes telegrafados, invocações, fase 2; inimigos comuns continuam aparecendo (menos).
- [ ] Morte, extração (a partir de 10:00) e vitória mostram as telas corretas; Núcleos creditados uma vez.

## 2. Santuário do Último Jardim
- [ ] Mecanismos ativam (som + animação), ondas de 2 criaturas, Jardineiro alterna blindado/exposto.

## 2b. Coração de Nymara (final)
- [ ] Concluir o Jardim mostra "JARDINEIRO DESATIVADO" e leva ao Coração; botão aparece no menu depois.
- [ ] Câmara de Acesso (estação, terminal, nave); ecos de Nymara dão registros; Núcleo do primeiro eco só uma vez.
- [ ] Etapa 1: raízes telegrafadas e invocações; aos 66% o núcleo se protege ("Protegido") e surgem 4 estruturas.
- [ ] Etapa 2: destruir as estruturas (contador no HUD); etapa 3: anel de projéteis; aos 12% a tela de decisão.
- [ ] Os dois finais mostram epílogos diferentes; "PARABÉNS" e créditos funcionam; morrer reinicia o Coração.
- [ ] `godot --headless --path . -s res://tools/smoke_heart.gd` termina com "Falhas: 0".

## 3. Interface e acessibilidade
- [ ] Menu: botões pequenos à esquerda crescem ao selecionar (mouse e teclado).
- [ ] HUD: ícones não cobrem o texto; caixa da Nuvem só aparece após a mutação.
- [ ] Configurações: volumes independentes, reduzir efeitos, números de dano, remapear teclas.
- [ ] Laboratório: comprar/reverter mutação com confirmação e antes/depois.

## 4. Gamepad
- [ ] Mover (analógico/D-pad), A/RB/X/Y/B/Back/Start; menus navegáveis com D-pad + A; cartas de mutação focam a primeira.

## 5. Áudio
- [ ] Crossfade explorar↔combate; música abaixa na pausa; silêncio ao perder o foco da janela/aba.
- [ ] No navegador: o som só começa após o primeiro clique/tecla (esperado).

## 6. Web (itch.io)
- [ ] Exportar com o preset **Web** (templates 4.7.x instalados), sem threads; testar em Chrome e Firefox.
- [ ] Salvamento persiste ao recarregar a página; pausa automática ao trocar de aba.
- [ ] 60 FPS no fim da expedição (inimigos ≤ 70); anotar FPS e memória.

## Problemas encontrados
(anote aqui: o que, onde, como reproduzir)
