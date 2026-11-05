class_name WaveStage
extends Resource
## Uma etapa do tempo da expedição: quais inimigos surgem e em que quantidade.

@export var nome: String = "Aprendizado"
## Segundo em que a etapa começa.
@export var inicio: float = 0.0
## id do inimigo -> peso de sorteio.
@export var pesos: Dictionary = {}
## Inimigos criados por vez.
@export var lote: int = 1
@export var max_elites: int = 1
