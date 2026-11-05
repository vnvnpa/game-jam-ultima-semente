#!/usr/bin/env python3
"""Gera os .wav de SFX e música em assets/audio/ (mesmas receitas do antigo
audio_manager.gd). Uso (raiz do projeto):  python3 tools/gen_audio.py
Substitua qualquer arquivo por outro .wav de mesmo nome sem mexer em código."""
import os, struct
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SFX_DIR = os.path.join(ROOT, "assets", "audio", "sfx")
MUS_DIR = os.path.join(ROOT, "assets", "audio", "music")
RATE = 22050
rng = np.random.default_rng(1337)


def tone(f0, f1, dur, vol, wave_t=0, attack=0.004):
    n = int(dur * RATE)
    t = np.arange(n) / n
    f = f0 + (f1 - f0) * t
    ph = np.cumsum(f / RATE)
    ph = ph - np.floor(ph)
    if wave_t == 0:
        s = np.sin(ph * 2 * np.pi)
    elif wave_t == 1:
        s = np.where(ph < .5, 1.0, -1.0)
    elif wave_t == 2:
        s = ph * 2 - 1
    else:
        s = rng.random(n) * 2 - 1
    env = (1 - t) ** 2
    atk = np.minimum(1.0, (np.arange(n) / RATE) / max(attack, 5e-4))
    return s * env * atk * vol


def cat(*p):
    return np.concatenate(p)


def mix(a, b):
    n = max(len(a), len(b))
    o = np.zeros(n)
    o[:len(a)] += a
    o[:len(b)] += b
    return o


def write(path, data, rate=RATE, loop=False):
	"""WAV 16-bit mono. Com loop=True grava um chunk 'smpl' (loop do início ao fim),
	que a Godot lê ao importar ("Detect From WAV")."""
	os.makedirs(os.path.dirname(path), exist_ok=True)
	pcm = (np.clip(data, -1, 1) * 30000).astype("<i2").tobytes()
	fmt = struct.pack("<HHIIHH", 1, 1, rate, rate * 2, 2, 16)
	chunks = b"fmt " + struct.pack("<I", len(fmt)) + fmt
	if loop:
		smpl = struct.pack("<IIIIIIIII", 0, 0, int(1e9 / rate), 60, 0, 0, 0, 1, 0) + struct.pack("<IIIIII", 0, 0, 0, len(data) - 1, 0, 0)
		chunks += b"smpl" + struct.pack("<I", len(smpl)) + smpl
	chunks += b"data" + struct.pack("<I", len(pcm)) + pcm
	with open(path, "wb") as f:
		f.write(b"RIFF" + struct.pack("<I", 4 + len(chunks)) + b"WAVE" + chunks)


SFX = {
    "shoot": tone(900, 420, .07, .16, 1), "hit": tone(300, 150, .05, .18, 3), "kill": tone(320, 110, .12, .22),
    "hurt": tone(220, 90, .18, .3, 2), "pickup": tone(660, 1000, .08, .2),
    "nucleus": cat(tone(880, 880, .1, .25), tone(1320, 1320, .1, .25), tone(1760, 1760, .25, .25)),
    "levelup": cat(tone(440, 440, .09, .22), tone(554, 554, .09, .22), tone(659, 659, .09, .22), tone(880, 880, .25, .22)),
    "pulse": mix(tone(160, 40, .4, .35), tone(400, 100, .3, .12, 3)), "dash": tone(1200, 300, .14, .14, 3),
    "click": tone(620, 560, .04, .16), "confirm": tone(500, 820, .1, .2), "error": tone(170, 150, .14, .2, 1),
    "alert": cat(tone(440, 440, .15, .22, 1), tone(330, 330, .2, .22, 1)), "o2": tone(520, 520, .12, .2),
    "boss": mix(tone(80, 45, .9, .35, 2), tone(120, 60, .9, .2, 1)), "explosion": tone(240, 40, .35, .4, 3),
    "mutation": tone(180, 520, .45, .3),
    "victory": cat(tone(523, 523, .15, .25), tone(659, 659, .15, .25), tone(784, 784, .15, .25), tone(1047, 1047, .5, .25)),
    "gameover": cat(tone(330, 330, .2, .25, 2), tone(247, 247, .2, .25, 2), tone(165, 110, .6, .25, 2)),
    "spit": tone(500, 700, .1, .15),
    # novos (usados nas próximas fases)
    "step": tone(140, 90, .05, .08, 3), "gate_open": mix(tone(90, 200, .8, .3, 2), tone(300, 120, .6, .12, 3)),
    "mechanism": cat(tone(300, 300, .08, .2, 1), tone(450, 450, .08, .2, 1), tone(600, 900, .2, .2)),
    "shield": tone(500, 900, .2, .2), "heal": cat(tone(520, 520, .08, .18), tone(780, 780, .12, .18)),
}


def pad(combat):
    sec, rate = 8.0, 8000
    n = int(sec * rate); t = np.arange(n) / rate; u = t / sec
    notes = [110.0, 130.5, 146.75, 164.75] if combat else [110.0, 130.5, 164.75, 196.0]
    s = np.zeros(n)
    for k, f in enumerate(notes):
        sw = .5 + .5 * np.sin(2 * np.pi * (u * (k + 1) + k * .25))
        s += np.sin(2 * np.pi * f * t) * (.04 + .05 * sw)
    s += np.sin(2 * np.pi * 55 * t) * .07
    if combat:
        beat = np.mod(t * 2, 1); s += np.sin(2 * np.pi * 55 * t) * .18 * np.exp(-beat * 8)
        hat = np.mod(t * 4 + .5, 1); s += np.sin(2 * np.pi * 880 * t) * .03 * np.exp(-hat * 14)
    else:
        lead = np.sin(2 * np.pi * u * 2); s += np.sin(2 * np.pi * 440 * t) * .02 * np.maximum(0, lead)
    return s, rate


def main():
    for k, v in SFX.items():
        write(os.path.join(SFX_DIR, k + ".wav"), v)
    for name, combat in (("explore_loop", False), ("combat_loop", True)):
        s, r = pad(combat); write(os.path.join(MUS_DIR, name + ".wav"), s, r, loop=True)
    print(f"OK: {len(SFX)} SFX + 2 músicas em assets/audio")


if __name__ == "__main__":
    main()
