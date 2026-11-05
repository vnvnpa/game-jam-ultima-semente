extends Node
## Autoload "GameData": carrega os catálogos de dados a partir de arquivos
## .tres em res://data/. Para criar um novo inimigo, mutação, item etc., basta
## duplicar um .tres da pasta correspondente no editor e alterar no Inspector.
## A ordem de exibição segue a ordem alfabética do nome do arquivo (01_, 02_...).

const DIR_ENEMIES: String = "res://data/enemies"
const DIR_MUTATIONS: String = "res://data/mutations"
const DIR_UPGRADES: String = "res://data/upgrades"
const DIR_SHOP: String = "res://data/shop"
const DIR_EQUIPMENT: String = "res://data/equipment"
const DIR_RECORDS: String = "res://data/records"
const DIR_WAVES: String = "res://data/waves"
const DIR_EVENTS: String = "res://data/events"
const DIR_ELITES: String = "res://data/elites"
const DIR_BUFFS: String = "res://data/buffs"
const RULES_PATH: String = "res://data/rules/stat_rules.tres"
const DIR_ABILITIES: String = "res://data/abilities"
const DART_PATH: String = "res://data/weapons/dardo_fotossintese.tres"
const WEAPON_PATH: String = "res://data/weapons/espinho_simbiotico.tres"

var enemies: Dictionary = {}              # id -> EnemyData
var permanent_mutations: Dictionary = {}  # id -> MutationData
var mutation_order: Array = []
var upgrades: Dictionary = {}             # id -> UpgradeData
var upgrade_order: Array = []
var shop_items: Dictionary = {}           # id -> ShopItemData
var shop_order: Array = []
var equipment: Dictionary = {}            # id -> EquipmentData
var equipment_order: Array = []
var weapon: WeaponData = null
var dart_weapon: WeaponData = null
var abilities: Dictionary = {}            # id -> AbilityData
var wave_profiles: Dictionary = {}        # id -> WaveProfile
var threat_events: Array = []             # ThreatEventData, ordenados por tempo
var elite_modifiers: Dictionary = {}      # id -> EliteModifier
var buffs: Dictionary = {}                # id -> BuffData
var stat_rules: StatRules = null
var records: Dictionary = {}              # id -> {"titulo": String, "texto": String}
var record_order: Array = []

const LINE_NAMES: Dictionary = {
	"defesa": "Linha A — Simbiose defensiva",
	"predacao": "Linha B — Predação adaptativa",
	"ressonancia": "Linha C — Ressonância da Semente",
}


func _ready() -> void:
	for r in _load_dir(DIR_ENEMIES):
		var e: EnemyData = r as EnemyData
		if e != null and e.id != "":
			enemies[e.id] = e
	for r in _load_dir(DIR_MUTATIONS):
		var m: MutationData = r as MutationData
		if m != null and m.id != "":
			permanent_mutations[m.id] = m
			mutation_order.append(m.id)
	for r in _load_dir(DIR_UPGRADES):
		var u: UpgradeData = r as UpgradeData
		if u != null and u.id != "":
			upgrades[u.id] = u
			upgrade_order.append(u.id)
	for r in _load_dir(DIR_SHOP):
		var it: ShopItemData = r as ShopItemData
		if it != null and it.id != "":
			shop_items[it.id] = it
			shop_order.append(it.id)
	for r in _load_dir(DIR_EQUIPMENT):
		var eq: EquipmentData = r as EquipmentData
		if eq != null and eq.id != "":
			equipment[eq.id] = eq
			equipment_order.append(eq.id)
	for r in _load_dir(DIR_RECORDS):
		var rec: RecordData = r as RecordData
		if rec != null and rec.id != "":
			records[rec.id] = {"titulo": rec.titulo, "texto": rec.texto}
			record_order.append(rec.id)
	for r in _load_dir(DIR_WAVES):
		var wp: WaveProfile = r as WaveProfile
		if wp != null and wp.id != "":
			wave_profiles[wp.id] = wp
	for r in _load_dir(DIR_EVENTS):
		var te: ThreatEventData = r as ThreatEventData
		if te != null:
			threat_events.append(te)
	threat_events.sort_custom(_by_time)
	for r in _load_dir(DIR_ELITES):
		var em: EliteModifier = r as EliteModifier
		if em != null and em.id != "":
			elite_modifiers[em.id] = em
	for r in _load_dir(DIR_BUFFS):
		var bd: BuffData = r as BuffData
		if bd != null and bd.id != "":
			buffs[bd.id] = bd
	stat_rules = load(RULES_PATH) as StatRules
	if stat_rules == null or stat_rules.base_values.is_empty():
		push_error("GameData: regras de atributos ausentes em %s." % RULES_PATH)
		stat_rules = StatRules.new()
	if wave_profiles.is_empty():
		push_error("GameData: nenhum perfil de ondas em %s." % DIR_WAVES)
	for r in _load_dir(DIR_ABILITIES):
		var ab: AbilityData = r as AbilityData
		if ab != null and ab.id != "":
			abilities[ab.id] = ab
	dart_weapon = load(DART_PATH) as WeaponData
	if dart_weapon == null:
		push_error("GameData: Dardo de Fotossíntese não encontrado em %s." % DART_PATH)
	weapon = load(WEAPON_PATH) as WeaponData
	if weapon == null:
		push_error("GameData: arma não encontrada em %s; usando valores padrão." % WEAPON_PATH)
		weapon = WeaponData.new()
	if enemies.is_empty() or permanent_mutations.is_empty() or upgrades.is_empty():
		push_error("GameData: pastas de dados vazias ou ilegíveis (res://data/...).")


## Carrega todos os recursos .tres/.res de uma pasta, em ordem alfabética.
## Em builds exportados, os arquivos aparecem com o sufixo ".remap".
func _load_dir(dir_path: String) -> Array:
	var names: Array = []
	for f in DirAccess.get_files_at(dir_path):
		var n: String = f
		if n.ends_with(".remap"):
			n = n.trim_suffix(".remap")
		if (n.ends_with(".tres") or n.ends_with(".res")) and not names.has(n):
			names.append(n)
	names.sort()
	var out: Array = []
	for n in names:
		var res: Resource = load(dir_path + "/" + str(n))
		if res != null:
			out.append(res)
		else:
			push_warning("GameData: falha ao carregar %s/%s" % [dir_path, n])
	return out


func _by_time(a: ThreatEventData, b: ThreatEventData) -> bool:
	return a.tempo < b.tempo
