class_name LevelCompleteScreen
extends Control
## Fim da expedição regional (Guardião de Raízes derrotado): libera o
## Santuário do Último Jardim. Layout em scenes/ui/level_complete_screen.tscn.

signal garden_pressed
signal menu_pressed

@onready var stats_label: Label = %StatsLabel
@onready var garden_button: Button = %GardenButton
@onready var menu_button: Button = %MenuButton


func _ready() -> void:
	garden_button.pressed.connect(func() -> void: garden_pressed.emit())
	menu_button.pressed.connect(func() -> void: menu_pressed.emit())
	UIKit.wire_buttons(self)


func setup(s: Dictionary) -> void:
	stats_label.text = "Tempo: %s   •   Nível: %d   •   Criaturas: %d   •   Ninhos: %d" % [
		GameManager.format_time(float(s.get("time", 0.0))),
		int(s.get("level", 1)), int(s.get("kills", 0)), int(s.get("nests", 0))]
