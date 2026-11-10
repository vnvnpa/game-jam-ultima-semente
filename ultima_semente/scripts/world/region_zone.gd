@tool
class_name RegionZone
extends Node2D
## Região nomeada do mundo (Floresta, Bacia, Santuário...). Define o nome mostrado
## no HUD e a cor no mapa. Se "Locked Until Gate" estiver marcado, inimigos não
## surgem na região enquanto a barreira estiver fechada.

@export var region_name: String = "Região"
@export var size: Vector2 = Vector2(1000, 1000):
	set(v):
		size = v
		queue_redraw()
@export var map_color: Color = Color(0.1, 0.25, 0.14, 1.0)
@export var locked_until_gate: bool = false
@export var draw_placeholder: bool = true


func get_rect() -> Rect2:
	return Rect2(global_position - size * 0.5, size)


func _enter_tree() -> void:
	if not Engine.is_editor_hint():
		WorldLayout.register_region(self)


func _exit_tree() -> void:
	if not Engine.is_editor_hint():
		WorldLayout.unregister_region(self)


func _draw() -> void:
	# Só aparece no editor, como guia; em jogo o terreno já mostra a região.
	if not Engine.is_editor_hint() or not draw_placeholder:
		return
	var r: Rect2 = Rect2(-size * 0.5, size)
	draw_rect(r, Color(map_color.r, map_color.g, map_color.b, 0.12))
	draw_rect(r, Color(map_color.r, map_color.g, map_color.b, 0.7), false, 3.0)
	draw_string(UIKit.font(), r.position + Vector2(12, 28), region_name, HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Color(1, 1, 1, 0.8))
