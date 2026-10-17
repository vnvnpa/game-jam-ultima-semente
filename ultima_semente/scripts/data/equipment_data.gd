class_name EquipmentData
extends Resource
## Equipamento de expedição: um traje e um módulo (GDD 10.2).

@export var id: String = ""
@export var nome: String = ""
## traje ou modulo
@export var slot: String = "traje"
@export var custo: int = 50
@export_multiline var vantagem: String = ""
@export_multiline var desvantagem: String = ""
@export var mods_add: Dictionary = {}
@export var mods_mul: Dictionary = {}
@export var especial: String = ""
