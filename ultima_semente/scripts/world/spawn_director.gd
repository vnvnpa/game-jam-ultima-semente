class_name SpawnDirector
extends Node
## Controla o surgimento de inimigos em mapa aberto (GDD 8): etapa por tempo,
## limite de ativos, tipos permitidos, posições válidas longe do jogador,
## elites e dificuldade com teto (não cresce sem limite).
## TODOS os números vêm de um WaveProfile (data/waves/*.tres, escolhido por
## `profile_id`): edite o .tres no Inspector para balancear.

const INVALID_POS: Vector2 = Vector2(-9999.0, -9999.0)

var run: Run = null
var profile: WaveProfile = null
var timer: float = 1.0
var elites_spawned: int = 0
var next_elite_time: float = 390.0
var event_boost: int = 0
## id do WaveProfile usado por esta fase (ex.: "floresta", "jardim").
@export var profile_id: String = "floresta"
## Fases dedicadas começam como se já tivessem passado `time_offset` segundos
## (etapa, teto de inimigos e vida inimiga usam o tempo + deslocamento).
@export var time_offset: float = 0.0
## Segundo de expedição em que a primeira elite surge.
@export var first_elite_time: float = 390.0


func setup(r: Run) -> void:
	run = r
	profile = GameData.wave_profiles.get(profile_id)
	if profile == null:
		push_error("SpawnDirector: perfil '%s' não encontrado." % profile_id)
		profile = WaveProfile.new()
	next_elite_time = first_elite_time - run.state.stat("elite_time_shift")


func _t() -> float:
	return run.state.run_time + time_offset


func min_distance() -> float:
	return profile.dist_min if profile != null else 250.0


## Etapa vigente no tempo t (a última cujo `inicio` já passou).
func _stage(t: float) -> WaveStage:
	var best: WaveStage = null
	if profile == null:
		return null
	for s in profile.stages:
		var st: WaveStage = s
		if t >= st.inicio and (best == null or st.inicio >= best.inicio):
			best = st
	return best


func stage_name_at(t: float) -> String:
	var st: WaveStage = _stage(t)
	return st.nome if st != null else ""


func _progress(t: float) -> float:
	return clampf(t / maxf(profile.tempo_rampa, 1.0), 0.0, 1.0)


func current_cap(t: float) -> int:
	var cap: int = roundi(lerpf(profile.cap_inicio, profile.cap_fim, _progress(t))) + event_boost
	if run.boss_active:
		cap = roundi(float(cap) * profile.chefe_mult_limite)
	return mini(cap, profile.limite_maximo)


func current_interval(t: float) -> float:
	var iv: float = lerpf(profile.intervalo_inicio, profile.intervalo_fim, _progress(t))
	if run != null and run.boss_active:
		iv *= profile.chefe_mult_intervalo
	return iv


## Lista de [id, peso] permitidos no tempo t.
func weights(t: float) -> Array:
	var out: Array = []
	var st: WaveStage = _stage(t)
	if st == null:
		return out
	for id in st.pesos:
		out.append([str(id), int(st.pesos[id])])
	return out


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
	return 1.0 + profile.escala_vida_max * _progress(t)


func max_elites(t: float) -> int:
	var st: WaveStage = _stage(t)
	return st.max_elites if st != null else 1


func find_spawn_pos(radius: float, dmin: float = -1.0, dmax: float = -1.0) -> Vector2:
	var lo: float = dmin if dmin >= 0.0 else profile.dist_min
	var hi: float = dmax if dmax >= 0.0 else profile.dist_max
	var center: Vector2 = run.player.global_position
	for i in 16:
		var pos: Vector2 = center + Vector2.from_angle(randf() * TAU) * randf_range(lo, hi)
		if run.is_spawn_valid(pos, radius):
			return pos
	return INVALID_POS


func spawn_group(count: int, dmin: float, dmax: float) -> int:
	var t: float = _t()
	var made: int = 0
	for i in count:
		if run.regular_enemy_count() >= profile.limite_maximo:
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
	var pos: Vector2 = find_spawn_pos(data.raio, profile.elite_dist_min, profile.elite_dist_max)
	if pos == INVALID_POS:
		return false
	var mods: Array = profile.elite_ids
	var mod_id: String = str(mods[randi() % mods.size()]) if not mods.is_empty() else ""
	var e: Enemy = run.spawn_enemy("anomalia", pos, hp_scale(t), mod_id)
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
	if run == null or profile == null or run.ended or run.player == null or run.player.dead:
		return
	var t: float = _t()
	timer -= delta
	if timer <= 0.0:
		timer = current_interval(t)
		var room: int = current_cap(t) - run.regular_enemy_count()
		if room > 0:
			var st: WaveStage = _stage(t)
			var batch: int = st.lote if st != null else 1
			spawn_group(mini(batch, room), profile.dist_min, profile.dist_max)
	var rt: float = run.state.run_time
	if rt >= next_elite_time and not run.boss_active:
		if elite_count() < max_elites(t):
			if spawn_elite():
				next_elite_time = rt + profile.elite_intervalo
			else:
				# Sem posição válida agora: tenta de novo em breve, não a cada quadro.
				next_elite_time = rt + profile.elite_nova_tentativa
		else:
			next_elite_time = rt + profile.elite_espera_cheio
