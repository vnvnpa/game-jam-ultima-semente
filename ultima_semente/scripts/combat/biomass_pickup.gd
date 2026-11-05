@tool
class_name BiomassPickup
extends Node2D
## Biomassa coletável. Itens soltos expiram; caches de exploração são fixos.

@export var draw_placeholder: bool = true
var run: Run = null
@export var value: int = 1
## Caches de exploração (fixos no mapa) não expiram nem somem sozinhos.
@export var persistent: bool = false
var life: float = 60.0
var magnet: bool = false
var vel: float = 0.0
var t: float = 0.0
var collected: bool = false

@onready var sprite: AnimatedSprite2D = get_node_or_null("Sprite") as AnimatedSprite2D


func _ready() -> void:
	t = randf() * 3.0
	if persistent:
		add_to_group("needs_run")
	if sprite != null:
		sprite.play(&"cache" if persistent else &"biomass")
	queue_redraw()


func _process(delta: float) -> void:
	if run == null or run.ended or collected:
		return
	t += delta
	var pl: Player = run.player
	if not persistent:
		life -= delta
		if life <= 0.0:
			queue_free()
			return
		modulate.a = 0.55 + 0.45 * absf(sin(t * 5.0)) if life < 8.0 else 1.0
	if pl == null or pl.dead:
		return
	var d: float = global_position.distance_to(pl.global_position)
	var reach: float = run.state.stat("pickup_radius")
	if persistent:
		reach = minf(reach, 60.0)
	if d < reach:
		magnet = true
	if magnet:
		vel = minf(vel + 1100.0 * delta, 760.0)
		global_position = global_position.move_toward(pl.global_position, vel * delta)
	if d < 14.0:
		collected = true
		run.collect_biomass(value)
		AudioManager.play_sfx("pickup", randf_range(0.95, 1.2))
		queue_free()
		return
	queue_redraw()


func _draw() -> void:
	var pulse: float = 0.8 + 0.2 * sin(t * 6.0)
	var s: float = (7.0 if persistent else 5.0) * pulse
	if persistent and run != null and run.player != null:
		var rv: float = run.state.stat("reveal_radius")
		if rv > 0.0 and global_position.distance_to(run.player.global_position) < rv:
			draw_arc(Vector2.ZERO, 16.0 + 3.0 * sin(t * 3.0), 0.0, TAU, 24, Color(0.85, 0.96, 0.35, 0.6), 2.0)
		if draw_placeholder:
			draw_circle(Vector2.ZERO, s + 5.0, Color(0.85, 0.96, 0.35, 0.16))
	if not draw_placeholder:
		return
	var col: Color = Color(0.85, 0.96, 0.35)
	var pts: PackedVector2Array = PackedVector2Array([Vector2(0, -s), Vector2(s * 0.8, 0), Vector2(0, s), Vector2(-s * 0.8, 0)])
	draw_colored_polygon(pts, col)
	draw_polyline(PackedVector2Array([pts[0], pts[1], pts[2], pts[3], pts[0]]), Color(1, 1, 0.8, 0.9), 1.0)
