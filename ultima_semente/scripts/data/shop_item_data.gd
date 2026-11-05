class_name ShopItemData
extends Resource
## Item consumível/temporário vendido em terminais (GDD 10.1).

@export var id: String = ""
@export var nome: String = ""
@export var custo: int = 20
@export_multiline var efeito: String = ""
@export_multiline var limitacao: String = ""
## Quantas vezes pode ser comprado por visita ao terminal.
@export var limite_por_visita: int = 3

## Como o item age: cura, buff, oxigenio, flag, escudo, isca ou carga_pulso.
@export var tipo: String = "buff"
## cura/oxigenio: fração (0.35 = 35%); escudo: quantidade.
@export var valor: float = 0.0
## escudo: teto do escudo; carga_pulso: máximo de cargas.
@export var valor_max: float = 0.0
## tipo buff: id do BuffData aplicado (a duração vem do buff).
@export var buff_id: String = ""
## tipo flag: modificadores permanentes na expedição (ex.: Módulo de Mira).
@export var mods_add: Dictionary = {}
@export var mods_mul: Dictionary = {}
## Sempre aparece nas ofertas do terminal (os demais são sorteados).
@export var sempre_oferecido: bool = false
