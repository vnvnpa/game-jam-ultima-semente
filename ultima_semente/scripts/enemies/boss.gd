class_name Boss
extends Enemy
## Guardião de Raízes: chefe do MVP com dois padrões de ataque
## (Raízes Esmagadoras e Invocação). Na fase 2 (<50% de vida) fica mais rápido.

var slam_timer: float = 3.0
var summon_timer: float = 8.0
var phase: int = 1
var summons: Array = []


func _behavior(delta: float, dir: Vector2, dist: float, _target: Vector2) -> Vector2:
	if phase == 1 and hp < max_hp * 0.5:
		phase = 2
		play_event(&"phase2", 0.5)
		run.notify("O Guardião enfurece! Fase 2.", Color(1.0, 0.5, 0.4), "boss")
	var fast: float = 1.0 if phase == 1 else 0.7
	if run.boss_immune_time <= 0.0:
		slam_timer -= delta
		summon_timer -= delta
		if slam_timer <= 0.0:
			slam_timer = 6.0 * fast
			_pattern_slam()
		if summon_timer <= 0.0:
			summon_timer = 14.0 * fast
			_pattern_summon()
	if dist > 110.0:
		return _steer(dir) * speed * (1.0 if phase == 1 else 1.3)
	return Vector2.ZERO


func _pattern_slam() -> void:
	play_event(&"slam", 0.75)
	var pl: Player = run.player
	if pl == null or pl.dead:
		return
	var count: int = 3 if phase == 1 else 5
	var dmg: float = data.parametro_a
	run.spawn_root_slam(pl.global_position, 62.0, dmg, 1.0)
	for i in count - 1:
		var off: Vector2 = Vector2.from_angle(randf() * TAU) * randf_range(90.0, 170.0)
		run.spawn_root_slam(pl.global_position + off, 62.0, dmg, 1.0 + 0.25 * float(i + 1))
	AudioManager.play_sfx("alert", 0.7, -6.0)


func _pattern_summon() -> void:
	play_event(&"summon", 0.75)
	var alive_n: Array = []
	for s in summons:
		if is_instance_valid(s) and (s as Enemy).alive:
			alive_n.append(s)
	summons = alive_n
	var count: int = 4 if phase == 1 else 6
	for i in count:
		if summons.size() >= 12:
			break
		var pos: Vector2 = global_position + Vector2.from_angle(randf() * TAU) * randf_range(60.0, 110.0)
		if run.is_free_spot(pos, 12.0):
			var e: Enemy = run.spawn_enemy("larva_fertil", pos, 1.0)
			if e != null:
				summons.append(e)
	run.fx_ring(global_position, 120.0, Color(0.7, 0.4, 0.9), 0.5)
	AudioManager.play_sfx("boss", 1.2, -8.0)


func _draw() -> void:
	if data == null:
		return
	if draw_placeholder:
		draw_circle(Vector2(0, radius * 0.8), radius * 1.1, Color(0, 0, 0, 0.3))
		var col: Color = _tint(data.cor)
		for i in 10:
			var a: float = float(i) * TAU / 10.0 + sin(anim_t * 0.7 + float(i)) * 0.15
			var p1: Vector2 = Vector2.from_angle(a) * radius * 0.8
			var p2: Vector2 = Vector2.from_angle(a + sin(anim_t + float(i)) * 0.3) * (radius * 1.7)
			draw_line(p1, p2, col.darkened(0.25), 6.0)
		draw_circle(Vector2.ZERO, radius, col)
		draw_arc(Vector2.ZERO, radius * 0.75, 0.0, TAU, 12, col.lightened(0.2), 3.0)
		var core: float = 0.6 + 0.4 * sin(anim_t * 4.0)
		var core_col: Color = Color(0.5, 0.95, 1.0) if run.boss_immune_time <= 0.0 else Color(0.6, 0.6, 0.7)
		draw_circle(Vector2.ZERO, radius * 0.4, Color(core_col.r, core_col.g, core_col.b, 0.35 + 0.4 * core))
		draw_circle(Vector2.ZERO, radius * 0.22, _tint(Color(0.7, 0.4, 1.0)))
	if run != null and run.state.has_special("consciencia_rede"):
		var font: Font = ThemeDB.fallback_font
		var txt: String = "Raízes em %.0fs  |  Invocação em %.0fs" % [maxf(0.0, slam_timer), maxf(0.0, summon_timer)]
		var sz: Vector2 = font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, 12)
		draw_string(font, Vector2(-sz.x * 0.5, -radius - 30.0), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color(0.7, 0.95, 1.0))
