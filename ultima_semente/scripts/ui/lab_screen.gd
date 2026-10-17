class_name LabScreen
extends Control
## Laboratório de Adaptação (GDD 11): comprar e reverter mutações permanentes.
## Reverter custa exatamente os Núcleos pagos na compra, sem reembolso, e
## sempre pede confirmação mostrando o antes/depois dos atributos.
## Layout em scenes/ui/lab_screen.tscn; cada cartão em mutation_card.tscn.

signal back_pressed

@export var card_scene: PackedScene

var _pending_id: String = ""
var _pending_kind: String = ""
var columns: Dictionary = {}

@onready var nuc_label: Label = %NucLabel
@onready var msg_label: Label = %MsgLabel
@onready var col_defesa: VBoxContainer = %ColDefesa
@onready var col_predacao: VBoxContainer = %ColPredacao
@onready var col_ressonancia: VBoxContainer = %ColRessonancia
@onready var back_button: Button = %BackButton
@onready var confirm_dialog: Control = %ConfirmDialog
@onready var conf_title: Label = %ConfTitle
@onready var conf_name: Label = %ConfName
@onready var conf_cost: Label = %ConfCost
@onready var conf_adv: Label = %ConfAdv
@onready var conf_side: Label = %ConfSide
@onready var conf_diff: Label = %ConfDiff
@onready var conf_ok: Button = %ConfOk
@onready var conf_cancel: Button = %ConfCancel


func _ready() -> void:
	columns = {"defesa": col_defesa, "predacao": col_predacao, "ressonancia": col_ressonancia}
	back_button.pressed.connect(func() -> void: back_pressed.emit())
	conf_ok.pressed.connect(_do)
	conf_cancel.pressed.connect(_close_confirm)
	confirm_dialog.visible = false
	UIKit.wire_buttons(self)
	_refresh()


func _refresh() -> void:
	nuc_label.text = "Núcleos Primordiais: %d" % SaveManager.get_nuclei()
	for line in columns:
		var col: VBoxContainer = columns[line]
		# remove só os cartões (o cabeçalho da coluna é um Label estático)
		for ch in col.get_children():
			if ch is MutationCard:
				col.remove_child(ch)
				ch.queue_free()
		for id in GameData.mutation_order:
			var m: MutationData = GameData.permanent_mutations[id]
			if m.linha == line:
				var card: MutationCard = card_scene.instantiate() as MutationCard
				col.add_child(card)
				card.setup(m)
				card.action_requested.connect(_ask)
				UIKit.wire_buttons(card)


func _ask(id: String, kind: String) -> void:
	if confirm_dialog.visible:
		return
	var m: MutationData = GameData.permanent_mutations.get(id)
	if m == null:
		return
	_pending_id = id
	_pending_kind = kind
	var before_ids: Array = SaveManager.owned_ids()
	var after_ids: Array = before_ids.duplicate()
	var cost: int = 0
	if kind == "buy":
		after_ids.append(id)
		cost = m.custo
	else:
		after_ids.erase(id)
		cost = SaveManager.revert_cost(id)
	var before: Array = RunState.make_preview(before_ids).attribute_lines()
	var after: Array = RunState.make_preview(after_ids).attribute_lines()
	conf_title.text = "CONFIRMAR AQUISIÇÃO" if kind == "buy" else "CONFIRMAR REVERSÃO"
	conf_name.text = m.nome
	if kind == "buy":
		conf_cost.text = "Custo: %d Núcleos (você tem %d)" % [cost, SaveManager.get_nuclei()]
		conf_adv.text = "+ %s" % m.vantagem
		conf_adv.visible = true
		conf_side.text = "− %s" % m.efeito_colateral
		conf_side.visible = m.efeito_colateral != ""
	else:
		conf_cost.text = "Custo da reversão: %d Núcleos — o mesmo valor pago na compra. Você NÃO recebe os Núcleos de volta." % cost
		conf_adv.visible = false
		conf_side.visible = false
	var lines: Array = []
	for i in before.size():
		var b_val: String = str(before[i][1])
		var a_val: String = str(after[i][1])
		if b_val != a_val:
			lines.append("%s: %s → %s" % [str(before[i][0]), b_val, a_val])
	if lines.is_empty():
		conf_diff.text = "Sem mudança nos atributos numéricos (efeito especial)."
	else:
		conf_diff.text = "\n".join(lines)
	confirm_dialog.visible = true


func _close_confirm() -> void:
	confirm_dialog.visible = false
	_pending_id = ""


func _do() -> void:
	if _pending_id == "":
		return
	var res: Dictionary
	if _pending_kind == "buy":
		res = SaveManager.buy_mutation(_pending_id)
	else:
		res = SaveManager.revert_mutation(_pending_id)
	_close_confirm()
	msg_label.text = str(res["msg"])
	msg_label.add_theme_color_override("font_color", UIKit.COL_GOOD if bool(res["ok"]) else UIKit.COL_BAD)
	AudioManager.play_sfx("mutation" if bool(res["ok"]) else "error")
	_refresh()
