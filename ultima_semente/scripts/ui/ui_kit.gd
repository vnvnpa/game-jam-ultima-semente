class_name UIKit
extends RefCounted
## Tema e utilitários de interface criados em código (sem assets externos).

const COL_BG: Color = Color(0.03, 0.06, 0.07, 0.96)
const COL_PANEL: Color = Color(0.06, 0.11, 0.12, 0.97)
const COL_PANEL_LIGHT: Color = Color(0.09, 0.16, 0.17, 0.98)
const COL_BORDER: Color = Color(0.22, 0.58, 0.52)
const COL_TEXT: Color = Color(0.9, 0.96, 0.93)
const COL_DIM: Color = Color(0.58, 0.72, 0.68)
const COL_GOOD: Color = Color(0.55, 0.95, 0.62)
const COL_BAD: Color = Color(1.0, 0.5, 0.52)
const COL_WARN: Color = Color(1.0, 0.82, 0.35)
const COL_BIO: Color = Color(0.85, 0.96, 0.4)
const COL_NUC: Color = Color(0.5, 0.9, 1.0)
const COL_ACCENT: Color = Color(0.3, 0.85, 0.7)

static var _theme: Theme = null


static func panel_style(bg: Color = COL_PANEL, border: Color = COL_BORDER, radius: int = 6, border_w: int = 2) -> StyleBoxFlat:
	var sb: StyleBoxFlat = StyleBoxFlat.new()
	sb.bg_color = bg
	sb.border_color = border
	sb.set_border_width_all(border_w)
	sb.set_corner_radius_all(radius)
	sb.content_margin_left = 12
	sb.content_margin_right = 12
	sb.content_margin_top = 8
	sb.content_margin_bottom = 8
	return sb


const THEME_PATH: String = "res://ui/game_theme.tres"
const FONT_PATH: String = "res://assets/art/ui/pixel.ttf"
static var _font: Font = null


## Fonte pixel do jogo (HUD, mundo e menus). Cai na fonte padrão se faltar.
static func font() -> Font:
	if _font == null:
		_font = load(FONT_PATH) as Font
		if _font == null:
			_font = ThemeDB.fallback_font
	return _font


## Tema da interface: carregado de res://ui/game_theme.tres (editável no editor).
## Se o arquivo faltar, usa um tema equivalente criado em código.
static func get_theme() -> Theme:
	if _theme != null:
		return _theme
	var loaded: Theme = load(THEME_PATH) as Theme
	if loaded != null:
		_theme = loaded
		return _theme
	push_warning("UIKit: %s não encontrado; usando tema de reserva." % THEME_PATH)
	return _build_fallback_theme()


## Liga o som de clique a todos os botões (inclusive CheckBox) abaixo de `root`.
static func wire_buttons(root: Node) -> void:
	var pad: bool = Input.get_connected_joypads().size() > 0
	var first: BaseButton = null
	for n in root.find_children("*", "BaseButton", true, false):
		var b: BaseButton = n as BaseButton
		if b == null:
			continue
		# Com gamepad conectado, os botões precisam poder receber foco (D-pad + A).
		if pad and b.focus_mode == Control.FOCUS_NONE:
			b.focus_mode = Control.FOCUS_ALL
		if first == null and not b.disabled and b.is_visible_in_tree():
			first = b
		if b.has_meta("wired"):
			continue
		b.set_meta("wired", true)
		b.pressed.connect(func() -> void: AudioManager.play_sfx("click"))
	if pad and first != null and root.is_inside_tree() and root.get_viewport().gui_get_focus_owner() == null:
		first.call_deferred("grab_focus")


static func _build_fallback_theme() -> Theme:
	var t: Theme = Theme.new()
	t.default_font_size = 16
	t.set_color("font_color", "Label", COL_TEXT)
	t.set_color("font_color", "Button", COL_TEXT)
	t.set_color("font_hover_color", "Button", Color(1, 1, 1))
	t.set_color("font_pressed_color", "Button", COL_ACCENT)
	t.set_color("font_disabled_color", "Button", Color(0.45, 0.52, 0.5))
	t.set_color("font_focus_color", "Button", Color(1, 1, 1))
	t.set_font_size("font_size", "Button", 16)
	t.set_stylebox("normal", "Button", panel_style(Color(0.08, 0.17, 0.17), COL_BORDER, 5, 2))
	t.set_stylebox("hover", "Button", panel_style(Color(0.12, 0.27, 0.26), COL_ACCENT, 5, 2))
	t.set_stylebox("pressed", "Button", panel_style(Color(0.05, 0.12, 0.12), COL_ACCENT, 5, 2))
	t.set_stylebox("disabled", "Button", panel_style(Color(0.06, 0.09, 0.09), Color(0.2, 0.28, 0.27), 5, 2))
	var focus: StyleBoxFlat = panel_style(Color(0, 0, 0, 0), COL_WARN, 5, 2)
	t.set_stylebox("focus", "Button", focus)
	t.set_stylebox("panel", "PanelContainer", panel_style())
	t.set_stylebox("panel", "Panel", panel_style())
	t.set_color("font_color", "CheckBox", COL_TEXT)
	t.set_constant("separation", "VBoxContainer", 8)
	t.set_constant("separation", "HBoxContainer", 10)
	_theme = t
	return t


static func clear_children(node: Node) -> void:
	for c in node.get_children():
		node.remove_child(c)
		c.queue_free()
