class_name MapOverlay
extends Control
## Mapa em tela cheia (tecla M). Não pausa o jogo. Recursos e ruínas só
## aparecem se já descobertos ou dentro do alcance do Sentido Biológico /
## Scanner de Ruínas.

const MAP_W: float = 720.0
const MAP_H: float = 520.0

var run: Run = null


func setup(r: Run) -> void:
	run = r


func _process(_delta: float) -> void:
	if visible:
		queue_redraw()


func _w2m(p: Vector2, origin: Vector2) -> Vector2:
	var s: float = MAP_W / WorldLayout.WORLD_RECT.size.x
	return origin + p * s


func _draw() -> void:
	if run == null or run.player == null:
		return
	var vs: Vector2 = get_viewport_rect().size
	var origin: Vector2 = (vs - Vector2(MAP_W, MAP_H)) * 0.5
	var s: float = MAP_W / WorldLayout.WORLD_RECT.size.x
	draw_rect(Rect2(origin - Vector2(16, 44), Vector2(MAP_W + 32, MAP_H + 70)), Color(0.02, 0.05, 0.06, 0.92))
	draw_rect(Rect2(origin - Vector2(16, 44), Vector2(MAP_W + 32, MAP_H + 70)), UIKit.COL_BORDER, false, 2.0)
	var font: Font = ThemeDB.fallback_font
	draw_string(font, origin + Vector2(0, -16), "MAPA DE NYMARA — [%s] fechar" % GameManager.key_text("map"), HORIZONTAL_ALIGNMENT_LEFT, -1, 18, UIKit.COL_ACCENT)
	# regiões
	for rg in WorldLayout.regions:
		var rz: RegionZone = rg
		var rr: Rect2 = rz.get_rect()
		draw_rect(Rect2(origin + rr.position * s, rr.size * s), rz.map_color)
		draw_string(font, origin + rr.position * s + Vector2(10, 20), rz.region_name, HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color(0.9, 1, 0.9))
	for hz in WorldLayout.hostile_zones:
		var rect: Rect2 = (hz as HostileZone).get_rect()
		draw_rect(Rect2(origin + rect.position * s, rect.size * s), Color(0.7, 0.15, 0.6, 0.45))
		draw_rect(Rect2(origin + rect.position * s, rect.size * s), Color(1.0, 0.4, 0.9), false, 1.0)
	for wr in run.map.wall_rects:
		var wrect: Rect2 = wr
		draw_rect(Rect2(origin + wrect.position * s, wrect.size * s), Color(0.5, 0.25, 0.55))
	var grect: Rect2 = run.map.gate.get_rect()
	var gate_col: Color = Color(1.0, 0.4, 0.4) if not run.map.gate.is_open else Color(0.4, 1.0, 0.5)
	draw_rect(Rect2(origin + grect.position * s, grect.size * s), gate_col)
	for stn in WorldLayout.stations:
		var st: Station = stn
		draw_circle(_w2m(st.global_position, origin), maxf(4.0, st.radius * s), Color(0.3, 0.9, 1.0, 0.5))
	var arena: BossArena = WorldLayout.boss_arena
	if arena != null:
		draw_circle(_w2m(arena.global_position, origin), arena.ring_radius * s, Color(0.7, 0.4, 0.9, 0.18))
		draw_string(font, _w2m(arena.global_position, origin) + Vector2(-26, 4), "Chefe", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color(0.9, 0.7, 1.0))
	var ppos: Vector2 = run.player.global_position
	var reveal: float = run.state.stat("reveal_radius")
	var scanner: bool = run.state.has_special("scanner")
	# ruínas
	for it in run.interactables:
		var poi: Interactable = it
		if poi.kind == "mechanism":
			var mcol: Color = Color(0.4, 0.95, 0.5) if poi.used else Color(1.0, 0.8, 0.3)
			draw_rect(Rect2(_w2m(poi.global_position, origin) - Vector2(5, 5), Vector2(10, 10)), mcol)
			continue
		if poi.kind != "poi":
			continue
		var known: bool = run.state.discovered_pois.has(poi.ref_id)
		var visible_poi: bool = known or scanner or (reveal > 0.0 and ppos.distance_to(poi.global_position) < reveal)
		if visible_poi:
			var pcol: Color = Color(0.55, 0.5, 0.6) if known else Color(0.85, 0.55, 1.0)
			draw_rect(Rect2(_w2m(poi.global_position, origin) - Vector2(4, 4), Vector2(8, 8)), pcol)
	# ninhos
	for e in run.enemies:
		if not is_instance_valid(e):
			continue
		var en: Enemy = e
		if en.alive and en.data.comportamento == "ninho" and (en.seen or (reveal > 0.0 and ppos.distance_to(en.global_position) < reveal)):
			draw_circle(_w2m(en.global_position, origin), 5.0, Color(0.95, 0.4, 0.65))
	# caches (apenas com Sentido Biológico)
	if reveal > 0.0:
		for ch in run.drops_node.get_children():
			var pk: BiomassPickup = ch as BiomassPickup
			if pk != null and pk.persistent and ppos.distance_to(pk.global_position) < reveal:
				draw_circle(_w2m(pk.global_position, origin), 2.5, UIKit.COL_BIO)
	# jogador
	var pm: Vector2 = _w2m(ppos, origin)
	draw_circle(pm, 6.0, Color(1.0, 1.0, 1.0))
	draw_circle(pm, 4.0, Color(1.0, 0.55, 0.2))
	draw_string(font, origin + Vector2(0, MAP_H + 22), "Laranja: você  Azul: ar  Magenta: contaminada  Rosa: ninho  Roxo: ruína  Dourado: mecanismo", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, UIKit.COL_DIM)
