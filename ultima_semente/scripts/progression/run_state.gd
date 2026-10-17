class_name RunState
extends RefCounted
## Estado único e centralizado de uma expedição (GDD 24.6): nível, recursos,
## melhorias, equipamento, buffs e atributos calculados. Também serve para
## pré-visualizar atributos no Laboratório de Adaptação.

const BASE_HP: float = 100.0
const BASE_SPEED: float = 190.0
const BASE_O2: float = 180.0

## Efeitos de buffs temporários. Chave = id do buff.
const BUFF_DEFS: Dictionary = {
	"catalisador": {"mul": {"damage_mult": 1.30}},
	"estimulante": {"mul": {"fire_rate_mult": 1.30, "o2_use_mult": 1.35}},
	"cartucho": {"special": "veneno"},
	"sobrecarga": {"mul": {"skill_damage_mult": 2.2}},
	"sobrecarga_recarga": {"mul": {"skill_cd_mult": 1.5}},
	"carapaca": {"mul": {"damage_taken_mult": 0.45, "speed_mult": 0.7}},
}

## Limites para impedir acúmulo ilimitado de bônus semelhantes (GDD 11.4).
const STAT_LIMITS: Dictionary = {
	"hp_mult": [0.5, 2.2],
	"speed_mult": [0.55, 1.6],
	"damage_mult": [0.4, 4.0],
	"fire_rate_mult": [0.5, 3.0],
	"range_mult": [0.5, 2.2],
	"pierce": [0.0, 6.0],
	"extra_projectiles": [0.0, 4.0],
	"proj_speed_mult": [0.5, 2.0],
	"skill_cd_mult": [0.4, 2.0],
	"skill_power_mult": [0.5, 3.0],
	"skill_damage_mult": [0.5, 4.0],
	"damage_taken_mult": [0.3, 1.8],
	"heal_mult": [0.5, 1.6],
	"regen": [0.0, 6.0],
	"o2_max_mult": [0.5, 2.0],
	"o2_use_mult": [0.3, 2.5],
	"o2_recover_mult": [0.5, 2.0],
	"xp_mult": [0.5, 2.5],
	"pickup_radius": [40.0, 300.0],
	"elite_dmg_mult": [0.5, 3.0],
	"common_dmg_mult": [0.5, 2.0],
	"event_biomass_bonus": [0.0, 30.0],
	"elite_time_shift": [0.0, 120.0],
	"event_time_mult": [0.5, 1.5],
	"event_size_mult": [0.5, 2.0],
	"reveal_radius": [0.0, 900.0],
	"companions": [0.0, 4.0],
	"mutation_power": [0.5, 2.0],
	"regen_delay_bonus": [0.0, 6.0],
}

var perm_ids: Array = []
var upgrades: Dictionary = {}       # id -> nível
var equip_traje: String = ""
var equip_modulo: String = ""
var buffs: Dictionary = {}          # id -> segundos restantes
var shop_flags: Dictionary = {}     # flags de compras da expedição (ex.: "mira")
var specials: Dictionary = {}
var stats: Dictionary = {}

var level: int = 1
var xp: int = 0
var pending_levels: int = 0
var biomass: int = 0
var biomass_total: int = 0
var nuclei_gained: int = 0
var kills: int = 0
var run_time: float = 0.0
var revive_used: bool = false
var boss_reward_claimed: bool = false
var boss_defeated: bool = false
var nests_destroyed: int = 0
var discovered_pois: Array = []
var records_found: Array = []
var pulse_charges: int = 0
var cause_of_death: String = ""


func _init() -> void:
	rebuild_stats()


# ------------------------------------------------------------ XP
static func xp_needed(lvl: int) -> int:
	var n: float = float(lvl - 1)
	return int(8.0 + 6.0 * n + 1.2 * pow(n, 1.6))


## Soma XP e retorna quantos níveis foram ganhos.
func add_xp(amount: int) -> int:
	if amount <= 0:
		return 0
	xp += amount
	var gained: int = 0
	while xp >= xp_needed(level):
		xp -= xp_needed(level)
		level += 1
		pending_levels += 1
		gained += 1
	return gained


# ------------------------------------------------------ Biomassa
func add_biomass(amount: int) -> void:
	if amount <= 0:
		return
	biomass += amount
	biomass_total += amount


func spend_biomass(amount: int) -> bool:
	if amount < 0 or biomass < amount:
		return false
	biomass -= amount
	return true


# ------------------------------------------------------ consultas
func stat(key: String) -> float:
	return float(stats.get(key, 0.0))


func has_special(special_name: String) -> bool:
	return specials.has(special_name)


func upgrade_level(id: String) -> int:
	return int(upgrades.get(id, 0))


## Quantas melhorias distintas (não evoluções) da família já foram escolhidas.
func family_count(familia: String) -> int:
	var n: int = 0
	for uid in upgrades:
		var u: UpgradeData = GameData.upgrades.get(uid)
		if u != null and not u.evolucao and u.familia == familia:
			n += 1
	return n


func total_upgrade_levels() -> int:
	var n: int = 0
	for uid in upgrades:
		n += int(upgrades[uid])
	return n


# ------------------------------------------------- cálculo de atributos
static func _base_stats() -> Dictionary:
	return {
		"hp_mult": 1.0, "speed_mult": 1.0, "damage_mult": 1.0, "fire_rate_mult": 1.0,
		"range_mult": 1.0, "pierce": 0.0, "extra_projectiles": 0.0, "proj_speed_mult": 1.0,
		"skill_cd_mult": 1.0, "skill_power_mult": 1.0, "skill_damage_mult": 1.0,
		"damage_taken_mult": 1.0, "heal_mult": 1.0, "regen": 0.0, "o2_max_mult": 1.0,
		"o2_use_mult": 1.0, "o2_recover_mult": 1.0, "xp_mult": 1.0, "pickup_radius": 70.0,
		"elite_dmg_mult": 1.0, "common_dmg_mult": 1.0, "event_biomass_bonus": 0.0,
		"elite_time_shift": 0.0, "event_time_mult": 1.0, "event_size_mult": 1.0,
		"reveal_radius": 0.0, "companions": 0.0, "mutation_power": 1.0,
		"regen_delay_bonus": 0.0,
	}


static func _apply_mods(s: Dictionary, add: Dictionary, mul: Dictionary, power: float) -> void:
	for k in add:
		s[k] = float(s.get(k, 0.0)) + float(add[k]) * power
	for k in mul:
		s[k] = float(s.get(k, 1.0)) * pow(float(mul[k]), power)


func rebuild_stats() -> void:
	var s: Dictionary = _base_stats()
	var sp: Dictionary = {}
	# 1) Equipamentos (definem a força das mutações)
	for eid in [equip_traje, equip_modulo]:
		if eid == "":
			continue
		var eq: EquipmentData = GameData.equipment.get(eid)
		if eq == null:
			continue
		_apply_mods(s, eq.mods_add, eq.mods_mul, 1.0)
		if eq.especial != "":
			sp[eq.especial] = true
	var power: float = clampf(float(s["mutation_power"]), 0.5, 2.0)
	# 2) Mutações permanentes
	for mid in perm_ids:
		var m: MutationData = GameData.permanent_mutations.get(mid)
		if m == null:
			continue
		_apply_mods(s, m.mods_add, m.mods_mul, power)
		if m.especial != "":
			sp[m.especial] = true
	# 3) Melhorias temporárias
	for uid in upgrades:
		var u: UpgradeData = GameData.upgrades.get(uid)
		if u == null:
			continue
		var lv: float = float(upgrades[uid])
		_apply_mods(s, u.mods_add, u.mods_mul, power * lv)
		if u.especial != "":
			sp[u.especial] = true
	# 4) Compras da expedição
	if bool(shop_flags.get("mira", false)):
		s["range_mult"] = float(s["range_mult"]) * 1.25
	# 5) Buffs temporários
	for bid in buffs:
		var bd: Dictionary = BUFF_DEFS.get(bid, {})
		var badd: Dictionary = bd.get("add", {})
		var bmul: Dictionary = bd.get("mul", {})
		_apply_mods(s, badd, bmul, 1.0)
		if bd.has("special"):
			sp[bd["special"]] = true
	# 6) Limites
	for k in STAT_LIMITS:
		var lim: Array = STAT_LIMITS[k]
		s[k] = clampf(float(s.get(k, 0.0)), float(lim[0]), float(lim[1]))
	stats = s
	specials = sp


func max_hp() -> float:
	return BASE_HP * stat("hp_mult")


func move_speed() -> float:
	return BASE_SPEED * stat("speed_mult")


func max_o2() -> float:
	return BASE_O2 * stat("o2_max_mult")


# ------------------------------------------------ pré-visualização
static func make_preview(ids: Array) -> RunState:
	var rs: RunState = RunState.new()
	rs.perm_ids = ids.duplicate()
	rs.rebuild_stats()
	return rs


static func _pct(v: float) -> String:
	return "%d%%" % roundi(v * 100.0)


## Lista de [rótulo, valor] para exibir atributos no Laboratório.
func attribute_lines() -> Array:
	var lines: Array = []
	lines.append(["Vida máxima", str(roundi(max_hp()))])
	lines.append(["Velocidade", str(roundi(move_speed()))])
	lines.append(["Dano da arma", _pct(stat("damage_mult"))])
	lines.append(["Cadência", _pct(stat("fire_rate_mult"))])
	lines.append(["Alcance de alvos", _pct(stat("range_mult"))])
	lines.append(["Dano recebido", _pct(stat("damage_taken_mult"))])
	lines.append(["Recarga de habilidades", _pct(stat("skill_cd_mult"))])
	lines.append(["Cura recebida", _pct(stat("heal_mult"))])
	lines.append(["Regeneração (vida/s)", "%.1f" % stat("regen")])
	lines.append(["Oxigênio máximo (s)", str(roundi(max_o2()))])
	lines.append(["Consumo de oxigênio", _pct(stat("o2_use_mult"))])
	lines.append(["Recuperação de oxigênio", _pct(stat("o2_recover_mult"))])
	lines.append(["Experiência obtida", _pct(stat("xp_mult"))])
	lines.append(["Dano contra elites", _pct(stat("elite_dmg_mult"))])
	lines.append(["Dano contra comuns", _pct(stat("common_dmg_mult"))])
	return lines
