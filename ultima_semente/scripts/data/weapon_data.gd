class_name WeaponData
extends Resource
## Arma automática (GDD 6.2).

@export var id: String = "espinho_simbiotico"
@export var nome: String = "Espinho Simbiótico"
@export var dano: float = 12.0
@export var intervalo: float = 0.55
@export var alcance: float = 360.0
@export var velocidade_projetil: float = 520.0
@export var raio_projetil: float = 5.0
@export var perfuracao: int = 0

## Dardo de Fotossíntese: bônus de dano contra alvos marcados (1.0 = sem bônus),
## duração da marca (s) e aumento de dano por nível da mutação.
@export var bonus_marcado: float = 1.0
@export var duracao_marca: float = 0.0
@export var escala_por_nivel: float = 0.0
