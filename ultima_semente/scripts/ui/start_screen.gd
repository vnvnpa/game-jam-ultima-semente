class_name StartScreen
extends Control
## Preparação da expedição: objetivo, controles e mutações ativas.
## Textos e layout em scenes/ui/start_screen.tscn.

signal start_pressed
signal back_pressed

@onready var mutations_label: Label = %MutationsLabel
@onready var start_button: Button = %StartButton
@onready var back_button: Button = %BackButton


func _ready() -> void:
	var names: Array = []
	for id in SaveManager.owned_ids():
		var mu: MutationData = GameData.permanent_mutations.get(id)
		if mu != null:
			names.append(mu.nome)
	var txt: String = "Mutações permanentes ativas: "
	txt += ", ".join(names) if names.size() > 0 else "nenhuma"
	mutations_label.text = txt
	start_button.pressed.connect(func() -> void: start_pressed.emit())
	back_button.pressed.connect(func() -> void: back_pressed.emit())
	UIKit.wire_buttons(self)
