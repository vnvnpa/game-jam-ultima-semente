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
