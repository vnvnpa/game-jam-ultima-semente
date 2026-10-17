class_name WorldLayout
extends RefCounted
## Consulta ao cenário em tempo de execução. NÃO guarda dados de nível: tudo
## (estações, zonas contaminadas, regiões, arena do chefe) vem dos nós colocados
## no editor em scenes/world/world_map.tscn, que se registram aqui ao entrar na
## cena e saem ao sair. Só o tamanho do mundo é constante.

const WORLD_RECT: Rect2 = Rect2(0, 0, 3600, 2600)

static var stations: Array = []
static var hostile_zones: Array = []
static var regions: Array = []
static var boss_arena: BossArena = null


static func register_station(s: Station) -> void:
	if not stations.has(s):
		stations.append(s)


static func unregister_station(s: Station) -> void:
	stations.erase(s)


static func register_hostile(z: HostileZone) -> void:
	if not hostile_zones.has(z):
		hostile_zones.append(z)


static func unregister_hostile(z: HostileZone) -> void:
	hostile_zones.erase(z)


static func register_region(r: RegionZone) -> void:
	if not regions.has(r):
		regions.append(r)


static func unregister_region(r: RegionZone) -> void:
	regions.erase(r)


static func station_at(pos: Vector2) -> Station:
	for s in stations:
		if not is_instance_valid(s):
			continue
		var st: Station = s
		if pos.distance_to(st.global_position) <= st.radius:
			return st
	return null


static func in_safe(pos: Vector2) -> bool:
	return station_at(pos) != null


static func is_hostile(pos: Vector2) -> bool:
	if in_safe(pos):
		return false
	for z in hostile_zones:
		if not is_instance_valid(z):
			continue
		if (z as HostileZone).get_rect().has_point(pos):
			return true
	return false


## Deslocamento necessário para tirar `pos` de dentro de uma estação segura
## (ou Vector2.ZERO se já estiver fora).
static func safe_push(pos: Vector2) -> Vector2:
	for s in stations:
		if not is_instance_valid(s):
			continue
		var st: Station = s
		var off: Vector2 = pos - st.global_position
		var d: float = off.length()
		if d < st.radius:
			if d < 0.01:
				off = Vector2.RIGHT
				d = 0.0
			return off.normalized() * (st.radius - d + 2.0)
	return Vector2.ZERO


static func nearest_station(pos: Vector2) -> Station:
	var best: Station = null
	var best_d: float = INF
	for s in stations:
		if not is_instance_valid(s):
			continue
		var st: Station = s
		var d: float = pos.distance_to(st.global_position)
		if d < best_d:
			best_d = d
			best = st
	return best


static func region_at(pos: Vector2) -> RegionZone:
	var found: RegionZone = null
	for r in regions:
		if not is_instance_valid(r):
			continue
		var rz: RegionZone = r
		if rz.get_rect().has_point(pos):
			found = rz   # a última região da lista tem prioridade em sobreposições
	return found


static func region_name(pos: Vector2) -> String:
	var r: RegionZone = region_at(pos)
	if r == null:
		return "Terras desconhecidas"
	return r.region_name


static func is_locked_region(pos: Vector2) -> bool:
	var r: RegionZone = region_at(pos)
	return r != null and r.locked_until_gate


static func zone_status(pos: Vector2) -> String:
	if in_safe(pos):
		return "pressurizado"
	if is_hostile(pos):
		return "hostil"
	return "respiravel"
