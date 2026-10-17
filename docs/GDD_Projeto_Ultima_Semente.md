# PROJETO: ÚLTIMA SEMENTE

## Game Design Document (GDD) --- Versão 1.2 — especificação consolidada

**Data:** Outubro de 2026\
**Status:** Especificação de design consolidada para orientar a implementação. Nenhum sistema descrito deve ser considerado implementado. As decisões de design estão fechadas para a primeira versão; valores numéricos continuam sujeitos a testes de balanceamento.

------------------------------------------------------------------------

## 1. Resumo executivo

**Projeto: Última Semente** é um jogo 2D top-down de ação,
sobrevivência, exploração e evolução biológica. O jogador controla um
explorador preso no planeta alienígena Nymara, onde uma rede de vida
descontrolada transformou a fauna, a flora e as antigas instalações
científicas em ameaças.

Durante expedições de aproximadamente 20--30 minutos, o jogador explora
um mapa conectado, enfrenta ondas de criaturas que surgem em áreas
próximas, ganha experiência, coleta Biomassa, compra melhorias e
incorpora mutações. Chefes e descobertas importantes concedem Núcleos
Primordiais, usados para desbloquear progressão permanente.

A principal identidade do jogo é a **adaptação com consequências**: as
mutações podem tornar o protagonista mais forte, mas algumas também
impõem efeitos colaterais. O jogador não constrói simplesmente o
personagem mais forte em todos os atributos; constrói o organismo mais
adequado ao seu estilo de jogo.

  -----------------------------------------------------------------------
  Elemento                            Definição
  ----------------------------------- -----------------------------------
  Gênero                              Ação, survivors-like, exploração e
                                      sobrevivência

  Perspectiva                         2D top-down

  Arte                                Pixel art atmosférica

  Plataforma inicial                  Navegador, com publicação no
                                      itch.io

  Modo                                Single-player

  Combate                             Híbrido: armas automáticas e
                                      habilidades manuais

  Estrutura                           Mapa conectado, regiões e eventos

  Duração-alvo                        20--30 minutos por expedição

  Progressão                          Temporária durante a expedição e
                                      permanente entre expedições

  Motor                               Godot 4.x estável; confirmar versão
                                      estável oficial no início da
                                      produção

  Autoria exibida nos créditos        vnvnpa
  -----------------------------------------------------------------------

## 2. Pilares de design

1.  **Exploração recompensadora:** ruínas, recursos, eventos e passagens
    descobertas devem justificar sair da rota mais segura.
2.  **Evolução com identidade:** mutações alteram o estilo de jogo e
    podem apresentar vantagens e desvantagens.
3.  **Combate híbrido:** armas automáticas reduzem a carga de execução;
    habilidades manuais criam decisões táticas.
4.  **Pressão crescente, não injustiça:** a ameaça cresce por tempo,
    ondas, região e eventos, sem aumentar todos os atributos inimigos
    indiscriminadamente.
5.  **Narrativa ambiental:** o jogador entende Nymara por locais,
    criaturas, registros curtos e encontros.
6.  **Escopo sustentável:** construir primeiro um MVP divertido;
    expandir o conteúdo só depois de validar o ciclo principal.

## 3. Universo e história

### 3.1 Nymara

Nymara era um planeta exuberante habitado pelos Arquitetos Verdes, uma
civilização que aprendeu a armazenar informação genética e ecológica em
sementes. Seu maior projeto, a Última Semente, deveria preservar o
modelo biológico de um ecossistema inteiro e permitir a restauração de
mundos devastados.

Durante um experimento, a rede de sementes entrou em contato com uma
inteligência biológica subterrânea. Essa inteligência passou a
interpretar toda vida independente como risco de extinção e começou a
assimilar organismos, máquinas e instalações. O planeta não morreu:
tornou-se um sistema vivo, interconectado e hostil.

Séculos depois, uma nave de exploração cai em Nymara. O único
sobrevivente, nome provisório **Kael**, encontra a Última Semente. Para
chegar ao núcleo da rede e descobrir o que aconteceu, ele precisa
absorver características das criaturas que enfrenta. Cada adaptação
aproxima o protagonista do poder necessário para sobreviver, mas também
pode alterar seu corpo e seu comportamento.

**Pergunta central:** é possível salvar um planeta vivo sem destruir
aquilo em que ele se transformou?

### 3.2 Personagens e forças

-   **Kael (nome provisório):** explorador equipado com traje de
    sobrevivência e um dispositivo de contenção biológica. Começa
    vulnerável e muda visualmente conforme adquire mutações.
-   **Última Semente:** organismo artificial que guarda o modelo
    genético de um ecossistema saudável. Reage a locais e criaturas
    especiais.
-   **Rede Raiz:** inteligência biológica que conecta os organismos de
    Nymara. Não precisa ser puramente maligna; acredita que assimilar
    toda a vida é a única forma de impedir outra catástrofe.
-   **Arquitetos Verdes:** civilização desaparecida, conhecida por meio
    de instalações, registros e equipamentos.

### 3.3 Estrutura narrativa e regiões

  -----------------------------------------------------------------------
  Região                  Função                  Conteúdo principal
  ----------------------- ----------------------- -----------------------
  Floresta do Despertar   Introdução e            Destroços, criaturas
                          sobrevivência           básicas e primeira
                                                  mutação

  Bacia dos Ecos          Revelação da            Pântanos, instalações e
                          civilização             inimigos especializados

  Santuário das Raízes    Acesso à rede           Elites, eventos de
                                                  risco e chefe regional

  Núcleo das Raízes       Encerramento da         Chefe final, decisão e
                          campanha                conclusão
  -----------------------------------------------------------------------

As três primeiras áreas podem compartilhar um mapa conectado. A quarta
região é a etapa final, reservada para o encerramento da campanha. A
produção inicial não precisa criar todas de uma vez.

## 4. Direção visual e áudio

### 4.1 Pixel art

-   Câmera top-down com leitura clara das silhuetas.
-   Tiles de 16×16 px como referência inicial; personagens podem ocupar
    aproximadamente 24--32 px de altura.
-   Vegetação saudável em verdes e turquesas; contaminação em roxos,
    magentas e vermelhos; tecnologia humana em laranja, cinza e branco.
-   Recursos comuns com brilho dourado/esverdeado; Núcleos Primordiais
    em ciano e violeta.
-   Mutações devem alterar gradualmente a silhueta do protagonista.
-   Efeitos de ataque e perigo precisam ser legíveis mesmo com muitas
    entidades na tela.

### 4.2 Áudio

-   Exploração: ambiência eletrônica suave, sons orgânicos e melodias
    espaçadas.
-   Combate: ritmo crescente e camadas de tensão.
-   Chefes: tema mais intenso, com variações por fase.
-   Coleta: sons curtos diferentes para Biomassa e Núcleos.
-   Mutações: sons de crescimento, pulsação e transformação.
-   Interface: confirmações e alertas discretos.

Para o MVP, bastam uma faixa de exploração, uma variação de combate e um
conjunto pequeno de efeitos sonoros.

## 5. Estrutura da expedição

### 5.1 Ciclo principal

1.  Explorar uma região e identificar pontos de interesse.
2.  Enfrentar criaturas que surgem nas proximidades.
3.  Coletar experiência e Biomassa.
4.  Escolher mutações ao subir de nível e comprar melhorias em pontos de
    serviço.
5.  Gerenciar vida, oxigênio e posição.
6.  Completar um evento, descobrir um registro ou derrotar um chefe.
7.  Concluir a expedição ou morrer.
8.  Preservar a progressão permanente e usar Núcleos Primordiais para
    desbloquear mutações.

### 5.2 Controles propostos

  -----------------------------------------------------------------------
  Ação                                Controle inicial
  ----------------------------------- -----------------------------------
  Movimento                           WASD ou setas

  Mirar                               Mouse

  Arma automática                     Ataca o alvo válido conforme a
                                      configuração da arma

  Habilidade ativa principal          Espaço ou botão configurável

  Habilidade secundária               Q

  Interagir                           E

  Mapa                                M

  Pausar                              Esc
  -----------------------------------------------------------------------

Os controles devem poder ser ajustados. O build web precisa lidar
corretamente com perda e retorno de foco da janela.

## 6. Combate híbrido

### 6.1 Categorias de ação

-   **Armas automáticas:** atacam inimigos válidos dentro do alcance.
-   **Habilidades ativas:** poderes acionados pelo jogador e sujeitos a
    recarga.
-   **Efeitos passivos:** mutações que alteram atributos, criam efeitos
    automáticos ou modificam habilidades.
-   **Equipamentos:** traje, módulos ou dispositivos que trocam uma
    vantagem por uma limitação.

O jogo não usará armas aleatórias espalhadas pelo chão como sistema
central. As descobertas no mapa serão principalmente recursos,
instalações, registros e oportunidades de compra. Equipamentos podem ser
encontrados como recompensa de eventos específicos, mas devem ser
apresentados como uma escolha clara, não como loot aleatório constante.

### 6.2 Habilidades iniciais propostas

  ----------------------------------------------------------------------------
  Habilidade        Tipo                  Função             Evolução possível
  ----------------- --------------------- ------------------ -----------------
  Espinho           Arma automática       Dispara contra o   Perfuração,
  Simbiótico                              inimigo válido     ricochete ou
                                          mais próximo       rajada

  Pulso de Raízes   Ativa                 Dano em área e     Raio maior ou
                                          empurrão           enraizamento

  Micélio Guardião  Passiva/companheiro   Ataca alvos        Mais frequência
                                          próximos           ou novo organismo

  Ruptura Celular   Ativa                 Arrancada para     Trilha de
                                          reposicionamento   espinhos ou
                                                             proteção curta

  Nuvem de Esporos  Ativa/controle        Cria uma zona que  Área maior ou
                                          enfraquece         contaminação em
                                          inimigos           cadeia

  Dardo de          Arma automática       Disparo rápido e   Dano maior contra
  Fotossíntese                            preciso            alvos marcados
  ----------------------------------------------------------------------------

O MVP começa com Espinho Simbiótico e uma habilidade manual. As outras
entram quando o núcleo do combate estiver estável.

### 6.3 Sinergias

  -----------------------------------------------------------------------
  Combinação                          Efeito proposto
  ----------------------------------- -----------------------------------
  Espinho Simbiótico + Cadência       Disparos mais frequentes

  Espinho Simbiótico + Núcleo         Projéteis atravessam mais alvos
  Perfurante                          

  Pulso de Raízes + Nuvem de Esporos  Inimigos atingidos ficam
                                      vulneráveis a dano biológico

  Micélio Guardião + Adaptabilidade   O companheiro troca de alvo com
                                      maior eficiência

  Ruptura Celular + Casca             A arrancada concede proteção breve
  Regenerativa                        

  Três mutações de uma família        Pode liberar uma evolução especial,
                                      se cumprir requisitos
  -----------------------------------------------------------------------

As evoluções devem alterar o funcionamento de uma habilidade ou abrir
uma estratégia, não apenas aumentar números. Uma referência inicial é
limitar o jogador a seis habilidades equipadas, com cinco níveis por
habilidade; os testes determinarão os valores finais.

## 7. Inimigos e chefes

### 7.1 Inimigos propostos

  Inimigo              Função
  -------------------- -------------------------------------------------
  Larva-Fértil         Perseguidor básico que tenta cercar em grupo
  Esporídeo            Cria zonas perigosas no chão
  Cortarraiz           Inimigo veloz que avança em rajadas
  Flor de Ruptura      Atacante de longa distância
  Casca-Túmulo         Tanque lento e resistente
  Parasita de Sinal    Fortalece inimigos próximos
  Anomalia             Elite com modificador especial
  Guardião de Raízes   Chefe regional com invocações e ataques de área

Cada tipo terá vida, dano, velocidade, experiência, recompensas, colisão
e habilidades configuráveis em recursos de dados do Godot, em vez de
valores espalhados pelo código.

### 7.2 Chefes

-   **Mãe dos Esporos:** alterna invocações, nuvens perigosas e períodos
    em que seu núcleo fica vulnerável.
-   **Jardineiro Vazio:** máquina antiga com disparos direcionados,
    raízes que bloqueiam caminhos e janelas de vulnerabilidade.
-   **Coração da Rede:** chefe final em três etapas: defesa do núcleo,
    exposição de pontos vulneráveis e confronto com padrões combinados.

Para o MVP, implementar somente um chefe com dois padrões de ataque. Os
outros são conteúdo planejado.

## 8. Ondas e dificuldade

A geração de inimigos deve funcionar em um mapa aberto, sem obrigar o
jogador a ficar numa arena fechada.

O controlador de surgimento: 1. calcula a etapa atual; 2. verifica o
limite de inimigos ativos; 3. seleciona tipos permitidos; 4. procura
posições válidas fora da proximidade imediata do jogador; 5. evita
paredes, obstáculos e locais inacessíveis; 6. cria as criaturas; 7.
ajusta a pressão com base no tempo, região e eventos.

### 8.1 Ritmo-alvo para uma expedição de 25 minutos

  Tempo        Fase
  ------------ ----------------------------------------------
  0--3 min     Aprendizado e ameaças leves
  3--7 min     Primeiras mutações e exploração
  7--12 min    Elites e eventos de ameaça
  12--17 min   Grupos combinados e áreas perigosas
  17--22 min   Crise biológica ou chefe regional
  22--27 min   Desafio principal e conclusão
  27--30 min   Margem opcional para exploração/encerramento

São metas de design, não tempos implementados. A dificuldade será mista:
tempo, número de ondas, região e eventos. Não aumentar vida, dano e
velocidade de todos os inimigos ao mesmo tempo.

### 8.2 Parâmetros iniciais para protótipo

  Parâmetro                           Faixa inicial
  --------------------------------- ---------------
  Inimigos ativos no início                   8--12
  Inimigos ativos no fim                     35--50
  Intervalo inicial de surgimento             1,5 s
  Intervalo avançado                     0,5--0,8 s
  Distância mínima de surgimento             250 px
  Distância máxima de surgimento             700 px
  Elites simultâneas                           1--3

Os valores dependem da resolução, da velocidade dos inimigos e do
desempenho no navegador.

## 9. Economia

Há dois recursos com finalidades diferentes.

### 9.1 Biomassa --- moeda de expedição

Obtida por inimigos, eventos e exploração. É usada para compras e
melhorias temporárias. A quantidade disponível é reiniciada ao terminar
a expedição.

  Fonte                     Recompensa inicial
  ----------------------- --------------------
  Inimigo comum                           1--3
  Inimigo especializado                   3--6
  Elite                                  8--15
  Evento                                10--25
  Ninho destruído                       15--30

### 9.2 Núcleos Primordiais --- moeda permanente

Obtidos principalmente de chefes e descobertas importantes. São
preservados após a morte e usados para mutações permanentes e
desbloqueios.

  Fonte                                Recompensa inicial
  -------------------------------- ----------------------
  Chefe regional                                     1--2
  Chefe final                                        3--5
  Descoberta importante                Possibilidade de 1
  Desafio opcional de alto risco     Recompensa ocasional

Inimigos comuns não devem entregar Núcleos Primordiais, para preservar o
valor de derrotar chefes.

## 10. Compras durante a expedição

A Biomassa não serve apenas para comprar atributos. Ela oferece escolhas
táticas entre poder, defesa, mobilidade e sobrevivência. As compras
ocorrem em santuários, estações ou terminais de campo claramente
identificados.

### 10.1 Catálogo inicial de compras

  -------------------------------------------------------------------------
  Item               Custo de referência Efeito            Limitação
  ---------------- --------------------- ----------------- ----------------
  Dose de Biomassa                    20 Recupera parte da Uso limitado por
                                         vida              visita

  Catalisador de                      30 Aumenta dano      Duração limitada
  Dano                                   temporariamente   

  Estimulante                         35 Aumenta cadência  Pode aumentar o
  Neural                                                   consumo de
                                                           oxigênio
                                                           enquanto ativo

  Ampola de                           25 Restaura parte do Não aumenta a
  Oxigênio                               oxigênio          capacidade
                                                           máxima

  Módulo de Mira                      30 Aumenta alcance   Não aumenta dano
                                         de aquisição de   diretamente
                                         alvos             

  Casca                               35 Absorve uma       Quebra ao
  Descartável                            quantidade de     atingir o limite
                                         dano              

  Semente de Isca                     20 Atrai inimigos    Pode tornar o
                                         para uma área     encontro mais
                                                           perigoso

  Pulso de                            40 Empurra inimigos  Recarga/uso
  Emergência                             próximos          limitado

  Cartucho de                         30 Adiciona um       Termina ao
  Espinhos                               efeito temporário acabar a duração
                                         à arma            ou a expedição
  -------------------------------------------------------------------------

Custos, duração e intensidade são valores iniciais de balanceamento. A
loja deve oferecer poucas opções por vez, mas o catálogo pode crescer
conforme novas regiões e sistemas forem adicionados.

### 10.2 Equipamentos com prós e contras

Os equipamentos são escolhas mais duradouras durante a expedição. O
jogador poderá equipar um traje e um módulo, evitando uma quantidade
excessiva de espaços.

  -----------------------------------------------------------------------
  Equipamento             Vantagem                Desvantagem
  ----------------------- ----------------------- -----------------------
  Traje de Astronauta     Reduz dano recebido     Reduz velocidade de
  Reforçado                                       movimento

  Traje de Explorador     Aumenta velocidade      Menor proteção
  Leve                                            

  Regulador de Oxigênio   Reduz consumo de        Ocupa o espaço de
                          oxigênio                módulo

  Amplificador Biológico  Aumenta força de        Aumenta ligeiramente o
                          mutações                consumo de oxigênio

  Escudo de Campo         Absorve dano periódico  Tem recarga longa e
                                                  pode atrasar a
                                                  regeneração natural

  Scanner de Ruínas       Revela pontos de        Não concede bônus
                          interesse               direto de combate
  -----------------------------------------------------------------------

Os equipamentos devem ser comprados com Biomassa ou liberados por
eventos definidos. Não serão distribuídos aleatoriamente no chão como
fonte principal de progressão.

### 10.3 Regras para compras

-   O preço aparece antes da confirmação.
-   O jogador não pode comprar sem recursos suficientes.
-   Itens temporários exibem duração e efeito.
-   Equipamentos com penalidades apresentam vantagens e desvantagens na
    mesma tela.
-   Efeitos iguais não se acumulam ilimitadamente.
-   A loja não pode ser necessária a cada minuto; ela deve apoiar a
    estratégia, não interromper o combate constantemente.

## 11. Mutações permanentes com efeitos colaterais

Esta é uma mecânica central do projeto. As mutações permanentes são
compradas com Núcleos Primordiais e representam alterações biológicas
que continuam existindo entre expedições.

A filosofia é: **quanto mais especializada for a adaptação, mais
importante será aceitar seu custo**. Nem toda mutação precisa ter uma
desvantagem grave. Algumas podem ser quase neutras, enquanto outras
oferecem grandes vantagens acompanhadas de um efeito colateral
relevante.

As mutações serão divididas em três linhas: defesa, predação e
ressonância. Os valores abaixo são exemplos para orientar os testes, não
números finais.

### 11.1 Linha A --- Simbiose defensiva

  ------------------------------------------------------------------------
  Mutação          Vantagem         Efeito colateral         Custo inicial
  ---------------- ---------------- ---------------- ---------------------
  Casca Celular    +10% de vida     -3% de                       2 Núcleos
                   máxima           velocidade       

  Raízes           Recupera         Recuperação de               3 Núcleos
  Regenerativas    lentamente vida  oxigênio 10%     
                   fora de perigo   mais lenta       

  Membrana         Reduz parte do   Aumenta                      4 Núcleos
  Adaptativa       dano recebido    ligeiramente o   
                                    tempo de recarga 
                                    de habilidades   

  Reserva Orgânica Uma vez por      Não pode ativar              6 Núcleos
                   expedição, evita novamente até    
                   uma morte e      outra expedição  
                   deixa o jogador                   
                   com pouca vida                    

  Carapaça         Grande redução   Velocidade                   7 Núcleos
  Profunda         de dano por um   reduzida         
                   curto período    enquanto o       
                   após sofrer um   efeito estiver   
                   golpe forte      ativo            
  ------------------------------------------------------------------------

### 11.2 Linha B --- Predação adaptativa

  -------------------------------------------------------------------------
  Mutação          Vantagem         Efeito colateral          Custo inicial
  ---------------- ---------------- ----------------- ---------------------
  Espinhos         +8% de dano da   -3% de eficácia               2 Núcleos
  Permanentes      arma biológica   de cura recebida  

  Metabolismo      +10% de cadência Consumo de                    3 Núcleos
  Acelerado                         oxigênio +8%      

  Instinto         Bônus de dano    Dano ligeiramente             4 Núcleos
  Predatório       contra elites    menor contra      
                                    inimigos comuns   

  Sangue Volátil   Eliminações      Explosões podem               5 Núcleos
                   podem causar     atingir o         
                   explosão         protagonista se   
                   biológica        estiver muito     
                                    perto             

  Sobrecarga       Habilidades      Depois do efeito,             7 Núcleos
  Celular          causam muito     a recarga fica    
                   mais dano por    temporariamente   
                   uma janela curta maior             
  -------------------------------------------------------------------------

### 11.3 Linha C --- Ressonância da Semente

  ------------------------------------------------------------------------
  Mutação          Vantagem         Efeito colateral         Custo inicial
  ---------------- ---------------- ---------------- ---------------------
  Sentido          Revela recursos  O alcance de                 2 Núcleos
  Biológico        e pontos de      aquisição        
                   interesse        automática de    
                   próximos         alvos é          
                                    ligeiramente     
                                    menor            

  Memória Genética +10% de          Elites podem                 3 Núcleos
                   experiência      surgir um pouco  
                   obtida           mais cedo        

  Ressonância      Libera           Aumenta a                    5 Núcleos
  Profunda         descobertas e    frequência de    
                   opções especiais eventos de       
                   de evolução      ameaça           

  Simbiose de      Recupera uma     Reduz a                      5 Núcleos
  Campo            pequena          capacidade       
                   quantidade de    máxima de        
                   Biomassa em      oxigênio         
                   eventos                           

  Consciência da   Revela           Aumenta a                    7 Núcleos
  Rede             informações      intensidade de   
                   sobre chefes e   certos eventos   
                   permite          da Rede Raiz     
                   identificar                       
                   padrões                           
  ------------------------------------------------------------------------

### 11.4 Regras de balanceamento das mutações

1.  Toda desvantagem deve ser compreensível antes da compra.
2.  O jogador não pode ficar preso a uma mutação ruim sem qualquer
    saída. O jogo pode permitir uma purificação cara, um reset limitado
    ou a substituição da mutação.
3.  Os efeitos colaterais devem ser relevantes, mas não tornar a
    habilidade inutilizável.
4.  Mutações incompatíveis devem ser sinalizadas.
5.  Bônus semelhantes devem ter limites de acumulação.
6.  Algumas mutações podem ser neutras ou oferecer benefícios
    situacionais, sem penalidade severa.
7.  O jogador deve poder criar builds diferentes: tanque, velocidade,
    dano, exploração ou controle de área.

### 11.5 Remoção e reversão — regra definitiva

A reversão acontece no **Laboratório de Adaptação**, acessível no menu entre expedições e em um terminal seguro desbloqueado na base. O custo para reverter uma mutação é **exatamente igual à quantidade de Núcleos Primordiais originalmente gasta para comprá-la**. Exemplo: se uma mutação custou 4 Núcleos, removê-la custa 4 Núcleos. O jogador não recebe os Núcleos de volta; ele paga o mesmo valor para desfazer a alteração.

Ao reverter uma mutação, todos os bônus e efeitos colaterais dela são removidos imediatamente. A interface deve mostrar o antes/depois dos atributos e o custo antes de pedir confirmação. Se o jogador não possuir Núcleos suficientes, a ação fica desativada e o custo é explicado.

Regras adicionais:
- A reversão não remove Núcleos já recebidos como recompensa e não apaga registros narrativos, bestiário ou regiões desbloqueadas.
- Uma mutação que seja pré-requisito de outra não pode ser removida enquanto a dependente estiver ativa. O jogo deve listar as mutações dependentes e exigir que elas sejam revertidas primeiro.
- Uma mutação comprada uma vez e depois revertida pode ser comprada novamente pelo custo normal.
- A confirmação é obrigatória; não há reversão acidental por um único clique.
- A reversão ocorre fora do combate. Não é possível abrir o laboratório durante uma expedição ativa.
- A compra e a reversão devem ser registradas de forma segura no salvamento para impedir duplicação ou perda de Núcleos em carregamentos repetidos.

Essa regra substitui qualquer referência anterior a taxa fixa, recuperação parcial ou perda de descobertas.

## 12. Oxigênio e sobrevivência ambiental

O oxigênio pode acrescentar identidade ao jogo, mas precisa apoiar a
exploração sem transformar cada combate em uma corrida frustrante contra
um cronômetro.

### 12.1 Modelo recomendado: autonomia do traje

O protagonista usa um traje de exploração com reserva limitada de
oxigênio. A reserva diminui gradualmente enquanto está em áreas não
seguras. O consumo pode aumentar em situações de esforço, como correr
continuamente ou usar mutações de alto metabolismo, mas esses
multiplicadores devem ser suaves.

O oxigênio **não deve ser consumido normalmente na base segura, no menu
ou durante uma pausa**. O combate, por si só, não deve esvaziar o tanque
rapidamente.

### 12.2 Regras propostas

-   O protagonista começa com uma capacidade de oxigênio definida.
-   Áreas seguras, como a nave ou um santuário pressurizado, permitem
    recarregar.
-   Ampolas compradas com Biomassa restauram parte da reserva.
-   Reguladores e mutações podem reduzir o consumo ou aumentar a
    capacidade.
-   Regiões profundas podem exigir preparação melhor.
-   O HUD mostra uma barra de oxigênio e alertas em níveis claros.
-   Em níveis críticos, efeitos sonoros e visuais indicam perigo sem
    esconder a ação.
-   A falta de oxigênio causa perda gradual de vida e efeitos de visão,
    em vez de morte instantânea.

### 12.3 Números iniciais para teste

  Parâmetro                                             Valor de protótipo
  ------------------------------- ----------------------------------------
  Capacidade inicial                180 segundos em zona sem ar respirável
  Consumo normal em zona hostil                      1 unidade por segundo
  Aviso de reserva baixa                                               30%
  Aviso crítico                                                        15%
  Dano por falta de oxigênio                         Pequeno e progressivo
  Recuperação em ponto seguro                  Rápida, mas não instantânea
  Ampola                                       Recupera 30--40% da reserva

Os 180 segundos são uma referência inicial, não uma promessa de que o
jogador só poderá explorar três minutos. O mapa deve ter bolsões de ar,
santuários ou zonas seguras para recarga. A capacidade será balanceada
para permitir trajetos de ida e volta com margem para combate.

### 12.4 Como integrar oxigênio à exploração

-   As primeiras áreas têm ar respirável em boa parte do mapa.
-   A Bacia dos Ecos contém trechos contaminados que exigem
    planejamento.
-   O Santuário das Raízes exige que o jogador escolha entre equipamento
    defensivo, mobilidade e autonomia.
-   Eventos podem oferecer uma estação de recarga ou uma ampola como
    recompensa.
-   Alguns atalhos economizam tempo, mas passam por zonas com consumo
    maior.
-   O jogador sempre recebe indicação visual da rota de retorno ou de um
    ponto seguro conhecido, quando aplicável.

### 12.5 Decisão de escopo e critério de qualidade

**O oxigênio faz parte do MVP**, mas só será consumido em setores hostis claramente sinalizados da Bacia dos Ecos. A Floresta do Despertar funciona como área de aprendizagem e não pune o jogador com falta de ar. O sistema deve gerar decisões interessantes — por exemplo, escolher entre um módulo defensivo e um regulador de oxigênio — e nunca exigir que o jogador atravesse uma área sem rota segura ou informação suficiente.

Durante os testes, medir quantas mortes e retornos forçados são causados pelo oxigênio. Se o sistema gerar frustração em vez de decisões, primeiro ajustar capacidade, consumo, alertas e pontos de recarga. Remover a mecânica só será uma decisão de revisão de escopo baseada em testes, não uma pendência de design.

## 13. Progressão entre expedições

O jogador preserva Núcleos Primordiais, mutações permanentes e registros
narrativos após morrer. Biomassa, bônus temporários e equipamentos de
expedição normalmente são perdidos ao encerrar a tentativa.

### 13.1 Recompensas preservadas

-   Núcleos Primordiais já creditados.
-   Mutações permanentes compradas.
-   Registros de história desbloqueados.
-   Entradas do catálogo de criaturas descobertas.
-   Estatísticas básicas de expedições.
-   Acessos a regiões já desbloqueados.

### 13.2 Recompensas não preservadas

-   Biomassa não gasta.
-   Bônus temporários.
-   Doses e consumíveis comprados para aquela expedição.
-   Equipamentos temporários, salvo se um evento os definir como
    desbloqueio permanente.

### 13.3 Salvamento

O arquivo de salvamento deverá conter versão do formato, recursos
permanentes, mutações, descobertas e estatísticas. O jogo precisa
validar os dados ao carregar e não duplicar recompensas quando a mesma
tela for reaberta ou a partida reiniciada.

## 14. Estrutura dos níveis finais e encerramento

A campanha terá **dois níveis finais dedicados**, além das regiões
exploráveis anteriores.

### 14.1 Penúltimo nível --- O Santuário do Último Jardim

O protagonista chega a uma instalação dos Arquitetos Verdes. Para
liberar a passagem ao núcleo, precisa: 1. explorar a instalação; 2.
ativar dois ou três mecanismos; 3. resistir a ondas de criaturas; 4.
enfrentar o Jardineiro Vazio ou outro guardião final da instalação; 5.
descobrir o verdadeiro propósito da Rede Raiz.

Esse nível deve ser um teste das ferramentas adquiridas, sem exigir que
o jogador tenha comprado todas as mutações permanentes.

### 14.2 Nível final --- Coração de Nymara

O jogador entra na região central da Rede Raiz. O cenário combina
tecnologia antiga, raízes gigantes e um núcleo biológico luminoso.

O chefe final possui três etapas: 1. **Defesa:** o núcleo invoca
criaturas e ataca com raízes. 2. **Exposição:** o jogador destrói
estruturas que protegem o núcleo. 3. **Decisão:** o jogador escolhe como
usar a Última Semente, levando a um encerramento narrativo.

Para o primeiro lançamento, o jogo pode ter um final principal e
pequenas variações de epílogo, em vez de múltiplas campanhas completas.

### 14.3 Tela de conclusão

Após vencer o chefe final e assistir ao epílogo, aparece uma tela
própria de conclusão. O texto central proposto:

> **PARABÉNS!**
>
> Você completou *Projeto: Última Semente* com sucesso.
>
> Nymara nunca mais será a mesma.

A tela deve oferecer: - **Continuar:** abre os créditos. - **Revisitar o
mundo:** se houver modo pós-jogo, permite explorar sem repetir a
campanha. - **Voltar ao menu:** retorna ao menu principal.

Se não houver conteúdo pós-jogo no primeiro lançamento, o botão
"Revisitar o mundo" fica fora do MVP.

### 14.4 Créditos e agradecimentos

Os créditos devem ser simples, legíveis e respeitar o tom do jogo.

Texto proposto:

> **PROJETO: ÚLTIMA SEMENTE**
>
> Criado por **vnvnpa**
>
> Obrigado por jogar e ajudar Kael a descobrir o destino de Nymara.
>
> **Quer ajudar a financiar um próximo projeto?**
>
> Se você gostou do jogo, poderá apoiar voluntariamente o próximo projeto
> pela página oficial de *Projeto: Última Semente* no itch.io.
>
> Baixar, concluir o jogo e assistir aos créditos nunca depende de pagar
> ou doar. Obrigado por fazer parte desta jornada.
>
> Contato: vnvnpa.oficial@gmail.com

O botão **Apoiar o projeto** só aparece quando o endereço público do projeto no itch.io estiver configurado e testado. Ele abre a página do jogo, onde o criador poderá oferecer contribuição voluntária conforme as configurações disponíveis na conta. Até lá, o convite pode aparecer sem botão. Nunca inventar endereço de pagamento nem usar o e-mail como link de pagamento. Se forem usados assets, músicas, fontes ou contribuições de terceiros, os créditos devem reconhecê-los de acordo com as respectivas licenças.

## 15. Interface

### HUD da expedição

-   Vida atual e máxima.
-   Barra de experiência e nível.
-   Biomassa e Núcleos Primordiais.
-   Barra de oxigênio, quando em área que consome ar.
-   Tempo e etapa da expedição.
-   Ícones de armas, habilidades e recargas.
-   Mapa e objetivos descobertos.
-   Alertas de eventos e chefes.

### Telas necessárias

1.  Menu principal.
2.  Seleção/início da expedição.
3.  HUD de jogo.
4.  Seleção de mutação ao subir de nível.
5.  Loja ou terminal de suprimentos.
6.  Menu de mutações permanentes.
7.  Pausa e configurações.
8.  Derrota e resumo da expedição.
9.  Conclusão de campanha.
10. Créditos e convite opcional para doação.
11. Arquivo biológico de inimigos, mutações e registros.

A interface deve ter texto legível, volumes independentes, opção de
reduzir tremor e efeitos intensos, alertas claros e controles ajustáveis
quando viável.

## 16. Arquitetura técnica no Godot

### 16.1 Base técnica

-   Godot 4.x estável; verificar a versão oficial vigente no início da
    produção.
-   GDScript.
-   Renderizador Compatibility como ponto de partida para navegador.
-   Exportação Web/HTML5 para itch.io.
-   Cenas modulares e recursos de dados.
-   Salvamento em `user://`.
-   Git para versionamento.

A versão estável mencionada no planejamento anterior era Godot 4.7.2,
mas deve ser confirmada no arquivo oficial no início da implementação,
pois a versão mais recente pode mudar.

### 16.2 Pastas propostas

``` text
ultima_semente/
├── project.godot
├── scenes/
│   ├── main/
│   ├── player/
│   ├── enemies/
│   ├── bosses/
│   ├── weapons/
│   ├── world/
│   ├── shops/
│   └── ui/
├── scripts/
│   ├── core/
│   ├── player/
│   ├── enemies/
│   ├── combat/
│   ├── progression/
│   ├── economy/
│   ├── oxygen/
│   ├── world/
│   └── ui/
├── resources/
│   ├── enemies/
│   ├── weapons/
│   ├── mutations/
│   ├── equipment/
│   └── items/
├── assets/
│   ├── sprites/
│   ├── tilesets/
│   ├── audio/
│   ├── fonts/
│   └── effects/
└── docs/
    └── GDD_Projeto_Ultima_Semente.md
```

### 16.3 Cena principal proposta

``` text
Game (Node2D)
├── World
│   ├── Terrain (TileMapLayer)
│   ├── Decorations (TileMapLayer)
│   ├── Obstacles (Node2D)
│   └── PointsOfInterest (Node2D)
├── Entities
│   ├── Player
│   ├── Enemies (Node2D)
│   ├── Projectiles (Node2D)
│   └── Drops (Node2D)
├── Systems
│   ├── SpawnDirector
│   ├── WorldEvents
│   ├── RunManager
│   ├── ResourceManager
│   └── OxygenManager
├── Camera2D
└── UI (CanvasLayer)
    ├── HUD
    ├── MutationMenu
    ├── ShopMenu
    ├── PauseMenu
    ├── GameOver
    ├── VictoryScreen
    └── Credits
```

### 16.4 Sistemas e responsabilidades

  Sistema           Responsabilidade
  ----------------- ----------------------------------------------------
  GameManager       Estados globais e transições de tela
  RunManager        Tempo, nível, expedição e condição de conclusão
  SaveManager       Salvamento e validação da progressão
  SpawnDirector     Ondas e limites de inimigos
  Enemy             Movimento, ataques, dano, morte e recompensa
  WeaponSystem      Aquisição de alvo e disparos
  MutationManager   Mutações temporárias e permanentes
  ResourceManager   Biomassa, Núcleos e transações
  ShopManager       Catálogo, preços e compras
  OxygenManager     Consumo, recarga, alertas e efeitos da falta de ar
  WorldEvents       Eventos e pontos de interesse
  HUD               Interface de jogo e atualização visual
  EndingManager     Conclusão, epílogo, créditos e retorno ao menu

### 16.5 Dados configuráveis

Inimigos, mutações, armas, equipamentos e itens devem usar Resources
personalizados e arquivos `.tres`, quando apropriado. Cada mutação deve
conter identificador único, descrição, custo, pré-requisitos, vantagens,
efeitos colaterais e regras de compatibilidade.

Exemplo de recurso de inimigo:

``` gdscript
extends Resource
class_name EnemyData

@export var nome: String = "Larva-Fértil"
@export var vida_maxima: float = 30.0
@export var dano: float = 5.0
@export var velocidade: float = 70.0
@export var experiencia: int = 2
@export var biomassa_minima: int = 1
@export var biomassa_maxima: int = 3
```

Este código é uma referência de arquitetura, não código já integrado ou
testado num projeto.

### 16.6 Performance

-   Limitar entidades ativas.
-   Remover projéteis expirados.
-   Evitar verificações desnecessárias em cada quadro.
-   Usar colisões simples.
-   Considerar pooling se medições demonstrarem benefício.
-   Testar a exportação web desde cedo.
-   Medir taxa de quadros e memória em computadores de referência.
-   Tratar o salvamento do navegador como parte do teste de publicação.

## 17. MVP --- primeira versão jogável

O MVP deve provar que movimentação, combate, ondas, economia e evolução
funcionam juntos.

### Incluído no MVP

-   Um protagonista.
-   Uma arena explorável.
-   Três inimigos comuns.
-   Uma arma automática e uma habilidade manual.
-   Experiência e escolhas de mutação.
-   Ondas com dificuldade crescente.
-   Biomassa e uma recompensa rara de chefe.
-   Uma loja simples com algumas melhorias.
-   Um chefe com dois padrões de ataque.
-   Três mutações permanentes, incluindo pelo menos uma com efeito
    colateral.
-   Uma implementação inicial de oxigênio em uma área hostil, se os
    testes confirmarem que é divertida.
-   HUD, tela de derrota e salvamento.
-   Exportação e teste no navegador.

### Fora do MVP

-   Três regiões completas.
-   Todos os inimigos e chefes.
-   Árvore permanente extensa.
-   Múltiplos finais.
-   Proceduralização complexa do mundo.
-   Grande catálogo de equipamentos.
-   Conteúdo pós-jogo.
-   Serviços externos de conquistas.

A tela de conclusão e os créditos devem ser implementados na fase de
finalização da campanha, mesmo que não façam parte do primeiro protótipo
de combate.

## 18. Cronograma de produção

Estimativa para uma pessoa, com assets próprios ou licenciados e
experiência crescente no Godot.

  -----------------------------------------------------------------------
  Fase                    Duração estimada        Entrega
  ----------------------- ----------------------- -----------------------
  1\. Movimento e câmera  1 semana                Protagonista e mapa
                                                  básico

  2\. Combate             1--2 semanas            Arma, projéteis,
                                                  inimigos e dano

  3\. Evolução temporária 1--2 semanas            Experiência, níveis e
                                                  mutações

  4\. Ondas e exploração  2 semanas               Spawn, eventos e pontos
                                                  de interesse

  5\. Economia e chefe    1--2 semanas            Compras, recompensas e
                                                  chefe

  6\. Progressão          1--2 semanas            Mutações com vantagens
  permanente                                      e efeitos colaterais

  7\. Oxigênio e          1 semana                Testar se a mecânica
  equipamentos                                    melhora a exploração

  8\. Arte, interface e   2--3 semanas            HUD, menus e
  áudio                                           apresentação

  9\. Níveis finais e     2--3 semanas            Chefe final, conclusão
  créditos                                        e tela de créditos

  10\. Testes e           1--2 semanas            Correções e build web
  publicação                                      
  -----------------------------------------------------------------------

Estimativa ampla: aproximadamente 12--19 semanas, sujeita a mudanças
conforme a experiência, a quantidade de arte e a complexidade dos
chefes.

## 19. Balanceamento e critérios de qualidade

  -----------------------------------------------------------------------
  Indicador                           Meta inicial
  ----------------------------------- -----------------------------------
  Duração comum                       20--30 minutos

  Primeira mutação                    Até 2 minutos

  Primeira elite                      Entre 5--8 minutos

  Primeiro grande evento              Entre 8--12 minutos

  Chefe regional                      Entre 15--22 minutos

  Desempenho                          Meta de 60 FPS em computadores de
                                      referência, reduzindo carga quando
                                      necessário

  Progressão                          Recompensa permanente relevante
                                      após algumas tentativas

  Oxigênio                            Pressiona a exploração sem exigir
                                      retornos constantes e frustrantes
  -----------------------------------------------------------------------

Testes obrigatórios: - Inimigos não surgem sobre o protagonista ou
dentro de obstáculos. - Inimigos mortos não atacam. - Projéteis não
causam dano duplicado indevido. - Recompensas de chefes são creditadas
uma única vez. - A morte encerra a expedição corretamente. - Mutações
não aplicam efeitos duplicados. - Compras validam o saldo antes de
descontar recursos. - Oxigênio não é consumido durante pausa ou em zonas
seguras. - O sistema de salvamento funciona no build web. - A
dificuldade não cresce sem limite além do encerramento previsto. - A
tela de vitória e os créditos aparecem somente após cumprir as condições
finais.

## 20. Riscos e mitigação

  -----------------------------------------------------------------------
  Risco                               Mitigação
  ----------------------------------- -----------------------------------
  Mapa grande demais                  Começar com uma região conectada

  Combate repetitivo                  Inimigos com papéis distintos e
                                      sinergias

  Mutações com penalidades            Mostrar efeitos antes da compra e
  frustrantes                         permitir reconfiguração limitada

  Oxigênio virar tarefa irritante     Bolsões seguros, alertas claros e
                                      consumo previsível

  Progressão permanente trivializar o Limitar bônus e preservar desafios
  jogo                                mecânicos

  Muitas funcionalidades antes do     Priorizar o MVP
  protótipo                           

  Queda de desempenho                 Limites de entidades e testes web
                                      contínuos

  Doação parecer obrigatória          Pedido opcional, sem bloquear
                                      créditos ou conclusão
  -----------------------------------------------------------------------

## 21. Decisões consolidadas e itens de produção

As decisões de design abaixo ficam fechadas para orientar a primeira versão. Elas não significam que os sistemas já foram programados.

1. **Protagonista:** o nome usado no documento e no primeiro lançamento será **Kael**. Pode ser renomeado antes de publicar, mas a implementação não deve ficar bloqueada por isso.
2. **Oxigênio:** incluído no MVP, restrito inicialmente a setores hostis sinalizados da Bacia dos Ecos; haverá áreas seguras, pontos de recarga e avisos de reserva.
3. **Reversão de mutações:** custa exatamente o mesmo número de Núcleos Primordiais gasto na compra original; o jogador paga para remover a mutação e não recebe reembolso.
4. **Lojas e equipamentos:** compras ocorrem em terminais fixos de suprimentos e santuários seguros. Eventos específicos podem oferecer equipamento como escolha explícita. Não haverá chuva de armas/equipamentos aleatórios no chão.
5. **Encerramento de expedição:** o jogador pode morrer, concluir o objetivo da expedição ou usar um ponto de extração desbloqueado. Morrer ou extrair encerra os bônus temporários, a Biomassa não gasta e os equipamentos temporários. Núcleos Primordiais são registrados imediatamente quando obtidos e permanecem após a morte; registros, entradas do bestiário e desbloqueios permanentes também permanecem. A extração voluntária não concede recompensa de chefe que não tenha sido derrotado.
6. **Campanha e níveis finais:** a campanha tem quatro regiões narrativas. O Santuário do Último Jardim é o penúltimo nível dedicado; o Coração de Nymara é o nível final. O acesso é liberado por objetivos narrativos e chefes, não por uma contagem arbitrária de minutos. As expedições comuns duram em média 20–30 minutos; cada nível final é uma missão dedicada, estimada em 8–12 minutos na primeira conclusão.
7. **Final:** um final principal, com pequenas variações de epílogo baseadas em registros e escolhas menores. Não criar múltiplas campanhas ou ramificações grandes na primeira versão.
8. **Doações:** a estratégia padrão será usar a página do projeto no itch.io com preço mínimo zero e opção de contribuição voluntária, se as configurações de pagamento da conta permitirem. O botão dentro do jogo só será ativado depois de a página pública existir e o endereço ter sido confirmado. Não inventar nem codificar um link antes disso. O Gmail pode ser exibido como contato, mas não é um sistema de doação.
9. **Contato público:** `vnvnpa.oficial@gmail.com` pode ser exibido na página do itch.io ou nos créditos como e-mail de contato. Como ficará público, considerar spam; não é necessário exibi-lo na tela de vitória.
10. **Licenças:** todo asset, fonte, música, efeito sonoro e contribuição de terceiros precisa ter licença registrada e atribuição quando exigida. Priorizar arte original ou recursos com licença compatível com distribuição comercial e web.
11. **Motor:** usar a versão estável de Godot 4 disponível no início do desenvolvimento, fixando a versão escolhida no README e evitando atualizar a versão no meio de uma etapa sem teste de regressão. Não assumir que uma versão específica continua sendo a mais recente.

### 21.1 O que ainda depende da produção, não de uma decisão de design

- Criar a página pública do jogo no itch.io e confirmar seu endereço final.
- Configurar e testar a forma de receber contribuições voluntárias na conta do criador.
- Escolher a versão exata do Godot no início do projeto e testar a exportação Web nos navegadores-alvo.
- Criar ou licenciar arte, música, fontes e efeitos sonoros; registrar os créditos.
- Medir e balancear valores de dano, vida, velocidade, custos, experiência, oxigênio, duração das ondas e dificuldade por meio de protótipos.
- Confirmar compatibilidade e desempenho no navegador, incluindo salvamento, foco da janela e limitações de áudio.

Esses itens são tarefas de execução e validação. Não devem ser usados por uma IA de implementação como licença para inventar novas mecânicas: seguir as regras deste GDD e registrar qualquer mudança proposta separadamente.

## 22. Créditos finais propostos

**PROJETO: ÚLTIMA SEMENTE**

Criado por **vnvnpa**

> Parabéns! Você completou este jogo com sucesso.
>
> Obrigado por explorar Nymara e descobrir o destino da Última Semente.
>
> Gostou da experiência? Se quiser, você pode apoiar o próximo projeto
> por meio da página oficial de *Projeto: Última Semente* no itch.io.
>
> Toda contribuição é voluntária. Baixar e concluir o jogo não depende
> de pagar ou doar.
>
> Contato: vnvnpa.oficial@gmail.com
>
> Obrigado por jogar!

A versão Web não deve depender de abrir links externos para permitir que o jogador conclua os créditos. O botão **Apoiar o projeto** só aparece quando o endereço público do projeto no itch.io estiver configurado e testado; ele abre essa página usando o mecanismo de abertura de URL suportado pela plataforma. Até lá, o convite pode ser exibido como texto sem botão. Nunca usar o endereço de e-mail como link de pagamento. A conclusão, os créditos e o retorno ao menu permanecem disponíveis sem contribuição.

## 23. Referências de produção

-   Godot Engine: https://godotengine.org/
-   Arquivo oficial de versões:
    https://godotengine.org/download/archive/
-   Documentação estável: https://docs.godotengine.org/en/stable/
-   Exportação para Web:
    https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html
-   Publicação: https://itch.io/

------------------------------------------------------------------------

## Resumo final

**Projeto: Última Semente** é um jogo de sobrevivência e exploração em
que o jogador cresce ao absorver a biologia de um planeta hostil. A
Biomassa alimenta decisões durante a expedição; os Núcleos Primordiais
desbloqueiam mutações permanentes. As mutações podem ter vantagens e
efeitos colaterais, enquanto equipamentos como trajes reforçados trocam
defesa por mobilidade.

O oxigênio integra o MVP em setores hostis sinalizados, com pontos de recarga e rotas justas. A reversão de mutações custa exatamente o mesmo número de Núcleos Primordiais gasto na compra. A campanha termina com dois níveis finais,
uma tela de conclusão, créditos de autoria para **vnvnpa** e um convite
opcional para apoiar projetos futuros.

O próximo passo de produção é construir o MVP e testar se exploração,
combate, compras, mutações e oxigênio formam um ciclo divertido antes de
expandir o conteúdo.


## 24. Instruções para a IA que receber este GDD

Este arquivo é a referência principal do projeto. Ao implementar funcionalidades:

1. Leia o GDD inteiro antes de alterar cenas ou scripts.
2. Use Godot 4.x e GDScript; não use sintaxe de Godot 3.x. Confirme a versão exata no projeto.
3. Não declare sistemas como implementados só porque estão especificados aqui. Diferencie claramente **planejado**, **implementado**, **testado** e **pendente de validação**.
4. Preserve o escopo do MVP e faça alterações incrementais. Não reescreva grandes scripts ou arquitetura sem explicar por que isso é necessário.
5. Use recursos de dados (`Resource`) para inimigos, armas, equipamentos e mutações sempre que isso evitar números repetidos em scripts. Exponha no Inspector os parâmetros que precisam de balanceamento.
6. Centralize estado de partida, progressão permanente, economia e salvamento para evitar recompensas duplicadas ou divergência entre telas. O jogo é single-player; não criar multiplayer.
7. Para qualquer compra, mutação, recompensa de chefe ou salvamento, valide custo, estado e execução única. Mostre feedback claro para ações inválidas.
8. Não invente o endereço do itch.io, um link de pagamento ou conteúdo externo. Use um valor de configuração vazio até que o criador forneça o endereço confirmado.
9. Antes de adicionar um recurso fora deste GDD, apresente a proposta, o benefício, o custo de implementação e o impacto no escopo; não o implemente silenciosamente.
10. Ao terminar cada etapa, liste arquivos alterados, como testar no editor, testes executados, problemas conhecidos e quais itens ainda não foram verificados.
11. Priorize primeiro o protótipo jogável do MVP; só depois expanda todas as regiões, inimigos, chefes e conteúdo narrativo.
12. Em builds Web, testar carregamento, controles, áudio após interação do usuário, salvamento persistente e comportamento ao perder o foco da aba.

**Critério de conclusão do documento:** as regras centrais de design estão especificadas para começar a produção. A conclusão do GDD não significa que o jogo está pronto; a implementação, o balanceamento, os testes e a publicação ainda precisam ser realizados.
