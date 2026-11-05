class_name SfxEntry
extends Resource
## Um efeito sonoro do banco (data/audio/sfx_bank.tres).

@export var id: String = ""
@export var stream: AudioStream
@export var volume_db: float = 0.0
## Multiplicador de tom aplicado antes do pitch pedido por quem toca o som.
@export var pitch: float = 1.0
## Tempo mínimo entre duas execuções do mesmo som (evita estouro de volume).
@export var cooldown_ms: int = 35
