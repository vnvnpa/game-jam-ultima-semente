class_name FriendlyCloud
extends Node2D
## Nuvem de Esporos do jogador: retarda e enfraquece (mais dano recebido) os
## inimigos dentro do raio. Números em data/abilities/01_nuvem_esporos.tres.

@export var draw_placeholder: bool = true
var run: Run = null
var data: AbilityData = null
var radius: float = 120.0
var life: float = 6.0
var t: float = 0.0
var tick: float = 0.0

@onready var sprite: AnimatedSprite2D = get_node_or_null("Sprite") as AnimatedSprite2D


func _ready() -> void:
	add_to_group("clouds")
	if sprite != null:
		var k: float = radius / 46.0
		sprite.scale = Vector2(k, k)
		sprite.modulate = Color(0.45, 1.0, 0.85, 0.85)


func _process(delta: float) -> void:
	if run == null or run.ended or data == null:
		return
	t += delta
	life -= delta
	if life <= 0.0:
		queue_free()
		return
	tick -= delta
	if tick <= 0.0:
		tick = 0.2
		for e in run.enemies:
			if not is_instance_valid(e):
				continue
			var en: Enemy = e
			if not en.alive:
				continue
			var rr: float = radius + en.radius
			if global_position.distance_squared_to(en.global_position) <= rr * rr:
				en.apply_weaken(data.duracao_fraqueza, data.vulnerabilidade, data.lentidao)
	if sprite != null:
		sprite.modulate.a = 0.85 * clampf(life / 1.2, 0.0, 1.0)
	queue_redraw()


func _draw() -> void:
	if not draw_placeholder:
		return
	var fade: float = clampf(life / 1.2, 0.0, 1.0)
	draw_circle(Vector2.ZERO, radius, Color(0.3, 0.9, 0.7, 0.18 * fade))
	draw_arc(Vector2.ZERO, radius, 0.0, TAU, 40, Color(0.5, 1.0, 0.8, 0.7 * fade), 2.0)
