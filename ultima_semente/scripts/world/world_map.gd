class_name WorldMap
extends Node2D
## Mundo da expedição. Todo o cenário (terreno, regiões, zonas contaminadas,
## estações, muralhas, barreira, obstáculos, caches, ruínas, ninhos e arena do
## chefe) é colocado NO EDITOR em scenes/world/world_map.tscn. Este script só
## lê os nós já existentes para as consultas de colisão/posicionamento.

var obstacles: Array = []     # {"pos": Vector2, "r": float}
var wall_rects: Array = []    # Rect2 no mundo

@onready var terrain: Sprite2D = $Terrain
@onready var gate: RootGate = $Gate
@onready var obstacles_node: Node2D = $Obstacles
@onready var walls_node: Node2D = $Walls


## Lê obstáculos e muralhas da cena. Chamado pelo Run ao iniciar.
func collect() -> void:
	obstacles.clear()
	wall_rects.clear()
	for ch in obstacles_node.get_children():
		var ob: Obstacle = ch as Obstacle
		if ob != null:
			obstacles.append({"pos": ob.global_position, "r": ob.radius})
	for ch in walls_node.get_children():
		var body: StaticBody2D = ch as StaticBody2D
		if body == null:
			continue
		for c in body.get_children():
			var cs: CollisionShape2D = c as CollisionShape2D
			if cs != null and cs.shape is RectangleShape2D:
				var sz: Vector2 = (cs.shape as RectangleShape2D).size
				wall_rects.append(Rect2(body.global_position + cs.position - sz * 0.5, sz))


func is_inside_obstacle(pos: Vector2, radius: float) -> bool:
	for o in obstacles:
		var op: Vector2 = o["pos"]
		var rr: float = float(o["r"]) + radius
		if pos.distance_squared_to(op) < rr * rr:
			return true
	for wr in wall_rects:
		var rect: Rect2 = wr
		if rect.grow(radius).has_point(pos):
			return true
	if not gate.is_open and gate.get_rect().grow(radius).has_point(pos):
		return true
	return false


## Só muralhas e a barreira fechada (não árvores/cristais): usado pelos projéteis.
func is_inside_wall(pos: Vector2, radius: float) -> bool:
	for wr in wall_rects:
		var rect: Rect2 = wr
		if rect.grow(radius).has_point(pos):
			return true
	if not gate.is_open and gate.get_rect().grow(radius).has_point(pos):
		return true
	return false
