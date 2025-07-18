
#!/usr/bin/env python3
# txt2wav.py – conversor texto → WAV
# Autor: ChatGPT   |   Licença: MIT
# -----------------------------------------------------

import math
import wave
import struct
from pathlib import Path
import sys

# ---------- parâmetros de áudio ----------
SAMPLE_RATE   = 44_100        # Hz
BITS_PER_SAMP = 16            # 16‑bit PCM
VOLUME        = 0.4           # 0.0–1.0
DUR_SEC       = 0.30          # duração de cada símbolo
PAUSE_SEC     = 0.05          # pausa entre símbolos

# ---------- tabelas de notas ----------
ACORDES = {
    '0': [60, 64, 67],  '1': [62, 65, 69],  '2': [64, 67, 71],
    '3': [65, 69, 72],  '4': [67, 71, 74],  '5': [69, 72, 76],
    '6': [71, 74, 77],  '7': [72, 76, 79],  '8': [74, 77, 81],
    '9': [76, 79, 83]
}
NOTAS = {
    'A': 69, 'B': 71, 'C': 60, 'D': 62,
    'E': 64, 'F': 65, 'G': 67, 'H': 70
}

def midi_to_freq(midi_note: int) -> float:
    """Converte nota MIDI para frequência (Hz)."""
    return 440.0 * (2 ** ((midi_note - 69) / 12))

def gerar_frames(notas, dur_s):
    """Devolve bytes PCM para uma lista de notas (podem ser acorde ou nota única)."""
    n_samp = int(dur_s * SAMPLE_RATE)
    frames = bytearray()
    for i in range(n_samp):
        t = i / SAMPLE_RATE
        # soma das ondas seno; normaliza pela quantidade de notas
        sample = sum(math.sin(2*math.pi*midi_to_freq(n)*t) for n in notas) / len(notas)
        sample *= VOLUME
        max_int = (2**(BITS_PER_SAMP-1)) - 1
        frames += struct.pack('<h', int(sample * max_int))
    return frames

def txt_para_wav(txt_path: Path):
    txt = txt_path.read_text(encoding='utf-8').upper()
    wav_path = txt_path.with_suffix('.wav')

    # prepara ficheiro WAV
    with wave.open(str(wav_path), 'w') as wav:
        wav.setnchannels(1)              # mono
        wav.setsampwidth(BITS_PER_SAMP // 8)
        wav.setframerate(SAMPLE_RATE)

        pause_frames = gerar_frames([NOTAS['C']], 0)  # placeholder
        pause_frames = struct.pack('<h', 0) * int(PAUSE_SEC * SAMPLE_RATE)

        for ch in txt:
            if ch in ACORDES:
                wav.writeframes(gerar_frames(ACORDES[ch], DUR_SEC))
                wav.writeframes(pause_frames)
            elif ch in NOTAS:
                wav.writeframes(gerar_frames([NOTAS[ch]], DUR_SEC))
                wav.writeframes(pause_frames)
            else:
                continue  # ignora caracteres não mapeados

    print(f'✅  WAV criado: {wav_path.resolve()}')

# ---------- execução ----------
if __name__ == '__main__':
    try:
        nome = input('\033c\033[43;30m\nNome do ficheiro de texto a converter: ').strip('"').strip()
        if not nome:
            raise ValueError('Nome vazio.')
        txt_para_wav(Path(nome))
    except KeyboardInterrupt:
        sys.exit('\nCancelado pelo utilizador.')
    except Exception as e:
        sys.exit(f'Erro: {e}')
