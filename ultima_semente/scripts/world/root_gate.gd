@tool
class_name RootGate
extends StaticBody2D
## Barreira de Raízes que fecha a passagem ao Santuário até 2 ninhos caírem.
## Posição e tamanho da colisão são definidos na cena (root_gate.tscn / world_map.tscn);
## o mapa e a lógica de surgimento leem esse retângulo via get_rect().

@export var draw_placeholder: bool = true
## Começa aberta (fases sem barreira, como o Coração de Nymara).
@export var start_open: bool = false

var is_open: bool = false
var openness: float = 0.0
var t: float = 0.0

@onready var shape_node: CollisionShape2D = $Shape
@onready var sprite: AnimatedSprite2D = get_node_or_null("Sprite") as AnimatedSprite2D


func _ready() -> void:
	if start_open and not Engine.is_editor_hint():
		is_open = true
		openness = 1.0
		shape_node.set_deferred("disabled", true)
		if sprite != null:
			sprite.play(&"open")


func open_gate() -> void:
	if is_open:
		return
	is_open = true
	AudioManager.play_sfx("gate_open")
	shape_node.set_deferred("disabled", true)
	if sprite != null:
		sprite.play(&"opening")
		if not sprite.animation_finished.is_connected(_on_opened):
			sprite.animation_finished.connect(_on_opened, CONNECT_ONE_SHOT)


func _on_opened() -> void:
	if sprite != null:
		sprite.play(&"open")


func _gate_size() -> Vector2:
	var rect: RectangleShape2D = shape_node.shape as RectangleShape2D
	if rect != null:
		return rect.size
	return Vector2(200, 36)


## Retângulo da barreira no mundo (posição + tamanho da colisão).
func get_rect() -> Rect2:
	var sz: Vector2 = _gate_size()
	return Rect2(global_position - sz * 0.5, sz)


func _process(delta: float) -> void:
	t += delta
	if is_open and openness < 1.0:
		openness = minf(1.0, openness + delta * 0.8)
	if openness < 1.0:
		queue_redraw()


func _draw() -> void:
	if not draw_placeholder:
		return
	var a: float = 1.0 - openness
	var sz: Vector2 = _gate_size()
	for i in 9:
		var x: float = -sz.x * 0.5 + (float(i) + 0.5) * sz.x / 9.0
		var wob: float = sin(t * 1.5 + float(i)) * 4.0
		draw_line(Vector2(x, sz.y * 0.5), Vector2(x + wob, -sz.y * 0.5 - 6.0), Color(0.4, 0.2, 0.45, a), 6.0)
		draw_line(Vector2(x, sz.y * 0.5), Vector2(x - wob, -sz.y * 0.5 - 6.0), Color(0.7, 0.3, 0.7, a), 2.0)
	draw_rect(Rect2(-sz.x * 0.5, -sz.y * 0.5, sz.x, sz.y), Color(0.7, 0.3, 0.7, a * 0.8), false, 2.0)
