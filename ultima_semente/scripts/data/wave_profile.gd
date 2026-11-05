class_name WaveProfile
extends Resource
## Perfil de dificuldade do SpawnDirector (GDD 8): etapas, limites e elites.

@export var id: String = ""
## Lista de WaveStage em ordem crescente de `inicio`.
@export var stages: Array = []
@export var cap_inicio: float = 10.0
@export var cap_fim: float = 45.0
## Tempo (s) em que a pressão para de crescer.
@export var tempo_rampa: float = 1320.0
@export var limite_maximo: int = 70
@export var intervalo_inicio: float = 1.5
@export var intervalo_fim: float = 0.6
## Acréscimo máximo de vida dos inimigos (0.5 = +50%). Dano e velocidade não escalam.
@export var escala_vida_max: float = 0.5
@export var dist_min: float = 250.0
@export var dist_max: float = 700.0
## Com o chefe ativo: fração do limite de inimigos e fator do intervalo.
@export var chefe_mult_limite: float = 0.4
@export var chefe_mult_intervalo: float = 1.3
@export var elite_intervalo: float = 210.0
@export var elite_nova_tentativa: float = 3.0
@export var elite_espera_cheio: float = 20.0
@export var elite_dist_min: float = 350.0
@export var elite_dist_max: float = 650.0
## ids de EliteModifier sorteados para as Anomalias.
@export var elite_ids: Array = []
