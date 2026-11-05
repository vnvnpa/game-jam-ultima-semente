@tool
class_name Interactable
extends Node2D
## Ponto de interação (tecla E): terminal de suprimentos, nave (extração)
## ponto de interesse com registro narrativo ou mecanismo de ativação (Jardim).

@export var draw_placeholder: bool = true
## Tipo: "shop" (terminal de suprimentos), "ship" (extração), "poi" (ruína com registro)
## ou "mechanism" (mecanismo do Santuário do Último Jardim).
@export_enum("shop", "ship", "poi", "mechanism") var kind: String = "poi"
## Para "shop": id do terminal (controla as ofertas). Para "poi": id único da ruína.
@export var ref_id: String = ""
@export var display_name: String = ""
@export var reach: float = 70.0
## Apenas "poi": id do registro (data/records) e id da recompensa única de Núcleo ("" = sem Núcleo).
@export var record_id: String = ""
@export var nuc_claim: String = ""
## Folhas de animação (nó "Sprite"): terminal, nave, ruína e mecanismo.
@export var shop_frames: SpriteFrames
@export var ship_frames: SpriteFrames
@export var poi_frames: SpriteFrames
@export var mechanism_frames: SpriteFrames

var run: Run = null
var used: bool = false
var t: float = 0.0

@onready var sprite: AnimatedSprite2D = get_node_or_null("Sprite") as AnimatedSprite2D


func _ready() -> void:
	add_to_group("interactables")
	add_to_group("needs_run")
	_setup_sprite()


## Escolhe a folha e a posição do pé conforme o tipo.
func _setup_sprite() -> void:
	if sprite == null:
		return
	var fr: SpriteFrames = poi_frames
	var off: Vector2 = Vector2(0.0, -10.0)
	match kind:
		"shop":
			fr = shop_frames
			off = Vector2(0.0, -4.0)
		"ship":
			fr = ship_frames
			off = Vector2(0.0, -2.0)
			z_index = -2   # a nave é grande e baixa: o Kael sempre passa na frente
		"mechanism":
			fr = mechanism_frames
			off = Vector2(0.0, -10.0)
	sprite.sprite_frames = fr
	sprite.position = off
	if fr != null and fr.has_animation(&"idle"):
		sprite.play(&"idle")


func prompt_text() -> String:
	var key: String = GameManager.key_text("interact")
	if kind == "shop":
		return "[%s] %s" % [key, display_name]
	if kind == "ship":
		return "[%s] Segure para extrair (encerra a expedição)" % key
	if kind == "mechanism":
		if used:
			return "%s — ativo" % display_name
		return "[%s] Ativar — %s (resista às criaturas)" % [key, display_name]
	if used:
		return "[%s] Reler registro — %s" % [key, display_name]
	return "[%s] Examinar — %s" % [key, display_name]


func _process(delta: float) -> void:
	t += delta
	if sprite != null and sprite.sprite_frames != null:
		if kind == "mechanism":
			var want: StringName = &"active" if used else &"idle"
			if sprite.animation != want and sprite.sprite_frames.has_animation(want):
				sprite.play(want)
		elif kind == "poi":
			sprite.modulate = Color(0.6, 0.6, 0.72) if used else Color.WHITE
	queue_redraw()


func _draw() -> void:
	if draw_placeholder:
		_draw_placeholder()
	else:
		_draw_hints()


## Anéis de dica que continuam visíveis mesmo com sprite.
func _draw_hints() -> void:
	if kind == "mechanism":
		var mc: Color = Color(0.4, 0.95, 0.5) if used else Color(1.0, 0.8, 0.3)
		draw_arc(Vector2.ZERO, 34.0, 0.0, TAU, 28, Color(mc.r, mc.g, mc.b, 0.35), 2.0)
	elif kind == "poi" and run != null and run.player != null and not used:
		var gl: float = 0.5 + 0.5 * sin(t * 2.0)
		var rv: float = run.state.stat("reveal_radius")
		if rv > 0.0 and global_position.distance_to(run.player.global_position) < rv:
			draw_arc(Vector2.ZERO, 30.0 + 4.0 * gl, 0.0, TAU, 28, Color(0.8, 0.5, 1.0, 0.6), 2.0)


func _draw_placeholder() -> void:
	match kind:
		"shop":
			draw_rect(Rect2(-14, -16, 28, 30), Color(0.2, 0.26, 0.28))
			draw_rect(Rect2(-14, -16, 28, 30), Color(0.4, 0.8, 0.8), false, 2.0)
			var glow: float = 0.7 + 0.3 * sin(t * 3.0)
			draw_rect(Rect2(-9, -11, 18, 12), Color(0.2, 0.9, 1.0, glow))
			draw_rect(Rect2(-9, 5, 6, 4), Color(0.9, 0.6, 0.2))
			draw_rect(Rect2(3, 5, 6, 4), Color(0.4, 0.9, 0.5))
		"ship":
			draw_colored_polygon(PackedVector2Array([Vector2(-60, 10), Vector2(-40, -18), Vector2(20, -22), Vector2(62, -2), Vector2(40, 22), Vector2(-30, 24)]), Color(0.5, 0.52, 0.55))
			draw_colored_polygon(PackedVector2Array([Vector2(-30, 0), Vector2(0, -12), Vector2(30, -4), Vector2(14, 10), Vector2(-20, 12)]), Color(0.95, 0.55, 0.2))
			draw_rect(Rect2(-4, -8, 14, 8), Color(0.55, 0.9, 1.0))
			draw_line(Vector2(-60, 10), Vector2(-70, 24), Color(0.3, 0.3, 0.3), 3.0)
			draw_circle(Vector2(-72, 26), 3.0, Color(1.0, 0.5, 0.2, 0.5 + 0.4 * sin(t * 5.0)))
		"mechanism":
			var mc: Color = Color(0.4, 0.95, 0.5) if used else Color(1.0, 0.8, 0.3)
			var pg: float = 0.5 + 0.5 * sin(t * (1.0 if used else 3.0))
			draw_rect(Rect2(-12, -24, 24, 44), Color(0.22, 0.25, 0.27))
			draw_rect(Rect2(-12, -24, 24, 44), mc, false, 2.0)
			draw_circle(Vector2(0, -8), 7.0, Color(mc.r, mc.g, mc.b, 0.35 + 0.5 * pg))
			draw_line(Vector2(-6, 8), Vector2(6, 8), mc, 2.0)
			draw_arc(Vector2.ZERO, 34.0, 0.0, TAU, 28, Color(mc.r, mc.g, mc.b, 0.35), 2.0)
		_:
			var col: Color = Color(0.7, 0.45, 0.95) if not used else Color(0.45, 0.4, 0.55)
			draw_rect(Rect2(-9, -22, 18, 38), Color(0.25, 0.27, 0.3))
			draw_rect(Rect2(-9, -22, 18, 38), col, false, 2.0)
			var gl: float = 0.5 + 0.5 * sin(t * 2.0)
			draw_circle(Vector2(0, -8), 5.0, Color(col.r, col.g, col.b, 0.4 + 0.5 * gl))
			draw_line(Vector2(-5, 4), Vector2(5, 4), col, 2.0)
			draw_line(Vector2(0, 4), Vector2(0, 12), col, 2.0)
			if run != null and run.player != null and not used:
				var rv: float = run.state.stat("reveal_radius")
				if rv > 0.0 and global_position.distance_to(run.player.global_position) < rv:
					draw_arc(Vector2.ZERO, 30.0 + 4.0 * gl, 0.0, TAU, 28, Color(0.8, 0.5, 1.0, 0.6), 2.0)
