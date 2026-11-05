class_name UpgradeData
extends Resource
## Mutação temporária escolhida ao subir de nível (vale só na expedição).

@export var id: String = ""
@export var nome: String = ""
## predacao, defesa ou ressonancia
@export var familia: String = "predacao"
@export var max_nivel: int = 5
@export_multiline var descricao: String = ""
@export_multiline var efeito_colateral: String = ""
## Aplicados uma vez por nível.
@export var mods_add: Dictionary = {}
@export var mods_mul: Dictionary = {}
@export var especial: String = ""
## Evoluções especiais só aparecem com requisitos cumpridos.
@export var evolucao: bool = false
@export var requer_familia: String = ""
## Id de outra melhoria que precisa estar escolhida antes desta aparecer.
@export var requer_upgrade: String = ""
