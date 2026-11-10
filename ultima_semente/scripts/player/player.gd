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
@onready var sprite: AnimatedSprite2D = get_node_or_null("Sprite") as AnimatedSprite2D
@onready var shield_fx: AnimatedSprite2D = get_node_or_null("ShieldFx") as AnimatedSprite2D
@onready var spines: Sprite2D = get_node_or_null("Spines") as Sprite2D
@onready var companions_node: Node2D = get_node_or_null("Companions") as Node2D
## Folhas de animação do companheiro (Micélio Guardião).
@export var companion_frames: SpriteFrames
var comp_sprites: Array = []
var _anim: StringName = &""
## Vista atual do Kael: "down" (frente), "up" (costas) ou "side" (perfil, espelhado pela mira).
var _view: String = "down"
## Inimigo travado pela arma automática (a retícula desliza até ele).
var aim_target: Enemy = null
var _weapon_front: bool = true
var _mouse_last: Vector2 = Vector2.ZERO
var _mouse_still_t: float = 0.0
@onready var weapon_sprite: Sprite2D = get_node_or_null("Weapon") as Sprite2D
var pulse_cd_max: float = 8.0
var dash_cd_max: float = 5.0
var cloud_cd: float = 0.0
var cloud_cd_max: float = 14.0
var dart_cd: float = 0.0
var _pad_mode: bool = false


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
		run.add_buff("carapaca")
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
	_show_death()
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
	cloud_cd = maxf(0.0, cloud_cd - delta)
	dart_cd = maxf(0.0, dart_cd - delta)
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
			run.notify("Escudo de Campo recarregado.", UIKit.COL_NUC, "shield")
	if st.has_special("casca_viva") and shield < 60.0:
		casca_viva_t += delta
		if casca_viva_t >= 10.0:
			casca_viva_t = 0.0
			add_shield(15.0, 60.0)
	# movimento
	var input: Vector2 = Input.get_vector("move_left", "move_right", "move_up", "move_down")
	var mouse_dir: Vector2 = get_global_mouse_position() - global_position
	var aim_in: Vector2 = Input.get_vector("aim_left", "aim_right", "aim_up", "aim_down")
	if aim_in.length() > 0.3:
		facing = aim_in.normalized()
	elif _pad_mode:
		if input.length() > 0.2:
			facing = input.normalized()
	elif mouse_dir.length() > 6.0:
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
	if Input.is_action_just_pressed("skill_3"):
		use_cloud()
	# arma automática
	var target: Enemy = _find_target()
	aim_target = target
	if target != null:
		aim_dir = (target.global_position - global_position).normalized()
		if fire_cd <= 0.0:
			_fire(target)
		if dart_cd <= 0.0 and st.has_special("dardo"):
			_fire_dart(target)
	else:
		# Sem alvo: o Kael olha para onde anda quando o mouse está parado (toque/gamepad/teclado).
		var mpos: Vector2 = get_viewport().get_mouse_position()
		if mpos.distance_to(_mouse_last) > 2.0:
			_mouse_still_t = 0.0
			_mouse_last = mpos
		else:
			_mouse_still_t += delta
		if aim_in.length() <= 0.3 and input.length() > 0.2 and (_pad_mode or _mouse_still_t > 0.5):
			facing = input.normalized()
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
		run.add_buff("sobrecarga")
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
	var cab: AbilityData = GameData.abilities.get("nuvem_esporos")
	if cab != null and st.has_special("nuvem_esporos"):
		_weaken_in_radius(rad, cab.fraqueza_pulso, cab.vulnerabilidade)
	run.fx_ring(global_position, rad, Color(0.5, 1.0, 0.6), 0.45)
	add_shake(5.0)
	AudioManager.play_sfx("pulse")


## Sinergia Pulso de Raízes + Nuvem de Esporos: quem é atingido fica vulnerável.
func _weaken_in_radius(rad: float, sec: float, mult: float) -> void:
	for e in run.enemies:
		if not is_instance_valid(e):
			continue
		var en: Enemy = e
		var rr: float = rad + en.radius
		if en.alive and global_position.distance_squared_to(en.global_position) <= rr * rr:
			en.apply_weaken(sec, mult, 1.0)


func use_cloud() -> void:
	if dead or cloud_cd > 0.0 or not run.state.has_special("nuvem_esporos"):
		return
	var ab: AbilityData = GameData.abilities.get("nuvem_esporos")
	if ab == null:
		return
	var st: RunState = run.state
	_trigger_overload()
	var rad: float = ab.raio * st.stat("cloud_power")
	cloud_cd_max = ab.recarga * st.stat("skill_cd_mult")
	cloud_cd = cloud_cd_max
	run.spawn_cloud(global_position, rad, ab.duracao, ab)
	run.fx_ring(global_position, rad, Color(0.5, 1.0, 0.8), 0.4)
	AudioManager.play_sfx("pulse", 0.7, -4.0)


## Dardo de Fotossíntese: segunda arma automática (mutação "dardo").
func _fire_dart(target: Enemy) -> void:
	var w: WeaponData = GameData.dart_weapon
	if w == null:
		return
	var st: RunState = run.state
	var lv: float = maxf(1.0, st.stat("dart_level"))
	dart_cd = w.intervalo / st.stat("fire_rate_mult")
	var p: Projectile = run.new_projectile()
	p.dir = (target.global_position - global_position).normalized()
	p.speed = w.velocidade_projetil * st.stat("proj_speed_mult")
	p.damage = w.dano * st.stat("damage_mult") * (1.0 + w.escala_por_nivel * (lv - 1.0))
	p.pierce = w.perfuracao
	p.life = (w.alcance * st.stat("range_mult") * 1.1) / p.speed
	p.radius = w.raio_projetil
	p.dart = true
	p.mark_bonus = w.bonus_marcado
	p.mark_time = w.duracao_marca
	p.color = Color(0.5, 1.0, 0.9)
	p.position = global_position + p.dir * 14.0
	run.spawn_projectile(p)
	AudioManager.play_sfx("shoot", 1.5, -12.0)


## Detecta se o último dispositivo usado foi o gamepad (mira = direção do movimento).
func _input(event: InputEvent) -> void:
	if event is InputEventJoypadButton:
		_pad_mode = true
	elif event is InputEventJoypadMotion and absf((event as InputEventJoypadMotion).axis_value) > 0.4:
		_pad_mode = true
	elif event is InputEventMouseMotion:
		_pad_mode = false


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


func _show_death() -> void:
	if shield_fx != null:
		shield_fx.visible = false
	if sprite != null and sprite.sprite_frames != null and sprite.sprite_frames.has_animation(&"death"):
		sprite.play(&"death")
		sprite.frame = sprite.sprite_frames.get_frame_count(&"death") - 1
		sprite.modulate.a = 1.0


## Escolhe a vista (frente/costas/perfil) pela direção de mira, com histerese
## para não piscar perto das diagonais.
func _pick_view(d: Vector2) -> String:
	var bias: float = 0.75 if _view == "side" else 1.35
	if absf(d.x) >= absf(d.y) * bias:
		return "side"
	return "up" if d.y < 0.0 else "down"


## Só visual (roda em _process): vista direcional, animação, arma girando para a
## mira, espinhos de mutação, escudo e companheiros.
func _process(_delta: float) -> void:
	if sprite == null or run == null or dead or sprite.sprite_frames == null:
		return
	var st: RunState = run.state
	var d: Vector2 = aim_dir if aim_dir.length() > 0.1 else facing
	_view = _pick_view(d)
	sprite.flip_h = _view == "side" and d.x < 0.0
	var base: String = "idle"
	if dash_t > 0.0:
		base = "dash"
	elif hurt_flash > 0.5:
		base = "hurt"
	elif velocity.length() > 10.0:
		base = "walk"
	var want: StringName = StringName("%s_%s" % [base, _view])
	if want != _anim and sprite.sprite_frames.has_animation(want):
		_anim = want
		sprite.play(want)
	var flick: bool = invuln > 0.0 and int(anim_t * 20.0) % 2 == 0
	sprite.modulate.a = 0.45 if flick else 1.0
	_update_weapon_visual(d)
	if spines != null:
		var n_mut: int = mini(8, st.perm_ids.size() + floori(float(st.total_upgrade_levels()) / 2.0))
		spines.visible = n_mut > 0
		if n_mut > 0 and spines.texture != null:
			spines.region_rect = Rect2(float((n_mut - 1) * 32), 0.0, 32.0, 32.0)
		spines.scale.x = -1.0 if (_view == "side" and d.x < 0.0) else 1.0
	if shield_fx != null:
		shield_fx.visible = shield > 0.0
	_sync_companion_sprites(int(st.stat("companions")))


## A arma aponta para a mira (rotação real) e passa por trás do corpo quando o Kael está de costas.
func _update_weapon_visual(d: Vector2) -> void:
	if weapon_sprite == null:
		return
	weapon_sprite.rotation = d.angle()
	weapon_sprite.flip_v = d.x < 0.0
	weapon_sprite.position = Vector2(0.0, -4.0) + d * 3.0
	var front: bool = d.y >= -0.35
	if front != _weapon_front and sprite != null:
		_weapon_front = front
		if front:
			move_child(weapon_sprite, sprite.get_index() + 1)
		else:
			move_child(weapon_sprite, sprite.get_index())


func _sync_companion_sprites(n: int) -> void:
	if companions_node == null or companion_frames == null:
		return
	while comp_sprites.size() < n:
		var s: AnimatedSprite2D = AnimatedSprite2D.new()
		s.sprite_frames = companion_frames
		s.play(&"idle")
		companions_node.add_child(s)
		comp_sprites.append(s)
	while comp_sprites.size() > n:
		var old: AnimatedSprite2D = comp_sprites.pop_back()
		old.queue_free()
	for i in n:
		(comp_sprites[i] as AnimatedSprite2D).position = Vector2.from_angle(comp_angle + float(i) * TAU / float(n)) * companion_orbit_radius


func _comp_attack_visual(i: int) -> void:
	if i >= comp_sprites.size():
		return
	var s: AnimatedSprite2D = comp_sprites[i]
	s.play(&"attack")
	s.animation_finished.connect(_on_comp_anim_done.bind(s), CONNECT_ONE_SHOT)


func _on_comp_anim_done(s: AnimatedSprite2D) -> void:
	if is_instance_valid(s):
		s.play(&"idle")


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
			_comp_attack_visual(i)
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
