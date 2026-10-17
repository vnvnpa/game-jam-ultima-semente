@tool
class_name HostileZone
extends Node2D
## Setor com ar irrespirável: só aqui o oxigênio é consumido (GDD 12.5).
## O retângulo é centrado no nó; ajuste "Size" no Inspector (scenes/world/hostile_zone.tscn).

@export var size: Vector2 = Vector2(600, 400):
	set(v):
		size = v
		queue_redraw()
@export var zone_label: String = "ZONA CONTAMINADA — oxigênio em consumo"
@export var draw_placeholder: bool = true


func get_rect() -> Rect2:
	return Rect2(global_position - size * 0.5, size)


func _enter_tree() -> void:
	if not Engine.is_editor_hint():
		WorldLayout.register_hostile(self)


func _exit_tree() -> void:
	if not Engine.is_editor_hint():
		WorldLayout.unregister_hostile(self)


func _draw() -> void:
	if not draw_placeholder:
		return
	var r: Rect2 = Rect2(-size * 0.5, size)
	draw_rect(r, Color(0.6, 0.1, 0.5, 0.18))
	draw_rect(r, Color(0.8, 0.2, 0.7), false, 2.0)
	draw_string(ThemeDB.fallback_font, r.position + Vector2(10, 22), zone_label, HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color(1.0, 0.5, 0.9, 0.85))
