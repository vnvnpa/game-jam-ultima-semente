class_name MutationManager
extends RefCounted
## Escolhe as opções de melhoria ao subir de nível e valida a aplicação.
## Mutações permanentes ficam em SaveManager (compra/reversão).


## Retorna até `count` UpgradeData distintas. Evoluções elegíveis têm prioridade.
static func roll_options(state: RunState, count: int = 3) -> Array:
	var normal: Array = []
	var evolutions: Array = []
	for uid in GameData.upgrade_order:
		var u: UpgradeData = GameData.upgrades.get(uid)
		if u == null:
			continue
		var lv: int = state.upgrade_level(uid)
		if lv >= u.max_nivel:
			continue
		if u.requer_upgrade != "" and state.upgrade_level(u.requer_upgrade) == 0:
			continue
		if u.evolucao:
			if lv == 0 and state.has_special("ressonancia_profunda") and state.family_count(u.requer_familia) >= 3:
				evolutions.append(u)
		else:
			normal.append(u)
	normal.shuffle()
	evolutions.shuffle()
	var result: Array = []
	if evolutions.size() > 0:
		result.append(evolutions[0])
	for u in normal:
		if result.size() >= count:
			break
		result.append(u)
	return result


## Aplica uma melhoria escolhida. Retorna false se inválida (nível máximo, id inexistente).
static func apply_upgrade(state: RunState, id: String) -> bool:
	var u: UpgradeData = GameData.upgrades.get(id)
	if u == null:
		return false
	var lv: int = state.upgrade_level(id)
	if lv >= u.max_nivel:
		return false
	state.upgrades[id] = lv + 1
	state.rebuild_stats()
	return true


static func family_label(familia: String) -> String:
	match familia:
		"predacao":
			return "Predação"
		"defesa":
			return "Defesa"
		"ressonancia":
			return "Ressonância"
	return familia
