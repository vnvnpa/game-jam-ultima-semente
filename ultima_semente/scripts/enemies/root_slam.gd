class_name RootSlam
extends Node2D
## Ataque em área telegrafado do chefe: aviso vermelho e depois dano.

@export var draw_placeholder: bool = true
var run: Run = null
var radius: float = 62.0
var damage: float = 26.0
var delay: float = 1.0
var t: float = 0.0

@onready var telegraph: Sprite2D = get_node_or_null("Telegraph") as Sprite2D
@onready var fill: Sprite2D = get_node_or_null("Fill") as Sprite2D


func _ready() -> void:
	if telegraph != null:
		var k: float = radius / 62.0
		telegraph.scale = Vector2(k, k)
	if fill != null:
		fill.scale = Vector2.ZERO


func _process(delta: float) -> void:
	if run == null or run.ended:
		return
	t += delta
	if t >= delay:
		_strike()
		queue_free()
		return
	var kk: float = clampf(t / maxf(delay, 0.001), 0.0, 1.0)
	if telegraph != null:
		telegraph.modulate.a = 0.45 + 0.55 * kk
	if fill != null:
		var f: float = maxf(0.02, kk * radius / 62.0)
		fill.scale = Vector2(f, f)
	queue_redraw()


func _strike() -> void:
	var pl: Player = run.player
	if pl != null and not pl.dead:
		if pl.global_position.distance_to(global_position) <= radius + Player.RADIUS * 0.6:
			pl.take_damage(damage, global_position)
	run.fx_ring(global_position, radius * 1.15, Color(0.6, 1.0, 0.45), 0.4)
	run.fx_burst(global_position, Color(0.4, 0.8, 0.3), 12, radius)
	run.shake(5.0)
	AudioManager.play_sfx("explosion", 0.8, -4.0)


func _draw() -> void:
	if not draw_placeholder:
		return
	var k: float = clampf(t / maxf(delay, 0.001), 0.0, 1.0)
	draw_circle(Vector2.ZERO, radius, Color(1.0, 0.2, 0.2, 0.10 + 0.22 * k))
	draw_circle(Vector2.ZERO, radius * k, Color(1.0, 0.3, 0.2, 0.28))
	draw_arc(Vector2.ZERO, radius, 0.0, TAU, 40, Color(1.0, 0.35, 0.3, 0.9), 3.0)
