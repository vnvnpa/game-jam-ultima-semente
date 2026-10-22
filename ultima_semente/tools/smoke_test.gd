extends SceneTree
## Teste de fumaça automatizado. Rode na raiz do projeto:
##   godot --headless --path . -s res://tools/smoke_test.gd
## Ele cria uma expedição, força cenários extremos (todos os inimigos, o chefe,
## todas as mutações, loja, oxigênio, todos os menus) e termina com código 0 se
## nenhum erro de script ocorrer. Erros aparecem no console da Godot.
## O teste faz backup e restaura o seu salvamento ao final.

var run: Run = null
var frame: int = 0
var backup: PackedByteArray = PackedByteArray()
var had_save: bool = false
var failures: Array = []


func _initialize() -> void:
	had_save = FileAccess.file_exists(SaveManager.SAVE_PATH)
	if had_save:
		backup = FileAccess.get_file_as_bytes(SaveManager.SAVE_PATH)
	print("[smoke] iniciando")
	_check_all_resources("res://")
	var run_scene: PackedScene = load("res://scenes/world/run.tscn")
	_check(run_scene != null, "run.tscn carrega")
	run = run_scene.instantiate() as Run
	root.add_child(run)


## Carrega todas as cenas e recursos do projeto; falhas de formato aparecem aqui.
func _check_all_resources(dir_path: String) -> void:
	for d in DirAccess.get_directories_at(dir_path):
		if d.begins_with("."):
			continue
		_check_all_resources(dir_path.path_join(d))
	for f in DirAccess.get_files_at(dir_path):
		var n: String = f.trim_suffix(".remap")
		if n.ends_with(".tscn") or n.ends_with(".tres"):
			var path: String = dir_path.path_join(n)
			var res: Resource = load(path)
			_check(res != null, "carrega " + path)
			if res is PackedScene:
				_check((res as PackedScene).can_instantiate(), "instancia " + path)


func _check(cond: bool, msg: String) -> void:
	if cond:
		print("[smoke] ok: ", msg)
	else:
		failures.append(msg)
		printerr("[smoke] FALHA: ", msg)


func _process(_delta: float) -> bool:
	frame += 1
	if run == null or not is_instance_valid(run):
		return true
	if frame == 5:
		_check(run.player != null and run.enemies.size() == 3, "3 ninhos pré-colocados na cena")
		_check(WorldLayout.stations.size() == 4, "4 estações vindas da cena")
		_check(WorldLayout.hostile_zones.size() == 3, "3 zonas contaminadas vindas da cena")
		_check(WorldLayout.regions.size() == 3, "3 regiões vindas da cena")
		_check(WorldLayout.boss_arena != null, "arena do chefe vinda da cena")
		_check(run.interactables.size() == 7, "nave, 2 terminais e 4 ruínas vindos da cena")
		_check(run.map.obstacles.size() == 130, "130 obstáculos lidos da cena")
		_check(run.map.wall_rects.size() == 3, "3 muralhas lidas da cena")
		_check(WorldLayout.region_name(Vector2(560, 1500)) == "Floresta do Despertar", "nome da região")
		_check(run.state.max_hp() == 100.0, "vida base 100")
	elif frame == 10:
		run.player.global_position = Vector2(2400, 1250)
		run.state.run_time = 700.0
	elif frame == 40:
		_check(run.oxygen.zone == "hostil", "zona hostil detectada")
		_check(run.oxygen.o2 < run.oxygen.max_o2, "oxigênio consumido na zona hostil")
		run.player.global_position = Vector2(560, 1500)
	elif frame == 60:
		_check(run.oxygen.zone == "pressurizado", "base pressurizada")
		for id in GameData.enemies:
			if id != "guardiao_raizes" and id != "jardineiro_vazio" and id != "ninho":
				run.spawn_enemy(str(id), run.player.global_position + Vector2(260, 40), 1.0, "veloz")
		for uid in GameData.upgrade_order:
			var u: UpgradeData = GameData.upgrades[uid]
			for i in u.max_nivel:
				MutationManager.apply_upgrade(run.state, str(uid))
		run.state.perm_ids = GameData.mutation_order.duplicate()
		run.state.biomass = 2000
		run.refresh_all_stats()
		for sid in GameData.shop_order:
			run.shop.terminals.clear()
			var t: Dictionary = run.shop.get_terminal("base")
			t["offers"] = GameData.shop_order.duplicate()
			var r: Dictionary = run.shop.buy_item("base", str(sid))
			print("[smoke] compra ", sid, " -> ", r["msg"])
		for eid in GameData.equipment_order:
			run.shop.buy_equipment(str(eid))
		_check(run.state.stat("damage_mult") > 1.0, "atributos recalculados")
	elif frame == 90:
		run.player.use_pulse()
		run.player.use_dash()
		run.player.use_emergency_pulse()
		run.damage_area(run.player.global_position, 400.0, 99999.0, 100.0, 1.0)
	elif frame == 130:
		run.map.gate.open_gate()
		run.player.global_position = Vector2(2600, 600)
	elif frame == 160:
		_check(run.boss != null, "chefe surgiu")
		if run.boss != null:
			run.boss.take_damage(500.0)
	elif frame == 200:
		for path in ["pause_menu", "lab_screen", "codex_screen", "credits_screen", "settings_panel", "start_screen", "main_menu", "game_over_screen", "loading_screen"]:
			var n: Node = (load("res://scenes/ui/%s.tscn" % path) as PackedScene).instantiate()
			root.add_child(n)
		var lu: LevelUpMenu = (load("res://scenes/ui/level_up_menu.tscn") as PackedScene).instantiate() as LevelUpMenu
		root.add_child(lu)
		lu.setup(run.state, MutationManager.roll_options(run.state, 3))
		var shop_menu: ShopMenu = (load("res://scenes/ui/shop_menu.tscn") as PackedScene).instantiate() as ShopMenu
		root.add_child(shop_menu)
		shop_menu.setup(run, "base")
		var rp: RecordPopup = (load("res://scenes/ui/record_popup.tscn") as PackedScene).instantiate() as RecordPopup
		root.add_child(rp)
		rp.setup("Teste", "Texto de teste")
		var vs: VictoryScreen = (load("res://scenes/ui/victory_screen.tscn") as PackedScene).instantiate() as VictoryScreen
		root.add_child(vs)
		vs.setup({"time": 900.0, "level": 10, "kills": 100, "nests": 3})
		print("[smoke] menus instanciados")
	elif frame == 260:
		var res: Dictionary = SaveManager.buy_mutation("casca_celular")
		print("[smoke] compra permanente: ", res["msg"])
		SaveManager.add_nuclei(3)
		var buy: Dictionary = SaveManager.buy_mutation("casca_celular")
		_check(bool(buy["ok"]) or SaveManager.has_mutation("casca_celular"), "compra de mutação permanente")
		var rev: Dictionary = SaveManager.revert_mutation("casca_celular")
		print("[smoke] reversão: ", rev["msg"])
	elif frame == 270:
		SaveManager.save_game()
		SaveManager.save_game()
		_check(SaveManager._read_file(SaveManager.BACKUP_PATH) != null, "backup do salvamento é válido")
		var bad: FileAccess = FileAccess.open(SaveManager.SAVE_PATH, FileAccess.WRITE)
		bad.store_string("{ isto nao e json")
		bad.close()
		SaveManager.save_game()
		_check(SaveManager._read_file(SaveManager.BACKUP_PATH) != null, "arquivo corrompido não sobrescreve o backup")
		SaveManager.add_codex_enemy("larva_fertil")
		var cdx: int = (SaveManager.data["codex_enemies"] as Array).size()
		SaveManager.add_codex_enemy("larva_fertil")
		_check((SaveManager.data["codex_enemies"] as Array).size() == cdx, "bestiário sem duplicatas")
	elif frame == 275:
		_check(not bool(GameManager.rebind("map", KEY_ESCAPE)["ok"]), "tecla reservada é recusada")
		_check(bool(GameManager.rebind("map", KEY_K)["ok"]) and GameManager.primary_key("map") == KEY_K, "remapear mapa para K")
		var has_k: bool = false
		for ev in InputMap.action_get_events("map"):
			if ev is InputEventKey and (ev as InputEventKey).physical_keycode == KEY_K:
				has_k = true
		_check(has_k, "InputMap recebeu a nova tecla")
		GameManager.rebind("interact", KEY_K)
		_check(GameManager.primary_key("map") == KEY_E and GameManager.primary_key("interact") == KEY_K, "teclas repetidas trocam entre si")
		GameManager.reset_bindings()
		_check(GameManager.primary_key("map") == KEY_M and GameManager.primary_key("interact") == KEY_E, "restaurar teclas padrão")
	elif frame == 300:
		run.end_run("extract")
		_check(run.ended, "expedição encerrada")
	elif frame == 320:
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
	print("[smoke] concluído. Falhas: ", failures.size())
