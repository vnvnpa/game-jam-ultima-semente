class_name SettingsPanel
extends Control
## Configurações: volumes independentes e opções de acessibilidade (GDD 15).
## Estrutura visual em scenes/ui/settings_panel.tscn.

signal back_pressed

@onready var music_slider: HSlider = %MusicSlider
@onready var sfx_slider: HSlider = %SfxSlider
@onready var reduce_fx_check: CheckBox = %ReduceFxCheck
@onready var damage_check: CheckBox = %DamageNumbersCheck
@onready var back_button: Button = %BackButton


func _ready() -> void:
	music_slider.value = float(SaveManager.get_setting("music"))
	sfx_slider.value = float(SaveManager.get_setting("sfx"))
	reduce_fx_check.button_pressed = bool(SaveManager.get_setting("reduce_fx"))
	damage_check.button_pressed = bool(SaveManager.get_setting("damage_numbers"))
	music_slider.value_changed.connect(_on_slider.bind("music"))
	sfx_slider.value_changed.connect(_on_slider.bind("sfx"))
	reduce_fx_check.toggled.connect(_on_check.bind("reduce_fx"))
	damage_check.toggled.connect(_on_check.bind("damage_numbers"))
	back_button.pressed.connect(func() -> void: back_pressed.emit())
	UIKit.wire_buttons(self)


func _on_slider(v: float, key: String) -> void:
	SaveManager.set_setting(key, v)
	AudioManager.apply_volumes()


func _on_check(v: bool, key: String) -> void:
	SaveManager.set_setting(key, v)
