@tool
class_name Station
extends Node2D
## Estação pressurizada: recarrega oxigênio e impede a entrada de inimigos.
## Posicione e ajuste o raio no editor (scenes/world/station.tscn). O nó "Sprite"
## (AnimatedSprite2D) é escalado pelo raio; o rótulo continua desenhado.

## Raio (px da arte) do anel desenhado em station.png.
const ART_RADIUS: float = 124.0

@export var station_id: String = "base"
@export var display_name: String = "Estação"
@export var radius: float = 120.0:
	set(v):
		radius = v
		queue_redraw()
		_apply_sprite()
@export var draw_placeholder: bool = true

@onready var sprite: AnimatedSprite2D = get_node_or_null("Sprite") as AnimatedSprite2D


func _ready() -> void:
	_apply_sprite()


func _apply_sprite() -> void:
	if sprite != null:
		var k: float = radius / ART_RADIUS
		sprite.scale = Vector2(k, k)


func _enter_tree() -> void:
	if not Engine.is_editor_hint():
		WorldLayout.register_station(self)


func _exit_tree() -> void:
	if not Engine.is_editor_hint():
		WorldLayout.unregister_station(self)


func _draw() -> void:
	if draw_placeholder:
		draw_circle(Vector2.ZERO, radius, Color(0.3, 0.9, 1.0, 0.07))
		draw_arc(Vector2.ZERO, radius, 0.0, TAU, 64, Color(0.4, 0.95, 1.0, 0.7), 2.0)
	var f: Font = ThemeDB.fallback_font
	var label: String = "%s (ar pressurizado)" % display_name
	var sz: Vector2 = f.get_string_size(label, HORIZONTAL_ALIGNMENT_LEFT, -1, 12)
	draw_string(f, Vector2(-sz.x * 0.5, -radius - 6.0), label, HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color(0.6, 1.0, 1.0, 0.9))
