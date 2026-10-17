class_name GameOverScreen
extends Control
## Derrota (ou extração) com resumo da expedição.
## Layout e textos fixos em scenes/ui/game_over_screen.tscn.

signal restart_pressed
signal menu_pressed

@onready var title_label: Label = %Title
@onready var sub_label: Label = %SubLabel
@onready var val_time: Label = %ValTime
@onready var val_level: Label = %ValLevel
@onready var val_kills: Label = %ValKills
@onready var val_nests: Label = %ValNests
@onready var val_biomass: Label = %ValBiomass
@onready var val_records: Label = %ValRecords
@onready var val_nuclei: Label = %ValNuclei
@onready var val_nuclei_total: Label = %ValNucleiTotal
@onready var restart_button: Button = %RestartButton
@onready var menu_button: Button = %MenuButton


func _ready() -> void:
	restart_button.pressed.connect(func() -> void: restart_pressed.emit())
	menu_button.pressed.connect(func() -> void: menu_pressed.emit())
	UIKit.wire_buttons(self)


func setup(s: Dictionary) -> void:
	var reason: String = str(s.get("reason", "death"))
	var title: String = "EXPEDIÇÃO ENCERRADA"
	var sub: String = ""
	if reason == "death":
		title = "VOCÊ MORREU"
		var cause: String = str(s.get("cause", ""))
		if cause == "oxigênio":
			sub = "Causa: falta de oxigênio. Use os bolsões de ar e fique de olho na barra azul."
		elif cause == "esporos":
			sub = "Causa: zonas de esporos. Mantenha-se em movimento."
		else:
			sub = "Kael foi vencido pelas criaturas de Nymara."
	elif reason == "extract":
		title = "EXTRAÇÃO CONCLUÍDA"
		sub = "Kael voltou à nave. Biomassa não gasta e bônus temporários foram descartados."
	title_label.text = title
	sub_label.text = sub
	sub_label.visible = sub != ""
	val_time.text = GameManager.format_time(float(s.get("time", 0.0)))
	val_level.text = str(int(s.get("level", 1)))
	val_kills.text = str(int(s.get("kills", 0)))
	val_nests.text = str(int(s.get("nests", 0)))
	val_biomass.text = str(int(s.get("biomass_total", 0)))
	val_records.text = str(int(s.get("records", 0)))
	val_nuclei.text = str(int(s.get("nuclei_gained", 0)))
	val_nuclei_total.text = str(SaveManager.get_nuclei())
