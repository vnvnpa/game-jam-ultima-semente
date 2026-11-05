class_name HUD
extends Control
## HUD da expedição (GDD 15): vida, oxigênio, XP, recursos, tempo, etapa,
## habilidades e recargas, alertas, barra de chefe e objetivo atual.

@export var alert_scene: PackedScene

var run: Run = null
var alerts: Array = []
var _t: float = 0.0

@onready var o2_vignette: TextureRect = %O2Vignette
@onready var hurt_vignette: TextureRect = %HurtVignette
@onready var hp_label: Label = %HpLabel
@onready var hp_bar: ProgressBar = %HpBar
@onready var o2_row: VBoxContainer = %O2Row
@onready var o2_label: Label = %O2Label
@onready var o2_bar: ProgressBar = %O2Bar
@onready var zone_label: Label = %ZoneLabel
@onready var objective_label: Label = %ObjectiveLabel
@onready var buff_label: Label = %BuffLabel
@onready var time_label: Label = %TimeLabel
@onready var stage_label: Label = %StageLabel
@onready var region_label: Label = %RegionLabel
@onready var bio_label: Label = %BioLabel
@onready var nuc_label: Label = %NucLabel
@onready var boss_panel: PanelContainer = %BossPanel
@onready var boss_label: Label = %BossLabel
@onready var boss_bar: ProgressBar = %BossBar
@onready var event_label: Label = %EventLabel
@onready var alerts_box: VBoxContainer = %Alerts
@onready var prompt_label: Label = %PromptLabel
@onready var xp_label: Label = %XpLabel
@onready var xp_bar: ProgressBar = %XpBar
@onready var pulse_label: Label = %PulseLabel
@onready var dash_label: Label = %DashLabel
@onready var emerg_label: Label = %EmergLabel
@onready var pulse_box: Control = %PulseBox
@onready var dash_box: Control = %DashBox
@onready var emerg_box: Control = %EmergBox
@onready var cloud_label: Label = %CloudLabel
@onready var cloud_box: Control = %CloudBox
@onready var hint_label: Label = %HintLabel


## Chamado pelo Run depois que o HUD já está pronto na árvore.
func setup(r: Run) -> void:
	run = r
	boss_panel.visible = false


func set_prompt(text: String) -> void:
	if prompt_label != null:
		prompt_label.text = text


func push_alert(text: String, color: Color) -> void:
	if alerts_box == null:
		return
	var l: Label = alert_scene.instantiate() as Label
	l.text = text
	l.add_theme_color_override("font_color", color)
	alerts_box.add_child(l)
	alerts.append({"node": l, "ttl": 4.5})
	while alerts.size() > 4:
		var old: Dictionary = alerts.pop_front()
		(old["node"] as Label).queue_free()


func _process(delta: float) -> void:
	if get_tree().paused:
		return
	_t += delta
	var keep: Array = []
	for a in alerts:
		a["ttl"] = float(a["ttl"]) - delta
		var n: Label = a["node"]
		if float(a["ttl"]) <= 0.0:
			n.queue_free()
		else:
			n.modulate.a = clampf(float(a["ttl"]) / 0.8, 0.0, 1.0)
			keep.append(a)
	alerts = keep


func _buff_name(id: String) -> String:
	var bd: BuffData = GameData.buffs.get(id)
	return bd.nome if bd != null else id


func _cd_text(cd: float, cd_max: float, title: String) -> String:
	if cd > 0.05:
		return "%s\n%.1fs" % [title, cd]
	return "%s\nPRONTO" % title


func refresh(r: Run) -> void:
	if r == null or r.player == null:
		return
	var st: RunState = r.state
	var pl: Player = r.player
	var maxhp: float = st.max_hp()
	hp_bar.value = clampf(pl.hp / maxhp, 0.0, 1.0)
	var shield_txt: String = ("  (+%d escudo)" % roundi(pl.shield)) if pl.shield > 0.5 else ""
	hp_label.text = "Vida %d/%d%s" % [roundi(pl.hp), roundi(maxhp), shield_txt]
	var ox: OxygenManager = r.oxygen
	o2_bar.value = ox.ratio()
	o2_label.text = "Oxigênio %d%%" % roundi(ox.ratio() * 100.0)
	o2_row.visible = ox.zone == "hostil" or ox.ratio() < 0.999
	if ox.ratio() <= 0.15:
		o2_bar.modulate = Color(1, 0.5, 0.5) if int(_t * 4.0) % 2 == 0 else Color(1, 1, 1)
	else:
		o2_bar.modulate = Color(1, 1, 1)
	var pos: Vector2 = pl.global_position
	region_label.text = WorldLayout.region_name(pos)
	if ox.zone == "hostil":
		zone_label.text = "ZONA CONTAMINADA — oxigênio em consumo"
		zone_label.add_theme_color_override("font_color", UIKit.COL_BAD)
	elif ox.zone == "pressurizado":
		zone_label.text = "Ar pressurizado — recarregando"
		zone_label.add_theme_color_override("font_color", UIKit.COL_NUC)
	else:
		zone_label.text = "Ar respirável"
		zone_label.add_theme_color_override("font_color", UIKit.COL_DIM)
	var need: int = RunState.xp_needed(st.level)
	xp_bar.value = clampf(float(st.xp) / float(need), 0.0, 1.0)
	xp_label.text = "Nível %d  —  XP %d/%d" % [st.level, st.xp, need]
	bio_label.text = "Biomassa: %d" % st.biomass
	nuc_label.text = "Núcleos: %d" % SaveManager.get_nuclei()
	time_label.text = GameManager.format_time(st.run_time)
	stage_label.text = "Etapa: %s" % r.director.stage_name_at(st.run_time + r.director.time_offset)
	# objetivo
	objective_label.text = r.objective_text()
	# buffs
	var parts: Array = []
	for id in st.buffs:
		parts.append("%s %ds" % [_buff_name(str(id)), ceili(float(st.buffs[id]))])
	buff_label.text = " | ".join(parts)
	# habilidades
	pulse_label.text = _cd_text(pl.pulse_cd, pl.pulse_cd_max, "[%s] Pulso" % GameManager.key_text("skill_1"))
	dash_label.text = _cd_text(pl.dash_cd, pl.dash_cd_max, "[%s] Ruptura" % GameManager.key_text("skill_2"))
	emerg_label.text = "[%s] Emergência\n×%d" % [GameManager.key_text("use_pulse"), st.pulse_charges]
	hint_label.text = "[%s] Mapa   [Esc] Pausa" % GameManager.key_text("map")
	pulse_box.modulate.a = 0.55 if pl.pulse_cd > 0.05 else 1.0
	dash_box.modulate.a = 0.55 if pl.dash_cd > 0.05 else 1.0
	emerg_box.modulate.a = 1.0 if st.pulse_charges > 0 else 0.4
	cloud_box.visible = st.has_special("nuvem_esporos")
	if cloud_box.visible:
		cloud_label.text = _cd_text(pl.cloud_cd, pl.cloud_cd_max, "[%s] Nuvem" % GameManager.key_text("skill_3"))
		cloud_box.modulate.a = 0.55 if pl.cloud_cd > 0.05 else 1.0
	# chefe
	if r.boss_active and r.boss != null and is_instance_valid(r.boss) and r.boss.alive:
		boss_panel.visible = true
		boss_bar.value = clampf(r.boss.hp / r.boss.max_hp, 0.0, 1.0)
		boss_label.text = "%s — Fase %d" % [r.boss.data.nome, (r.boss as Boss).phase]
	else:
		boss_panel.visible = false
	# evento
	if r.events.active:
		event_label.text = "%s — %ds" % [r.events.title(), ceili(r.events.remaining)]
	else:
		event_label.text = ""
	# vinhetas
	o2_vignette.modulate.a = ox.danger_level() * 0.7
	var low: float = clampf((0.35 - pl.hp / maxhp) / 0.35, 0.0, 1.0)
	var pulse: float = 0.75 + 0.25 * sin(_t * 6.0)
	if GameManager.reduce_fx():
		pulse = 1.0
	hurt_vignette.modulate.a = low * 0.55 * pulse + pl.hurt_flash * 0.3
