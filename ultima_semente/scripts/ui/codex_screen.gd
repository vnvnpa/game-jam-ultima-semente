class_name CodexScreen
extends Control
## Arquivo biológico: criaturas, mutações e registros descobertos.
## Layout em scenes/ui/codex_screen.tscn; entradas em codex_entry.tscn.

signal back_pressed

@export var entry_scene: PackedScene

@onready var tabs: TabContainer = %Tabs
@onready var enemy_list: VBoxContainer = %EnemyList
@onready var mutation_list: VBoxContainer = %MutationList
@onready var record_list: VBoxContainer = %RecordList
@onready var back_button: Button = %BackButton


func _ready() -> void:
	tabs.set_tab_title(0, "Criaturas")
	tabs.set_tab_title(1, "Mutações")
	tabs.set_tab_title(2, "Registros")
	back_button.pressed.connect(func() -> void: back_pressed.emit())
	_fill_enemies()
	_fill_mutations()
	_fill_records()
	UIKit.wire_buttons(self)


func _add(list: VBoxContainer, title: String, body: String, locked: bool = false) -> void:
	var e: CodexEntry = entry_scene.instantiate() as CodexEntry
	list.add_child(e)
	e.setup(title, body, locked)
	list.add_child(HSeparator.new())


func _fill_enemies() -> void:
	for id in GameData.enemies:
		var e: EnemyData = GameData.enemies[id]
		if SaveManager.has_codex_enemy(str(id)):
			_add(enemy_list, e.nome, "%s\nVida %d • Dano %d • Velocidade %d" % [e.descricao, roundi(e.vida_maxima), roundi(e.dano), roundi(e.velocidade)])
		else:
			_add(enemy_list, "??? — ainda não encontrado", "", true)


func _fill_mutations() -> void:
	for id in GameData.mutation_order:
		var m: MutationData = GameData.permanent_mutations[id]
		var owned: bool = SaveManager.has_mutation(str(id))
		_add(mutation_list, "%s%s  (%s)" % ["✓ " if owned else "", m.nome, GameData.LINE_NAMES[m.linha]], "Vantagem: %s\nEfeito colateral: %s" % [m.vantagem, m.efeito_colateral])


func _fill_records() -> void:
	for id in GameData.record_order:
		if SaveManager.has_record(str(id)):
			var r: Dictionary = GameData.records[id]
			_add(record_list, str(r["titulo"]), str(r["texto"]))
		else:
			_add(record_list, "Registro não descoberto", "", true)
