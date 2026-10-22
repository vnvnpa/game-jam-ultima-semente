class_name Gardener
extends Boss
## Jardineiro Vazio (GDD 7.2 e 14.1): máquina antiga com disparos
## direcionados, raízes que cercam o jogador e janelas de vulnerabilidade.
## Fica blindado na maior parte do tempo; só recebe dano com o núcleo exposto.
## Fase 2 (<50% de vida): mais disparos, janelas mais curtas e invocações.
## parametro_a = dano de cada disparo; parametro_b = dano das raízes.

const SHIELDED_TIME: float = 7.0
const EXPOSED_TIME_P1: float = 5.5
const EXPOSED_TIME_P2: float = 4.0

var vulnerable: bool = false
var cycle_t: float = 5.0
var shoot_t: float = 2.5
var roots_t: float = 6.0
var shield_text_cd: float = 0.0


func _behavior(delta: float, dir: Vector2, dist: float, _target: Vector2) -> Vector2:
	if phase == 1 and hp < max_hp * 0.5:
		phase = 2
		run.notify("O Jardineiro acelera os ciclos! Fase 2.", Color(1.0, 0.6, 0.4), "boss")
	var fast: float = 1.0 if phase == 1 else 0.75
	shield_text_cd = maxf(0.0, shield_text_cd - delta)
	if run.boss_immune_time > 0.0:
		return Vector2.ZERO
	cycle_t -= delta
	if cycle_t <= 0.0:
		vulnerable = not vulnerable
		if vulnerable:
			cycle_t = EXPOSED_TIME_P1 if phase == 1 else EXPOSED_TIME_P2
			run.notify("Núcleo exposto! Ataque agora!", UIKit.COL_WARN, "alert")
		else:
			cycle_t = SHIELDED_TIME * fast
		run.fx_ring(global_position, radius * 2.2, Color(1.0, 0.85, 0.4) if vulnerable else Color(0.5, 0.8, 1.0), 0.5)
	shoot_t -= delta
	if shoot_t <= 0.0:
		shoot_t = (3.2 if vulnerable else 2.2) * fast
		_pattern_shots()
	roots_t -= delta
	if roots_t <= 0.0 and not vulnerable:
		roots_t = 7.0 * fast
		_pattern_roots()
	if phase == 2:
		summon_timer -= delta
		if summon_timer <= 0.0:
			summon_timer = 16.0
			_pattern_summon()
	if dist > 280.0:
		return _steer(dir) * speed
	if dist < 150.0:
		return -dir * speed * 0.6
	return dir.orthogonal() * strafe_side * speed * 0.5


## Leque de disparos mirados no jogador.
func _pattern_shots() -> void:
	var pl: Player = run.player
	if pl == null or pl.dead:
		return
	var count: int = 3 if phase == 1 else 5
	var base: Vector2 = (pl.global_position - global_position).normalized()
	for i in count:
		var off: float = (float(i) - float(count - 1) * 0.5) * 0.22
		var p: Projectile = run.new_projectile()
		p.friendly = false
		p.dir = base.rotated(off)
		p.speed = 260.0
		p.damage = data.parametro_a
		p.life = 3.0
		p.radius = 7.0
		p.color = Color(1.0, 0.7, 0.3)
		p.position = global_position + p.dir * (radius + 6.0)
		run.spawn_projectile(p)
	AudioManager.play_sfx("spit", 0.7, -4.0)


## Raízes telegrafadas em linha entre o Jardineiro e o jogador (bloqueiam a rota).
func _pattern_roots() -> void:
	var pl: Player = run.player
	if pl == null or pl.dead:
		return
	var n: int = 5 if phase == 1 else 7
	for i in n:
		var k: float = float(i + 1) / float(n + 1)
		var pos: Vector2 = global_position.lerp(pl.global_position, k) + Vector2.from_angle(randf() * TAU) * 24.0
		run.spawn_root_slam(pos, 58.0, data.parametro_b, 1.0 + 0.2 * float(i))
	AudioManager.play_sfx("alert", 0.7, -6.0)


func take_damage(amount: float, _tag: String = "") -> void:
	if not alive or run == null:
		return
	if not vulnerable:
		flash = maxf(flash, 0.2)
		if shield_text_cd <= 0.0:
			shield_text_cd = 1.2
			run.float_text(global_position + Vector2(0.0, -radius - 12.0), "Blindado", Color(0.6, 0.8, 1.0))
		return
	super.take_damage(amount, _tag)


## Veneno e outros danos contínuos também respeitam a blindagem.
func _apply_dot(amount: float) -> void:
	if not vulnerable:
		return
	super._apply_dot(amount)


func _draw() -> void:
	if data == null or not draw_placeholder:
		return
	draw_circle(Vector2(0, radius * 0.8), radius * 1.1, Color(0, 0, 0, 0.3))
	var col: Color = _tint(data.cor)
	for i in 8:
		var a: float = float(i) * TAU / 8.0 + sin(anim_t * 0.5 + float(i)) * 0.12
		var p1: Vector2 = Vector2.from_angle(a) * radius * 0.9
		var p2: Vector2 = Vector2.from_angle(a + sin(anim_t * 0.8 + float(i)) * 0.25) * radius * 1.8
		draw_line(p1, p2, Color(0.25, 0.35, 0.22), 6.0)
		draw_line(p1, p2, Color(0.45, 0.6, 0.35), 2.0)
	draw_circle(Vector2.ZERO, radius, col)
	draw_arc(Vector2.ZERO, radius * 0.8, anim_t * 0.6, anim_t * 0.6 + TAU * 0.75, 18, data.cor_detalhe, 3.0)
	draw_arc(Vector2.ZERO, radius * 0.55, -anim_t, -anim_t + TAU * 0.6, 14, col.lightened(0.25), 3.0)
	var pulse: float = 0.6 + 0.4 * sin(anim_t * 5.0)
	if vulnerable:
		draw_circle(Vector2.ZERO, radius * 0.42, Color(1.0, 0.85, 0.3, 0.4 + 0.5 * pulse))
		draw_circle(Vector2.ZERO, radius * 0.22, Color(1.0, 1.0, 0.8))
		draw_arc(Vector2.ZERO, radius + 8.0, 0.0, TAU, 32, Color(1.0, 0.85, 0.3, 0.6 + 0.3 * pulse), 3.0)
	else:
		draw_circle(Vector2.ZERO, radius * 0.3, Color(0.35, 0.4, 0.45))
		draw_arc(Vector2.ZERO, radius + 8.0, 0.0, TAU, 32, Color(0.5, 0.8, 1.0, 0.45 + 0.2 * pulse), 3.0)
	if run != null and run.state.has_special("consciencia_rede"):
		var font: Font = ThemeDB.fallback_font
		var txt: String = "%s em %.0fs" % ["Fecha" if vulnerable else "Núcleo expõe", maxf(0.0, cycle_t)]
		var sz: Vector2 = font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, 12)
		draw_string(font, Vector2(-sz.x * 0.5, -radius - 30.0), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color(0.7, 0.95, 1.0))
