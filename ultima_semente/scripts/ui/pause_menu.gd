class_name PauseMenu
extends Control
## Menu de pausa. Abandonar exige confirmação (segundo clique).
## Estrutura em scenes/ui/pause_menu.tscn (inclui o painel de configurações).

signal resume_pressed
signal abandon_pressed

var _confirming: bool = false

@onready var resume_button: Button = %ResumeButton
@onready var settings_button: Button = %SettingsButton
@onready var abandon_button: Button = %AbandonButton
@onready var settings: SettingsPanel = %Settings


func _ready() -> void:
	settings.visible = false
	resume_button.pressed.connect(func() -> void: resume_pressed.emit())
	settings_button.pressed.connect(func() -> void: settings.visible = true)
	settings.back_pressed.connect(func() -> void: settings.visible = false)
	abandon_button.pressed.connect(_on_abandon)
	UIKit.wire_buttons(self)


func _on_abandon() -> void:
	if not _confirming:
		_confirming = true
		abandon_button.text = "Clique de novo para confirmar"
		return
	abandon_pressed.emit()
