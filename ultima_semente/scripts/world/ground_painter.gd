class_name GroundPainter
extends TileMapLayer
## Pinta o chão (TileMapLayer) ao iniciar a expedição, a partir das regiões e
## zonas contaminadas do mapa, e espalha decoração (grama, flores, pedras).
## Tudo é determinístico (mesma semente = mesmo chão). O TileSet vem de
## assets/art/world/ground_tileset.tres (fontes: 0 floresta, 1 bacia, 2 santuário,
## 3 jardim, 4 estufa, 5 núcleo; linhas: 0 chão, 1 trilha, 2 pedra, 3 contaminado, 4 muralha).
## Trilhas (linha 1) ligam estações, terminais, ruínas, mecanismos e a arena do chefe.

const TILE: int = 32
const VARIANT_WEIGHTS: Array = [55, 25, 13, 7]

@export var seed_value: int = 1337
## Nome da região -> id da fonte do TileSet.
@export var biome_sources: Dictionary = {"Floresta do Despertar": 0, "Bacia dos Ecos": 1, "Santuário das Raízes": 2}
@export var default_source: int = 0
@export var stone_threshold: float = 0.45
@export var decor_texture: Texture2D
@export var decor_per_region: int = 45
## Pinta trilhas ligando os pontos de interesse do mapa.
@export var paint_trails: bool = true
## Meia-largura da trilha, em tiles.
@export var trail_half_width: int = 1
## Nome da região -> tipos de decoração (0 grama, 1 flores, 2 pedras, 3 manchas).
@export var decor_kinds: Dictionary = {"Floresta do Despertar": [0, 0, 1, 1, 2], "Bacia dos Ecos": [2, 3, 3], "Santuário das Raízes": [2, 2, 3]}


func _ready() -> void:
	_paint()
	_scatter_decor()
	var terrain: Node = get_parent().get_node_or_null("Terrain")
	if terrain != null:
		(terrain as CanvasItem).visible = false


func _pick_variant(rng: RandomNumberGenerator) -> int:
	var roll: int = rng.randi() % 100
	var acc: int = 0
	for i in VARIANT_WEIGHTS.size():
		acc += int(VARIANT_WEIGHTS[i])
		if roll < acc:
			return i
	return 0


func _paint() -> void:
	var noise: FastNoiseLite = FastNoiseLite.new()
	noise.seed = seed_value
	noise.frequency = 0.035
	var rng: RandomNumberGenerator = RandomNumberGenerator.new()
	rng.seed = seed_value
	var cols: int = ceili(WorldLayout.WORLD_RECT.size.x / float(TILE))
	var rows: int = ceili(WorldLayout.WORLD_RECT.size.y / float(TILE))
	for y in rows:
		for x in cols:
			var pos: Vector2 = Vector2(float(x * TILE + TILE / 2), float(y * TILE + TILE / 2))
			var region: RegionZone = WorldLayout.region_at(pos)
			var src: int = default_source
			if region != null:
				src = int(biome_sources.get(region.region_name, default_source))
			var row: int = 0
			if WorldLayout.is_hostile(pos):
				row = 3
			elif noise.get_noise_2d(float(x), float(y)) > stone_threshold:
				row = 2
			set_cell(Vector2i(x, y), src, Vector2i(_pick_variant(rng), row))
	if paint_trails:
		_paint_trails(rng)


func _scatter_decor() -> void:
	if decor_texture == null:
		return
	var decor: Node2D = Node2D.new()
	decor.name = "Decor"
	add_child(decor)
	var obs: Array = []
	var obs_node: Node = get_parent().get_node_or_null("Obstacles")
	if obs_node != null:
		for ch in obs_node.get_children():
			var ob: Obstacle = ch as Obstacle
			if ob != null:
				obs.append({"pos": ob.global_position, "r": ob.radius})
	var rng: RandomNumberGenerator = RandomNumberGenerator.new()
	rng.seed = seed_value + 7
	for rg in WorldLayout.regions:
		var rz: RegionZone = rg
		var kinds: Array = decor_kinds.get(rz.region_name, [])
		if kinds.is_empty():
			continue
		var rect: Rect2 = rz.get_rect().intersection(WorldLayout.WORLD_RECT.grow(-40.0))
		for i in decor_per_region:
			for attempt in 8:
				var pos: Vector2 = rect.position + Vector2(rng.randf() * rect.size.x, rng.randf() * rect.size.y)
				if WorldLayout.region_at(pos) != rz or WorldLayout.in_safe(pos) or WorldLayout.is_hostile(pos):
					continue
				var blocked: bool = false
				for o in obs:
					var op: Vector2 = o["pos"]
					if pos.distance_to(op) < float(o["r"]) + 16.0:
						blocked = true
						break
				if blocked:
					continue
				var kind: int = int(kinds[rng.randi() % kinds.size()])
				var idx: int = kind + 4 * (rng.randi() % 4)
				var sp: Sprite2D = Sprite2D.new()
				sp.texture = decor_texture
				sp.region_enabled = true
				sp.region_rect = Rect2(float(idx * 32), 0.0, 32.0, 32.0)
				sp.position = pos
				sp.flip_h = rng.randf() < 0.5
				var tone: float = rng.randf_range(0.85, 1.0)
				sp.modulate = Color(tone, tone, tone, 1.0)
				decor.add_child(sp)
				break


## Pontos que as trilhas ligam: estações, interativos e arena do chefe.
func _trail_points() -> Array:
	var pts: Array = []
	for st in WorldLayout.stations:
		if is_instance_valid(st):
			pts.append((st as Node2D).global_position)
	var inter: Node = get_parent().get_node_or_null("Interactables")
	if inter != null:
		for ch in inter.get_children():
			var n2: Node2D = ch as Node2D
			if n2 != null:
				pts.append(n2.global_position)
	if WorldLayout.boss_arena != null:
		pts.append(WorldLayout.boss_arena.global_position)
	return pts


## Encadeia os pontos pelo vizinho mais próximo (a partir do primeiro) e pinta
## cada ligação com um leve serpentear. Zonas contaminadas e pedra não são sobrescritas.
func _paint_trails(rng: RandomNumberGenerator) -> void:
	var pts: Array = _trail_points()
	if pts.size() < 2:
		return
	var left: Array = pts.duplicate()
	var cur: Vector2 = left.pop_front()
	while not left.is_empty():
		var bi: int = 0
		var bd: float = INF
		for i in left.size():
			var d: float = cur.distance_to(left[i])
			if d < bd:
				bd = d
				bi = i
		var nxt: Vector2 = left[bi]
		left.remove_at(bi)
		_trail_between(cur, nxt, rng)
		cur = nxt


func _trail_between(a: Vector2, b: Vector2, rng: RandomNumberGenerator) -> void:
	var steps: int = maxi(2, int(a.distance_to(b) / 16.0))
	var perp: Vector2 = (b - a).orthogonal().normalized()
	var phase: float = rng.randf() * TAU
	for i in steps + 1:
		var t: float = float(i) / float(steps)
		var fade: float = sin(t * PI)
		var p: Vector2 = a.lerp(b, t) + perp * sin(t * 9.0 + phase) * 26.0 * fade
		var cell: Vector2i = Vector2i(int(p.x / float(TILE)), int(p.y / float(TILE)))
		for dy in range(-trail_half_width, trail_half_width + 1):
			for dx in range(-trail_half_width, trail_half_width + 1):
				if absi(dx) + absi(dy) > trail_half_width + (rng.randi() % 2):
					continue
				var c2: Vector2i = cell + Vector2i(dx, dy)
				var wp: Vector2 = Vector2(float(c2.x * TILE + TILE / 2), float(c2.y * TILE + TILE / 2))
				if not WorldLayout.WORLD_RECT.has_point(wp) or WorldLayout.is_hostile(wp) or WorldLayout.in_safe(wp):
					continue
				var src: int = get_cell_source_id(c2)
				if src < 0:
					continue
				var ac: Vector2i = get_cell_atlas_coords(c2)
				if ac.y == 0:
					set_cell(c2, src, Vector2i(ac.x, 1))
