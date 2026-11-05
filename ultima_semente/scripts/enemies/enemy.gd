@tool
class_name Enemy
extends CharacterBody2D
## Inimigo genérico guiado por EnemyData. O comportamento muda conforme
## data.comportamento. Inimigos mortos nunca atacam (alive == false).

var run: Run = null
var data: EnemyData = null
var hp: float = 1.0
var max_hp: float = 1.0
var alive: bool = true
var elite: bool = false
var elite_mod: String = ""
var elite_data: EliteModifier = null
var is_boss: bool = false
var damage: float = 5.0
var speed: float = 60.0
var radius: float = 10.0
var xp_value: int = 1
var bio_min: int = 1
var bio_max: int = 3
var flank_angle: float = 0.0
var contact_cd: float = 0.0
var knock: Vector2 = Vector2.ZERO
var knock_mult: float = 1.0
var root_time: float = 0.0
var poison_time: float = 0.0
var weaken_time: float = 0.0
var weaken_mult: float = 1.0
var weaken_slow: float = 1.0
var mark_time: float = 0.0
var poison_dps: float = 0.0
var empower_time: float = 0.0
var flash: float = 0.0
var anim_t: float = 0.0
var timer_a: float = 0.0
var timer_b: float = 0.0
var mode: int = 0
var charge_dir: Vector2 = Vector2.RIGHT
var look_dir: Vector2 = Vector2.RIGHT
var slide_bias_time: float = 0.0
var slide_side: float = 1.0
var strafe_side: float = 1.0
var regen_rate: float = 0.0
var explode_on_death: bool = false
var nest_children: Array = []
var seen: bool = false

@export var draw_placeholder: bool = true
## Para inimigos colocados direto no mapa (ex.: ninhos): dados usados ao iniciar a expedição.
@export var preset_data: EnemyData

@onready var shape_node: CollisionShape2D = $Shape
@onready var sprite: AnimatedSprite2D = get_node_or_null("Sprite") as AnimatedSprite2D
@onready var shadow: Sprite2D = get_node_or_null("Shadow") as Sprite2D
@onready var aura: AnimatedSprite2D = get_node_or_null("Aura") as AnimatedSprite2D
var event_anim: StringName = &""
var event_t: float = 0.0
var _cur: StringName = &""


func _ready() -> void:
	if preset_data != null and data == null:
		radius = preset_data.raio
		_apply_frames()
		if not Engine.is_editor_hint():
			add_to_group("preplaced_enemies")
		queue_redraw()


func _dd() -> EnemyData:
	return data if data != null else preset_data


func setup(r: Run, d: EnemyData, hp_mult: float, modifier: String) -> void:
	run = r
	data = d
	radius = d.raio
	max_hp = d.vida_maxima * hp_mult
	damage = d.dano
	speed = d.velocidade
	xp_value = d.experiencia
	bio_min = d.biomassa_minima
	bio_max = d.biomassa_maxima
	flank_angle = randf() * TAU
	timer_a = randf_range(0.3, 1.5)
	strafe_side = 1.0 if randf() < 0.5 else -1.0
	elite_mod = modifier
	elite = (d.id == "anomalia")
	if elite:
		var em: EliteModifier = GameData.elite_modifiers.get(modifier)
		if em != null:
			elite_data = em
			max_hp *= em.hp_mult
			speed *= em.speed_mult
			knock_mult = em.knock_mult
			explode_on_death = em.explode_on_death
			regen_rate = max_hp * em.regen_pct
	if d.comportamento == "tanque":
		knock_mult = 0.25
	if d.comportamento == "ninho" or d.comportamento == "estrutura":
		knock_mult = 0.0
	hp = max_hp
	# O CircleShape2D da cena é "local to scene": cada inimigo tem o seu.
	var circle: CircleShape2D = shape_node.shape as CircleShape2D
	if circle != null:
		circle.radius = maxf(4.0, radius * 0.8)
	_apply_frames()


## Liga o sprite (folha de animação do EnemyData) ao tamanho e ao raio do inimigo.
func _apply_frames() -> void:
	var d: EnemyData = _dd()
	if sprite == null or d == null or d.frames == null:
		return
	sprite.sprite_frames = d.frames
	var first: StringName = &"idle"
	if not d.frames.has_animation(first):
		var names: PackedStringArray = d.frames.get_animation_names()
		if names.is_empty():
			return
		first = StringName(names[0])
	var tex: Texture2D = d.frames.get_frame_texture(first, 0)
	var fw: float = float(tex.get_width())
	var fh: float = float(tex.get_height())
	var k: float = maxf(0.5, radius / (0.3 * fw))
	sprite.scale = Vector2(k, k)
	sprite.position = Vector2(0.0, radius * 0.8 - 0.4 * fh * k)
	_cur = first
	sprite.play(first)
	if shadow != null:
		var sk: float = radius * 2.0 / 28.0
		shadow.scale = Vector2(sk, sk)
		shadow.position = Vector2(0.0, radius * 0.75)
	if aura != null:
		aura.visible = elite and elite_mod != "" and aura.sprite_frames != null and aura.sprite_frames.has_animation(StringName(elite_mod))
		if aura.visible:
			var ak: float = (radius + 6.0) / 20.0
			aura.scale = Vector2(ak, ak)
			aura.position = Vector2(0.0, -2.0)
			aura.play(StringName(elite_mod))


## Toca uma animação de ação (tiro, esporos, invocação...) por `dur` segundos.
func play_event(anim: StringName, dur: float) -> void:
	if sprite == null or sprite.sprite_frames == null or not sprite.sprite_frames.has_animation(anim):
		return
	event_anim = anim
	event_t = dur
	_cur = anim
	sprite.play(anim)


## Animação de base (sem evento); subclasses podem sobrescrever.
func _base_anim() -> StringName:
	var fr: SpriteFrames = sprite.sprite_frames
	if data != null and data.comportamento == "veloz":
		var names: Array = [&"walk", &"windup", &"charge", &"recover"]
		var nm: StringName = names[clampi(mode, 0, 3)]
		if fr.has_animation(nm):
			return nm
	var moving: bool = velocity.length() > 5.0
	var order: Array = [&"walk", &"float", &"idle"] if moving else [&"idle", &"float", &"walk"]
	for a in order:
		if fr.has_animation(a):
			return a
	return _cur


## Só visual: escolhe a animação, espelha e tinge o sprite.
func _process(delta: float) -> void:
	if sprite == null or sprite.sprite_frames == null or run == null or not alive:
		return
	event_t = maxf(0.0, event_t - delta)
	var want: StringName = event_anim if event_t > 0.0 else _base_anim()
	if event_t <= 0.0 and flash > 0.6 and not is_boss and sprite.sprite_frames.has_animation(&"hurt"):
		want = &"hurt"
	if want != _cur and sprite.sprite_frames.has_animation(want):
		_cur = want
		sprite.play(want)
	if run.player != null:
		sprite.flip_h = run.player.global_position.x < global_position.x
	var f: float = 1.0 + flash * 0.8
	var c: Color = Color(f, f, f, 1.0)
	if empower_time > 0.0:
		c = Color(0.75 * f, f, f, 1.0)
	elif root_time > 0.0:
		c = Color(0.7 * f, f, 0.6 * f, 1.0)
	elif poison_time > 0.0:
		c = Color(0.8 * f, f, 0.7 * f, 1.0)
	sprite.modulate = c


## Cópia só visual do sprite para tocar a morte depois que o inimigo some.
func _spawn_death_visual() -> void:
	if sprite == null or sprite.sprite_frames == null or run == null or not sprite.sprite_frames.has_animation(&"death"):
		return
	if run.enemies_node.get_child_count() > 160:
		return
	# O corpo morto entra na mesma ordenação em Y dos inimigos (e não no nó de efeitos).
	var holder: Node2D = Node2D.new()
	run.enemies_node.add_child(holder)
	holder.global_position = global_position
	var v: AnimatedSprite2D = AnimatedSprite2D.new()
	v.sprite_frames = sprite.sprite_frames
	v.scale = sprite.scale
	v.flip_h = sprite.flip_h
	v.position = sprite.position
	holder.add_child(v)
	v.play(&"death")
	v.animation_finished.connect(holder.queue_free)


func display_name() -> String:
	if elite and elite_mod != "":
		return "Anomalia %s" % (elite_data.nome if elite_data != null else elite_mod.capitalize())
	return data.nome


# ------------------------------------------------------------- dano
func take_damage(amount: float, _tag: String = "") -> void:
	if not alive or run == null:
		return
	var mult: float = run.state.stat("elite_dmg_mult") if (elite or is_boss) else run.state.stat("common_dmg_mult")
	var final_dmg: float = amount * mult
	if weaken_time > 0.0:
		final_dmg *= weaken_mult
	if is_boss and run.boss_immune_time > 0.0:
		final_dmg = 0.0
	hp -= final_dmg
	flash = 1.0
	if final_dmg > 0.0:
		run.float_text(global_position + Vector2(0.0, -radius - 8.0), str(maxi(1, roundi(final_dmg))), Color(1.0, 0.95, 0.6))
		AudioManager.play_sfx("hit", randf_range(0.9, 1.2), -7.0)
	if hp <= 0.0:
		die()


func _apply_dot(amount: float) -> void:
	if not alive:
		return
	hp -= amount
	flash = maxf(flash, 0.3)
	if hp <= 0.0:
		die()


func die() -> void:
	if not alive:
		return
	alive = false
	hp = 0.0
	collision_layer = 0
	_spawn_death_visual()
	visible = false
	set_physics_process(false)
	run.on_enemy_killed(self)
	run.mark_dead(self)


func apply_knockback(v: Vector2) -> void:
	knock += v * knock_mult
	if knock.length() > 650.0:
		knock = knock.normalized() * 650.0


## Enfraquecimento (Nuvem de Esporos / sinergia do Pulso): mais dano recebido e,
## se `slow` < 1, movimento mais lento.
func apply_weaken(sec: float, dmg_mult: float, slow: float) -> void:
	if weaken_time <= 0.0:
		weaken_mult = dmg_mult
		weaken_slow = slow
	else:
		weaken_mult = maxf(weaken_mult, dmg_mult)
		weaken_slow = minf(weaken_slow, slow)
	weaken_time = maxf(weaken_time, sec)


func apply_poison(dps: float, dur: float) -> void:
	poison_dps = maxf(poison_dps, dps)
	poison_time = maxf(poison_time, dur)


func apply_root(sec: float) -> void:
	if is_boss or data.comportamento == "ninho":
		return
	root_time = maxf(root_time, sec)


# ------------------------------------------------------------- loop
func _physics_process(delta: float) -> void:
	if not alive or run == null or run.ended:
		return
	anim_t += delta
	contact_cd = maxf(0.0, contact_cd - delta)
	flash = maxf(0.0, flash - delta * 5.0)
	empower_time = maxf(0.0, empower_time - delta)
	weaken_time = maxf(0.0, weaken_time - delta)
	mark_time = maxf(0.0, mark_time - delta)
	slide_bias_time = maxf(0.0, slide_bias_time - delta)
	if regen_rate > 0.0:
		hp = minf(max_hp, hp + regen_rate * delta)
	if poison_time > 0.0:
		poison_time -= delta
		_apply_dot(poison_dps * delta)
		if not alive:
			return
	var target: Vector2 = run.get_enemy_target_pos(global_position)
	var to_t: Vector2 = target - global_position
	var dist: float = to_t.length()
	var dir: Vector2 = Vector2.ZERO
	if dist > 0.001:
		dir = to_t / dist
	var move: Vector2 = Vector2.ZERO
	if root_time > 0.0:
		root_time -= delta
	else:
		move = _behavior(delta, dir, dist, target)
		if move.length() > 1.0:
			look_dir = move.normalized()
	if empower_time > 0.0:
		move *= 1.3
	if weaken_time > 0.0 and not is_boss:
		move *= weaken_slow
	knock = knock.move_toward(Vector2.ZERO, 1100.0 * delta)
	velocity = move + knock
	move_and_slide()
	if get_slide_collision_count() > 0 and move.length() > 1.0 and slide_bias_time <= 0.0:
		slide_bias_time = 0.6
		slide_side = 1.0 if randf() < 0.5 else -1.0
		flank_angle += PI * 0.5
	if not is_boss:
		var push: Vector2 = WorldLayout.safe_push(global_position)
		if push != Vector2.ZERO:
			global_position += push
	_try_contact()
	queue_redraw()


func _steer(d: Vector2) -> Vector2:
	if slide_bias_time > 0.0:
		return d.rotated(slide_side * 0.9)
	return d


func _has_contact() -> bool:
	var c: String = data.comportamento
	return c != "distancia" and c != "ninho" and c != "estrutura"


func _try_contact() -> void:
	if not _has_contact() or contact_cd > 0.0:
		return
	var pl: Player = run.player
	if pl == null or pl.dead:
		return
	var rr: float = radius + Player.RADIUS
	if global_position.distance_squared_to(pl.global_position) <= rr * rr:
		var dmg: float = damage * (1.25 if empower_time > 0.0 else 1.0)
		pl.take_damage(dmg, global_position)
		contact_cd = maxf(0.5, data.intervalo_ataque)


func _behavior(delta: float, dir: Vector2, dist: float, target: Vector2) -> Vector2:
	var c: String = data.comportamento
	if c == "veloz":
		return _b_charger(delta, dir, dist, target)
	if c == "distancia":
		return _b_ranged(delta, dir, dist)
	if c == "esporideo":
		return _b_spore(delta, dir)
	if c == "parasita":
		return _b_parasite(delta, dir, dist)
	if c == "ninho":
		return _b_nest(delta)
	if c == "estrutura":
		return _b_structure(delta)
	if c == "tanque":
		return _steer(dir) * speed
	return _b_chase(dir, dist, target)


func _b_chase(dir: Vector2, dist: float, target: Vector2) -> Vector2:
	var goal: Vector2 = target + Vector2.from_angle(flank_angle) * clampf(dist * 0.35, 0.0, 80.0)
	var d: Vector2 = goal - global_position
	if dist < 60.0 or d.length() < 1.0:
		d = dir
	else:
		d = d.normalized()
	return _steer(d) * speed


func _b_charger(delta: float, dir: Vector2, dist: float, target: Vector2) -> Vector2:
	if mode == 0:
		timer_a -= delta
		if timer_a <= 0.0 and dist < 340.0 and dist > 80.0:
			mode = 1
			timer_b = 0.4
		return _steer(dir) * speed * 0.9
	if mode == 1:
		timer_b -= delta
		flash = maxf(flash, 0.55)
		if timer_b <= 0.0:
			mode = 2
			timer_b = 0.45
			charge_dir = (target - global_position).normalized()
		return Vector2.ZERO
	if mode == 2:
		timer_b -= delta
		if timer_b <= 0.0:
			mode = 3
			timer_b = 0.7
		return charge_dir * data.parametro_a
	timer_b -= delta
	if timer_b <= 0.0:
		mode = 0
		timer_a = data.parametro_b + randf() * 0.8
	return Vector2.ZERO


func _b_ranged(delta: float, dir: Vector2, dist: float) -> Vector2:
	var pref: float = data.alcance_preferido
	var m: Vector2 = Vector2.ZERO
	if dist > pref + 40.0:
		m = dir
	elif dist < pref - 70.0:
		m = -dir
	else:
		m = dir.orthogonal() * strafe_side * 0.5
	timer_a -= delta
	if timer_a <= 0.0 and dist < pref + 140.0:
		timer_a = data.intervalo_ataque + randf() * 0.5
		_shoot(run.player.global_position)
	return _steer(m) * speed


func _shoot(at: Vector2) -> void:
	play_event(&"shoot", 0.4)
	var p: Projectile = run.new_projectile()
	p.friendly = false
	p.dir = (at - global_position).normalized()
	p.speed = 230.0
	p.damage = damage
	p.life = 2.4
	p.radius = 6.0
	p.color = Color(0.95, 0.35, 0.85)
	p.position = global_position + p.dir * (radius + 4.0)
	run.spawn_projectile(p)
	AudioManager.play_sfx("spit", randf_range(0.9, 1.1), -9.0)


func _b_spore(delta: float, dir: Vector2) -> Vector2:
	timer_a -= delta
	if timer_a <= 0.0:
		timer_a = data.intervalo_ataque
		play_event(&"spore", 0.4)
		run.spawn_spore_zone(global_position, data.parametro_a, data.parametro_b, 6.0)
	return _steer(dir) * speed


func _b_parasite(delta: float, dir: Vector2, dist: float) -> Vector2:
	timer_a -= delta
	if timer_a <= 0.0:
		timer_a = 0.5
		play_event(&"pulse", 0.5)
		var r2: float = data.parametro_a * data.parametro_a
		for e in run.enemies:
			if not is_instance_valid(e) or e == self:
				continue
			var en: Enemy = e
			if en.alive and en.global_position.distance_squared_to(global_position) <= r2:
				en.empower_time = 1.0
	var pref: float = data.alcance_preferido
	var m: Vector2 = Vector2.ZERO
	if dist > pref + 30.0:
		m = dir
	elif dist < pref - 50.0:
		m = -dir
	else:
		m = dir.orthogonal() * strafe_side * 0.4
	return _steer(m) * speed


## Estrutura do Coração: parada, lança raízes telegrafadas sobre o jogador.
func _b_structure(delta: float) -> Vector2:
	timer_a -= delta
	if timer_a <= 0.0:
		timer_a = data.intervalo_ataque
		var pl: Player = run.player
		if pl != null and not pl.dead and global_position.distance_to(pl.global_position) < 700.0:
			run.spawn_root_slam(pl.global_position, 52.0, data.parametro_a, 1.0)
	return Vector2.ZERO


func _b_nest(delta: float) -> Vector2:
	if run.player != null and global_position.distance_to(run.player.global_position) < 700.0:
		seen = true
	timer_a -= delta
	if timer_a <= 0.0:
		timer_a = data.intervalo_ataque
		var pl: Player = run.player
		if pl != null and global_position.distance_to(pl.global_position) < 900.0:
			var alive_children: Array = []
			for c in nest_children:
				if is_instance_valid(c) and (c as Enemy).alive:
					alive_children.append(c)
			nest_children = alive_children
			if nest_children.size() < 4:
				var pos: Vector2 = global_position + Vector2.from_angle(randf() * TAU) * (radius + 22.0)
				if run.is_free_spot(pos, 12.0):
					play_event(&"spawn", 0.5)
					var child: Enemy = run.spawn_enemy("larva_fertil", pos, 1.0)
					if child != null:
						nest_children.append(child)
	return Vector2.ZERO


# ----------------------------------------------------------- desenho
func _tint(c: Color) -> Color:
	return c.lerp(Color(1, 1, 1), clampf(flash * 0.75, 0.0, 0.85))


func _draw() -> void:
	if _dd() == null:
		return
	if draw_placeholder:
		draw_circle(Vector2(0, radius * 0.7), radius * 0.9, Color(0, 0, 0, 0.28))
		_draw_body()
	if hp < max_hp and not is_boss:
		var w: float = maxf(18.0, radius * 2.0)
		var y: float = -radius - 8.0
		draw_rect(Rect2(-w * 0.5, y, w, 3.0), Color(0, 0, 0, 0.7))
		draw_rect(Rect2(-w * 0.5, y, w * clampf(hp / max_hp, 0.0, 1.0), 3.0), Color(0.9, 0.3, 0.35))
	if elite:
		draw_arc(Vector2.ZERO, radius + 5.0, 0.0, TAU, 28, Color(1.0, 0.8, 0.2, 0.6 + 0.3 * sin(anim_t * 5.0)), 2.0)
		var font: Font = ThemeDB.fallback_font
		var label: String = display_name()
		var sz: Vector2 = font.get_string_size(label, HORIZONTAL_ALIGNMENT_LEFT, -1, 11)
		draw_string(font, Vector2(-sz.x * 0.5, -radius - 14.0), label, HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color(1.0, 0.9, 0.5))
	if weaken_time > 0.0:
		draw_arc(Vector2.ZERO, radius + 8.0, 0.0, TAU, 20, Color(0.5, 1.0, 0.8, 0.55), 1.5)
	if mark_time > 0.0:
		draw_colored_polygon(PackedVector2Array([Vector2(0, -radius - 20.0), Vector2(5, -radius - 14.0), Vector2(0, -radius - 8.0), Vector2(-5, -radius - 14.0)]), Color(1.0, 0.85, 0.3, 0.9))
	if empower_time > 0.0:
		draw_arc(Vector2.ZERO, radius + 3.0, 0.0, TAU, 20, Color(0.5, 0.95, 1.0, 0.7), 1.5)
	if root_time > 0.0:
		draw_arc(Vector2.ZERO, radius + 6.0, 0.0, TAU, 20, Color(0.5, 1.0, 0.4, 0.8), 2.0)


func _draw_body() -> void:
	var d: EnemyData = _dd()
	var col: Color = _tint(d.cor)
	var det: Color = _tint(d.cor_detalhe)
	var id: String = d.id
	var wob: float = sin(anim_t * 9.0) * 1.5
	if id == "cortarraiz":
		var f: Vector2 = look_dir
		var s: Vector2 = f.orthogonal()
		draw_colored_polygon(PackedVector2Array([f * radius * 1.5, s * radius * 0.8 - f * radius * 0.8, -f * radius * 0.3, -s * radius * 0.8 - f * radius * 0.8]), col)
		draw_circle(f * radius * 0.3, 2.5, det)
	elif id == "flor_ruptura":
		for i in 6:
			var a: float = anim_t * 0.8 + float(i) * TAU / 6.0
			draw_circle(Vector2.from_angle(a) * radius * 0.8, radius * 0.45, col)
		draw_circle(Vector2.ZERO, radius * 0.55, det)
	elif id == "casca_tumulo":
		draw_circle(Vector2.ZERO, radius, col)
		draw_arc(Vector2.ZERO, radius * 0.7, 0.0, TAU, 6, det, 3.0)
		draw_circle(Vector2.ZERO, radius * 0.3, det)
	elif id == "esporideo":
		draw_circle(Vector2.ZERO, radius, col)
		for i in 5:
			var a2: float = float(i) * TAU / 5.0 + anim_t * 0.5
			draw_circle(Vector2.from_angle(a2) * radius * 0.9, 3.5, det)
	elif id == "parasita_sinal":
		draw_circle(Vector2.ZERO, radius * 0.8, col)
		draw_arc(Vector2.ZERO, radius * 1.3 + wob, 0.0, TAU, 16, det, 1.5)
		draw_circle(Vector2(0, -2), 2.5, det)
	elif id == "anomalia":
		draw_circle(Vector2.ZERO, radius, col)
		for i in 7:
			var a3: float = float(i) * TAU / 7.0 + anim_t
			var p0: Vector2 = Vector2.from_angle(a3) * radius
			draw_line(p0, p0 * 1.4, det, 3.0)
		draw_circle(Vector2(-4, -3), 2.5, det)
		draw_circle(Vector2(4, -3), 2.5, det)
	elif id == "ninho":
		var pulse: float = 1.0 + 0.08 * sin(anim_t * 3.0)
		draw_circle(Vector2.ZERO, radius * pulse, col)
		draw_circle(Vector2(-8, -6), radius * 0.5, _tint(d.cor.lightened(0.15)))
		draw_circle(Vector2(8, -4), radius * 0.45, _tint(d.cor.lightened(0.1)))
		draw_circle(Vector2(0, 8), radius * 0.4, det)
		var w: float = 44.0
		draw_rect(Rect2(-w * 0.5, -radius - 12.0, w, 4.0), Color(0, 0, 0, 0.7))
		draw_rect(Rect2(-w * 0.5, -radius - 12.0, w * clampf(hp / max_hp, 0.0, 1.0), 4.0), Color(0.95, 0.45, 0.7))
	else:
		draw_circle(Vector2(0, wob * 0.3), radius, col)
		draw_circle(Vector2(-3, -2 + wob * 0.3), 2.0, det)
		draw_circle(Vector2(3, -2 + wob * 0.3), 2.0, det)
