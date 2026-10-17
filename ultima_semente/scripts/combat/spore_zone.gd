class_name SporeZone
extends Node2D
## Zona de esporos no chão: causa dano contínuo ao jogador dentro do raio.

@export var draw_placeholder: bool = true
var run: Run = null
var radius: float = 40.0
var dps: float = 5.0
var life: float = 6.0
var t: float = 0.0
var tick: float = 0.0


func _process(delta: float) -> void:
	if run == null or run.ended:
		return
	t += delta
	life -= delta
	if life <= 0.0:
		queue_free()
		return
	tick -= delta
	if tick <= 0.0:
		tick = 0.25
		var pl: Player = run.player
		if pl != null and not pl.dead and not WorldLayout.in_safe(pl.global_position):
			if pl.global_position.distance_to(global_position) < radius + Player.RADIUS * 0.5:
				pl.take_dot(dps * 0.25)
	queue_redraw()


func _draw() -> void:
	if not draw_placeholder:
		return
	var fade: float = clampf(life / 1.2, 0.0, 1.0)
	draw_circle(Vector2.ZERO, radius, Color(0.55, 0.75, 0.15, 0.22 * fade))
	draw_arc(Vector2.ZERO, radius, 0.0, TAU, 32, Color(0.8, 1.0, 0.3, 0.7 * fade), 2.0)
	for i in 6:
		var a: float = t * 0.8 + float(i) * TAU / 6.0
		var r: float = radius * (0.35 + 0.4 * absf(sin(t * 1.3 + float(i))))
		draw_circle(Vector2.from_angle(a) * r, 2.5, Color(0.95, 1.0, 0.5, 0.8 * fade))
