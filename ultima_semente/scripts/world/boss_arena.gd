@tool
class_name BossArena
extends Node2D
## Arena do chefe: o chefe surge no centro quando o jogador entra no raio de ativação
## (e a barreira já estiver aberta). Edite em scenes/world/boss_arena.tscn.
## O nó "Sprite" (anel animado) é escalado pelo raio do anel.

## Raio (px da arte) do anel desenhado em arena.png.
const ART_RADIUS: float = 265.0

@export var ring_radius: float = 260.0:
	set(v):
		ring_radius = v
		queue_redraw()
		_apply_sprite()
@export var trigger_radius: float = 480.0
@export var draw_placeholder: bool = true

@onready var sprite: AnimatedSprite2D = get_node_or_null("Sprite") as AnimatedSprite2D


func _ready() -> void:
	_apply_sprite()


func _apply_sprite() -> void:
	if sprite != null:
		var k: float = ring_radius / ART_RADIUS
		sprite.scale = Vector2(k, k)


func _enter_tree() -> void:
	if not Engine.is_editor_hint():
		WorldLayout.boss_arena = self


func _exit_tree() -> void:
	if not Engine.is_editor_hint() and WorldLayout.boss_arena == self:
		WorldLayout.boss_arena = null


func _draw() -> void:
	if draw_placeholder:
		draw_arc(Vector2.ZERO, ring_radius, 0.0, TAU, 64, Color(0.7, 0.4, 0.9, 0.35), 3.0)
	if Engine.is_editor_hint():
		draw_arc(Vector2.ZERO, trigger_radius, 0.0, TAU, 64, Color(1.0, 0.5, 0.5, 0.25), 1.0)
		draw_string(UIKit.font(), Vector2(-40, 4), "Arena do chefe", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(0.9, 0.7, 1.0))
