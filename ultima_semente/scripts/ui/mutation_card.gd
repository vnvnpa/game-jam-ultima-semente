class_name MutationCard
extends PanelContainer
## Cartão de uma mutação permanente no Laboratório (scenes/ui/mutation_card.tscn).

signal action_requested(id: String, kind: String)

var mutation_id: String = ""
var _kind: String = "buy"

@onready var name_label: Label = %NameLabel
@onready var cost_label: Label = %CostLabel
@onready var adv_label: Label = %AdvLabel
@onready var side_label: Label = %SideLabel
@onready var req_label: Label = %ReqLabel
@onready var inc_label: Label = %IncLabel
@onready var action_button: Button = %ActionButton
@onready var note_label: Label = %NoteLabel


func _ready() -> void:
	action_button.pressed.connect(func() -> void: action_requested.emit(mutation_id, _kind))


func setup(m: MutationData) -> void:
	mutation_id = m.id
	var owned: bool = SaveManager.has_mutation(m.id)
	name_label.text = "%s%s" % ["✓ " if owned else "", m.nome]
	name_label.theme_type_variation = &"GoodLabel" if owned else &""
	if owned:
		theme_type_variation = &"OwnedCardPanel"
	cost_label.text = "Custo: %d Núcleos" % m.custo
	adv_label.text = "+ %s" % m.vantagem
	side_label.visible = m.efeito_colateral != ""
	side_label.text = "− %s" % m.efeito_colateral
	req_label.visible = m.prerequisitos.size() > 0
	if req_label.visible:
		var names: Array = []
		for pid in m.prerequisitos:
			var pm: MutationData = GameData.permanent_mutations.get(pid)
			names.append(pm.nome if pm != null else str(pid))
		req_label.text = "Requer: %s" % ", ".join(names)
	inc_label.visible = m.incompativeis.size() > 0
	if inc_label.visible:
		var inames: Array = []
		for iid in m.incompativeis:
			var im: MutationData = GameData.permanent_mutations.get(iid)
			inames.append(im.nome if im != null else str(iid))
		inc_label.text = "Incompatível com: %s" % ", ".join(inames)
	var note: String = ""
	if owned:
		_kind = "revert"
		var chk: Dictionary = SaveManager.can_revert_mutation(m.id)
		action_button.text = "Reverter (%d Núcleos)" % SaveManager.revert_cost(m.id)
		action_button.disabled = not bool(chk["ok"])
		note = str(chk["msg"])
	else:
		_kind = "buy"
		var chk2: Dictionary = SaveManager.can_buy_mutation(m.id)
		action_button.text = "Adquirir (%d Núcleos)" % m.custo
		action_button.disabled = not bool(chk2["ok"])
		note = str(chk2["msg"])
	note_label.visible = action_button.disabled and note != ""
	note_label.text = note
