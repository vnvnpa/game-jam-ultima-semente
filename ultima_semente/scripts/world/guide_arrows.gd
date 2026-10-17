class_name GuideArrows
extends Node2D
## Setas-guia no mundo: rota de retorno ao ar seguro (GDD 12.4) e, com o
## Scanner de Ruínas, direção do ponto de interesse mais próximo.

var run: Run = null


func _process(_delta: float) -> void:
	queue_redraw()


func _arrow(from: Vector2, dir: Vector2, col: Color, label: String) -> void:
	var tip: Vector2 = from + dir * 78.0
	var side: Vector2 = dir.orthogonal()
	draw_colored_polygon(PackedVector2Array([tip, tip - dir * 14.0 + side * 8.0, tip - dir * 14.0 - side * 8.0]), col)
	draw_line(from + dir * 52.0, tip - dir * 12.0, col, 3.0)
	var f: Font = ThemeDB.fallback_font
	draw_string(f, tip + dir * 8.0 + Vector2(-10, 4), label, HORIZONTAL_ALIGNMENT_LEFT, -1, 12, col)


func _draw() -> void:
	if run == null or run.player == null or run.player.dead or run.ended:
		return
	var p: Vector2 = run.player.global_position
	var ox: OxygenManager = run.oxygen
	var show_return: bool = (ox.zone == "hostil" and ox.ratio() < 0.5) or ox.ratio() < 0.3
	if show_return and ox.zone != "pressurizado":
		var st: Station = WorldLayout.nearest_station(p)
		if st != null:
			var d: Vector2 = st.global_position - p
			if d.length() > 40.0:
				_arrow(p, d.normalized(), Color(0.4, 0.95, 1.0, 0.9), "AR")
	if run.state.has_special("scanner"):
		var best: Vector2 = Vector2.ZERO
		var best_d: float = INF
		for it in run.interactables:
			var poi: Interactable = it
			if poi.kind != "poi" or run.state.discovered_pois.has(poi.ref_id):
				continue
			var dd: float = p.distance_to(poi.global_position)
			if dd < best_d:
				best_d = dd
				best = poi.global_position
		if best_d < INF and best_d > 60.0:
			_arrow(p, (best - p).normalized(), Color(0.8, 0.5, 1.0, 0.85), "RUÍNA")
