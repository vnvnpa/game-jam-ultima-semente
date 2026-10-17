class_name EnemyData
extends Resource
## Dados configuráveis de um inimigo (GDD 16.5). Editáveis no Inspector.

@export var id: String = ""
@export var nome: String = "Larva-Fértil"
@export_multiline var descricao: String = ""
## perseguidor, veloz, distancia, tanque, esporideo, parasita, ninho, chefe
@export var comportamento: String = "perseguidor"
@export var vida_maxima: float = 30.0
@export var dano: float = 5.0
@export var velocidade: float = 70.0
@export var experiencia: int = 2
@export var biomassa_minima: int = 1
@export var biomassa_maxima: int = 3
@export var raio: float = 10.0
@export var cor: Color = Color(0.8, 0.3, 0.6)
@export var cor_detalhe: Color = Color(1.0, 0.8, 0.9)
## Intervalo entre ataques de contato ou disparos, em segundos.
@export var intervalo_ataque: float = 0.8
## Distância preferida do alvo (inimigos de longa distância).
@export var alcance_preferido: float = 0.0
## Parâmetros livres por comportamento (ex.: multiplicador de investida).
@export var parametro_a: float = 0.0
@export var parametro_b: float = 0.0
## Cena instanciada para este inimigo (editável: troque por uma cena própria).
@export var cena: PackedScene
