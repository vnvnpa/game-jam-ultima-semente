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
	if str(_summary.get("level_id", "")) == "heart":
		return _heart_epilogue()
	var recs: int = (SaveManager.data["records"] as Array).size()
	var t: String = "O Jardineiro Vazio se desliga, e o Último Jardim respira pela primeira vez em séculos. "
	if recs >= 7:
		t += "Kael entendeu cada registro dos Arquitetos Verdes: a Rede Raiz não é cruel, apenas aterrorizada. "
	elif recs >= 4:
		t += "Kael reuniu o bastante para suspeitar que a Rede Raiz age por medo, não por maldade. "
	else:
		t += "Kael ainda tem mais perguntas que respostas sobre o que a Rede Raiz realmente quer. "
	t += "Sob as raízes, algo ainda pulsa: o Coração de Nymara espera."
	return t


## Epílogo do Coração de Nymara: depende da escolha final e dos registros lidos.
func _heart_epilogue() -> String:
	var recs: int = (SaveManager.data["records"] as Array).size()
	var t: String = ""
	if str(_summary.get("ending", "")) == "coexistir":
		t = "Kael abaixa a mão. A Última Semente não é plantada nem destruída: é entregue à Rede Raiz como um pacto. As raízes recuam das instalações e passam a crescer ao lado delas. "
		if recs >= 8:
			t += "Como Kael entendeu o medo da Rede, ela aprende a soltar: Nymara continua viva e estranha, e pela primeira vez não está sozinha."
		else:
			t += "Ninguém sabe se o pacto vai durar, mas, por ora, a Rede escuta."
	else:
		t = "Kael planta a Última Semente no coração da Rede. O modelo de um ecossistema inteiro se abre em raízes de luz e Nymara começa a se refazer. "
		if recs >= 8:
			t += "A Rede Raiz, que só queria impedir outro fim, descobre que crescer não é perder, e deixa a floresta voltar a ser livre."
		else:
			t += "A Rede resiste por um instante, depois cede. O que nascerá no lugar, só o tempo dirá."
	return t
