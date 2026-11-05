class_name MainMenuScreen
extends Control
## Menu principal com fundo animado de esporos (desenhado em _draw).
## Layout, textos e botões em scenes/ui/main_menu.tscn.

signal action(id: String)

const MENU_GROW: float = 1.18

@export var draw_backdrop: bool = true

var _t: float = 0.0
var _spores: Array = []

@onready var status_label: Label = %StatusLabel
@onready var notice_label: Label = %NoticeLabel
@onready var version_label: Label = %VersionLabel
@onready var play_button: Button = %PlayButton
@onready var garden_button: Button = %GardenButton
@onready var heart_button: Button = %HeartButton
@onready var lab_button: Button = %LabButton
@onready var codex_button: Button = %CodexButton
@onready var settings_button: Button = %SettingsButton
@onready var credits_button: Button = %CreditsButton
@onready var quit_button: Button = %QuitButton


func _ready() -> void:
	for i in 70:
		_spores.append({"x": randf(), "y": randf(), "s": randf_range(0.01, 0.04), "r": randf_range(1.5, 4.0), "c": randf()})
	var total: int = GameData.mutation_order.size()
	var owned: int = SaveManager.owned_ids().size()
	status_label.text = "Núcleos Primordiais: %d   •   Mutações permanentes: %d/%d" % [SaveManager.get_nuclei(), owned, total]
	notice_label.text = SaveManager.load_notice
	notice_label.visible = SaveManager.load_notice != ""
	version_label.text = "v%s  •  Criado por %s" % [GameConfig.GAME_VERSION, GameConfig.CREATOR]
	quit_button.visible = not GameManager.is_web()
	_bind(play_button, "play")
	garden_button.visible = SaveManager.is_garden_unlocked()
	_bind(garden_button, "garden")
	heart_button.visible = SaveManager.is_heart_unlocked()
	_bind(heart_button, "heart")
	_bind(lab_button, "lab")
	_bind(codex_button, "codex")
	_bind(settings_button, "settings")
	_bind(credits_button, "credits")
	_bind(quit_button, "quit")
	for b in [play_button, garden_button, heart_button, lab_button, codex_button, settings_button, credits_button, quit_button]:
		_make_selectable(b)
	play_button.call_deferred("grab_focus")
	UIKit.wire_buttons(self)


## Botão do menu: pequeno, alinhado à esquerda; cresce quando selecionado
## (mouse por cima ou foco do teclado: setas/Tab + Enter).
func _make_selectable(b: Button) -> void:
	b.focus_mode = Control.FOCUS_ALL
	b.pivot_offset = Vector2(0.0, b.size.y * 0.5)
	b.resized.connect(_update_pivot.bind(b))
	b.mouse_entered.connect(b.grab_focus)
	b.focus_entered.connect(_grow.bind(b, MENU_GROW))
	b.focus_exited.connect(_grow.bind(b, 1.0))


func _update_pivot(b: Button) -> void:
	b.pivot_offset = Vector2(0.0, b.size.y * 0.5)


func _grow(b: Button, k: float) -> void:
	if b.has_meta("grow_tween"):
		var old: Variant = b.get_meta("grow_tween")
		if old is Tween and (old as Tween).is_valid():
			(old as Tween).kill()
	var tw: Tween = create_tween()
	tw.tween_property(b, "scale", Vector2(k, k), 0.12).set_trans(Tween.TRANS_SINE)
	b.set_meta("grow_tween", tw)


func _bind(b: Button, id: String) -> void:
	b.pressed.connect(func() -> void: action.emit(id))


func _process(delta: float) -> void:
	_t += delta
	queue_redraw()


func _draw() -> void:
	var vs: Vector2 = size
	if draw_backdrop:
		_draw_backdrop(vs)
	_draw_spores(vs)


func _draw_backdrop(vs: Vector2) -> void:
	draw_rect(Rect2(Vector2.ZERO, vs), Color(0.02, 0.05, 0.05))
	draw_circle(Vector2(vs.x * 0.78, vs.y * 0.55), vs.y * 0.55, Color(0.08, 0.2, 0.18, 0.5))
	draw_circle(Vector2(vs.x * 0.78, vs.y * 0.55), vs.y * 0.35, Color(0.1, 0.3, 0.26, 0.5))
	var pulse: float = 0.85 + 0.15 * sin(_t * 1.6)
	var c: Vector2 = Vector2(vs.x * 0.78, vs.y * 0.55)
	draw_circle(c, 90.0 * pulse, Color(0.3, 0.9, 0.9, 0.18))
	draw_circle(c, 56.0 * pulse, Color(0.4, 0.95, 0.85, 0.35))
	draw_circle(c, 30.0, Color(0.7, 1.0, 1.0, 0.9))
	for i in 8:
		var a: float = float(i) * TAU / 8.0 + _t * 0.2
		draw_line(c + Vector2.from_angle(a) * 100.0, c + Vector2.from_angle(a) * (150.0 + 20.0 * sin(_t + float(i))), Color(0.75, 0.4, 0.9, 0.7), 4.0)


func _draw_spores(vs: Vector2) -> void:
	for sp in _spores:
		var yy: float = fmod(float(sp["y"]) - _t * float(sp["s"]) + 10.0, 1.0)
		var xx: float = float(sp["x"]) + sin(_t * 0.5 + float(sp["c"]) * 6.0) * 0.01
		var col: Color = Color(0.5, 1.0, 0.7, 0.5) if float(sp["c"]) < 0.5 else Color(0.8, 0.5, 1.0, 0.5)
		draw_circle(Vector2(xx * vs.x, yy * vs.y), float(sp["r"]), col)
