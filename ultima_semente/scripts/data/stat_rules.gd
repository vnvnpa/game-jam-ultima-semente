class_name StatRules
extends Resource
## Regras de atributos do jogador (valores-base e limites). Editável em
## data/rules/stat_rules.tres. Todo cálculo fica em RunState.

@export var base_hp: float = 100.0
@export var base_speed: float = 190.0
@export var base_o2: float = 180.0
## Atributo -> valor inicial (multiplicadores começam em 1.0, somas em 0.0).
@export var base_values: Dictionary = {}
## Atributo -> [mínimo, máximo]; impede acúmulo ilimitado de bônus (GDD 11.4).
@export var limits: Dictionary = {}
