class_name Decoy
extends Node2D
## Semente de Isca: atrai inimigos próximos por alguns segundos.

@export var draw_placeholder: bool = true
var life: float = 8.0
var t: float = 0.0

@onready var sprite: AnimatedSprite2D = get_node_or_null("Sprite") as AnimatedSprite2D


func _process(delta: float) -> void:
	t += delta
	life -= delta
	if life <= 0.0:
		queue_free()
		return
	if sprite != null:
		sprite.modulate.a = clampf(life / 1.0, 0.0, 1.0)
	queue_redraw()


func _draw() -> void:
	if not draw_placeholder:
		return
	var p: float = 1.0 + 0.15 * sin(t * 8.0)
	draw_circle(Vector2.ZERO, 22.0 * p, Color(0.5, 1.0, 0.5, 0.12))
	draw_arc(Vector2.ZERO, 22.0 * p, 0.0, TAU, 24, Color(0.5, 1.0, 0.55, 0.6), 2.0)
	draw_circle(Vector2(0, 2), 7.0, Color(0.35, 0.8, 0.35))
	draw_circle(Vector2(0, -3), 4.0, Color(0.8, 1.0, 0.6))
