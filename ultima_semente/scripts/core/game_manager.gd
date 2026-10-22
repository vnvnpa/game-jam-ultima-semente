extends Node
## Autoload "GameManager": registra os controles (GDD 5.2), permite remapear as
## teclas principais (guardadas em SaveManager > settings > "keys"), expõe
## configurações de acessibilidade e utilitários globais.
## Regras do remapeamento: muda-se a tecla PRINCIPAL de cada ação; as setas
## continuam como alternativa de movimento. Esc, setas e 1–3 são reservadas
## (pausa, movimento alternativo e escolha de cartas). Se a nova tecla já é a
## principal de outra ação, as duas trocam de tecla.

signal bindings_changed

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

const ACTION_LABELS: Dictionary = {
	"move_up": "Mover para cima",
	"move_down": "Mover para baixo",
	"move_left": "Mover para a esquerda",
	"move_right": "Mover para a direita",
	"skill_1": "Pulso de Raízes",
	"skill_2": "Ruptura Celular",
	"use_pulse": "Pulso de Emergência",
	"interact": "Interagir",
	"map": "Mapa",
}

## Ações cuja tecla principal o jogador pode trocar (ordem de exibição).
const REBINDABLE: Array = ["move_up", "move_down", "move_left", "move_right", "skill_1", "skill_2", "use_pulse", "interact", "map"]
const RESERVED_KEYS: Array = [KEY_ESCAPE, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_1, KEY_2, KEY_3]


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_validate_bindings()
	_setup_input()
	AudioManager.apply_volumes()


# --------------------------------------------------------- teclas
func _raw_keys() -> Dictionary:
	var v: Variant = SaveManager.get_setting("keys")
	if typeof(v) == TYPE_DICTIONARY:
		return v
	return {}


## Tecla principal efetiva de uma ação (personalizada, se válida; senão a padrão).
func primary_key(action: String) -> int:
	var defaults: Array = ACTIONS.get(action, [])
	if defaults.is_empty():
		return KEY_NONE
	var custom: Dictionary = _raw_keys()
	if REBINDABLE.has(action) and custom.has(action):
		var k: int = int(custom[action])
		if k > 0 and not RESERVED_KEYS.has(k):
			return k
	return int(defaults[0])


## Nome legível da tecla principal (ex.: "Espaço", "Q").
func key_text(action: String) -> String:
	return key_name(primary_key(action))


static func key_name(code: int) -> String:
	if code == KEY_SPACE:
		return "Espaço"
	var logical: int = DisplayServer.keyboard_get_keycode_from_physical(code as Key)
	if logical == KEY_NONE:
		logical = code
	var n: String = OS.get_keycode_string(logical as Key)
	if n == "":
		return "Tecla %d" % code
	return n


## Se o salvamento tiver teclas inválidas ou repetidas, volta ao padrão.
func _validate_bindings() -> void:
	var seen: Dictionary = {}
	var bad: bool = false
	for a in REBINDABLE:
		var k: int = primary_key(str(a))
		if seen.has(k):
			bad = true
		seen[k] = true
	if bad:
		push_warning("GameManager: teclas salvas inválidas; usando o padrão.")
		SaveManager.set_setting("keys", {})


func _setup_input() -> void:
	for action_name in ACTIONS:
		if not InputMap.has_action(action_name):
			InputMap.add_action(action_name)
	_apply_all()


func _apply_all() -> void:
	for action_name in ACTIONS:
		_apply_action(str(action_name))


func _apply_action(action: String) -> void:
	InputMap.action_erase_events(action)
	var keys: Array = (ACTIONS[action] as Array).duplicate()
	keys[0] = primary_key(action)
	var seen: Array = []
	for k in keys:
		var code: int = int(k)
		if seen.has(code):
			continue
		seen.append(code)
		var ev: InputEventKey = InputEventKey.new()
		ev.physical_keycode = code as Key
		InputMap.action_add_event(action, ev)


## Troca a tecla principal de uma ação. Retorna {"ok": bool, "msg": String}.
func rebind(action: String, code: int) -> Dictionary:
	if not REBINDABLE.has(action):
		return {"ok": false, "msg": "Esta ação não pode ser configurada."}
	if code <= 0 or RESERVED_KEYS.has(code):
		return {"ok": false, "msg": "Tecla reservada (Esc, setas e 1–3). Escolha outra."}
	var old: int = primary_key(action)
	if old == code:
		return {"ok": true, "msg": "Sem mudança."}
	var keys: Dictionary = _raw_keys().duplicate()
	var msg: String = "%s: %s." % [str(ACTION_LABELS[action]), key_name(code)]
	for other in REBINDABLE:
		var o: String = str(other)
		if o != action and primary_key(o) == code:
			keys[o] = old
			msg += " %s passou para %s." % [str(ACTION_LABELS[o]), key_name(old)]
	keys[action] = code
	SaveManager.set_setting("keys", keys)
	_apply_all()
	bindings_changed.emit()
	return {"ok": true, "msg": msg}


func reset_bindings() -> void:
	SaveManager.set_setting("keys", {})
	_apply_all()
	bindings_changed.emit()


# ------------------------------------------------------ utilitários
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
