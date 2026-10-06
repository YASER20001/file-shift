import json, os, sys
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro
from script import LINES, VOICE, SPEED

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "vo")
os.makedirs(OUT, exist_ok=True)
k = Kokoro(os.path.join(HERE, "..", "models", "kokoro-v1.0.onnx"),
           os.path.join(HERE, "..", "models", "voices-v1.0.bin"))

durs = {}
for lid, text in LINES:
    path = os.path.join(OUT, f"{lid}.wav")
    if not text:
        durs[lid] = 0.0
        continue
    s, sr = k.create(text, voice=VOICE, speed=SPEED, lang="en-us")
    # trim leading/trailing silence (< -45 dBFS)
    thr = 10 ** (-45 / 20)
    idx = np.where(np.abs(s) > thr)[0]
    if len(idx):
        s = s[max(0, idx[0] - int(0.05 * sr)): min(len(s), idx[-1] + int(0.15 * sr))]
    sf.write(path, s, sr)
    durs[lid] = round(len(s) / sr, 3)
    print(f"{lid:8s} {durs[lid]:6.2f}s  {text[:60]}")

json.dump(durs, open(os.path.join(OUT, "durations.json"), "w"), indent=1)
print("total VO", round(sum(durs.values()), 1), "s")
