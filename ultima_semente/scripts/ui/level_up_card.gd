class_name LevelUpCard
extends PanelContainer
## Carta de uma mutação temporária (scenes/ui/level_up_card.tscn).

signal picked(id: String)

var upgrade_id: String = ""

@onready var family_label: Label = %FamilyLabel
@onready var name_label: Label = %NameLabel
@onready var level_label: Label = %LevelLabel
@onready var desc_label: Label = %DescLabel
@onready var side_label: Label = %SideLabel
@onready var pick_button: Button = %PickButton


func _ready() -> void:
	pick_button.pressed.connect(func() -> void: picked.emit(upgrade_id))


func setup(u: UpgradeData, state: RunState, index: int) -> void:
	upgrade_id = u.id
	if u.evolucao:
		theme_type_variation = &"EvoCardPanel"
	var fam: String = "EVOLUÇÃO — " if u.evolucao else ""
	family_label.text = "%s%s" % [fam, MutationManager.family_label(u.familia)]
	name_label.text = u.nome
	var lv: int = state.upgrade_level(u.id)
	level_label.text = "Nível %d → %d (máx. %d)" % [lv, lv + 1, u.max_nivel]
	desc_label.text = u.descricao
	side_label.visible = u.efeito_colateral != ""
	side_label.text = "Efeito colateral: %s" % u.efeito_colateral
	pick_button.text = "Escolher [%d]" % index
	pick_button.disabled = true


func set_enabled(v: bool) -> void:
	pick_button.disabled = not v
