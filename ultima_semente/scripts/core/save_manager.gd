extends Node
## Autoload "SaveManager": progressão permanente, salvamento em user://,
## compra/reversão de mutações e recompensas únicas (GDD 11.5, 13 e 24.6/24.7).
## Toda operação que altera Núcleos valida o estado, executa uma única vez e
## desfaz a alteração em memória se o arquivo não puder ser gravado.

signal data_changed

const SAVE_PATH: String = "user://ultima_semente_save.json"
const BACKUP_PATH: String = "user://ultima_semente_save.bak"
const SAVE_VERSION: int = 1
const MAX_NUCLEI: int = 9999

var data: Dictionary = {}
var load_notice: String = ""


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	load_game()


# ------------------------------------------------------ estrutura
static func default_data() -> Dictionary:
	return {
		"version": SAVE_VERSION,
		"nuclei": 0,
		"mutations": {},
		"records": [],
		"codex_enemies": [],
		"claimed_rewards": [],
		"campaign_completed": false,
		"stats": {
			"runs": 0, "deaths": 0, "extractions": 0, "victories": 0, "abandons": 0,
			"kills": 0, "best_time": 0.0, "total_time": 0.0, "bosses_defeated": 0,
			"biomass_total": 0, "max_level": 1,
		},
		"settings": {"music": 0.7, "sfx": 0.8, "reduce_fx": false, "damage_numbers": true},
	}


static func _to_int(v: Variant, fallback: int = 0) -> int:
	var t: int = typeof(v)
	if t == TYPE_INT:
		return v
	if t == TYPE_FLOAT:
		if is_nan(v) or is_inf(v):
			return fallback
		return int(v)
	return fallback


static func _to_float(v: Variant, fallback: float = 0.0) -> float:
	var t: int = typeof(v)
	if t == TYPE_INT or t == TYPE_FLOAT:
		var f: float = float(v)
		if is_nan(f) or is_inf(f):
			return fallback
		return f
	return fallback


func _string_list(v: Variant) -> Array:
	var out: Array = []
	if typeof(v) != TYPE_ARRAY:
		return out
	for item in v:
		if typeof(item) == TYPE_STRING and not out.has(item):
			out.append(item)
	return out


## Valida e normaliza dados lidos do disco. Nunca confia no conteúdo.
func _sanitize(raw: Dictionary) -> Dictionary:
	var d: Dictionary = default_data()
	d["nuclei"] = clampi(_to_int(raw.get("nuclei", 0)), 0, MAX_NUCLEI)
	# Mutações: id válido -> núcleos pagos (>= 0)
	var muts: Dictionary = {}
	var raw_muts: Variant = raw.get("mutations", {})
	if typeof(raw_muts) == TYPE_DICTIONARY:
		for id in raw_muts:
			if typeof(id) == TYPE_STRING and GameData.permanent_mutations.has(id):
				var m: MutationData = GameData.permanent_mutations[id]
				muts[id] = clampi(_to_int(raw_muts[id], m.custo), 0, MAX_NUCLEI)
	d["mutations"] = muts
	d["records"] = _string_list(raw.get("records", []))
	d["codex_enemies"] = _string_list(raw.get("codex_enemies", []))
	d["claimed_rewards"] = _string_list(raw.get("claimed_rewards", []))
	d["campaign_completed"] = bool(raw.get("campaign_completed", false)) if typeof(raw.get("campaign_completed", false)) == TYPE_BOOL else false
	var base_stats: Dictionary = d["stats"]
	var raw_stats: Variant = raw.get("stats", {})
	if typeof(raw_stats) == TYPE_DICTIONARY:
		for k in base_stats:
			if raw_stats.has(k):
				if typeof(base_stats[k]) == TYPE_FLOAT:
					base_stats[k] = maxf(0.0, _to_float(raw_stats[k], 0.0))
				else:
					base_stats[k] = maxi(0, _to_int(raw_stats[k], 0))
	base_stats["max_level"] = maxi(1, int(base_stats["max_level"]))
	d["stats"] = base_stats
	var base_set: Dictionary = d["settings"]
	var raw_set: Variant = raw.get("settings", {})
	if typeof(raw_set) == TYPE_DICTIONARY:
		base_set["music"] = clampf(_to_float(raw_set.get("music", 0.7), 0.7), 0.0, 1.0)
		base_set["sfx"] = clampf(_to_float(raw_set.get("sfx", 0.8), 0.8), 0.0, 1.0)
		if typeof(raw_set.get("reduce_fx", false)) == TYPE_BOOL:
			base_set["reduce_fx"] = raw_set["reduce_fx"]
		if typeof(raw_set.get("damage_numbers", true)) == TYPE_BOOL:
			base_set["damage_numbers"] = raw_set["damage_numbers"]
	d["settings"] = base_set
	return d


# ----------------------------------------------------- disco
func _read_file(path: String) -> Variant:
	if not FileAccess.file_exists(path):
		return null
	var f: FileAccess = FileAccess.open(path, FileAccess.READ)
	if f == null:
		return null
	var text: String = f.get_as_text()
	f.close()
	var parsed: Variant = JSON.parse_string(text)
	if typeof(parsed) != TYPE_DICTIONARY:
		return null
	return parsed


func load_game() -> void:
	load_notice = ""
	var loaded: Variant = _read_file(SAVE_PATH)
	if loaded == null:
		var backup: Variant = _read_file(BACKUP_PATH)
		if backup != null:
			loaded = backup
			load_notice = "Salvamento principal inválido; backup restaurado."
	if loaded == null:
		data = default_data()
	else:
		var d: Dictionary = loaded
		if _to_int(d.get("version", 0)) > SAVE_VERSION:
			load_notice = "Salvamento de versão mais nova; alguns dados podem ser ignorados."
		data = _sanitize(d)
	data_changed.emit()


## Grava em disco. Retorna false em caso de falha (o chamador deve desfazer).
func save_game() -> bool:
	data["version"] = SAVE_VERSION
	var text: String = JSON.stringify(data, "\t")
	if FileAccess.file_exists(SAVE_PATH):
		var old_text: String = FileAccess.get_file_as_string(SAVE_PATH)
		if old_text != "":
			var b: FileAccess = FileAccess.open(BACKUP_PATH, FileAccess.WRITE)
			if b != null:
				b.store_string(old_text)
				b.close()
	var f: FileAccess = FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if f == null:
		push_warning("SaveManager: não foi possível abrir o arquivo para escrita.")
		return false
	f.store_string(text)
	f.close()
	return true


# ---------------------------------------------------- Núcleos
func get_nuclei() -> int:
	return int(data.get("nuclei", 0))


## Credita Núcleos e salva imediatamente (GDD 21.5). Retorna false se falhou.
func add_nuclei(amount: int) -> bool:
	if amount <= 0:
		return true
	# Créditos nunca são desfeitos: se a gravação falhar, o valor continua na
	# memória e será gravado no próximo salvamento bem-sucedido.
	data["nuclei"] = mini(MAX_NUCLEI, get_nuclei() + amount)
	var saved: bool = save_game()
	data_changed.emit()
	return saved


## Recompensa única (descoberta importante): só credita na 1ª vez.
## Retorna true se foi creditada agora.
func claim_once(reward_id: String, amount: int) -> bool:
	var claimed: Array = data["claimed_rewards"]
	if claimed.has(reward_id):
		return false
	claimed.append(reward_id)
	data["nuclei"] = mini(MAX_NUCLEI, get_nuclei() + maxi(0, amount))
	save_game()
	data_changed.emit()
	return true


# ---------------------------------------------- mutações permanentes
func owned_mutations() -> Dictionary:
	return data["mutations"]


func owned_ids() -> Array:
	return (data["mutations"] as Dictionary).keys()


func has_mutation(id: String) -> bool:
	return (data["mutations"] as Dictionary).has(id)


## Verifica se uma compra é possível. Retorna {"ok": bool, "msg": String}.
func can_buy_mutation(id: String) -> Dictionary:
	var m: MutationData = GameData.permanent_mutations.get(id)
	if m == null:
		return {"ok": false, "msg": "Mutação desconhecida."}
	if has_mutation(id):
		return {"ok": false, "msg": "Esta mutação já foi adquirida."}
	for pid in m.prerequisitos:
		if not has_mutation(pid):
			var pm: MutationData = GameData.permanent_mutations.get(pid)
			var pname: String = pm.nome if pm != null else str(pid)
			return {"ok": false, "msg": "Requer a mutação «%s»." % pname}
	for iid in m.incompativeis:
		if has_mutation(iid):
			var im: MutationData = GameData.permanent_mutations.get(iid)
			var iname: String = im.nome if im != null else str(iid)
			return {"ok": false, "msg": "Incompatível com «%s» (reverta-a primeiro)." % iname}
	if get_nuclei() < m.custo:
		return {"ok": false, "msg": "Núcleos insuficientes (%d/%d)." % [get_nuclei(), m.custo]}
	return {"ok": true, "msg": ""}


func buy_mutation(id: String) -> Dictionary:
	var check: Dictionary = can_buy_mutation(id)
	if not bool(check["ok"]):
		return check
	var m: MutationData = GameData.permanent_mutations[id]
	var old_nuclei: int = get_nuclei()
	var muts: Dictionary = data["mutations"]
	data["nuclei"] = old_nuclei - m.custo
	muts[id] = m.custo
	if not save_game():
		data["nuclei"] = old_nuclei
		muts.erase(id)
		return {"ok": false, "msg": "Falha ao salvar. Nada foi alterado."}
	data_changed.emit()
	return {"ok": true, "msg": "«%s» adquirida." % m.nome}


## Lista de ids de mutações ativas que dependem de `id`.
func dependents_of(id: String) -> Array:
	var out: Array = []
	for oid in owned_ids():
		var om: MutationData = GameData.permanent_mutations.get(oid)
		if om != null and om.prerequisitos.has(id):
			out.append(oid)
	return out


## Custo de reversão = exatamente o que foi pago (GDD 11.5).
func revert_cost(id: String) -> int:
	return int((data["mutations"] as Dictionary).get(id, 0))


func can_revert_mutation(id: String) -> Dictionary:
	if not has_mutation(id):
		return {"ok": false, "msg": "Esta mutação não está ativa."}
	var deps: Array = dependents_of(id)
	if deps.size() > 0:
		var names: Array = []
		for did in deps:
			var dm: MutationData = GameData.permanent_mutations.get(did)
			names.append(dm.nome if dm != null else str(did))
		return {"ok": false, "msg": "Reverta primeiro: %s." % ", ".join(names)}
	var cost: int = revert_cost(id)
	if get_nuclei() < cost:
		return {"ok": false, "msg": "Núcleos insuficientes (%d/%d)." % [get_nuclei(), cost]}
	return {"ok": true, "msg": ""}


func revert_mutation(id: String) -> Dictionary:
	var check: Dictionary = can_revert_mutation(id)
	if not bool(check["ok"]):
		return check
	var cost: int = revert_cost(id)
	var old_nuclei: int = get_nuclei()
	var muts: Dictionary = data["mutations"]
	var old_paid: int = int(muts[id])
	data["nuclei"] = old_nuclei - cost
	muts.erase(id)
	if not save_game():
		data["nuclei"] = old_nuclei
		muts[id] = old_paid
		return {"ok": false, "msg": "Falha ao salvar. Nada foi alterado."}
	data_changed.emit()
	var m: MutationData = GameData.permanent_mutations.get(id)
	return {"ok": true, "msg": "«%s» revertida." % (m.nome if m != null else id)}


# ------------------------------------------- registros e bestiário
func add_record(id: String) -> bool:
	var arr: Array = data["records"]
	if arr.has(id):
		return false
	arr.append(id)
	save_game()
	data_changed.emit()
	return true


func has_record(id: String) -> bool:
	return (data["records"] as Array).has(id)


func add_codex_enemy(id: String) -> void:
	var arr: Array = data["codex_enemies"]
	if not arr.has(id):
		arr.append(id)


func has_codex_enemy(id: String) -> bool:
	return (data["codex_enemies"] as Array).has(id)


# --------------------------------------------------- estatísticas
## Registra o resumo de uma expedição. Chamado uma única vez por Run.end_run().
func record_run(summary: Dictionary) -> void:
	var st: Dictionary = data["stats"]
	st["runs"] = int(st["runs"]) + 1
	st["kills"] = int(st["kills"]) + int(summary.get("kills", 0))
	st["total_time"] = float(st["total_time"]) + float(summary.get("time", 0.0))
	st["biomass_total"] = int(st["biomass_total"]) + int(summary.get("biomass_total", 0))
	st["max_level"] = maxi(int(st["max_level"]), int(summary.get("level", 1)))
	var reason: String = str(summary.get("reason", ""))
	match reason:
		"death":
			st["deaths"] = int(st["deaths"]) + 1
		"extract":
			st["extractions"] = int(st["extractions"]) + 1
		"abandon":
			st["abandons"] = int(st["abandons"]) + 1
		"victory":
			st["victories"] = int(st["victories"]) + 1
			data["campaign_completed"] = true
	if bool(summary.get("boss_defeated", false)):
		st["bosses_defeated"] = int(st["bosses_defeated"]) + 1
	if reason == "victory":
		var t: float = float(summary.get("time", 0.0))
		var best: float = float(st["best_time"])
		if best <= 0.0 or t < best:
			st["best_time"] = t
	save_game()
	data_changed.emit()


# -------------------------------------------------- configurações
func get_setting(key: String) -> Variant:
	return (data["settings"] as Dictionary).get(key)


func set_setting(key: String, value: Variant) -> void:
	var settings: Dictionary = data["settings"]
	settings[key] = value
	save_game()
