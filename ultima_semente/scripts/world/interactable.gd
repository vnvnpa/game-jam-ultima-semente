@tool
class_name Interactable
extends Node2D
## Ponto de interação (tecla E): terminal de suprimentos, nave (extração)
## ou ponto de interesse com registro narrativo.

@export var draw_placeholder: bool = true
## Tipo: "shop" (terminal de suprimentos), "ship" (extração) ou "poi" (ruína com registro).
@export_enum("shop", "ship", "poi") var kind: String = "poi"
## Para "shop": id do terminal (controla as ofertas). Para "poi": id único da ruína.
@export var ref_id: String = ""
@export var display_name: String = ""
@export var reach: float = 70.0
## Apenas "poi": id do registro (data/records) e id da recompensa única de Núcleo ("" = sem Núcleo).
@export var record_id: String = ""
@export var nuc_claim: String = ""

var run: Run = null
var used: bool = false
var t: float = 0.0


func _ready() -> void:
	add_to_group("interactables")
	add_to_group("needs_run")


func prompt_text() -> String:
	if kind == "shop":
		return "[E] %s" % display_name
	if kind == "ship":
		return "[E] Segure para extrair (encerra a expedição)"
	if used:
		return "[E] Reler registro — %s" % display_name
	return "[E] Examinar — %s" % display_name


func _process(delta: float) -> void:
	t += delta
	queue_redraw()


func _draw() -> void:
	if not draw_placeholder:
		return
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
