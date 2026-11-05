class_name DecisionScreen
extends Control
## Escolha final do Coração de Nymara (GDD 14.2, etapa 3 "Decisão").
## Layout em scenes/ui/decision_screen.tscn. Emite `chosen("restaurar" | "coexistir")`.

signal chosen(id: String)

var _enabled: bool = false

@onready var hint_label: Label = %Hint
@onready var restore_button: Button = %RestoreButton
@onready var spare_button: Button = %SpareButton


func _ready() -> void:
	restore_button.disabled = true
	spare_button.disabled = true
	restore_button.pressed.connect(_pick.bind("restaurar"))
	spare_button.pressed.connect(_pick.bind("coexistir"))
	UIKit.wire_buttons(self)
	# Evita cliques acidentais logo ao abrir.
	get_tree().create_timer(0.8, true).timeout.connect(_enable)


func setup(records: int) -> void:
	hint_label.text = "Registros descobertos: %d. Quanto mais você entendeu a Rede Raiz, mais o desfecho reflete isso." % records


func _enable() -> void:
	_enabled = true
	restore_button.disabled = false
	spare_button.disabled = false
	if Input.get_connected_joypads().size() > 0:
		restore_button.grab_focus()


func _pick(id: String) -> void:
	if not _enabled:
		return
	_enabled = false
	chosen.emit(id)
