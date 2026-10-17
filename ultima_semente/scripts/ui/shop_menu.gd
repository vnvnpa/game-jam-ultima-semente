class_name ShopMenu
extends Control
## Terminal de suprimentos: lista, detalhes (preço, efeito e limitação na
## mesma tela) e confirmação explícita antes de comprar (GDD 10.3).
## Layout em scenes/ui/shop_menu.tscn.

signal closed

@export var list_button_scene: PackedScene

var run: Run = null
var tid: String = ""
var tab: String = "supplies"
var selected: String = ""

@onready var bio_label: Label = %BioLabel
@onready var supplies_tab: Button = %SuppliesTab
@onready var equip_tab: Button = %EquipTab
@onready var list_box: VBoxContainer = %ListBox
@onready var detail_hint: Label = %DetailHint
@onready var detail_body: VBoxContainer = %DetailBody
@onready var detail_name: Label = %DetailName
@onready var detail_slot: Label = %DetailSlot
@onready var detail_adv: Label = %DetailAdv
@onready var detail_side: Label = %DetailSide
@onready var detail_extra: Label = %DetailExtra
@onready var detail_price: Label = %DetailPrice
@onready var buy_button: Button = %BuyButton
@onready var detail_reason: Label = %DetailReason
@onready var msg_label: Label = %MsgLabel
@onready var close_button: Button = %CloseButton


func _ready() -> void:
	supplies_tab.pressed.connect(_set_tab.bind("supplies"))
	equip_tab.pressed.connect(_set_tab.bind("equipment"))
	buy_button.pressed.connect(_confirm)
	close_button.pressed.connect(func() -> void: closed.emit())
	UIKit.wire_buttons(self)


func setup(r: Run, terminal_id: String) -> void:
	run = r
	tid = terminal_id
	msg_label.text = ""
	_refresh()


func _set_tab(t: String) -> void:
	tab = t
	selected = ""
	msg_label.text = ""
	_refresh()


func _select(id: String) -> void:
	selected = id
	_refresh()


func _ids_for_tab() -> Array:
	if tab == "equipment":
		return GameData.equipment_order
	return run.shop.get_terminal(tid)["offers"]


func _refresh() -> void:
	bio_label.text = "Biomassa: %d" % run.state.biomass
	supplies_tab.disabled = (tab == "supplies")
	equip_tab.disabled = (tab == "equipment")
	UIKit.clear_children(list_box)
	for id in _ids_for_tab():
		var sid: String = str(id)
		var label: String = ""
		var cost: int = 0
		if tab == "equipment":
			var eq: EquipmentData = GameData.equipment[sid]
			cost = eq.custo
			var equipped: bool = (run.state.equip_traje == sid or run.state.equip_modulo == sid)
			label = "%s%s — %d" % ["✓ " if equipped else "", eq.nome, cost]
		else:
			var it: ShopItemData = GameData.shop_items[sid]
			cost = it.custo
			label = "%s — %d" % [it.nome, cost]
		var b: Button = list_button_scene.instantiate() as Button
		b.text = label
		if sid == selected:
			b.add_theme_color_override("font_color", UIKit.COL_WARN)
		if run.state.biomass < cost:
			b.add_theme_color_override("font_color", Color(0.6, 0.45, 0.45))
		b.pressed.connect(_select.bind(sid))
		list_box.add_child(b)
	UIKit.wire_buttons(list_box)
	_refresh_detail()


func _refresh_detail() -> void:
	if selected == "" or not _ids_for_tab().has(selected):
		detail_hint.visible = true
		detail_body.visible = false
		return
	detail_hint.visible = false
	detail_body.visible = true
	var cost: int = 0
	var can: bool = true
	var reason: String = ""
	detail_extra.visible = false
	if tab == "equipment":
		var eq: EquipmentData = GameData.equipment[selected]
		cost = eq.custo
		detail_name.text = eq.nome
		detail_slot.text = "Espaço: %s" % ("traje" if eq.slot == "traje" else "módulo")
		detail_adv.text = "Vantagem: %s" % eq.vantagem
		detail_side.text = "Desvantagem: %s" % eq.desvantagem
		var current: String = run.state.equip_traje if eq.slot == "traje" else run.state.equip_modulo
		if current == selected:
			can = false
			reason = "Já equipado."
		elif current != "":
			var cur: EquipmentData = GameData.equipment[current]
			detail_extra.text = "Substituirá: %s (sem reembolso)." % cur.nome
			detail_extra.visible = true
	else:
		var it: ShopItemData = GameData.shop_items[selected]
		cost = it.custo
		var used: int = run.shop.bought_count(tid, selected)
		detail_name.text = it.nome
		detail_slot.text = "Comprado nesta visita: %d/%d" % [used, it.limite_por_visita]
		detail_adv.text = "Efeito: %s" % it.efeito
		detail_side.text = "Limitação: %s" % it.limitacao
		if used >= it.limite_por_visita:
			can = false
			reason = "Limite por visita atingido."
	detail_price.text = "Preço: %d Biomassa" % cost
	if can and run.state.biomass < cost:
		can = false
		reason = "Biomassa insuficiente (faltam %d)." % (cost - run.state.biomass)
	buy_button.text = "Confirmar compra (%d)" % cost
	buy_button.disabled = not can
	detail_reason.visible = not can
	detail_reason.text = reason


func _confirm() -> void:
	if selected == "":
		return
	var res: Dictionary
	if tab == "equipment":
		res = run.shop.buy_equipment(selected)
	else:
		res = run.shop.buy_item(tid, selected)
	msg_label.text = str(res["msg"])
	msg_label.add_theme_color_override("font_color", UIKit.COL_GOOD if bool(res["ok"]) else UIKit.COL_BAD)
	if not bool(res["ok"]):
		AudioManager.play_sfx("error")
	_refresh()
