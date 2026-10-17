extends Node
## Autoload "AudioManager": efeitos e música gerados proceduralmente (sem
## assets de terceiros). Barras separadas Music/SFX com volumes independentes.
## Em navegadores o áudio só começa após a primeira interação do jogador;
## a Godot cuida do desbloqueio, e o jogo só toca sons após cliques/teclas.

const RATE: int = 22050
const MUSIC_RATE: int = 8000
const MUSIC_SECONDS: float = 8.0
const POOL_SIZE: int = 12

var _sfx: Dictionary = {}
var _pool: Array = []
var _last_play: Dictionary = {}
var _music_calm: AudioStreamPlayer = null
var _music_combat: AudioStreamPlayer = null
var _combat_target: float = 0.0
var _combat_level: float = 0.0
var _music_on: bool = false
var _rng: RandomNumberGenerator = RandomNumberGenerator.new()


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_rng.seed = 1337
	_ensure_bus("Music")
	_ensure_bus("SFX")
	_build_sfx()
	for i in POOL_SIZE:
		var p: AudioStreamPlayer = AudioStreamPlayer.new()
		p.bus = "SFX"
		add_child(p)
		_pool.append(p)
	_build_music()
	apply_volumes()


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


# --------------------------------------------------------- geração
func _to_wav(samples: PackedFloat32Array, rate: int, looped: bool) -> AudioStreamWAV:
	var bytes: PackedByteArray = PackedByteArray()
	bytes.resize(samples.size() * 2)
	for i in samples.size():
		var v: int = int(clampf(samples[i], -1.0, 1.0) * 30000.0)
		bytes.encode_s16(i * 2, v)
	var w: AudioStreamWAV = AudioStreamWAV.new()
	w.format = AudioStreamWAV.FORMAT_16_BITS
	w.mix_rate = rate
	w.stereo = false
	w.data = bytes
	if looped:
		w.loop_mode = AudioStreamWAV.LOOP_FORWARD
		w.loop_begin = 0
		w.loop_end = samples.size()
	return w


## Tom com varredura de frequência. wave: 0 seno, 1 quadrada, 2 serra, 3 ruído.
func _tone(f0: float, f1: float, dur: float, vol: float, wave: int = 0, attack: float = 0.004) -> PackedFloat32Array:
	var n: int = int(dur * RATE)
	var out: PackedFloat32Array = PackedFloat32Array()
	out.resize(n)
	var phase: float = 0.0
	for i in n:
		var t: float = float(i) / float(n)
		var f: float = lerpf(f0, f1, t)
		phase += f / float(RATE)
		var ph: float = phase - floorf(phase)
		var s: float = 0.0
		match wave:
			0:
				s = sin(ph * TAU)
			1:
				s = 1.0 if ph < 0.5 else -1.0
			2:
				s = ph * 2.0 - 1.0
			_:
				s = _rng.randf() * 2.0 - 1.0
		var env: float = pow(1.0 - t, 2.0)
		var atk: float = minf(1.0, (float(i) / float(RATE)) / maxf(attack, 0.0005))
		out[i] = s * env * atk * vol
	return out


func _concat(parts: Array) -> PackedFloat32Array:
	var out: PackedFloat32Array = PackedFloat32Array()
	for p in parts:
		out.append_array(p)
	return out


func _mix(a: PackedFloat32Array, b: PackedFloat32Array) -> PackedFloat32Array:
	var n: int = maxi(a.size(), b.size())
	var out: PackedFloat32Array = PackedFloat32Array()
	out.resize(n)
	for i in n:
		var va: float = a[i] if i < a.size() else 0.0
		var vb: float = b[i] if i < b.size() else 0.0
		out[i] = va + vb
	return out


func _build_sfx() -> void:
	_sfx["shoot"] = _to_wav(_tone(900.0, 420.0, 0.07, 0.16, 1), RATE, false)
	_sfx["hit"] = _to_wav(_tone(300.0, 150.0, 0.05, 0.18, 3), RATE, false)
	_sfx["kill"] = _to_wav(_tone(320.0, 110.0, 0.12, 0.22, 0), RATE, false)
	_sfx["hurt"] = _to_wav(_tone(220.0, 90.0, 0.18, 0.3, 2), RATE, false)
	_sfx["pickup"] = _to_wav(_tone(660.0, 1000.0, 0.08, 0.2, 0), RATE, false)
	_sfx["nucleus"] = _to_wav(_concat([_tone(880.0, 880.0, 0.1, 0.25), _tone(1320.0, 1320.0, 0.1, 0.25), _tone(1760.0, 1760.0, 0.25, 0.25)]), RATE, false)
	_sfx["levelup"] = _to_wav(_concat([_tone(440.0, 440.0, 0.09, 0.22), _tone(554.0, 554.0, 0.09, 0.22), _tone(659.0, 659.0, 0.09, 0.22), _tone(880.0, 880.0, 0.25, 0.22)]), RATE, false)
	_sfx["pulse"] = _to_wav(_mix(_tone(160.0, 40.0, 0.4, 0.35, 0), _tone(400.0, 100.0, 0.3, 0.12, 3)), RATE, false)
	_sfx["dash"] = _to_wav(_tone(1200.0, 300.0, 0.14, 0.14, 3), RATE, false)
	_sfx["click"] = _to_wav(_tone(620.0, 560.0, 0.04, 0.16, 0), RATE, false)
	_sfx["confirm"] = _to_wav(_tone(500.0, 820.0, 0.1, 0.2, 0), RATE, false)
	_sfx["error"] = _to_wav(_tone(170.0, 150.0, 0.14, 0.2, 1), RATE, false)
	_sfx["alert"] = _to_wav(_concat([_tone(440.0, 440.0, 0.15, 0.22, 1), _tone(330.0, 330.0, 0.2, 0.22, 1)]), RATE, false)
	_sfx["o2"] = _to_wav(_tone(520.0, 520.0, 0.12, 0.2, 0), RATE, false)
	_sfx["boss"] = _to_wav(_mix(_tone(80.0, 45.0, 0.9, 0.35, 2), _tone(120.0, 60.0, 0.9, 0.2, 1)), RATE, false)
	_sfx["explosion"] = _to_wav(_tone(240.0, 40.0, 0.35, 0.4, 3), RATE, false)
	_sfx["mutation"] = _to_wav(_tone(180.0, 520.0, 0.45, 0.3, 0), RATE, false)
	_sfx["victory"] = _to_wav(_concat([_tone(523.0, 523.0, 0.15, 0.25), _tone(659.0, 659.0, 0.15, 0.25), _tone(784.0, 784.0, 0.15, 0.25), _tone(1047.0, 1047.0, 0.5, 0.25)]), RATE, false)
	_sfx["gameover"] = _to_wav(_concat([_tone(330.0, 330.0, 0.2, 0.25, 2), _tone(247.0, 247.0, 0.2, 0.25, 2), _tone(165.0, 110.0, 0.6, 0.25, 2)]), RATE, false)
	_sfx["spit"] = _to_wav(_tone(500.0, 700.0, 0.1, 0.15, 0), RATE, false)


## Trilha ambiente em loop perfeito: todas as frequências completam ciclos
## inteiros nos 8 s do loop (múltiplos de 1/8 Hz).
func _make_pad(combat: bool) -> AudioStreamWAV:
	var n: int = int(MUSIC_SECONDS * float(MUSIC_RATE))
	var out: PackedFloat32Array = PackedFloat32Array()
	out.resize(n)
	var notes: Array = [110.0, 130.5, 164.75, 196.0]
	if combat:
		notes = [110.0, 130.5, 146.75, 164.75]
	for i in n:
		var t: float = float(i) / float(MUSIC_RATE)
		var u: float = t / MUSIC_SECONDS
		var s: float = 0.0
		for k in notes.size():
			var f: float = float(notes[k])
			var swell: float = 0.5 + 0.5 * sin(TAU * (u * float(k + 1) + float(k) * 0.25))
			s += sin(TAU * f * t) * (0.04 + 0.05 * swell)
		s += sin(TAU * 55.0 * t) * 0.07
		if combat:
			var beat: float = fmod(t * 2.0, 1.0)
			s += sin(TAU * 55.0 * t) * 0.18 * exp(-beat * 8.0)
			var hat: float = fmod(t * 4.0 + 0.5, 1.0)
			s += sin(TAU * 880.0 * t) * 0.03 * exp(-hat * 14.0)
		else:
			var lead: float = sin(TAU * 1.0 * u * 2.0)
			s += sin(TAU * 440.0 * t) * 0.02 * maxf(0.0, lead)
		out[i] = s
	return _to_wav(out, MUSIC_RATE, true)


func _build_music() -> void:
	_music_calm = AudioStreamPlayer.new()
	_music_calm.bus = "Music"
	_music_calm.stream = _make_pad(false)
	_music_calm.volume_db = -6.0
	add_child(_music_calm)
	_music_combat = AudioStreamPlayer.new()
	_music_combat.bus = "Music"
	_music_combat.stream = _make_pad(true)
	_music_combat.volume_db = -80.0
	add_child(_music_combat)


# ------------------------------------------------------------- API
func play_sfx(sfx_name: String, pitch: float = 1.0, volume_db: float = 0.0) -> void:
	var stream: AudioStream = _sfx.get(sfx_name)
	if stream == null:
		return
	var now: int = Time.get_ticks_msec()
	var last: int = int(_last_play.get(sfx_name, -1000))
	if now - last < 35:
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
	chosen.stream = stream
	chosen.pitch_scale = clampf(pitch, 0.5, 2.0)
	chosen.volume_db = volume_db
	chosen.play()


func start_music() -> void:
	if _music_on:
		return
	_music_on = true
	_music_calm.play()
	_music_combat.play()


func stop_music() -> void:
	_music_on = false
	_music_calm.stop()
	_music_combat.stop()


## Intensidade de combate de 0 a 1 (mistura entre as duas camadas).
func set_combat_intensity(v: float) -> void:
	_combat_target = clampf(v, 0.0, 1.0)


func _process(delta: float) -> void:
	_combat_level = move_toward(_combat_level, _combat_target, delta * 0.4)
	if _music_on:
		_music_combat.volume_db = lerpf(-80.0, -9.0, _combat_level) if _combat_level > 0.02 else -80.0
		_music_calm.volume_db = lerpf(-6.0, -16.0, _combat_level)
