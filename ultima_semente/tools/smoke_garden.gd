extends SceneTree
## Teste de fumaça do Santuário do Último Jardim. Rode na raiz do projeto:
##   godot --headless --path . -s res://tools/smoke_garden.gd
## Percorre: estrutura da cena, ativação dos 3 mecanismos, abertura da
## passagem, Jardineiro Vazio (blindagem e janela de vulnerabilidade) e vitória.
## Usa uma máquina de passos com tempo-limite (não depende de quadros fixos).
## Faz backup e restaura o seu salvamento ao final.

var run: Run = null
var step: int = 0
var step_frames: int = 0
var mi: int = 0
var mechs: Array = []
var failures: Array = []
var backup: PackedByteArray = PackedByteArray()
var had_save: bool = false
const TIMEOUT_FRAMES: int = 4000


func _initialize() -> void:
	had_save = FileAccess.file_exists(SaveManager.SAVE_PATH)
	if had_save:
		backup = FileAccess.get_file_as_bytes(SaveManager.SAVE_PATH)
	print("[garden] iniciando")
	var scn: PackedScene = load("res://scenes/world/garden_run.tscn")
	_check(scn != null and scn.can_instantiate(), "garden_run.tscn carrega e instancia")
	if scn == null:
		return
	run = scn.instantiate() as Run
	root.add_child(run)


func _check(cond: bool, msg: String) -> void:
	if cond:
		print("[garden] ok: ", msg)
	else:
		failures.append(msg)
		printerr("[garden] FALHA: ", msg)


func _goto(n: int) -> void:
	step = n
	step_frames = 0


func _process(_delta: float) -> bool:
	if run == null or not is_instance_valid(run):
		return true
	step_frames += 1
	if step_frames > TIMEOUT_FRAMES:
		_check(false, "tempo esgotado no passo %d" % step)
		return true
	if run.player != null and not run.player.dead:
		run.player.hp = run.state.max_hp()
	match step:
		0:
			if step_frames < 5:
				return false
			_check(run.level_id == "garden" and run.boss_id == "jardineiro_vazio", "parâmetros do nível")
			_check(run.objectives != null, "objetivos do jardim presentes")
			for it in run.interactables:
				if (it as Interactable).kind == "mechanism":
					mechs.append(it)
			_check(mechs.size() == 3, "3 mecanismos na cena")
			_check(run.interactables.size() == 8, "2 terminais, 3 mecanismos e 3 registros")
			_check(WorldLayout.stations.size() == 4, "4 estações")
			_check(WorldLayout.hostile_zones.size() == 2, "2 zonas contaminadas")
			_check(WorldLayout.regions.size() == 3, "3 regiões")
			_check(WorldLayout.boss_arena != null, "arena do chefe")
			_check(run.map.obstacles.size() >= 100, "obstáculos lidos da cena")
			_check(not run.map.gate.is_open, "passagem começa fechada")
			_check(run.director.time_offset > 0.0, "diretor com deslocamento de dificuldade")
			_check(run.events.schedule.is_empty(), "eventos aleatórios desligados no jardim")
			_check(WorldLayout.region_name(Vector2(450, 2150)) == "Estufas Esquecidas", "nome da região inicial")
			run.objectives.activation_time = 0.5
			_goto(1)
		1:
			if mi >= mechs.size():
				_goto(3)
				return false
			var m: Interactable = mechs[mi]
			run.player.global_position = m.global_position + Vector2(40, 0)
			run.objectives.try_activate(m)
			_check(run.objectives.active == m, "ativação iniciada no mecanismo %d" % (mi + 1))
			_goto(2)
		2:
			var cur: Interactable = mechs[mi]
			if run.objectives.activated.has(cur.ref_id):
				_check(cur.used, "mecanismo %d marcado como ativo" % (mi + 1))
				mi += 1
				_goto(1)
		3:
			_check(run.objectives.activated_count() == 3, "3 mecanismos ativados")
			_check(run.map.gate.is_open, "passagem aberta após os mecanismos")
			run.player.global_position = Vector2(2650, 600)
			_goto(4)
		4:
			if run.boss != null:
				_check(run.boss is Gardener, "Jardineiro Vazio surgiu")
				_goto(5)
		5:
			var g: Gardener = run.boss as Gardener
			run.boss_immune_time = 0.0
			g.vulnerable = false
			g.cycle_t = 9999.0
			var before: float = g.hp
			g.take_damage(100.0)
			_check(is_equal_approx(g.hp, before), "blindado não recebe dano")
			g.vulnerable = true
			g.take_damage(100.0)
			_check(g.hp < before, "núcleo exposto recebe dano")
			g.take_damage(99999.0)
			_check(not g.alive, "Jardineiro derrotado")
			_goto(6)
		6:
			if run.ended:
				_check(str(run.summary.get("reason", "")) == "victory", "campanha encerra com vitória")
				_check(bool(SaveManager.data["campaign_completed"]), "campanha marcada como concluída")
				_check(int(run.summary.get("mechanisms", 0)) == 3, "resumo registra os mecanismos")
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
	print("[garden] concluído. Falhas: ", failures.size())
