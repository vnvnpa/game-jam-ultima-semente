class_name MutationData
extends Resource
## Mutação permanente comprada com Núcleos Primordiais (GDD 11 e 16.5).

@export var id: String = ""
@export var nome: String = ""
## defesa, predacao ou ressonancia
@export var linha: String = "defesa"
@export_multiline var vantagem: String = ""
@export_multiline var efeito_colateral: String = ""
@export var custo: int = 2
## Ids de mutações que precisam estar ativas antes desta.
@export var prerequisitos: Array = []
## Ids de mutações incompatíveis com esta.
@export var incompativeis: Array = []
## Modificadores aditivos: { chave_de_atributo: valor }
@export var mods_add: Dictionary = {}
## Modificadores multiplicativos: { chave_de_atributo: fator }
@export var mods_mul: Dictionary = {}
## Efeito especial tratado em código (vazio se for apenas numérico).
@export var especial: String = ""
