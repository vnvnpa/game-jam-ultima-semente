class_name ShopManager
extends Node
## Catálogo, preços e compras (GDD 10). Valida saldo, limites por visita e
## utilidade ANTES de descontar Biomassa; cada compra executa uma única vez.

const REFRESH_SECONDS: float = 120.0

var run: Run = null
var terminals: Dictionary = {}


func setup(r: Run) -> void:
	run = r


## Retorna o estado do terminal, renovando as ofertas após um tempo.
func get_terminal(tid: String) -> Dictionary:
	var now: float = run.state.run_time
	var term: Dictionary = terminals.get(tid, {})
	if term.is_empty() or now - float(term["stamp"]) > REFRESH_SECONDS:
		var pool: Array = []
		for id in GameData.shop_order:
			if id != "dose" and id != "ampola":
				pool.append(id)
		pool.shuffle()
		var offers: Array = ["dose", "ampola"]
		for i in 3:
			offers.append(pool[i])
		term = {"stamp": now, "offers": offers, "counts": {}}
		terminals[tid] = term
	return term


func bought_count(tid: String, item_id: String) -> int:
	var term: Dictionary = get_terminal(tid)
	var counts: Dictionary = term["counts"]
	return int(counts.get(item_id, 0))


func buy_item(tid: String, item_id: String) -> Dictionary:
	var it: ShopItemData = GameData.shop_items.get(item_id)
	if it == null:
		return {"ok": false, "msg": "Item inexistente."}
	var term: Dictionary = get_terminal(tid)
	if not (term["offers"] as Array).has(item_id):
		return {"ok": false, "msg": "Item não disponível neste terminal."}
	if bought_count(tid, item_id) >= it.limite_por_visita:
		return {"ok": false, "msg": "Limite por visita atingido."}
	var pl: Player = run.player
	var st: RunState = run.state
	# Recusas que evitam gastar sem efeito
	match item_id:
		"dose":
			if pl.hp >= st.max_hp() - 0.5:
				return {"ok": false, "msg": "Sua vida já está cheia."}
		"ampola":
			if run.oxygen.o2 >= run.oxygen.max_o2 - 0.5:
				return {"ok": false, "msg": "Seu oxigênio já está cheio."}
		"mira":
			if bool(st.shop_flags.get("mira", false)):
				return {"ok": false, "msg": "O Módulo de Mira já está instalado."}
		"casca_descartavel":
			if pl.shield >= 60.0:
				return {"ok": false, "msg": "Escudo já está no limite."}
		"isca":
			if run.decoy_active():
				return {"ok": false, "msg": "Já existe uma isca ativa."}
		"pulso_emergencia":
			if st.pulse_charges >= 2:
				return {"ok": false, "msg": "Você já carrega 2 cargas."}
	if st.biomass < it.custo:
		return {"ok": false, "msg": "Biomassa insuficiente (%d/%d)." % [st.biomass, it.custo]}
	if not st.spend_biomass(it.custo):
		return {"ok": false, "msg": "Biomassa insuficiente."}
	match item_id:
		"dose":
			pl.heal(st.max_hp() * 0.35)
		"catalisador":
			run.add_buff("catalisador", 45.0)
		"estimulante":
			run.add_buff("estimulante", 40.0)
		"ampola":
			run.oxygen.add_percent(0.35)
		"mira":
			st.shop_flags["mira"] = true
			run.refresh_all_stats()
		"casca_descartavel":
			pl.add_shield(40.0, 60.0)
		"isca":
			run.place_decoy(pl.global_position)
		"pulso_emergencia":
			st.pulse_charges += 1
		"cartucho":
			run.add_buff("cartucho", 30.0)
	var counts: Dictionary = term["counts"]
	counts[item_id] = int(counts.get(item_id, 0)) + 1
	AudioManager.play_sfx("confirm")
	return {"ok": true, "msg": "%s adquirido." % it.nome}


func buy_equipment(eid: String) -> Dictionary:
	var eq: EquipmentData = GameData.equipment.get(eid)
	if eq == null:
		return {"ok": false, "msg": "Equipamento inexistente."}
	var st: RunState = run.state
	var current: String = st.equip_traje if eq.slot == "traje" else st.equip_modulo
	if current == eid:
		return {"ok": false, "msg": "Já equipado."}
	if st.biomass < eq.custo:
		return {"ok": false, "msg": "Biomassa insuficiente (%d/%d)." % [st.biomass, eq.custo]}
	if not st.spend_biomass(eq.custo):
		return {"ok": false, "msg": "Biomassa insuficiente."}
	if eq.slot == "traje":
		st.equip_traje = eid
	else:
		st.equip_modulo = eid
	run.refresh_all_stats()
	AudioManager.play_sfx("confirm")
	return {"ok": true, "msg": "%s equipado." % eq.nome}
