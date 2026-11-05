class_name BuffData
extends Resource
## Efeito temporário (comprado na loja ou disparado por mutações).

@export var id: String = ""
## Nome mostrado no HUD.
@export var nome: String = ""
## Duração padrão em segundos.
@export var duracao: float = 30.0
@export var mods_add: Dictionary = {}
@export var mods_mul: Dictionary = {}
@export var especial: String = ""
