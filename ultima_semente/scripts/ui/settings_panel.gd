class_name SettingsPanel
extends Control
## Configurações: volumes independentes, acessibilidade (GDD 15) e remapeamento
## de teclas (GDD 5.2). Estrutura em scenes/ui/settings_panel.tscn; as linhas
## de teclas são criadas aqui a partir de GameManager.REBINDABLE.
## Os sliders aplicam o volume na hora, mas o salvamento em disco é agrupado
## (0,5 s depois da última mudança) para não gravar a cada tique do slider.

signal back_pressed

const SAVE_DELAY: float = 0.5

var _save_timer: Timer = null
var _listening: String = ""
var _key_buttons: Dictionary = {}

@onready var options_box: VBoxContainer = %OptionsBox
@onready var keys_box: VBoxContainer = %KeysBox
@onready var keys_list: VBoxContainer = %KeysList
@onready var keys_msg: Label = %KeysMsg
@onready var keys_button: Button = %KeysButton
@onready var keys_back_button: Button = %KeysBackButton
@onready var reset_keys_button: Button = %ResetKeysButton
@onready var music_title: Label = %MusicTitle
@onready var sfx_title: Label = %SfxTitle
@onready var music_slider: HSlider = %MusicSlider
@onready var sfx_slider: HSlider = %SfxSlider
@onready var reduce_fx_check: CheckBox = %ReduceFxCheck
@onready var damage_check: CheckBox = %DamageNumbersCheck
@onready var back_button: Button = %BackButton


func _ready() -> void:
	_save_timer = Timer.new()
	_save_timer.one_shot = true
	_save_timer.wait_time = SAVE_DELAY
	_save_timer.timeout.connect(_flush)
	add_child(_save_timer)
	music_slider.value = float(SaveManager.get_setting("music"))
	sfx_slider.value = float(SaveManager.get_setting("sfx"))
	reduce_fx_check.button_pressed = bool(SaveManager.get_setting("reduce_fx"))
	damage_check.button_pressed = bool(SaveManager.get_setting("damage_numbers"))
	_update_titles()
	music_slider.value_changed.connect(_on_slider.bind("music"))
	sfx_slider.value_changed.connect(_on_slider.bind("sfx"))
	reduce_fx_check.toggled.connect(_on_check.bind("reduce_fx"))
	damage_check.toggled.connect(_on_check.bind("damage_numbers"))
	back_button.pressed.connect(func() -> void: back_pressed.emit())
	keys_button.pressed.connect(func() -> void: _show_keys(true))
	keys_back_button.pressed.connect(func() -> void: _show_keys(false))
	reset_keys_button.pressed.connect(_on_reset_keys)
	visibility_changed.connect(_on_visibility_changed)
	_build_key_rows()
	_show_keys(false)
	UIKit.wire_buttons(self)


func _exit_tree() -> void:
	# Se o painel for fechado antes do tempo, não perde a última mudança.
	if _save_timer != null and not _save_timer.is_stopped():
		_save_timer.stop()
		SaveManager.save_game()


func _flush() -> void:
	SaveManager.save_game()


func _on_slider(v: float, key: String) -> void:
	SaveManager.set_setting(key, v, false)
	AudioManager.apply_volumes()
	_update_titles()
	_save_timer.start()


## Mostra o valor em porcentagem ao lado do nome de cada volume.
func _update_titles() -> void:
	music_title.text = "Volume da música — %d%%" % roundi(music_slider.value * 100.0)
	sfx_title.text = "Volume dos efeitos — %d%%" % roundi(sfx_slider.value * 100.0)


func _on_check(v: bool, key: String) -> void:
	SaveManager.set_setting(key, v)


# ----------------------------------------------------- teclas
func _build_key_rows() -> void:
	UIKit.clear_children(keys_list)
	_key_buttons.clear()
	for a in GameManager.REBINDABLE:
		var action: String = str(a)
		var row: HBoxContainer = HBoxContainer.new()
		var lbl: Label = Label.new()
		lbl.text = str(GameManager.ACTION_LABELS[action])
		lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var btn: Button = Button.new()
		btn.custom_minimum_size = Vector2(190.0, 38.0)
		btn.focus_mode = Control.FOCUS_NONE
		btn.pressed.connect(_start_listening.bind(action))
		row.add_child(lbl)
		row.add_child(btn)
		keys_list.add_child(row)
		_key_buttons[action] = btn
	UIKit.wire_buttons(keys_list)
	_refresh_keys()


func _refresh_keys() -> void:
	for action in _key_buttons:
		var btn: Button = _key_buttons[action]
		if str(action) == _listening:
			btn.text = "Pressione uma tecla..."
		else:
			btn.text = GameManager.keyboard_text(str(action))


func _show_keys(on: bool) -> void:
	_listening = ""
	options_box.visible = not on
	keys_box.visible = on
	back_button.visible = not on
	keys_msg.text = ""
	_refresh_keys()


func _start_listening(action: String) -> void:
	_listening = action
	keys_msg.text = "Pressione a nova tecla (Esc cancela)."
	keys_msg.add_theme_color_override("font_color", UIKit.COL_WARN)
	_refresh_keys()


func _on_reset_keys() -> void:
	_listening = ""
	GameManager.reset_bindings()
	keys_msg.text = "Teclas restauradas ao padrão."
	keys_msg.add_theme_color_override("font_color", UIKit.COL_GOOD)
	_refresh_keys()


func _on_visibility_changed() -> void:
	if not is_visible_in_tree():
		_show_keys(false)


## Captura a próxima tecla enquanto uma ação aguarda remapeamento. Consome o
## evento para que Esc (pausa) e as demais teclas não vazem para o jogo.
func _input(event: InputEvent) -> void:
	if _listening == "":
		return
	var ke: InputEventKey = event as InputEventKey
	if ke == null or not ke.pressed or ke.echo:
		return
	get_viewport().set_input_as_handled()
	var code: int = ke.physical_keycode
	if code == KEY_NONE:
		code = ke.keycode
	if code == KEY_ESCAPE:
		_listening = ""
		keys_msg.text = ""
		_refresh_keys()
		return
	var res: Dictionary = GameManager.rebind(_listening, code)
	var ok: bool = bool(res["ok"])
	_listening = ""
	keys_msg.text = str(res["msg"])
	keys_msg.add_theme_color_override("font_color", UIKit.COL_GOOD if ok else UIKit.COL_BAD)
	AudioManager.play_sfx("confirm" if ok else "error")
	_refresh_keys()
