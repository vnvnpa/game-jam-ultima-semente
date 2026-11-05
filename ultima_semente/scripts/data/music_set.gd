class_name MusicSet
extends Resource
## Trilhas e mistura da música (data/audio/music_set.tres).

@export var explorar: AudioStream
@export var combate: AudioStream
@export var explorar_db: float = -6.0
@export var combate_db: float = -9.0
## Quanto a trilha calma abaixa (dB) quando o combate está no máximo.
@export var explorar_queda_db: float = -10.0
## Redução da música enquanto o jogo está pausado.
@export var duck_pausa_db: float = -9.0
## Duração da entrada gradual ao iniciar a música (s).
@export var entrada_s: float = 1.5
## Velocidade do crossfade explorar <-> combate (unidades de intensidade por s).
@export var velocidade_mistura: float = 0.4
