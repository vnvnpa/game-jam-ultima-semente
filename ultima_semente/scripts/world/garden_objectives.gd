class_name GardenObjectives
extends Node
## Objetivos do Santuário do Último Jardim (GDD 14.1): ativar mecanismos
## resistindo a ondas de criaturas, abrir a Câmara e enfrentar o Jardineiro
## Vazio. Fica em scenes/world/garden_run.tscn (World/Objectives); todos os
## valores são ajustáveis no Inspector. Os mecanismos são Interactables
## do tipo "mechanism" colocados em scenes/world/garden_map.tscn.

@export var required: int = 3
## Segundos de resistência para ativar cada mecanismo.
@export var activation_time: float = 30.0
## Distância máxima do mecanismo para a ativação continuar.
@export var hold_radius: float = 260.0
@export var wave_interval: float = 3.5
@export var wave_size: int = 2
@export var reward_biomass: int = 20

var run: Run = null
var active: Interactable = null
var progress: float = 0.0
var activated: Array = []
var wave_t: float = 0.0
var out_of_range: bool = false
var opened: bool = false


func setup(r: Run) -> void:
	run = r


func activated_count() -> int:
	return activated.size()


func is_activated(it: Interactable) -> bool:
	return activated.has(it.ref_id)


## Mecanismo ainda inativo mais próximo de `from` (ou null).
func nearest_pending(from: Vector2) -> Interactable:
	var best: Interactable = null
	var best_d: float = INF
	for it in run.interactables:
		var m: Interactable = it
		if m.kind != "mechanism" or is_activated(m):
			continue
		var d: float = from.distance_to(m.global_position)
		if d < best_d:
			best_d = d
			best = m
	return best


func try_activate(it: Interactable) -> void:
	if run == null or run.ended:
		return
	if is_activated(it):
		run.notify("Este mecanismo já está ativo.", UIKit.COL_DIM, "")
		return
	if active != null:
		if active == it:
			run.notify("Ativação em curso: resista!", UIKit.COL_WARN, "")
		else:
			run.notify("Termine a ativação em curso antes.", UIKit.COL_WARN, "error")
		return
	active = it
	progress = 0.0
	wave_t = 1.0
	out_of_range = false
	run.director.event_boost = 8
	run.notify("Mecanismo em ativação! Fique por perto e resista às criaturas.", UIKit.COL_BAD, "alert")


func objective_text() -> String:
	if run.state.boss_defeated:
		return "Jardineiro Vazio derrotado!"
	if opened:
		return "Objetivo: enfrente o Jardineiro Vazio na Câmara (norte). Ataque quando o núcleo estiver exposto."
	if active != null:
		if out_of_range:
			return "Volte ao mecanismo para continuar a ativação!"
		return "Ativando mecanismo: %d%% — resista às criaturas!" % roundi(clampf(progress / maxf(activation_time, 0.1), 0.0, 1.0) * 100.0)
	return "Objetivo: ative os mecanismos (%d/%d) resistindo às ondas." % [activated.size(), required]


func _physics_process(delta: float) -> void:
	if run == null or run.ended or run.player == null or run.player.dead:
		return
	if active == null:
		return
	out_of_range = run.player.global_position.distance_to(active.global_position) > hold_radius
	if out_of_range:
		return
	progress += delta
	wave_t -= delta
	if wave_t <= 0.0:
		wave_t = wave_interval
		var growth: float = 1.0 + 0.25 * float(activated.size())
		var n: int = roundi(float(wave_size) * run.state.stat("event_size_mult") * growth)
		run.director.spawn_group(maxi(1, n), 260.0, 520.0)
	if progress >= activation_time:
		_complete()


func _complete() -> void:
	var it: Interactable = active
	active = null
	progress = 0.0
	run.director.event_boost = 0
	it.used = true
	activated.append(it.ref_id)
	var reward: int = reward_biomass + int(run.state.stat("event_biomass_bonus"))
	run.state.add_biomass(reward)
	run.float_text(run.player.global_position + Vector2(0, -34), "+%d Biomassa" % reward, UIKit.COL_BIO)
	AudioManager.play_sfx("mechanism")
	run.notify("Mecanismo ativado (%d/%d)! +%d Biomassa" % [activated.size(), required, reward], UIKit.COL_GOOD, "levelup")
	if activated.size() >= required and not opened:
		opened = true
		run.map.gate.open_gate()
		run.notify("A passagem para a Câmara do Jardineiro se abriu!", UIKit.COL_NUC, "mutation")
