class_name VictoryScreen
extends Control
## Epílogo curto → tela "PARABÉNS!" → créditos (GDD 14.3). Só é criada
## depois que o chefe foi derrotado (Run.end_run valida isso).
## As três páginas são filhos de scenes/ui/victory_screen.tscn.

signal menu_pressed

var _summary: Dictionary = {}

@onready var epilogue: Control = %Epilogue
@onready var congrats: Control = %Congrats
@onready var credits: CreditsScreen = %Credits
@onready var epilogue_text: Label = %EpilogueText
@onready var congrats_stats: Label = %CongratsStats
@onready var continue_button: Button = %ContinueButton
@onready var credits_button: Button = %CreditsButton
@onready var menu_button: Button = %MenuButton


func _ready() -> void:
	continue_button.pressed.connect(_show_congrats)
	credits_button.pressed.connect(_show_credits)
	menu_button.pressed.connect(func() -> void: menu_pressed.emit())
	credits.back_pressed.connect(func() -> void: menu_pressed.emit())
	_show_page(epilogue)
	UIKit.wire_buttons(self)


func setup(s: Dictionary) -> void:
	_summary = s
	epilogue_text.text = _epilogue_text()
	congrats_stats.text = "Tempo: %s   •   Nível: %d   •   Criaturas: %d" % [GameManager.format_time(float(s.get("time", 0.0))), int(s.get("level", 1)), int(s.get("kills", 0))]


func _show_page(page: Control) -> void:
	epilogue.visible = (page == epilogue)
	congrats.visible = (page == congrats)
	credits.visible = (page == credits)


func _show_congrats() -> void:
	_show_page(congrats)


func _show_credits() -> void:
	_show_page(credits)


func _epilogue_text() -> String:
	var recs: int = (SaveManager.data["records"] as Array).size()
	var nests: int = int(_summary.get("nests", 0))
	var t: String = "O Guardião de Raízes desaba, e o Santuário respira pela primeira vez em séculos. "
	if recs >= 5:
		t += "Kael entendeu cada registro dos Arquitetos Verdes: a Rede Raiz não é cruel, apenas aterrorizada. "
	elif recs >= 3:
		t += "Kael reuniu o bastante para suspeitar que a Rede Raiz age por medo, não por maldade. "
	else:
		t += "Kael ainda tem mais perguntas que respostas sobre o que a Rede Raiz realmente quer. "
	if nests >= 3:
		t += "Os ninhos silenciaram, e a floresta ao redor parece cicatrizar."
	else:
		t += "Ao longe, raízes ainda pulsam no escuro."
	return t
