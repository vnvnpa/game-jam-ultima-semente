class_name OxygenManager
extends Node
## Oxigênio (GDD 12). Só é consumido em setores hostis sinalizados; recarrega
## em estações/bolsões; a falta causa perda gradual de vida. Como é um nó
## pausável, não consome durante pausa, menus ou lojas.

var run: Run = null
var o2: float = 180.0
var max_o2: float = 180.0
var zone: String = "respiravel"
var low_alerted: bool = false
var crit_alerted: bool = false
var beep_t: float = 0.0
var suffocation_t: float = 0.0


func setup(r: Run) -> void:
	run = r
	max_o2 = run.state.max_o2()
	o2 = max_o2


func refresh_max() -> void:
	var new_max: float = run.state.max_o2()
	if new_max > max_o2:
		o2 += new_max - max_o2
	max_o2 = new_max
	o2 = minf(o2, max_o2)


func ratio() -> float:
	return clampf(o2 / maxf(max_o2, 1.0), 0.0, 1.0)


func add_percent(frac: float) -> void:
	o2 = minf(max_o2, o2 + max_o2 * frac)


## 0 = tranquilo, 1 = crítico (para o efeito de visão).
func danger_level() -> float:
	if zone != "hostil":
		return 0.0
	if o2 <= 0.0:
		return 1.0
	return clampf((0.3 - ratio()) / 0.3, 0.0, 0.8)


func _physics_process(delta: float) -> void:
	if run == null or run.ended or run.player == null or run.player.dead:
		return
	var st: RunState = run.state
	zone = WorldLayout.zone_status(run.player.global_position)
	if zone == "hostil":
		o2 = maxf(0.0, o2 - 1.0 * st.stat("o2_use_mult") * delta)
	elif zone == "pressurizado":
		o2 = minf(max_o2, o2 + (max_o2 / 6.0) * st.stat("o2_recover_mult") * delta)
	else:
		o2 = minf(max_o2, o2 + 5.0 * st.stat("o2_recover_mult") * delta)
	var r: float = ratio()
	if r > 0.45:
		low_alerted = false
		crit_alerted = false
	if zone == "hostil":
		if r <= 0.3 and not low_alerted:
			low_alerted = true
			run.notify("Reserva de oxigênio baixa! Volte a um bolsão de ar.", UIKit.COL_WARN, "o2")
		if r <= 0.15 and not crit_alerted:
			crit_alerted = true
			run.notify("OXIGÊNIO CRÍTICO!", UIKit.COL_BAD, "alert")
		if r <= 0.15:
			beep_t -= delta
			if beep_t <= 0.0:
				beep_t = 1.2
				AudioManager.play_sfx("o2")
	if zone == "hostil" and o2 <= 0.0:
		suffocation_t += delta
		var rate: float = minf(7.0, 2.0 + suffocation_t * 0.4)
		run.player.lose_hp(rate * delta, "oxigênio")
	else:
		suffocation_t = maxf(0.0, suffocation_t - delta * 2.0)
