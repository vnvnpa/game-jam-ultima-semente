extends SceneTree
## Teste de fumaça do Coração de Nymara. Rode na raiz do projeto:
##   godot --headless --path . -s res://tools/smoke_heart.gd
## Percorre as 3 etapas do chefe, a escolha final e o fim da expedição.
## Faz backup e restaura o seu salvamento ao final.

var run: Run = null
var frame: int = 0
var step: int = 0
var backup: PackedByteArray = PackedByteArray()
var had_save: bool = false
var failures: Array = []


func _initialize() -> void:
	had_save = FileAccess.file_exists(SaveManager.SAVE_PATH)
	if had_save:
		backup = FileAccess.get_file_as_bytes(SaveManager.SAVE_PATH)
	print("[heart] iniciando")
	var scn: PackedScene = load("res://scenes/world/heart_run.tscn")
	_check(scn != null, "heart_run.tscn carrega")
	run = scn.instantiate() as Run
	root.add_child(run)


func _check(cond: bool, msg: String) -> void:
	if cond:
		print("[heart] ok: ", msg)
	else:
		failures.append(msg)
		printerr("[heart] FALHA: ", msg)


func _process(_delta: float) -> bool:
	frame += 1
	if run == null or not is_instance_valid(run):
		return true
	if frame == 5:
		_check(run.level_id == "heart", "fase heart")
		_check(WorldLayout.boss_arena != null, "arena do chefe")
		_check(WorldLayout.stations.size() == 1, "1 estação (Câmara de Acesso)")
		_check(run.map.gate.is_open, "barreira começa aberta")
		_check(run.director.profile != null and run.director.profile.id == "coracao", "perfil de ondas coracao")
		run.player.global_position = WorldLayout.boss_arena.global_position + Vector2(-260.0, 0.0)
	if frame > 4000:
		_check(false, "tempo esgotado no passo %d" % step)
		return true
	var h: HeartBoss = run.boss as HeartBoss
	match step:
		0:
			if h != null and run.boss_immune_time <= 0.0:
				_check(h.stage == 1, "etapa 1 (Defesa)")
				h.take_damage(99999.0)
				step = 1
		1:
			if h.stage == 2:
				_check(h.structures.size() == 4, "4 estruturas criadas")
				var hp_before: float = h.hp
				h.take_damage(500.0)
				_check(is_equal_approx(h.hp, hp_before), "núcleo protegido na etapa 2")
				for s in h.structures:
					(s as Enemy).die()
				step = 2
		2:
			if h.stage == 3:
				_check(h.alive, "núcleo vivo na etapa 3")
				h.take_damage(99999.0)
				step = 3
		3:
			if h.decision_started:
				_check(h.alive and h.hp > 0.0, "Coração não morre antes da decisão")
				step = 4
		4:
			if run.modal == "decision":
				_check(run.modal_node is DecisionScreen, "tela de decisão aberta")
				(run.modal_node as DecisionScreen).chosen.emit("coexistir")
				step = 5
		5:
			if run.ended:
				_check(str(run.summary.get("reason", "")) == "victory", "fim com vitória")
				_check(str(run.summary.get("ending", "")) == "coexistir", "final escolhido registrado")
				_check(run.state.boss_defeated, "chefe derrotado")
				return true
	return false


func _finalize() -> void:
	if had_save:
		var f: FileAccess = FileAccess.open(SaveManager.SAVE_PATH, FileAccess.WRITE)
		if f != null:
			f.store_buffer(backup)
			f.close()
	elif FileAccess.file_exists(SaveManager.SAVE_PATH):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(SaveManager.SAVE_PATH))
	print("[heart] concluído. Falhas: ", failures.size())
