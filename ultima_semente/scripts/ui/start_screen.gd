class_name StartScreen
extends Control
## Preparação da expedição: objetivo, controles e mutações ativas.
## Textos e layout em scenes/ui/start_screen.tscn.

signal start_pressed
signal back_pressed

@onready var controls_label: Label = %Controls
@onready var mutations_label: Label = %MutationsLabel
@onready var start_button: Button = %StartButton
@onready var back_button: Button = %BackButton


func _move_keys_text() -> String:
	var names: Array = []
	var single: bool = true
	for a in ["move_up", "move_left", "move_down", "move_right"]:
		var n: String = GameManager.key_text(a)
		if n.length() != 1:
			single = false
		names.append(n)
	return "".join(names) if single else "/".join(names)


func _controls_text() -> String:
	var l1: String = "%s / Setas: mover   •   Mouse: mirar   •   A arma dispara sozinha no inimigo mais próximo" % _move_keys_text()
	var l2: String = "%s: Pulso de Raízes   •   %s: Ruptura Celular (arrancada)   •   %s: Pulso de Emergência" % [GameManager.key_text("skill_1"), GameManager.key_text("skill_2"), GameManager.key_text("use_pulse")]
	var l3: String = "%s: interagir (terminais, ruínas)   •   %s: mapa   •   Esc: pausa   •   Teclas ajustáveis em Configurações" % [GameManager.key_text("interact"), GameManager.key_text("map")]
	return "%s\n%s\n%s" % [l1, l2, l3]


func _ready() -> void:
	controls_label.text = _controls_text()
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
