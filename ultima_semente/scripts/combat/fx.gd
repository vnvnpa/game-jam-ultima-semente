class_name Fx
extends Node2D
## Efeito visual curto (anel, faíscas ou texto flutuante). Remove-se sozinho.

@export var draw_placeholder: bool = true
var kind: String = "ring"
var life: float = 0.4
var t: float = 0.0
var color: Color = Color.WHITE
var radius: float = 40.0
var text: String = ""
var vel: Vector2 = Vector2(0.0, -42.0)
var sparks: Array = []   # cada item: {"dir": Vector2, "dist": float}
var font_size: int = 14


func _process(delta: float) -> void:
	t += delta
	if t >= life:
		queue_free()
		return
	if kind == "text":
		position += vel * delta
	queue_redraw()


func _draw() -> void:
	if not draw_placeholder:
		return
	var k: float = clampf(t / maxf(life, 0.001), 0.0, 1.0)
	match kind:
		"ring":
			var a: float = (1.0 - k)
			draw_circle(Vector2.ZERO, radius * k, Color(color.r, color.g, color.b, a * 0.12))
			draw_arc(Vector2.ZERO, maxf(1.0, radius * k), 0.0, TAU, 48, Color(color.r, color.g, color.b, a * 0.95), 3.0)
		"burst":
			var a2: float = (1.0 - k)
			for s in sparks:
				var d: Vector2 = s["dir"]
				var dist: float = float(s["dist"]) * k
				draw_line(d * dist, d * (dist + 5.0), Color(color.r, color.g, color.b, a2), 2.0)
		"text":
			var font: Font = ThemeDB.fallback_font
			var size: Vector2 = font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size)
			var pos: Vector2 = Vector2(-size.x * 0.5, 0.0)
			var a3: float = 1.0 - maxf(0.0, (k - 0.6) / 0.4)
			draw_string(font, pos + Vector2(1.0, 1.0), text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size, Color(0, 0, 0, a3))
			draw_string(font, pos, text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size, Color(color.r, color.g, color.b, a3))
