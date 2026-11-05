class_name ThreatEventData
extends Resource
## Evento de ameaça cronometrado (enxame, crise...). Ordem de exibição = nome do arquivo.

@export var id: String = ""
@export var titulo: String = "ENXAME"
## Segundo da expedição em que começa (multiplicado por event_time_mult).
@export var tempo: float = 540.0
@export var duracao: float = 40.0
## Intervalo entre levas de inimigos e tamanho base de cada leva.
@export var intervalo_surgimento: float = 3.0
@export var tamanho_base: float = 4.0
@export var dist_min: float = 300.0
@export var dist_max: float = 560.0
## Inimigos extras permitidos em cena enquanto o evento dura.
@export var impulso_limite: int = 12
@export var recompensa_min: int = 10
@export var recompensa_max: int = 25
@export var elite_no_inicio: bool = false
