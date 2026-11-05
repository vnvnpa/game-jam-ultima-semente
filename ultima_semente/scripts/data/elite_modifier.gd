class_name EliteModifier
extends Resource
## Modificador da Anomalia (elite): blindada, veloz, explosiva ou regenerante.
## O id é também o nome da animação da aura (anomalia_auras.tres).

@export var id: String = ""
@export var nome: String = ""
@export var hp_mult: float = 1.0
@export var speed_mult: float = 1.0
@export var knock_mult: float = 1.0
## Regeneração por segundo, como fração da vida máxima.
@export var regen_pct: float = 0.0
@export var explode_on_death: bool = false
@export var explosion_radius: float = 90.0
@export var explosion_enemy_damage: float = 20.0
@export var explosion_player_damage: float = 18.0
