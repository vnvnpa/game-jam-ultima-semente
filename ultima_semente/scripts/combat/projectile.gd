class_name Projectile
extends Node2D
## Projétil sem física: movimento manual e teste de distância (leve no navegador).
## Cada inimigo só pode ser atingido uma vez por projétil (hit_ids).

var run: Run = null
var dir: Vector2 = Vector2.RIGHT
var speed: float = 500.0
var damage: float = 10.0
var pierce: int = 0
var life: float = 1.0
var friendly: bool = true
var radius: float = 5.0
var hit_ids: Array = []
var poison: bool = false
var shard: bool = false
var color: Color = Color(0.7, 1.0, 0.55)
var done: bool = false

@export var draw_placeholder: bool = true


func _physics_process(delta: float) -> void:
	if done or run == null or run.ended:
		return
	global_position += dir * speed * delta
	life -= delta
	if life <= 0.0 or not WorldLayout.WORLD_RECT.has_point(global_position):
		_finish()
		return
	if friendly:
		_check_enemies()
	else:
		_check_player()


func _check_enemies() -> void:
	for e in run.enemies:
		if not is_instance_valid(e):
			continue
		var en: Enemy = e
		if not en.alive:
			continue
		var rr: float = radius + en.radius
		if global_position.distance_squared_to(en.global_position) > rr * rr:
			continue
		var id: int = en.get_instance_id()
		if hit_ids.has(id):
			continue
		hit_ids.append(id)
		en.take_damage(damage, "proj")
		if poison and en.alive:
			en.apply_poison(4.0 + damage * 0.15, 3.0)
		if not en.alive and not shard and run.state.has_special("estilhaco"):
			_spawn_shards(en.global_position)
		pierce -= 1
		if pierce < 0:
			_finish()
			return


func _check_player() -> void:
	var pl: Player = run.player
	if pl == null or pl.dead:
		return
	if WorldLayout.in_safe(global_position):
		_finish()
		return
	var rr: float = radius + Player.RADIUS
	if global_position.distance_squared_to(pl.global_position) <= rr * rr:
		pl.take_damage(damage, global_position)
		_finish()


func _spawn_shards(pos: Vector2) -> void:
	for i in 3:
		var p: Projectile = run.new_projectile()
		p.shard = true
		p.dir = dir.rotated(TAU * float(i) / 3.0 + 0.5)
		p.speed = 430.0
		p.damage = damage * 0.5
		p.life = 0.38
		p.radius = 4.0
		p.color = Color(0.9, 1.0, 0.5)
		p.position = pos
		p.poison = poison
		run.spawn_projectile(p)


func _finish() -> void:
	if done:
		return
	done = true
	queue_free()


func _draw() -> void:
	if not draw_placeholder:
		return
	draw_line(-dir * 9.0, Vector2.ZERO, Color(color.r, color.g, color.b, 0.55), 3.0)
	draw_circle(Vector2.ZERO, radius, color)
	draw_circle(Vector2.ZERO, radius * 0.5, Color(1, 1, 1, 0.9))
