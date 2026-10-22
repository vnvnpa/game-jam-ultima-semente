class_name SpawnDirector
extends Node
## Controla o surgimento de inimigos em mapa aberto (GDD 8): etapa por tempo,
## limite de ativos, tipos permitidos, posições válidas longe do jogador
## (250–700 px), elites e dificuldade com teto (não cresce sem limite).

const INVALID_POS: Vector2 = Vector2(-9999.0, -9999.0)
const MIN_DIST: float = 250.0
const MAX_DIST: float = 700.0
const CAP_START: float = 10.0
const CAP_END: float = 45.0
const RAMP_TIME: float = 1320.0   # 22 min: a pressão para de crescer aqui
const HARD_CAP: int = 70

var run: Run = null
var timer: float = 1.0
var elites_spawned: int = 0
var next_elite_time: float = 390.0
var event_boost: int = 0
## Fases dedicadas começam como se já tivessem passado `time_offset` segundos
## (etapa, teto de inimigos e vida inimiga usam o tempo + deslocamento).
@export var time_offset: float = 0.0
## Segundo de expedição em que a primeira elite surge.
@export var first_elite_time: float = 390.0


func setup(r: Run) -> void:
	run = r
	next_elite_time = first_elite_time - run.state.stat("elite_time_shift")


func _t() -> float:
	return run.state.run_time + time_offset


static func stage_name(t: float) -> String:
	if t < 180.0:
		return "Aprendizado"
	if t < 420.0:
		return "Exploração"
	if t < 720.0:
		return "Ameaça crescente"
	if t < 1020.0:
		return "Grupos combinados"
	if t < 1320.0:
		return "Crise biológica"
	return "Desafio principal"


func _progress(t: float) -> float:
	return clampf(t / RAMP_TIME, 0.0, 1.0)


func current_cap(t: float) -> int:
	var cap: int = roundi(lerpf(CAP_START, CAP_END, _progress(t))) + event_boost
	if run.boss_active:
		cap = roundi(float(cap) * 0.5)
	return mini(cap, HARD_CAP)


func current_interval(t: float) -> float:
	return lerpf(1.5, 0.6, _progress(t))


## Lista de [id, peso] permitidos no tempo t.
func weights(t: float) -> Array:
	if t < 180.0:
		return [["larva_fertil", 100]]
	if t < 420.0:
		return [["larva_fertil", 70], ["cortarraiz", 30]]
	if t < 720.0:
		return [["larva_fertil", 45], ["cortarraiz", 25], ["flor_ruptura", 20], ["esporideo", 10]]
	if t < 1020.0:
		return [["larva_fertil", 30], ["cortarraiz", 20], ["flor_ruptura", 16], ["esporideo", 12], ["casca_tumulo", 12]]
	return [["larva_fertil", 24], ["cortarraiz", 16], ["flor_ruptura", 14], ["esporideo", 10], ["casca_tumulo", 12], ["parasita_sinal", 10]]


func pick_type(t: float) -> String:
	var list: Array = weights(t)
	var total: int = 0
	for w in list:
		total += int(w[1])
	var roll: int = randi() % maxi(total, 1)
	for w in list:
		roll -= int(w[1])
		if roll < 0:
			return str(w[0])
	return "larva_fertil"


## Escalonamento leve de vida por etapa (dano e velocidade NÃO escalam).
func hp_scale(t: float) -> float:
	return 1.0 + 0.5 * _progress(t)


func max_elites(t: float) -> int:
	if t < 720.0:
		return 1
	if t < 1020.0:
		return 2
	return 3


func find_spawn_pos(radius: float, dmin: float = MIN_DIST, dmax: float = MAX_DIST) -> Vector2:
	var center: Vector2 = run.player.global_position
	for i in 16:
		var pos: Vector2 = center + Vector2.from_angle(randf() * TAU) * randf_range(dmin, dmax)
		if run.is_spawn_valid(pos, radius):
			return pos
	return INVALID_POS


func spawn_group(count: int, dmin: float, dmax: float) -> int:
	var t: float = _t()
	var made: int = 0
	for i in count:
		if run.regular_enemy_count() >= HARD_CAP:
			break
		var id: String = pick_type(t)
		var data: EnemyData = GameData.enemies[id]
		var pos: Vector2 = find_spawn_pos(data.raio, dmin, dmax)
		if pos == INVALID_POS:
			continue
		run.spawn_enemy(id, pos, hp_scale(t))
		made += 1
	return made


func spawn_elite() -> bool:
	var t: float = _t()
	var data: EnemyData = GameData.enemies["anomalia"]
	var pos: Vector2 = find_spawn_pos(data.raio, 350.0, 650.0)
	if pos == INVALID_POS:
		return false
	var mods: Array = ["blindada", "veloz", "explosiva", "regenerante"]
	var e: Enemy = run.spawn_enemy("anomalia", pos, hp_scale(t), str(mods[randi() % mods.size()]))
	if e == null:
		return false
	elites_spawned += 1
	run.notify("Uma Anomalia surgiu: %s" % e.display_name(), UIKit.COL_WARN, "alert")
	return true


func elite_count() -> int:
	var n: int = 0
	for e in run.enemies:
		if is_instance_valid(e) and (e as Enemy).alive and (e as Enemy).elite:
			n += 1
	return n


func _physics_process(delta: float) -> void:
	if run == null or run.ended or run.player == null or run.player.dead:
		return
	var t: float = _t()
	timer -= delta
	if timer <= 0.0:
		timer = current_interval(t)
		var room: int = current_cap(t) - run.regular_enemy_count()
		if room > 0:
			var batch: int = 1 if t < 720.0 else 2
			spawn_group(mini(batch, room), MIN_DIST, MAX_DIST)
	var rt: float = run.state.run_time
	if rt >= next_elite_time and not run.boss_active:
		if elite_count() < max_elites(t):
			if spawn_elite():
				next_elite_time = rt + 210.0
			else:
				# Sem posição válida agora: tenta de novo em 3 s, não a cada quadro.
				next_elite_time = rt + 3.0
		else:
			next_elite_time = rt + 20.0
