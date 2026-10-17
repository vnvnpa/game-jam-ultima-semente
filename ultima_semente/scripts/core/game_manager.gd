extends Node
## Autoload "GameManager": registra os controles (GDD 5.2), expõe
## configurações de acessibilidade e utilitários globais.

const ACTIONS: Dictionary = {
	"move_up": [KEY_W, KEY_UP],
	"move_down": [KEY_S, KEY_DOWN],
	"move_left": [KEY_A, KEY_LEFT],
	"move_right": [KEY_D, KEY_RIGHT],
	"skill_1": [KEY_SPACE],
	"skill_2": [KEY_Q],
	"use_pulse": [KEY_R],
	"interact": [KEY_E],
	"map": [KEY_M],
	"pause": [KEY_ESCAPE],
}


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_setup_input()
	AudioManager.apply_volumes()


func _setup_input() -> void:
	for action_name in ACTIONS:
		if not InputMap.has_action(action_name):
			InputMap.add_action(action_name)
		var keys: Array = ACTIONS[action_name]
		for k in keys:
			var ev: InputEventKey = InputEventKey.new()
			ev.physical_keycode = k
			InputMap.action_add_event(action_name, ev)


func reduce_fx() -> bool:
	return bool(SaveManager.get_setting("reduce_fx"))


func show_damage_numbers() -> bool:
	return bool(SaveManager.get_setting("damage_numbers"))


func is_web() -> bool:
	return OS.has_feature("web")


## Formata segundos como MM:SS.
static func format_time(seconds: float) -> String:
	var total: int = maxi(0, int(seconds))
	var minutes: int = floori(float(total) / 60.0)
	return "%02d:%02d" % [minutes, total - minutes * 60]
