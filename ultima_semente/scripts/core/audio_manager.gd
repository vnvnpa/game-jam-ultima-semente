extends Node
## Autoload "AudioManager": toca efeitos (SfxBank) e música (MusicSet) a partir
## de recursos editáveis em data/audio/. Barramentos Music/SFX com volumes
## independentes (default_bus_layout.tres). Em navegadores o áudio só começa após
## a primeira interação do jogador; a Godot cuida do desbloqueio.

const BANK_PATH: String = "res://data/audio/sfx_bank.tres"
const MUSIC_PATH: String = "res://data/audio/music_set.tres"
const POOL_SIZE: int = 12

var _bank: Dictionary = {}        # id -> SfxEntry
var _music_set: MusicSet = null
var _pool: Array = []
var _last_play: Dictionary = {}
var _music_calm: AudioStreamPlayer = null
var _music_combat: AudioStreamPlayer = null
var _combat_target: float = 0.0
var _combat_level: float = 0.0
var _music_on: bool = false
var _fade: float = 0.0
var _duck: float = 0.0
var _muted_by_focus: bool = false


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_ensure_bus("Music")
	_ensure_bus("SFX")
	_load_resources()
	for i in POOL_SIZE:
		var p: AudioStreamPlayer = AudioStreamPlayer.new()
		p.bus = "SFX"
		add_child(p)
		_pool.append(p)
	_music_calm = _make_music_player(_music_set.explorar if _music_set != null else null)
	_music_combat = _make_music_player(_music_set.combate if _music_set != null else null)
	apply_volumes()


func _load_resources() -> void:
	var bank: SfxBank = load(BANK_PATH) as SfxBank
	if bank == null:
		push_error("AudioManager: banco de sons ausente em %s." % BANK_PATH)
	else:
		for e in bank.entries:
			var en: SfxEntry = e as SfxEntry
			if en != null and en.id != "":
				_bank[en.id] = en
	_music_set = load(MUSIC_PATH) as MusicSet
	if _music_set == null:
		push_error("AudioManager: conjunto de músicas ausente em %s." % MUSIC_PATH)
		_music_set = MusicSet.new()


func _make_music_player(stream: AudioStream) -> AudioStreamPlayer:
	var p: AudioStreamPlayer = AudioStreamPlayer.new()
	p.bus = "Music"
	p.stream = stream
	p.volume_db = -80.0
	# Reserva: se a trilha não tiver marcador de loop, recomeça ao terminar.
	p.finished.connect(_on_music_finished.bind(p))
	add_child(p)
	return p


func _on_music_finished(p: AudioStreamPlayer) -> void:
	if _music_on:
		p.play()


func _ensure_bus(bus_name: String) -> void:
	if AudioServer.get_bus_index(bus_name) != -1:
		return
	AudioServer.add_bus()
	var idx: int = AudioServer.bus_count - 1
	AudioServer.set_bus_name(idx, bus_name)
	AudioServer.set_bus_send(idx, "Master")


func apply_volumes() -> void:
	_set_bus_linear("Music", float(SaveManager.get_setting("music")))
	_set_bus_linear("SFX", float(SaveManager.get_setting("sfx")))


func _set_bus_linear(bus_name: String, v: float) -> void:
	var idx: int = AudioServer.get_bus_index(bus_name)
	if idx == -1:
		return
	if v <= 0.001:
		AudioServer.set_bus_mute(idx, true)
	else:
		AudioServer.set_bus_mute(idx, false)
		AudioServer.set_bus_volume_db(idx, linear_to_db(v))


# ------------------------------------------------------------- API
func has_sfx(sfx_name: String) -> bool:
	return _bank.has(sfx_name)


func play_sfx(sfx_name: String, pitch: float = 1.0, volume_db: float = 0.0) -> void:
	var en: SfxEntry = _bank.get(sfx_name)
	if en == null or en.stream == null:
		return
	var now: int = Time.get_ticks_msec()
	var last: int = int(_last_play.get(sfx_name, -100000))
	if now - last < en.cooldown_ms:
		return
	_last_play[sfx_name] = now
	var chosen: AudioStreamPlayer = null
	for p in _pool:
		var ap: AudioStreamPlayer = p
		if not ap.playing:
			chosen = ap
			break
	if chosen == null:
		chosen = _pool[0]
	chosen.stream = en.stream
	chosen.pitch_scale = clampf(en.pitch * pitch, 0.5, 2.0)
	chosen.volume_db = en.volume_db + volume_db
	chosen.play()


func start_music() -> void:
	if _music_on:
		return
	_music_on = true
	_fade = 0.0
	if _music_calm.stream != null:
		_music_calm.play()
	if _music_combat.stream != null:
		_music_combat.play()


func stop_music() -> void:
	_music_on = false
	_music_calm.stop()
	_music_combat.stop()


## Intensidade de combate de 0 a 1 (crossfade entre as duas trilhas).
func set_combat_intensity(v: float) -> void:
	_combat_target = clampf(v, 0.0, 1.0)


func _process(delta: float) -> void:
	if not _music_on or _music_set == null:
		return
	_combat_level = move_toward(_combat_level, _combat_target, delta * _music_set.velocidade_mistura)
	var duck_target: float = _music_set.duck_pausa_db if get_tree().paused else 0.0
	_duck = move_toward(_duck, duck_target, delta * 30.0)
	_fade = move_toward(_fade, 1.0, delta / maxf(_music_set.entrada_s, 0.1))
	var extra: float = _duck + linear_to_db(maxf(_fade, 0.0001))
	if _combat_level > 0.02:
		_music_combat.volume_db = lerpf(-80.0, _music_set.combate_db, _combat_level) + extra
	else:
		_music_combat.volume_db = -80.0
	_music_calm.volume_db = lerpf(_music_set.explorar_db, _music_set.explorar_db + _music_set.explorar_queda_db, _combat_level) + extra


## Silencia tudo quando a janela/aba perde o foco e restaura ao voltar.
func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT or what == NOTIFICATION_WM_WINDOW_FOCUS_OUT:
		if not _muted_by_focus:
			_muted_by_focus = true
			AudioServer.set_bus_mute(0, true)
	elif what == NOTIFICATION_APPLICATION_FOCUS_IN or what == NOTIFICATION_WM_WINDOW_FOCUS_IN:
		if _muted_by_focus:
			_muted_by_focus = false
			AudioServer.set_bus_mute(0, false)
