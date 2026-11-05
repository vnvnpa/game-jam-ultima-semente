class_name HeartBoss
extends Boss
## Coração de Nymara (GDD 14.2): chefe final em 3 etapas.
## 1 Defesa: invoca criaturas e esmaga o chão com raízes (vulnerável até 66%).
## 2 Exposição: o núcleo fica protegido; destrua as 4 estruturas ao redor.
## 3 Decisão: núcleo exposto com padrões combinados; aos 12% a Rede se rende e o
##   jogador escolhe o destino da Última Semente (Run.open_decision).
## parametro_a = dano das raízes; dano = dano dos projéteis em anel.

const STAGE2_AT: float = 0.66
const DECISION_AT: float = 0.12
const STRUCTURE_COUNT: int = 4
const STRUCTURE_RING: float = 300.0

var stage: int = 1
var structures: Array = []
var last_alive: int = -1
var decision_started: bool = false
var decision_done: bool = false
var decision_opened: bool = false
var decision_t: float = 1.4
var shield_text_cd: float = 0.0
var volley_t: float = 4.0


func _behavior(delta: float, _dir: Vector2, _dist: float, _target: Vector2) -> Vector2:
	phase = stage
	shield_text_cd = maxf(0.0, shield_text_cd - delta)
	if run.boss_immune_time > 0.0:
		return Vector2.ZERO
	if decision_started:
		decision_t -= delta
		if decision_t <= 0.0 and not decision_opened:
			decision_opened = run.open_decision(self)
		return Vector2.ZERO
	var fast: float = 1.0
	if stage == 2:
		fast = 1.15
	elif stage == 3:
		fast = 0.8
	slam_timer -= delta
	summon_timer -= delta
	if slam_timer <= 0.0:
		slam_timer = 6.5 * fast
		_pattern_slam()
	if summon_timer <= 0.0:
		summon_timer = 14.0 * fast
		_pattern_summon()
	if stage == 2:
		_watch_structures()
	elif stage == 3:
		volley_t -= delta
		if volley_t <= 0.0:
			volley_t = 5.0
			_pattern_volley()
	return Vector2.ZERO


func _enter_stage(n: int) -> void:
	stage = n
	phase = n
	if n == 2:
		run.notify("As raízes se fecham! Destrua as estruturas que protegem o núcleo.", UIKit.COL_WARN, "boss")
		run.fx_ring(global_position, radius * 3.0, Color(0.6, 0.9, 1.0), 0.7)
		slam_timer = 4.0
		summon_timer = 6.0
		_spawn_structures()
	elif n == 3:
		run.notify("O núcleo está exposto! Ataque até a Rede Raiz se render.", UIKit.COL_BAD, "boss")
		run.fx_ring(global_position, radius * 3.0, Color(1.0, 0.8, 0.4), 0.7)
		slam_timer = 3.0
		summon_timer = 8.0
		volley_t = 3.0
	run.shake(6.0)


func _spawn_structures() -> void:
	structures.clear()
	for i in STRUCTURE_COUNT:
		var ang: float = TAU * (float(i) + 0.5) / float(STRUCTURE_COUNT)
		var pos: Vector2 = global_position + Vector2.from_angle(ang) * STRUCTURE_RING
		if not run.is_free_spot(pos, 22.0):
			pos = global_position + Vector2.from_angle(ang) * (STRUCTURE_RING * 0.6)
		var st: Enemy = run.spawn_enemy("estrutura_raiz", pos, 1.0)
		if st != null:
			structures.append(st)
	last_alive = structures.size()


func _alive_structures() -> int:
	var n: int = 0
	for s in structures:
		if is_instance_valid(s) and (s as Enemy).alive:
			n += 1
	return n


func _watch_structures() -> void:
	var alive_n: int = _alive_structures()
	if alive_n != last_alive:
		last_alive = alive_n
		if alive_n > 0:
			run.notify("Estruturas restantes: %d" % alive_n, UIKit.COL_WARN, "")
	if alive_n == 0:
		_enter_stage(3)


## Anel de projéteis para fora (etapa 3).
func _pattern_volley() -> void:
	play_event(&"slam", 0.6)
	var n: int = 10
	var off: float = randf() * TAU
	for i in n:
		var p: Projectile = run.new_projectile()
		p.friendly = false
		p.dir = Vector2.from_angle(off + TAU * float(i) / float(n))
		p.speed = 210.0
		p.damage = data.dano
		p.life = 3.5
		p.radius = 6.0
		p.color = Color(1.0, 0.5, 0.8)
		p.position = global_position + p.dir * (radius + 6.0)
		run.spawn_projectile(p)
	AudioManager.play_sfx("spit", 0.6, -4.0)


func _check_stage() -> void:
	if not alive:
		return
	if stage == 1 and hp <= max_hp * STAGE2_AT:
		hp = max_hp * STAGE2_AT
		_enter_stage(2)
	elif stage == 3 and not decision_started and hp <= max_hp * DECISION_AT:
		hp = max_hp * DECISION_AT
		_start_decision()


func _start_decision() -> void:
	decision_started = true
	decision_t = 1.4
	run.notify("A Rede Raiz hesita... O Coração para de lutar.", UIKit.COL_NUC, "mutation")
	run.fx_ring(global_position, radius * 4.0, Color(0.6, 1.0, 1.0), 0.9)
	for e in run.enemies.duplicate():
		if is_instance_valid(e):
			var en: Enemy = e
			if en.alive and not en.is_boss and en.data.comportamento != "ninho":
				en.die()


## Chamado por Run depois que o jogador escolhe o final.
func finish_after_decision() -> void:
	decision_done = true
	hp = 0.0
	die()


func take_damage(amount: float, _tag: String = "") -> void:
	if not alive or run == null:
		return
	if stage == 2 or decision_started:
		flash = maxf(flash, 0.2)
		if shield_text_cd <= 0.0:
			shield_text_cd = 1.2
			run.float_text(global_position + Vector2(0.0, -radius - 12.0), "Protegido", Color(0.6, 0.8, 1.0))
		return
	super.take_damage(amount, _tag)
	_check_stage()


## Veneno e danos contínuos também respeitam as etapas.
func _apply_dot(amount: float) -> void:
	if stage == 2 or decision_started:
		return
	super._apply_dot(amount)
	_check_stage()


## O Coração nunca morre antes da decisão: um golpe fatal só leva o HP ao limite da etapa.
func die() -> void:
	if not decision_done:
		hp = max_hp * (STAGE2_AT if stage == 1 else DECISION_AT)
		return
	super.die()


func _base_anim() -> StringName:
	if stage == 2:
		return &"shielded"
	if stage == 3 or decision_started:
		return &"exposed"
	return &"idle"
