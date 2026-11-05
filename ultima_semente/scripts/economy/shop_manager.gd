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
		var offers: Array = []
		for id in GameData.shop_order:
			var cand: ShopItemData = GameData.shop_items[id]
			if cand.sempre_oferecido:
				offers.append(id)
			else:
				pool.append(id)
		pool.shuffle()
		for i in mini(3, pool.size()):
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
	match it.tipo:
		"cura":
			if pl.hp >= st.max_hp() - 0.5:
				return {"ok": false, "msg": "Sua vida já está cheia."}
		"oxigenio":
			if run.oxygen.o2 >= run.oxygen.max_o2 - 0.5:
				return {"ok": false, "msg": "Seu oxigênio já está cheio."}
		"flag":
			if bool(st.shop_flags.get(item_id, false)):
				return {"ok": false, "msg": "O %s já está instalado." % it.nome}
		"escudo":
			if pl.shield >= it.valor_max:
				return {"ok": false, "msg": "Escudo já está no limite."}
		"isca":
			if run.decoy_active():
				return {"ok": false, "msg": "Já existe uma isca ativa."}
		"carga_pulso":
			if st.pulse_charges >= int(it.valor_max):
				return {"ok": false, "msg": "Você já carrega %d cargas." % int(it.valor_max)}
	if st.biomass < it.custo:
		return {"ok": false, "msg": "Biomassa insuficiente (%d/%d)." % [st.biomass, it.custo]}
	if not st.spend_biomass(it.custo):
		return {"ok": false, "msg": "Biomassa insuficiente."}
	match it.tipo:
		"cura":
			pl.heal(st.max_hp() * it.valor)
			AudioManager.play_sfx("heal")
		"buff":
			run.add_buff(it.buff_id)
		"oxigenio":
			run.oxygen.add_percent(it.valor)
		"flag":
			st.shop_flags[item_id] = true
			run.refresh_all_stats()
		"escudo":
			pl.add_shield(it.valor, it.valor_max)
		"isca":
			run.place_decoy(pl.global_position)
		"carga_pulso":
			st.pulse_charges += 1
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
