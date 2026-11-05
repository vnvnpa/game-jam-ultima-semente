extends Node
## Cena principal (scenes/main/main.tscn): alterna entre menus e expedição, e
## pausa a expedição quando a janela/aba do navegador perde o foco.
## As cenas de cada tela são configuradas nas propriedades exportadas.

@export var main_menu_scene: PackedScene
@export var start_scene: PackedScene
@export var lab_scene: PackedScene
@export var codex_scene: PackedScene
@export var settings_scene: PackedScene
@export var credits_scene: PackedScene
@export var loading_scene: PackedScene
@export var run_scene: PackedScene
@export var garden_run_scene: PackedScene
@export var heart_run_scene: PackedScene

var screen: Control = null
var run: Run = null
var _starting: bool = false
var _level: String = "region"

@onready var ui: CanvasLayer = %Ui


func _ready() -> void:
	get_window().title = "Projeto: Última Semente"
	get_window().focus_exited.connect(_on_focus_lost)
	show_main_menu()


func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT or what == NOTIFICATION_WM_WINDOW_FOCUS_OUT:
		_on_focus_lost()


func _on_focus_lost() -> void:
	if run != null and is_instance_valid(run):
		run.pause_for_focus()


func _set_screen(s: Control) -> void:
	_clear_screen()
	screen = s
	ui.add_child(s)


func _clear_screen() -> void:
	if screen != null and is_instance_valid(screen):
		screen.queue_free()
	screen = null
	get_viewport().gui_release_focus()


func _cleanup_run() -> void:
	if run != null and is_instance_valid(run):
		run.queue_free()
	run = null
	get_tree().paused = false


func show_main_menu() -> void:
	_cleanup_run()
	AudioManager.set_combat_intensity(0.0)
	AudioManager.start_music()
	var m: MainMenuScreen = main_menu_scene.instantiate() as MainMenuScreen
	_set_screen(m)
	m.action.connect(_on_menu_action)


func _on_menu_action(id: String) -> void:
	if id == "play":
		var s: StartScreen = start_scene.instantiate() as StartScreen
		_set_screen(s)
		s.start_pressed.connect(func() -> void: start_run("region"))
		s.back_pressed.connect(show_main_menu)
	elif id == "garden":
		start_run("garden")
	elif id == "heart":
		start_run("heart")
	elif id == "lab":
		var l: LabScreen = lab_scene.instantiate() as LabScreen
		_set_screen(l)
		l.back_pressed.connect(show_main_menu)
	elif id == "codex":
		var c: CodexScreen = codex_scene.instantiate() as CodexScreen
		_set_screen(c)
		c.back_pressed.connect(show_main_menu)
	elif id == "settings":
		var st: SettingsPanel = settings_scene.instantiate() as SettingsPanel
		_set_screen(st)
		st.back_pressed.connect(show_main_menu)
	elif id == "credits":
		var cr: CreditsScreen = credits_scene.instantiate() as CreditsScreen
		_set_screen(cr)
		cr.back_pressed.connect(show_main_menu)
	elif id == "quit":
		get_tree().quit()


func start_run(level: String = "region") -> void:
	if _starting:
		return
	_starting = true
	_level = level
	_cleanup_run()
	_set_screen(loading_scene.instantiate() as Control)
	# Dois quadros para a tela de carregamento aparecer antes da geração do mundo.
	await get_tree().process_frame
	await get_tree().process_frame
	var scn: PackedScene = run_scene
	if level == "garden":
		scn = garden_run_scene
	elif level == "heart":
		scn = heart_run_scene
	run = scn.instantiate() as Run
	run.request_menu.connect(show_main_menu)
	run.request_restart.connect(func() -> void: start_run(_level))
	run.request_garden.connect(func() -> void: start_run("garden"))
	run.request_heart.connect(func() -> void: start_run("heart"))
	add_child(run)
	_clear_screen()
	_starting = false
