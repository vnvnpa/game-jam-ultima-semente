class_name AimReticle
extends Node2D
## Retícula em pixel art (assets/art/ui/crosshair.png: 4 frames x 2 linhas).
## - Mouse: acompanha o cursor; o cursor do sistema fica escondido durante a partida.
## - Controle: aparece na direção do analógico direito / movimento, a uma distância fixa.
## - Quando a arma automática trava num inimigo, a retícula desliza até ele e troca
##   para a versão dourada (linha 2 da folha).
## Fica sempre visível só durante o jogo: em menus/pausa/lojas volta o cursor normal.

const TEX_PATH: String = "res://assets/art/ui/crosshair.png"
const PAD_DISTANCE: float = 110.0
const FPS: float = 8.0

var run: Run = null
var _sprite: Sprite2D = null
var _t: float = 0.0
var _locked: bool = false
var _hidden_cursor: bool = false


func setup(r: Run) -> void:
	run = r
	z_index = 35
	_sprite = Sprite2D.new()
	_sprite.texture = load(TEX_PATH) as Texture2D
	_sprite.hframes = 4
	_sprite.vframes = 2
	add_child(_sprite)
	visible = false


func _exit_tree() -> void:
	_set_cursor_hidden(false)


func _set_cursor_hidden(v: bool) -> void:
	if v == _hidden_cursor:
		return
	_hidden_cursor = v
	Input.mouse_mode = Input.MOUSE_MODE_HIDDEN if v else Input.MOUSE_MODE_VISIBLE


func _process(delta: float) -> void:
	if run == null or run.player == null or _sprite == null:
		return
	var playing: bool = not run.ended and run.modal == "" and not get_tree().paused and not run.player.dead
	visible = playing
	_set_cursor_hidden(playing and not GameManager.using_pad)
	if not playing:
		return
	_t += delta
	var pl: Player = run.player
	var tgt: Enemy = pl.aim_target
	var goal: Vector2
	if tgt != null and is_instance_valid(tgt) and tgt.alive:
		goal = tgt.global_position
		_locked = true
	else:
		_locked = false
		if GameManager.using_pad:
			goal = pl.global_position + pl.facing * PAD_DISTANCE
		else:
			goal = get_global_mouse_position()
	if _locked:
		global_position = global_position.lerp(goal, minf(1.0, 22.0 * delta))
	else:
		global_position = goal
	global_position = global_position.round()
	_sprite.frame = (1 if _locked else 0) * 4 + int(_t * FPS) % 4
