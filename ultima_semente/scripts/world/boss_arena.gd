@tool
class_name BossArena
extends Node2D
## Arena do chefe: o chefe surge no centro quando o jogador entra no raio de ativação
## (e a barreira já estiver aberta). Edite em scenes/world/boss_arena.tscn.

@export var ring_radius: float = 260.0:
	set(v):
		ring_radius = v
		queue_redraw()
@export var trigger_radius: float = 480.0
@export var draw_placeholder: bool = true


func _enter_tree() -> void:
	if not Engine.is_editor_hint():
		WorldLayout.boss_arena = self


func _exit_tree() -> void:
	if not Engine.is_editor_hint() and WorldLayout.boss_arena == self:
		WorldLayout.boss_arena = null


func _draw() -> void:
	if not draw_placeholder:
		return
	draw_arc(Vector2.ZERO, ring_radius, 0.0, TAU, 64, Color(0.7, 0.4, 0.9, 0.35), 3.0)
	if Engine.is_editor_hint():
		draw_arc(Vector2.ZERO, trigger_radius, 0.0, TAU, 64, Color(1.0, 0.5, 0.5, 0.25), 1.0)
		draw_string(ThemeDB.fallback_font, Vector2(-40, 4), "Arena do chefe", HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color(0.9, 0.7, 1.0))
