extends Node
## Autoload "GameManager": registra os controles (GDD 5.2), permite remapear as
## teclas principais (guardadas em SaveManager > settings > "keys"), expõe
## configurações de acessibilidade e utilitários globais.
## Regras do remapeamento: muda-se a tecla PRINCIPAL de cada ação; as setas
## continuam como alternativa de movimento. Esc, setas e 1–3 são reservadas
## (pausa, movimento alternativo e escolha de cartas). Se a nova tecla já é a
## principal de outra ação, as duas trocam de tecla.

signal bindings_changed

## As ações e as teclas PADRÃO vivem no Input Map do project.godot (Projeto >
## Configurações do Projeto > Mapa de Entrada). Aqui só guardamos uma cópia dos
## padrões (lida no _ready, antes de aplicar o remapeamento do jogador).
const ACTION_NAMES: Array = ["move_up", "move_down", "move_left", "move_right", "skill_1", "skill_2", "skill_3", "use_pulse", "interact", "map", "pause"]

## ação -> Array[int] de physical_keycode padrão (a primeira é a "principal").
var _defaults: Dictionary = {}

## true quando o último dispositivo usado foi o controle (textos mostram botões).
var using_pad: bool = false

## Rótulos dos botões do controle (layout Xbox; PlayStation: A=X, B=O, X=Quadrado, Y=Triângulo).
const PAD_LABELS: Dictionary = {
	"move_up": "Analógico E", "move_down": "Analógico E", "move_left": "Analógico E", "move_right": "Analógico E",
	"skill_1": "A", "skill_2": "RB", "skill_3": "Y", "use_pulse": "X",
	"interact": "B", "map": "Back", "pause": "Start",
}

const ACTION_LABELS: Dictionary = {
	"move_up": "Mover para cima",
	"move_down": "Mover para baixo",
	"move_left": "Mover para a esquerda",
	"move_right": "Mover para a direita",
	"skill_1": "Pulso de Raízes",
	"skill_2": "Ruptura Celular",
	"skill_3": "Nuvem de Esporos",
	"use_pulse": "Pulso de Emergência",
	"interact": "Interagir",
	"map": "Mapa",
}

## Ações cuja tecla principal o jogador pode trocar (ordem de exibição).
const REBINDABLE: Array = ["move_up", "move_down", "move_left", "move_right", "skill_1", "skill_2", "skill_3", "use_pulse", "interact", "map"]
const RESERVED_KEYS: Array = [KEY_ESCAPE, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_1, KEY_2, KEY_3]


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_read_defaults()
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
	var defaults: Array = _defaults.get(action, [])
	if defaults.is_empty():
		return KEY_NONE
	var custom: Dictionary = _raw_keys()
	if REBINDABLE.has(action) and custom.has(action):
		var k: int = int(custom[action])
		if k > 0 and not RESERVED_KEYS.has(k):
			return k
	return int(defaults[0])


## Nome legível da tecla principal (ex.: "Espaço", "Q"); com controle em uso, o botão (ex.: "A", "RB").
func key_text(action: String) -> String:
	if using_pad and PAD_LABELS.has(action):
		return str(PAD_LABELS[action])
	return keyboard_text(action)


## Sempre o nome da tecla do teclado (tela de remapeamento).
func keyboard_text(action: String) -> String:
	return key_name(primary_key(action))


## "Start" no controle, "Esc" no teclado.
func pause_text() -> String:
	return "Start" if using_pad else "Esc"


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


## Lê do Input Map (project.godot) as teclas padrão de cada ação.
func _read_defaults() -> void:
	_defaults.clear()
	for action_name in ACTION_NAMES:
		var a: String = str(action_name)
		if not InputMap.has_action(a):
			push_error("GameManager: ação '%s' ausente do Input Map (project.godot)." % a)
			continue
		var codes: Array = []
		for e in InputMap.action_get_events(a):
			if e is InputEventKey:
				codes.append(int((e as InputEventKey).physical_keycode))
		_defaults[a] = codes


func _input(event: InputEvent) -> void:
	if event is InputEventJoypadButton:
		using_pad = true
	elif event is InputEventJoypadMotion and absf((event as InputEventJoypadMotion).axis_value) > 0.5:
		using_pad = true
	elif event is InputEventKey or event is InputEventMouseButton:
		using_pad = false
	elif event is InputEventMouseMotion and (event as InputEventMouseMotion).relative.length() > 3.0:
		using_pad = false


func _setup_input() -> void:
	_apply_all()


func _apply_all() -> void:
	for action_name in _defaults:
		_apply_action(str(action_name))


func _apply_action(action: String) -> void:
	var keys: Array = (_defaults.get(action, []) as Array).duplicate()
	if keys.is_empty():
		return
	# Preserva os eventos que não são de teclado (gamepad) definidos no Input Map.
	var others: Array = []
	for ev0 in InputMap.action_get_events(action):
		if not (ev0 is InputEventKey):
			others.append(ev0)
	InputMap.action_erase_events(action)
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
	for o in others:
		InputMap.action_add_event(action, o)


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
	# Guarda SÓ as diferenças em relação ao Input Map padrão.
	for k in keys.keys():
		var d: Array = _defaults.get(str(k), [])
		if not d.is_empty() and int(keys[k]) == int(d[0]):
			keys.erase(k)
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
