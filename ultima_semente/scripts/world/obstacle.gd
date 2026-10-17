@tool
class_name Obstacle
extends StaticBody2D
## Obstáculo com colisão (árvore, cristal ou pilar). Cada tipo tem a sua cena
## (scenes/world/tree.tscn, crystal.tscn, pillar.tscn): edite o visual nelas.

@export_enum("Árvore", "Cristal", "Pilar") var kind: int = 0
@export var radius: float = 20.0:
	set(v):
		radius = v
		_apply_radius()
@export var draw_placeholder: bool = true

@onready var shape_node: CollisionShape2D = $Shape


func _ready() -> void:
	_apply_radius()


func _apply_radius() -> void:
	queue_redraw()
	if shape_node == null:
		return
	# O CircleShape2D da cena é "local to scene": cada obstáculo tem a sua cópia.
	var c: CircleShape2D = shape_node.shape as CircleShape2D
	if c != null:
		c.radius = radius * 0.8


func _draw() -> void:
	if not draw_placeholder:
		return
	var r: float = radius
	draw_circle(Vector2(0, r * 0.6), r * 0.9, Color(0, 0, 0, 0.25))
	if kind == 0:
		draw_rect(Rect2(Vector2(-3, 0), Vector2(6, r * 0.8)), Color(0.28, 0.18, 0.12))
		draw_circle(Vector2(0, -r * 0.3), r, Color(0.07, 0.25, 0.14))
		draw_circle(Vector2(-r * 0.3, -r * 0.5), r * 0.7, Color(0.12, 0.38, 0.2))
		draw_circle(Vector2(r * 0.25, -r * 0.7), r * 0.5, Color(0.2, 0.5, 0.28))
	elif kind == 1:
		var pts: PackedVector2Array = PackedVector2Array([Vector2(0, -r * 1.5), Vector2(r * 0.7, 0), Vector2(0, r * 0.6), Vector2(-r * 0.7, 0)])
		draw_colored_polygon(pts, Color(0.45, 0.2, 0.6))
		draw_colored_polygon(PackedVector2Array([pts[0], pts[1], Vector2(0, -r * 0.2)]), Color(0.75, 0.45, 0.9))
	else:
		draw_rect(Rect2(Vector2(-r * 0.7, -r), Vector2(r * 1.4, r * 1.7)), Color(0.34, 0.37, 0.36))
		draw_rect(Rect2(Vector2(-r * 0.7, -r), Vector2(r * 1.4, r * 0.4)), Color(0.4, 0.55, 0.4))
