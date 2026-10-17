class_name CreditsScreen
extends Control
## Créditos (GDD 14.4 e 22). Concluir e ver os créditos nunca depende de
## pagar. O botão de apoio só existe se GameConfig.ITCH_URL estiver preenchido.
## Textos e layout em scenes/ui/credits_screen.tscn.

signal back_pressed

@onready var creator_label: Label = %CreatorLabel
@onready var contact_label: Label = %ContactLabel
@onready var support_button: Button = %SupportButton
@onready var back_button: Button = %BackButton


func _ready() -> void:
	creator_label.text = "Criado por %s" % GameConfig.CREATOR
	contact_label.text = "Contato: %s" % GameConfig.CONTACT_EMAIL
	support_button.visible = GameConfig.ITCH_URL != ""
	support_button.pressed.connect(func() -> void: OS.shell_open(GameConfig.ITCH_URL))
	back_button.pressed.connect(func() -> void: back_pressed.emit())
	UIKit.wire_buttons(self)
