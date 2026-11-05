class_name Run
extends Node2D
## Uma expedição completa. Orquestra mundo, entidades, sistemas, menus
## modais e o encerramento (morte, extração, vitória ou abandono).
## Toda a lógica de jogo vive em `world` (pausável); a UI roda sempre.

signal request_menu
signal request_restart
signal request_garden
signal request_heart

const EXTRACT_UNLOCK_TIME: float = 600.0
const EXTRACT_HOLD_TIME: float = 2.0

@export_group("Regras da expedição")
## "region" (expedição principal) ou "garden" (Santuário do Último Jardim).
@export var level_id: String = "region"
## Id (em data/enemies) do chefe que desperta na arena.
@export var boss_id: String = "guardiao_raizes"
## Registro narrativo concedido ao iniciar ("" = nenhum).
@export var starting_record: String = "reg_queda"
@export_multiline var intro_text: String = "Expedição iniciada. Explore, sobreviva e destrua os ninhos."
@export var nests_required: int = 2
@export_group("Cenas instanciadas durante a expedição")
@export var enemy_scene: PackedScene
@export var boss_scene: PackedScene
@export var projectile_scene: PackedScene
@export var pickup_scene: PackedScene
@export var spore_scene: PackedScene
@export var slam_scene: PackedScene
@export var decoy_scene: PackedScene
@export var fx_scene: PackedScene
@export var decision_scene: PackedScene
@export var cloud_scene: PackedScene
@export_group("Menus modais")
@export var level_up_scene: PackedScene
@export var shop_scene: PackedScene
@export var pause_scene: PackedScene
@export var record_scene: PackedScene
@export var game_over_scene: PackedScene
@export var victory_scene: PackedScene
@export var level_complete_scene: PackedScene
@export_group("")

var state: RunState = null
var enemies: Array = []
var dead_queue: Array = []
var ended: bool = false
var boss: Enemy = null
var boss_active: bool = false
var boss_immune_time: float = 0.0
var boss_death_timer: float = -1.0
var rng: RandomNumberGenerator = RandomNumberGenerator.new()
var interactables: Array = []
var decoy: Decoy = null
var modal: String = ""
var modal_node: Control = null
var extract_hold: float = 0.0
var nearest: Interactable = null
var objectives: GardenObjectives = null
var summary: Dictionary = {}
var final_choice: String = ""
var _in_explosion: bool = false
var _last_float_ms: int = 0
var _audio_t: float = 0.0

# Nós da cena run.tscn (nomes únicos, editáveis no editor)
@onready var world: Node2D = %World
@onready var map: WorldMap = %Map
@onready var zones_node: Node2D = %Zones
@onready var drops_node: Node2D = %Drops
@onready var enemies_node: Node2D = %Enemies
@onready var player: Player = %Player
@onready var projectiles_node: Node2D = %Projectiles
@onready var fx_node: Node2D = %Effects
@onready var guide_arrows: GuideArrows = %GuideArrows
@onready var director: SpawnDirector = %SpawnDirector
@onready var events: WorldEvents = %WorldEvents
@onready var oxygen: OxygenManager = %Oxygen
@onready var shop: ShopManager = %Shop
@onready var ui_layer: CanvasLayer = %UI
@onready var hud: HUD = %Hud
@onready var map_overlay: MapOverlay = %MapOverlay


func _ready() -> void:
	rng.randomize()
	state = RunState.new()
	state.perm_ids = SaveManager.owned_ids()
	state.rebuild_stats()
	map.collect()
	player.setup(self)
	guide_arrows.run = self
	director.setup(self)
	events.setup(self)
	oxygen.setup(self)
	shop.setup(self)
	hud.setup(self)
	map_overlay.setup(self)
	objectives = get_node_or_null("%Objectives") as GardenObjectives
	if objectives != null:
		objectives.setup(self)
	_bind_scene_actors()
	if starting_record != "" and SaveManager.add_record(starting_record):
		state.records_found.append(starting_record)
	AudioManager.start_music()
	notify(intro_text, UIKit.COL_TEXT, "")


# ------------------------------------------------------ preparação
## Liga ao Run os elementos colocados no editor: coletáveis fixos, pontos de
## interação (nave, terminais, ruínas) e inimigos pré-colocados (ninhos).
func _bind_scene_actors() -> void:
	for n in get_tree().get_nodes_in_group("needs_run"):
		if is_ancestor_of(n):
			n.set("run", self)
	interactables.clear()
	for n in get_tree().get_nodes_in_group("interactables"):
		var it: Interactable = n as Interactable
		if it != null and is_ancestor_of(it):
			interactables.append(it)
	for n in get_tree().get_nodes_in_group("preplaced_enemies"):
		var e: Enemy = n as Enemy
		if e != null and is_ancestor_of(e) and e.preset_data != null:
			e.setup(self, e.preset_data, 1.0, "")
			enemies.append(e)


# ---------------------------------------------------------- queries
func is_free_spot(pos: Vector2, radius: float) -> bool:
	if not WorldLayout.WORLD_RECT.grow(-40.0).has_point(pos):
		return false
	if WorldLayout.in_safe(pos):
		return false
	return not map.is_inside_obstacle(pos, radius)


func is_spawn_valid(pos: Vector2, radius: float) -> bool:
	if not is_free_spot(pos, radius + 6.0):
		return false
	for stn in WorldLayout.stations:
		var st: Station = stn
		if pos.distance_to(st.global_position) < st.radius + 40.0:
			return false
	if WorldLayout.is_locked_region(pos) and not map.gate.is_open:
		return false
	if player != null and pos.distance_to(player.global_position) < director.min_distance():
		return false
	return true


func regular_enemy_count() -> int:
	var n: int = 0
	for e in enemies:
		if not is_instance_valid(e):
			continue
		var en: Enemy = e
		if en.alive and not en.is_boss and en.data.comportamento != "ninho":
			n += 1
	return n


func decoy_active() -> bool:
	return decoy != null and is_instance_valid(decoy)


## Texto do objetivo atual para o HUD.
func objective_text() -> String:
	if level_id == "heart":
		return _heart_objective()
	if objectives != null:
		return objectives.objective_text()
	if state.boss_defeated:
		return "Guardião derrotado!"
	if not map.gate.is_open:
		return "Objetivo: destrua %d ninhos (%d/%d) para abrir o Santuário." % [nests_required, state.nests_destroyed, nests_required]
	return "Objetivo: derrote o Guardião de Raízes no Santuário (norte)."


func _heart_objective() -> String:
	if state.boss_defeated:
		return "A Rede Raiz se calou. Nymara respira."
	var h: HeartBoss = boss as HeartBoss
	if h == null:
		return "Objetivo: entre na arena e enfrente o Coração de Nymara."
	if h.decision_started:
		return "Decida o destino da Última Semente."
	if h.stage == 1:
		return "Etapa 1 — Defesa: resista às raízes e fira o núcleo."
	if h.stage == 2:
		return "Etapa 2 — Exposição: destrua as estruturas (%d restantes)." % maxi(0, h.last_alive)
	return "Etapa 3 — Decisão: derrube as defesas finais do núcleo."


func get_enemy_target_pos(from: Vector2) -> Vector2:
	if decoy_active() and from.distance_to(decoy.global_position) < 420.0:
		return decoy.global_position
	return player.global_position


# ------------------------------------------------------------ spawns
func spawn_enemy(id: String, pos: Vector2, hp_mult: float = 1.0, modifier: String = "") -> Enemy:
	var data: EnemyData = GameData.enemies.get(id)
	if data == null:
		return null
	var scn: PackedScene = data.cena
	if scn == null:
		scn = boss_scene if data.comportamento == "chefe" else enemy_scene
	var e: Enemy = scn.instantiate() as Enemy
	e.position = pos
	enemies_node.add_child(e)
	e.setup(self, data, hp_mult, modifier)
	if data.comportamento == "chefe":
		e.is_boss = true
		e.knock_mult = 0.0
	enemies.append(e)
	return e


## Cria um projétil a partir da cena configurada (ainda sem adicionar à árvore).
func new_projectile() -> Projectile:
	var p: Projectile = projectile_scene.instantiate() as Projectile
	p.run = self
	return p


func spawn_projectile(p: Projectile) -> void:
	if projectiles_node.get_child_count() > 240:
		p.queue_free()
		return
	projectiles_node.add_child(p)


func spawn_biomass(pos: Vector2, amount: int, persistent: bool = false) -> void:
	if amount <= 0:
		return
	if drops_node.get_child_count() >= 160:
		state.add_biomass(amount)
		return
	var pk: BiomassPickup = pickup_scene.instantiate() as BiomassPickup
	pk.run = self
	pk.value = amount
	pk.persistent = persistent
	pk.position = pos + Vector2(randf_range(-10.0, 10.0), randf_range(-10.0, 10.0))
	drops_node.add_child(pk)


func spawn_spore_zone(pos: Vector2, radius: float, dps: float, duration: float) -> void:
	if zones_node.get_child_count() > 40 or WorldLayout.in_safe(pos):
		return
	var z: SporeZone = spore_scene.instantiate() as SporeZone
	z.run = self
	z.radius = radius
	z.dps = dps
	z.life = duration
	z.position = pos
	zones_node.add_child(z)


func spawn_root_slam(pos: Vector2, radius: float, damage: float, delay: float) -> void:
	var s: RootSlam = slam_scene.instantiate() as RootSlam
	s.run = self
	s.radius = radius
	s.damage = damage
	s.delay = delay
	s.position = pos
	zones_node.add_child(s)


## Nuvem de Esporos do jogador (substitui a mais antiga se passar do limite).
func spawn_cloud(pos: Vector2, radius: float, life: float, ab: AbilityData) -> void:
	if cloud_scene == null:
		return
	var active: Array = get_tree().get_nodes_in_group("clouds")
	if active.size() >= ab.max_ativas:
		(active[0] as Node).queue_free()
	var c: FriendlyCloud = cloud_scene.instantiate() as FriendlyCloud
	c.run = self
	c.data = ab
	c.radius = radius
	c.life = life
	c.position = pos
	zones_node.add_child(c)


func place_decoy(pos: Vector2) -> bool:
	if decoy_active():
		return false
	decoy = decoy_scene.instantiate() as Decoy
	decoy.position = pos
	zones_node.add_child(decoy)
	return true


# -------------------------------------------------------------- efeitos
func fx_ring(pos: Vector2, radius: float, color: Color, duration: float = 0.4) -> void:
	if fx_node.get_child_count() > 100:
		return
	var f: Fx = fx_scene.instantiate() as Fx
	f.kind = "ring"
	f.radius = radius
	f.color = color
	f.life = duration
	f.position = pos
	fx_node.add_child(f)


func fx_burst(pos: Vector2, color: Color, count: int = 8, dist: float = 26.0) -> void:
	if fx_node.get_child_count() > 100:
		return
	var f: Fx = fx_scene.instantiate() as Fx
	f.kind = "burst"
	f.color = color
	f.life = 0.3
	f.position = pos
	for i in count:
		f.sparks.append({"dir": Vector2.from_angle(randf() * TAU), "dist": dist * randf_range(0.5, 1.0)})
	fx_node.add_child(f)


func float_text(pos: Vector2, text: String, color: Color) -> void:
	var is_number: bool = text.is_valid_int() or text.begins_with("-")
	if is_number and not GameManager.show_damage_numbers():
		return
	var now: int = Time.get_ticks_msec()
	if is_number and now - _last_float_ms < 30:
		return
	_last_float_ms = now
	if fx_node.get_child_count() > 100:
		return
	var f: Fx = fx_scene.instantiate() as Fx
	f.kind = "text"
	f.text = text
	f.color = color
	f.life = 0.7
	f.position = pos + Vector2(randf_range(-6.0, 6.0), 0.0)
	fx_node.add_child(f)


func notify(text: String, color: Color = UIKit.COL_TEXT, sfx_name: String = "") -> void:
	if hud != null:
		hud.push_alert(text, color)
	if sfx_name != "":
		AudioManager.play_sfx(sfx_name)


func shake(amount: float) -> void:
	if player != null:
		player.add_shake(amount)


# ------------------------------------------------------- recursos / XP
func collect_biomass(amount: int) -> void:
	state.add_biomass(amount)


func add_xp(amount: int) -> void:
	var gained: int = state.add_xp(roundi(float(amount) * state.stat("xp_mult")))
	if gained > 0:
		AudioManager.play_sfx("levelup")
		fx_ring(player.global_position, 60.0, Color(1.0, 0.95, 0.5), 0.5)


## `duration` < 0 usa a duração padrão do BuffData (data/buffs).
func add_buff(id: String, duration: float = -1.0) -> void:
	var dur: float = duration
	if dur < 0.0:
		var bd: BuffData = GameData.buffs.get(id)
		dur = bd.duracao if bd != null else 0.0
	state.buffs[id] = dur
	refresh_all_stats()


## Aplica um buff sem recalcular atributos (o chamador recalcula depois).
func add_buff_silent(id: String) -> void:
	var bd: BuffData = GameData.buffs.get(id)
	if bd != null:
		state.buffs[id] = bd.duracao


func refresh_all_stats() -> void:
	state.rebuild_stats()
	if player != null:
		player.refresh_stats()
	if oxygen != null:
		oxygen.refresh_max()


func damage_area(center: Vector2, radius: float, dmg: float, knock: float, root: float) -> int:
	var hits: int = 0
	for e in enemies:
		if not is_instance_valid(e):
			continue
		var en: Enemy = e
		if not en.alive:
			continue
		var rr: float = radius + en.radius
		if center.distance_squared_to(en.global_position) > rr * rr:
			continue
		hits += 1
		if dmg > 0.0:
			en.take_damage(dmg, "area")
		if en.alive:
			if knock > 0.0:
				var dir: Vector2 = en.global_position - center
				if dir.length() < 0.5:
					dir = Vector2.from_angle(randf() * TAU)
				en.apply_knockback(dir.normalized() * knock)
			if root > 0.0:
				en.apply_root(root)
	return hits


# ------------------------------------------------------ eventos de jogo
func mark_dead(e: Enemy) -> void:
	dead_queue.append(e)


func on_enemy_killed(e: Enemy) -> void:
	state.kills += 1
	var d: EnemyData = e.data
	SaveManager.add_codex_enemy(d.id)
	add_xp(e.xp_value)
	spawn_biomass(e.global_position, rng.randi_range(e.bio_min, e.bio_max))
	fx_burst(e.global_position, d.cor, 8, 22.0)
	AudioManager.play_sfx("kill", randf_range(0.9, 1.2), -6.0)
	if state.has_special("nuvem_cadeia") and e.weaken_time > 0.0:
		var cab: AbilityData = GameData.abilities.get("nuvem_esporos")
		if cab != null and rng.randf() < cab.cadeia_chance:
			spawn_cloud(e.global_position, cab.raio * cab.cadeia_raio_mult * state.stat("cloud_power"), cab.cadeia_duracao, cab)
	if e.is_boss:
		_on_boss_killed()
	elif d.comportamento == "ninho":
		_on_nest_killed()
	if d.comportamento == "esporideo":
		spawn_spore_zone(e.global_position, 55.0, 6.0, 5.0)
	if e.explode_on_death and e.elite_data != null:
		_explode(e.global_position, e.elite_data.explosion_radius, e.elite_data.explosion_enemy_damage, e.elite_data.explosion_player_damage)
	elif state.has_special("sangue_volatil") and not _in_explosion and randf() < 0.35:
		_explode(e.global_position, 70.0, 20.0 * state.stat("damage_mult"), 10.0)


## Explosão: fere inimigos próximos e, se perto, o jogador. Não encadeia.
func _explode(pos: Vector2, radius: float, enemy_dmg: float, player_dmg: float) -> void:
	if _in_explosion:
		return
	_in_explosion = true
	fx_ring(pos, radius, Color(1.0, 0.5, 0.3), 0.35)
	AudioManager.play_sfx("explosion", 1.0, -6.0)
	damage_area(pos, radius, enemy_dmg, 120.0, 0.0)
	if player != null and not player.dead and pos.distance_to(player.global_position) < radius * 0.8:
		player.take_damage(player_dmg, pos)
	_in_explosion = false


func _on_nest_killed() -> void:
	state.nests_destroyed += 1
	notify("Ninho destruído! (%d/%d)" % [state.nests_destroyed, nests_required], UIKit.COL_GOOD, "levelup")
	if state.nests_destroyed >= nests_required and not map.gate.is_open:
		map.gate.open_gate()
		notify("A Barreira de Raízes do Santuário se abriu!", UIKit.COL_NUC, "mutation")


func _spawn_boss() -> void:
	if WorldLayout.boss_arena == null:
		return
	boss = spawn_enemy(boss_id, WorldLayout.boss_arena.global_position, 1.0)
	if boss == null:
		return
	boss_active = true
	boss_immune_time = 2.0
	notify("%s desperta!" % boss.data.nome, UIKit.COL_BAD, "boss")
	shake(6.0)


func _on_boss_killed() -> void:
	boss_active = false
	state.boss_defeated = true
	# Recompensa de chefe: creditada UMA única vez, imediatamente (GDD 21.5).
	if not state.boss_reward_claimed:
		state.boss_reward_claimed = true
		var nmin: int = boss.data.nucleos_min if boss != null else 1
		var nmax: int = boss.data.nucleos_max if boss != null else 2
		var n: int = rng.randi_range(nmin, maxi(nmin, nmax))
		var ok: bool = SaveManager.add_nuclei(n)
		state.nuclei_gained += n
		AudioManager.play_sfx("nucleus")
		notify("Núcleo Primordial +%d" % n, UIKit.COL_NUC, "")
		if not ok:
			notify("Aviso: não foi possível gravar o salvamento agora.", UIKit.COL_WARN, "")
	var boss_name: String = boss.data.nome if boss != null else "O chefe"
	notify("%s caiu!" % boss_name, UIKit.COL_GOOD, "victory")
	boss_death_timer = 3.5
	for e in enemies.duplicate():
		if is_instance_valid(e):
			var en: Enemy = e
			if en.alive and not en.is_boss and en.data.comportamento != "ninho":
				en.die()


func on_player_died(cause: String) -> void:
	state.cause_of_death = cause
	end_run("death")


# ----------------------------------------------------------- loop
func _physics_process(delta: float) -> void:
	if ended or get_tree().paused:
		return
	_flush_dead()
	state.run_time += delta
	_update_buffs(delta)
	if boss_immune_time > 0.0:
		boss_immune_time = maxf(0.0, boss_immune_time - delta)
	var arena: BossArena = WorldLayout.boss_arena
	if boss == null and not state.boss_defeated and map.gate.is_open and arena != null:
		if player.global_position.distance_to(arena.global_position) < arena.trigger_radius:
			_spawn_boss()
	if boss_death_timer > 0.0:
		boss_death_timer -= delta
		if boss_death_timer <= 0.0:
			var end_reason: String = "region_clear"
			if level_id == "garden":
				end_reason = "garden_clear"
			elif level_id == "heart":
				end_reason = "victory"
			end_run(end_reason)
			return
	_audio_t -= delta
	if _audio_t <= 0.0:
		_audio_t = 0.5
		var near: int = 0
		for e in enemies:
			if is_instance_valid(e) and (e as Enemy).alive and (e as Enemy).global_position.distance_squared_to(player.global_position) < 90000.0:
				near += 1
		AudioManager.set_combat_intensity(float(near) / 12.0)


func _flush_dead() -> void:
	if dead_queue.is_empty():
		return
	for e in dead_queue:
		if is_instance_valid(e):
			enemies.erase(e)
			(e as Node).queue_free()
	dead_queue.clear()


func _update_buffs(delta: float) -> void:
	if state.buffs.is_empty():
		return
	var expired: Array = []
	for id in state.buffs:
		state.buffs[id] = float(state.buffs[id]) - delta
		if float(state.buffs[id]) <= 0.0:
			expired.append(id)
	if expired.is_empty():
		return
	for id in expired:
		state.buffs.erase(id)
		if id == "sobrecarga" and state.has_special("sobrecarga_celular"):
			add_buff_silent("sobrecarga_recarga")
	refresh_all_stats()


func _process(delta: float) -> void:
	if ended:
		return
	if hud != null:
		hud.refresh(self)
	if get_tree().paused:
		return
	if modal == "" and state.pending_levels > 0:
		_open_level_up()
		return
	_update_interaction(delta)


func _nearest_interactable() -> Interactable:
	var best: Interactable = null
	var best_d: float = INF
	for it in interactables:
		var i: Interactable = it
		var d: float = player.global_position.distance_to(i.global_position)
		if d <= i.reach and d < best_d:
			best_d = d
			best = i
	return best


func _update_interaction(delta: float) -> void:
	nearest = _nearest_interactable()
	if nearest == null:
		extract_hold = 0.0
		hud.set_prompt("")
		return
	if nearest.kind == "ship":
		if state.run_time < EXTRACT_UNLOCK_TIME:
			extract_hold = 0.0
			hud.set_prompt("Extração disponível aos %s (faltam %s)" % [GameManager.format_time(EXTRACT_UNLOCK_TIME), GameManager.format_time(EXTRACT_UNLOCK_TIME - state.run_time)])
			return
		if Input.is_action_pressed("interact"):
			extract_hold += delta
			hud.set_prompt("Extraindo... %d%%" % roundi(clampf(extract_hold / EXTRACT_HOLD_TIME, 0.0, 1.0) * 100.0))
			if extract_hold >= EXTRACT_HOLD_TIME:
				end_run("extract")
		else:
			extract_hold = 0.0
			hud.set_prompt(nearest.prompt_text())
		return
	extract_hold = 0.0
	hud.set_prompt(nearest.prompt_text())
	if Input.is_action_just_pressed("interact"):
		if nearest.kind == "shop":
			open_shop(nearest.ref_id)
		elif nearest.kind == "poi":
			_read_poi(nearest)
		elif nearest.kind == "mechanism" and objectives != null:
			objectives.try_activate(nearest)


func _read_poi(it: Interactable) -> void:
	var rec_id: String = it.record_id
	var claim: String = it.nuc_claim
	if rec_id == "":
		return
	if not it.used:
		it.used = true
		state.discovered_pois.append(it.ref_id)
		if SaveManager.add_record(rec_id):
			state.records_found.append(rec_id)
		if claim != "":
			if SaveManager.claim_once(claim, 1):
				state.nuclei_gained += 1
				AudioManager.play_sfx("nucleus")
				notify("Descoberta importante! Núcleo Primordial +1", UIKit.COL_NUC, "")
	_show_record(rec_id)


# ------------------------------------------------------------ modais
func _close_modal() -> void:
	if modal_node != null and is_instance_valid(modal_node):
		modal_node.queue_free()
	modal_node = null
	modal = ""
	get_tree().paused = false
	get_viewport().gui_release_focus()


func _open_level_up() -> void:
	var opts: Array = MutationManager.roll_options(state, 3)
	if opts.is_empty():
		state.pending_levels -= 1
		state.add_biomass(15)
		player.heal(state.max_hp() * 0.1)
		notify("Todas as mutações no máximo: +15 Biomassa.", UIKit.COL_BIO, "")
		return
	modal = "levelup"
	get_tree().paused = true
	var menu: LevelUpMenu = level_up_scene.instantiate() as LevelUpMenu
	ui_layer.add_child(menu)
	menu.setup(state, opts)
	menu.chosen.connect(_on_upgrade_chosen)
	modal_node = menu
	AudioManager.play_sfx("mutation")


func _on_upgrade_chosen(id: String) -> void:
	if modal != "levelup":
		return
	if MutationManager.apply_upgrade(state, id):
		state.pending_levels = maxi(0, state.pending_levels - 1)
		var u: UpgradeData = GameData.upgrades.get(id)
		if u != null:
			notify("Mutação: %s (nível %d)" % [u.nome, state.upgrade_level(id)], UIKit.COL_GOOD, "")
		refresh_all_stats()
	_close_modal()


func open_shop(tid: String) -> void:
	if modal != "":
		return
	modal = "shop"
	get_tree().paused = true
	var menu: ShopMenu = shop_scene.instantiate() as ShopMenu
	ui_layer.add_child(menu)
	menu.setup(self, tid)
	menu.closed.connect(_close_modal)
	modal_node = menu
	AudioManager.play_sfx("confirm")


func _show_record(rec_id: String) -> void:
	if modal != "":
		return
	var rec: Dictionary = GameData.records.get(rec_id, {})
	if rec.is_empty():
		return
	modal = "record"
	get_tree().paused = true
	var popup: RecordPopup = record_scene.instantiate() as RecordPopup
	ui_layer.add_child(popup)
	popup.setup(str(rec["titulo"]), str(rec["texto"]))
	popup.closed.connect(_close_modal)
	modal_node = popup


func open_pause() -> void:
	if modal != "" or ended:
		return
	modal = "pause"
	get_tree().paused = true
	var menu: PauseMenu = pause_scene.instantiate() as PauseMenu
	ui_layer.add_child(menu)
	menu.resume_pressed.connect(_close_modal)
	menu.abandon_pressed.connect(_abandon)
	modal_node = menu


## Chamado quando a janela/aba perde o foco (build web).
func pause_for_focus() -> void:
	if not ended and modal == "":
		open_pause()


func _unhandled_input(event: InputEvent) -> void:
	if ended:
		return
	if event.is_action_pressed("pause"):
		if modal == "":
			open_pause()
		elif modal == "pause" or modal == "shop" or modal == "record":
			_close_modal()
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("map"):
		if modal == "" and map_overlay != null:
			map_overlay.visible = not map_overlay.visible
			get_viewport().set_input_as_handled()


# ------------------------------------------------------- encerramento
func end_run(reason: String) -> void:
	if ended:
		return
	ended = true
	if (reason == "victory" or reason == "region_clear" or reason == "garden_clear") and not state.boss_defeated:
		reason = "extract"
	summary = {
		"reason": reason,
		"time": state.run_time,
		"level": state.level,
		"kills": state.kills,
		"biomass_total": state.biomass_total,
		"biomass_left": state.biomass,
		"nuclei_gained": state.nuclei_gained,
		"boss_defeated": state.boss_defeated,
		"cause": state.cause_of_death,
		"records": state.records_found.size(),
		"nests": state.nests_destroyed,
		"level_id": level_id,
		"ending": final_choice,
		"mechanisms": objectives.activated_count() if objectives != null else 0,
	}
	SaveManager.record_run(summary)
	AudioManager.set_combat_intensity(0.0)
	if modal_node != null and is_instance_valid(modal_node):
		modal_node.queue_free()
	modal_node = null
	modal = "end"
	if map_overlay != null:
		map_overlay.visible = false
	if hud != null:
		hud.visible = false
	get_tree().paused = true
	if reason == "abandon":
		get_tree().paused = false
		request_menu.emit()
		return
	if reason == "victory":
		AudioManager.play_sfx("victory")
		var v: VictoryScreen = victory_scene.instantiate() as VictoryScreen
		ui_layer.add_child(v)
		v.setup(summary)
		v.menu_pressed.connect(_go_menu)
	elif reason == "region_clear" or reason == "garden_clear":
		AudioManager.play_sfx("victory")
		var lc: LevelCompleteScreen = level_complete_scene.instantiate() as LevelCompleteScreen
		ui_layer.add_child(lc)
		lc.setup(summary)
		if reason == "garden_clear":
			lc.garden_pressed.connect(_go_heart)
		else:
			lc.garden_pressed.connect(_go_garden)
		lc.menu_pressed.connect(_go_menu)
	else:
		AudioManager.play_sfx("gameover")
		var g: GameOverScreen = game_over_scene.instantiate() as GameOverScreen
		ui_layer.add_child(g)
		g.setup(summary)
		g.restart_pressed.connect(_go_restart)
		g.menu_pressed.connect(_go_menu)


func _abandon() -> void:
	end_run("abandon")


func _go_menu() -> void:
	get_tree().paused = false
	request_menu.emit()


## Abre a escolha final do Coração de Nymara. Retorna true se tratou o pedido.
func open_decision(heart: Enemy) -> bool:
	if ended:
		return true
	if decision_scene == null:
		_on_decision_chosen("restaurar", heart)
		return true
	if modal != "":
		return false
	modal = "decision"
	get_tree().paused = true
	var scr: DecisionScreen = decision_scene.instantiate() as DecisionScreen
	ui_layer.add_child(scr)
	scr.setup((SaveManager.data["records"] as Array).size())
	scr.chosen.connect(_on_decision_chosen.bind(heart))
	modal_node = scr
	return true


func _on_decision_chosen(id: String, heart: Enemy) -> void:
	final_choice = id
	if modal == "decision":
		_close_modal()
	if heart != null and is_instance_valid(heart) and heart is HeartBoss:
		(heart as HeartBoss).finish_after_decision()


func _go_heart() -> void:
	get_tree().paused = false
	request_heart.emit()


func _go_garden() -> void:
	get_tree().paused = false
	request_garden.emit()


func _go_restart() -> void:
	get_tree().paused = false
	request_restart.emit()
