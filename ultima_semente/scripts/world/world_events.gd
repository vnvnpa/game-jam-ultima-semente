class_name WorldEvents
extends Node
## Eventos de ameaça (GDD 8 e 9.1): enxames cronometrados que dão Biomassa
## ao serem sobrevividos. Não começam enquanto o chefe estiver ativo.

var run: Run = null
var schedule: Array = []
var active: bool = false
var kind: String = ""
var current: ThreatEventData = null
var remaining: float = 0.0
var spawn_timer: float = 0.0
## Desligue em fases dedicadas que têm seus próprios objetivos.
@export var enabled: bool = true
var completed: int = 0


func setup(r: Run) -> void:
	run = r
	if not enabled:
		schedule = []
		return
	var m: float = run.state.stat("event_time_mult")
	schedule = []
	for e in GameData.threat_events:
		var ev: ThreatEventData = e
		schedule.append({"time": ev.tempo * m, "data": ev, "done": false})


func title() -> String:
	return current.titulo if current != null else ""


func _start(ev: Dictionary) -> void:
	ev["done"] = true
	current = ev["data"]
	active = true
	kind = current.id
	remaining = current.duracao
	spawn_timer = 0.5
	run.director.event_boost = current.impulso_limite
	run.notify("ALERTA: %s! Sobreviva por %d s." % [title(), roundi(remaining)], UIKit.COL_BAD, "alert")
	if current.elite_no_inicio:
		run.director.spawn_elite()


func _finish() -> void:
	active = false
	run.director.event_boost = 0
	completed += 1
	var reward: int = randi_range(current.recompensa_min, current.recompensa_max) + int(run.state.stat("event_biomass_bonus"))
	run.state.add_biomass(reward)
	run.float_text(run.player.global_position + Vector2(0, -34), "+%d Biomassa" % reward, UIKit.COL_BIO)
	run.notify("Evento concluído! +%d Biomassa" % reward, UIKit.COL_GOOD, "levelup")


## Interrompe o evento sem recompensa (o chefe despertou).
func _abort() -> void:
	active = false
	run.director.event_boost = 0
	run.notify("O Guardião interrompeu a ameaça.", UIKit.COL_WARN, "")


func _physics_process(delta: float) -> void:
	if run == null or run.ended or run.player == null or run.player.dead:
		return
	if not active:
		if run.boss_active:
			return
		for ev in schedule:
			if not bool(ev["done"]) and run.state.run_time >= float(ev["time"]):
				_start(ev)
				break
		return
	if run.boss_active:
		_abort()
		return
	remaining -= delta
	spawn_timer -= delta
	if spawn_timer <= 0.0:
		spawn_timer = current.intervalo_surgimento
		var n: int = roundi(current.tamanho_base * run.state.stat("event_size_mult"))
		run.director.spawn_group(n, current.dist_min, current.dist_max)
	if remaining <= 0.0:
		_finish()
