class_name LevelUpMenu
extends Control
## Escolha de mutação temporária ao subir de nível (3 cartas).
## Layout em scenes/ui/level_up_menu.tscn; cada carta em level_up_card.tscn.

signal chosen(id: String)

@export var card_scene: PackedScene

var _cards: Array = []
var _enabled: bool = false

@onready var title_label: Label = %Title
@onready var cards_box: HBoxContainer = %Cards


func setup(state: RunState, options: Array) -> void:
	title_label.text = "NÍVEL %d — ESCOLHA UMA MUTAÇÃO" % state.level
	var idx: int = 1
	for o in options:
		var u: UpgradeData = o
		var card: LevelUpCard = card_scene.instantiate() as LevelUpCard
		cards_box.add_child(card)
		card.setup(u, state, idx)
		card.picked.connect(_pick)
		_cards.append(card)
		idx += 1
	UIKit.wire_buttons(self)
	# Evita cliques acidentais logo ao abrir.
	get_tree().create_timer(0.4, true).timeout.connect(_enable)


func _enable() -> void:
	_enabled = true
	for c in _cards:
		(c as LevelUpCard).set_enabled(true)


func _pick(id: String) -> void:
	if not _enabled:
		return
	_enabled = false
	chosen.emit(id)


func _unhandled_key_input(event: InputEvent) -> void:
	if not _enabled or not (event is InputEventKey):
		return
	var k: InputEventKey = event
	if not k.pressed or k.echo:
		return
	var i: int = -1
	if k.physical_keycode == KEY_1:
		i = 0
	elif k.physical_keycode == KEY_2:
		i = 1
	elif k.physical_keycode == KEY_3:
		i = 2
	if i >= 0 and i < _cards.size():
		get_viewport().set_input_as_handled()
		_pick((_cards[i] as LevelUpCard).upgrade_id)
