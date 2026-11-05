class_name AbilityData
extends Resource
## Habilidade ativa extra (Nuvem de Esporos). Números editáveis em data/abilities/.

@export var id: String = ""
@export var nome: String = ""
@export var recarga: float = 14.0
@export var raio: float = 120.0
@export var duracao: float = 6.0
## Dano recebido pelos inimigos enfraquecidos (1.25 = +25%).
@export var vulnerabilidade: float = 1.25
## Velocidade dos inimigos dentro da nuvem (0.65 = 35% mais lentos).
@export var lentidao: float = 0.65
## Quanto o enfraquecimento dura depois de sair da nuvem (s).
@export var duracao_fraqueza: float = 1.0
## Sinergia: enfraquecimento (s) aplicado pelo Pulso de Raízes a quem for atingido.
@export var fraqueza_pulso: float = 5.0
@export var max_ativas: int = 4
## Evolução (nuvem em cadeia): chance, raio (fração) e duração da nuvem criada
## quando um inimigo enfraquecido morre.
@export var cadeia_chance: float = 0.4
@export var cadeia_raio_mult: float = 0.55
@export var cadeia_duracao: float = 3.5
