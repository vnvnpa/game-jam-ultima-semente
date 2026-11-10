@tool
class_name HostileZone
extends Node2D
## Setor com ar irrespirável: só aqui o oxigênio é consumido (GDD 12.5).
## O retângulo é centrado no nó; ajuste "Size" no Inspector (scenes/world/hostile_zone.tscn).
## O nó "Fog" (Sprite2D com textura repetida) cobre o retângulo com névoa.

@export var size: Vector2 = Vector2(600, 400):
	set(v):
		size = v
		queue_redraw()
		_apply_fog()
@export var zone_label: String = "ZONA CONTAMINADA — oxigênio em consumo"
@export var draw_placeholder: bool = true

var t: float = 0.0

@onready var fog: Sprite2D = get_node_or_null("Fog") as Sprite2D


func get_rect() -> Rect2:
	return Rect2(global_position - size * 0.5, size)


func _ready() -> void:
	t = randf() * 6.0
	_apply_fog()


func _apply_fog() -> void:
	if fog != null:
		fog.texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
		fog.region_enabled = true
		fog.region_rect = Rect2(Vector2.ZERO, size)


func _process(delta: float) -> void:
	t += delta
	if fog != null:
		fog.modulate.a = 0.75 + 0.2 * sin(t * 1.2)


func _enter_tree() -> void:
	if not Engine.is_editor_hint():
		WorldLayout.register_hostile(self)


func _exit_tree() -> void:
	if not Engine.is_editor_hint():
		WorldLayout.unregister_hostile(self)


func _draw() -> void:
	var r: Rect2 = Rect2(-size * 0.5, size)
	if draw_placeholder:
		draw_rect(r, Color(0.6, 0.1, 0.5, 0.18))
	draw_rect(r, Color(0.8, 0.2, 0.7, 0.8), false, 2.0)
	draw_string(UIKit.font(), r.position + Vector2(10, 22), zone_label, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(1.0, 0.5, 0.9, 0.85))
