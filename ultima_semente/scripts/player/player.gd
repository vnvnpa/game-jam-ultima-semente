class_name Player
extends CharacterBody2D
## Kael: movimento, arma automática (Espinho Simbiótico), habilidades
## (Pulso de Raízes, Ruptura Celular), vida, escudo e câmera.

const RADIUS: float = 11.0

@export_group("Pulso de Raízes (Espaço)")
@export var pulse_radius: float = 150.0
@export var pulse_damage: float = 30.0
@export var pulse_cooldown: float = 8.0
@export var pulse_knockback: float = 320.0
@export_group("Ruptura Celular (Q)")
@export var dash_speed: float = 720.0
@export var dash_duration: float = 0.18
@export var dash_cooldown: float = 5.0
@export_group("Pulso de Emergência (R)")
@export var emergency_radius: float = 190.0
@export var emergency_knockback: float = 520.0
@export_group("Sobrevivência")
@export var hit_invulnerability: float = 0.35
@export var companion_orbit_radius: float = 46.0
@export var companion_damage: float = 8.0
@export_group("Visual")
@export var draw_placeholder: bool = true
@export_group("")

var run: Run = null
var hp: float = 100.0
var last_max_hp: float = 100.0
var shield: float = 0.0
var dead: bool = false
var facing: Vector2 = Vector2.RIGHT
var aim_dir: Vector2 = Vector2.RIGHT
var fire_cd: float = 0.0
var pulse_cd: float = 0.0
var dash_cd: float = 0.0
var dash_t: float = 0.0
var dash_dir: Vector2 = Vector2.RIGHT
var invuln: float = 0.0
var since_damage: float = 99.0
var carapace_cd: float = 0.0
var field_shield_t: float = 0.0
var casca_viva_t: float = 0.0
var comp_cd: Array = []
var comp_angle: float = 0.0
var shake_power: float = 0.0
var hurt_flash: float = 0.0
var anim_t: float = 0.0
@onready var camera: Camera2D = $Camera
var pulse_cd_max: float = 8.0
var dash_cd_max: float = 5.0


func setup(r: Run) -> void:
	run = r
	last_max_hp = run.state.max_hp()
	hp = last_max_hp


## Chamado sempre que os atributos são recalculados.
func refresh_stats() -> void:
	var new_max: float = run.state.max_hp()
	if new_max > last_max_hp:
		hp += new_max - last_max_hp
	hp = minf(hp, new_max)
	last_max_hp = new_max
	hp = maxf(hp, 1.0) if not dead else hp


func add_shake(amount: float) -> void:
	if GameManager.reduce_fx():
		return
	shake_power = maxf(shake_power, amount)


# ---------------------------------------------------------- vida
func heal(amount: float, apply_mult: bool = true) -> void:
	if dead or amount <= 0.0:
		return
	var a: float = amount
	if apply_mult:
		a *= run.state.stat("heal_mult")
	hp = minf(run.state.max_hp(), hp + a)


func add_shield(amount: float, cap: float) -> void:
	if dead:
		return
	shield = minf(cap, shield + amount)
	if shield > cap:
		shield = cap


func take_damage(amount: float, _from_pos: Vector2 = Vector2.ZERO) -> void:
	if dead or invuln > 0.0 or run == null or run.ended:
		return
	var st: RunState = run.state
	var dmg: float = amount * st.stat("damage_taken_mult")
	since_damage = 0.0
	hurt_flash = 1.0
	if shield > 0.0:
		var absorbed: float = minf(shield, dmg)
		shield -= absorbed
		dmg -= absorbed
		if dmg <= 0.0:
			invuln = 0.2
			AudioManager.play_sfx("hit", 0.7, -4.0)
			return
	hp -= dmg
	invuln = hit_invulnerability
	add_shake(4.0)
	AudioManager.play_sfx("hurt")
	run.float_text(global_position + Vector2(0, -26), "-%d" % maxi(1, roundi(dmg)), Color(1.0, 0.45, 0.45))
	if st.has_special("carapaca_profunda") and carapace_cd <= 0.0 and dmg >= 0.12 * st.max_hp():
		run.add_buff("carapaca", 3.0)
		carapace_cd = 10.0
	if hp <= 0.0:
		_on_lethal("inimigo")


## Dano contínuo (esporos): sem tempo de invulnerabilidade.
func take_dot(amount: float) -> void:
	if dead or run == null or run.ended or dash_t > 0.0:
		return
	var dmg: float = amount * run.state.stat("damage_taken_mult")
	since_damage = 0.0
	if shield > 0.0:
		var absorbed: float = minf(shield, dmg)
		shield -= absorbed
		dmg -= absorbed
	hp -= dmg
	if hp <= 0.0:
		_on_lethal("esporos")


## Perda de vida direta (falta de oxigênio): ignora escudo e invulnerabilidade.
func lose_hp(amount: float, cause: String) -> void:
	if dead or run == null or run.ended:
		return
	hp -= amount
	hurt_flash = maxf(hurt_flash, 0.4)
	if hp <= 0.0:
		_on_lethal(cause)


func _on_lethal(cause: String) -> void:
	var st: RunState = run.state
	if st.has_special("reserva_organica") and not st.revive_used:
		st.revive_used = true
		hp = maxf(1.0, st.max_hp() * 0.1)
		invuln = 2.0
		run.damage_area(global_position, 220.0, 0.0, 600.0, 0.0)
		run.fx_ring(global_position, 220.0, Color(0.5, 1.0, 0.6), 0.6)
		if cause == "oxigênio":
			run.oxygen.add_percent(0.4)
		run.notify("Reserva Orgânica ativada! Você sobreviveu.", UIKit.COL_GOOD, "mutation")
		return
	dead = true
	hp = 0.0
	run.on_player_died(cause)


# --------------------------------------------------------- loop
func _physics_process(delta: float) -> void:
	if dead or run == null or run.ended:
		return
	anim_t += delta
	var st: RunState = run.state
	invuln = maxf(0.0, invuln - delta)
	since_damage += delta
	hurt_flash = maxf(0.0, hurt_flash - delta * 4.0)
	fire_cd = maxf(0.0, fire_cd - delta)
	pulse_cd = maxf(0.0, pulse_cd - delta)
	dash_cd = maxf(0.0, dash_cd - delta)
	carapace_cd = maxf(0.0, carapace_cd - delta)
	comp_angle += 2.2 * delta
	# regeneração fora de perigo
	var regen: float = st.stat("regen")
	if regen > 0.0 and since_damage > 4.0 + st.stat("regen_delay_bonus") and hp < st.max_hp():
		heal(regen * delta)
	# escudos periódicos
	if st.has_special("escudo_campo") and shield < 60.0:
		field_shield_t += delta
		if field_shield_t >= 20.0:
			field_shield_t = 0.0
			add_shield(25.0, 60.0)
			run.notify("Escudo de Campo recarregado.", UIKit.COL_NUC, "")
	if st.has_special("casca_viva") and shield < 60.0:
		casca_viva_t += delta
		if casca_viva_t >= 10.0:
			casca_viva_t = 0.0
			add_shield(15.0, 60.0)
	# movimento
	var input: Vector2 = Input.get_vector("move_left", "move_right", "move_up", "move_down")
	var mouse_dir: Vector2 = get_global_mouse_position() - global_position
	if mouse_dir.length() > 6.0:
		facing = mouse_dir.normalized()
	if dash_t > 0.0:
		dash_t -= delta
		velocity = dash_dir * dash_speed
	else:
		velocity = input * st.move_speed()
	move_and_slide()
	var clamped: Vector2 = Vector2(
		clampf(global_position.x, 14.0, WorldLayout.WORLD_RECT.size.x - 14.0),
		clampf(global_position.y, 14.0, WorldLayout.WORLD_RECT.size.y - 14.0))
	global_position = clamped
	# habilidades
	if Input.is_action_just_pressed("skill_1"):
		use_pulse()
	if Input.is_action_just_pressed("skill_2"):
		use_dash()
	if Input.is_action_just_pressed("use_pulse"):
		use_emergency_pulse()
	# arma automática
	var target: Enemy = _find_target()
	if target != null:
		aim_dir = (target.global_position - global_position).normalized()
		if fire_cd <= 0.0:
			_fire(target)
	else:
		aim_dir = facing
	_update_companions(delta)
	# câmera
	if camera != null:
		shake_power = move_toward(shake_power, 0.0, 30.0 * delta)
		if shake_power > 0.05:
			camera.offset = Vector2(randf_range(-1.0, 1.0), randf_range(-1.0, 1.0)) * shake_power
		else:
			camera.offset = Vector2.ZERO
	queue_redraw()


func _find_target() -> Enemy:
	var rng: float = GameData.weapon.alcance * run.state.stat("range_mult")
	var best: Enemy = null
	var best_d: float = rng * rng
	for e in run.enemies:
		if not is_instance_valid(e):
			continue
		var en: Enemy = e
		if not en.alive:
			continue
		var d: float = global_position.distance_squared_to(en.global_position)
		if d < best_d:
			best_d = d
			best = en
	return best


func _fire(target: Enemy) -> void:
	var st: RunState = run.state
	var w: WeaponData = GameData.weapon
	fire_cd = w.intervalo / st.stat("fire_rate_mult")
	var base_dir: Vector2 = (target.global_position - global_position).normalized()
	var n: int = 1 + int(st.stat("extra_projectiles"))
	var dmg: float = w.dano * st.stat("damage_mult")
	var spd: float = w.velocidade_projetil * st.stat("proj_speed_mult")
	var poison: bool = st.has_special("veneno")
	for i in n:
		var off: float = (float(i) - float(n - 1) * 0.5) * 0.16
		var p: Projectile = run.new_projectile()
		p.dir = base_dir.rotated(off)
		p.speed = spd
		p.damage = dmg
		p.pierce = w.perfuracao + int(st.stat("pierce"))
		p.life = (w.alcance * st.stat("range_mult") * 1.15) / spd
		p.radius = w.raio_projetil
		p.poison = poison
		p.color = Color(0.55, 1.0, 0.6) if not poison else Color(0.8, 1.0, 0.3)
		p.position = global_position + p.dir * 14.0
		run.spawn_projectile(p)
	AudioManager.play_sfx("shoot", randf_range(0.92, 1.12), -8.0)


# ------------------------------------------------------ habilidades
func _trigger_overload() -> void:
	var st: RunState = run.state
	if st.has_special("sobrecarga_celular") and not st.buffs.has("sobrecarga") and not st.buffs.has("sobrecarga_recarga"):
		run.add_buff("sobrecarga", 4.0)
		run.notify("Sobrecarga Celular!", UIKit.COL_WARN, "")


func use_pulse() -> void:
	if dead or pulse_cd > 0.0:
		return
	var st: RunState = run.state
	_trigger_overload()
	var power: float = st.stat("skill_power_mult")
	var rad: float = pulse_radius * power
	var dmg: float = pulse_damage * st.stat("damage_mult") * st.stat("skill_damage_mult") * power
	pulse_cd_max = pulse_cooldown * st.stat("skill_cd_mult")
	pulse_cd = pulse_cd_max
	var root: float = 1.6 if st.has_special("enraizar") else 0.0
	run.damage_area(global_position, rad, dmg, pulse_knockback, root)
	run.fx_ring(global_position, rad, Color(0.5, 1.0, 0.6), 0.45)
	add_shake(5.0)
	AudioManager.play_sfx("pulse")


func use_emergency_pulse() -> void:
	if dead or run.state.pulse_charges <= 0:
		return
	run.state.pulse_charges -= 1
	run.damage_area(global_position, emergency_radius, 0.0, emergency_knockback, 0.0)
	run.fx_ring(global_position, emergency_radius, Color(0.5, 0.9, 1.0), 0.4)
	add_shake(4.0)
	AudioManager.play_sfx("pulse", 1.3)


func use_dash() -> void:
	if dead or dash_cd > 0.0 or dash_t > 0.0:
		return
	var st: RunState = run.state
	var d: Vector2 = Input.get_vector("move_left", "move_right", "move_up", "move_down")
	if d == Vector2.ZERO:
		d = facing
	dash_dir = d.normalized()
	dash_t = dash_duration
	invuln = maxf(invuln, 0.26)
	dash_cd_max = dash_cooldown * st.stat("skill_cd_mult")
	dash_cd = dash_cd_max
	run.fx_burst(global_position, Color(0.6, 1.0, 0.8), 8, 22.0)
	var lv: int = st.upgrade_level("casca_regenerativa")
	if lv > 0:
		add_shield(8.0 * float(lv), 60.0)
	AudioManager.play_sfx("dash")


func _update_companions(delta: float) -> void:
	var n: int = int(run.state.stat("companions"))
	while comp_cd.size() < n:
		comp_cd.append(randf() * 0.8)
	while comp_cd.size() > n:
		comp_cd.pop_back()
	for i in n:
		comp_cd[i] = float(comp_cd[i]) - delta
		if float(comp_cd[i]) > 0.0:
			continue
		var cpos: Vector2 = global_position + Vector2.from_angle(comp_angle + float(i) * TAU / float(n)) * companion_orbit_radius
		var best: Enemy = null
		var best_d: float = 150.0 * 150.0
		for e in run.enemies:
			if not is_instance_valid(e):
				continue
			var en: Enemy = e
			if not en.alive:
				continue
			var dd: float = cpos.distance_squared_to(en.global_position)
			if dd < best_d:
				best_d = dd
				best = en
		if best != null:
			comp_cd[i] = 1.1
			best.take_damage(companion_damage * run.state.stat("damage_mult"), "mic")
			run.fx_burst(best.global_position, Color(0.8, 0.5, 1.0), 4, 12.0)
		else:
			comp_cd[i] = 0.25


# ------------------------------------------------------- desenho
func _draw() -> void:
	if not draw_placeholder:
		return
	var st: RunState = run.state if run != null else null
	var moving: bool = velocity.length() > 10.0
	var walk: float = sin(anim_t * 14.0) * 2.5 if moving else 0.0
	draw_circle(Vector2(0, 11), 9.0, Color(0, 0, 0, 0.3))
	var mut_count: int = 0
	if st != null:
		mut_count = mini(8, st.perm_ids.size() + floori(float(st.total_upgrade_levels()) / 2.0))
	# espinhos de mutação (silhueta evolui)
	for i in mut_count:
		var a: float = PI + (float(i) - float(mut_count - 1) * 0.5) * 0.4
		var base: Vector2 = Vector2.from_angle(a + facing.angle() + PI) * 8.0
		draw_line(base, base * 2.0, Color(0.75, 0.4, 0.95), 3.0)
	var flick: bool = invuln > 0.0 and int(anim_t * 20.0) % 2 == 0
	var a_mod: float = 0.45 if flick else 1.0
	draw_rect(Rect2(-5, 6 + walk * 0.4, 4, 7), Color(0.3, 0.32, 0.36, a_mod))
	draw_rect(Rect2(1, 6 - walk * 0.4, 4, 7), Color(0.3, 0.32, 0.36, a_mod))
	var suit: Color = Color(0.95, 0.55, 0.2, a_mod).lerp(Color(1, 0.3, 0.3, a_mod), hurt_flash * 0.7)
	draw_rect(Rect2(-6, -8, 12, 15), suit)
	draw_rect(Rect2(-6, -2, 12, 3), Color(0.92, 0.92, 0.9, a_mod))
	draw_circle(Vector2(0, -13), 7.0, Color(0.82, 0.84, 0.86, a_mod))
	draw_circle(Vector2(facing.x * 2.5, -13 + facing.y * 2.0), 3.5, Color(0.3, 0.9, 1.0, a_mod))
	draw_line(Vector2(0, -3), aim_dir * 17.0 + Vector2(0, -3), Color(0.4, 0.85, 0.5, a_mod), 4.0)
	draw_circle(aim_dir * 17.0 + Vector2(0, -3), 2.5, Color(0.8, 1.0, 0.6, a_mod))
	if shield > 0.0:
		draw_arc(Vector2(0, -2), 17.0, 0.0, TAU, 28, Color(0.5, 0.9, 1.0, 0.4 + 0.3 * sin(anim_t * 6.0)), 2.0)
	if st != null:
		var n: int = int(st.stat("companions"))
		for i in n:
			var cp: Vector2 = Vector2.from_angle(comp_angle + float(i) * TAU / float(n)) * companion_orbit_radius
			draw_circle(cp, 6.0, Color(0.75, 0.45, 0.95))
			draw_circle(cp + Vector2(0, -2), 3.0, Color(1.0, 0.8, 1.0))
