# PIMX promo video — production pipeline

Everything that built `PIMX_promo.mp4` from the three screen recordings in `../videos/`.

| File | What it does |
|---|---|
| `script.py` | The narration, one line per shot. Edit this to change what the narrator says. |
| `vo.py` | Generates the voice-over with Kokoro (offline TTS). Writes `vo/*.wav` + `vo/durations.json`. |
| `music.py` | Synthesises the ambient music bed, the whoosh and the callout "pop" (numpy only). |
| `mg.js` | Renders the title cards, chapter cards, lower thirds and callout chips (HTML/CSS → PNG via Playwright). |
| `build.py` | The edit: shot list (source timecodes, speed, framing, overlays), ffmpeg assembly, audio mix. |

Shot timing is driven by the narration: each shot lasts as long as its voice line plus a small pad,
and the footage is sped up / held to fit.

## Rebuild
```
pip install kokoro-onnx soundfile numpy pillow      # + ffmpeg, node + playwright
# models: kokoro-v1.0.onnx + voices-v1.0.bin from github.com/thewh1teagle/kokoro-onnx releases → ../models/
python3 vo.py && python3 music.py 210 && node mg.js && python3 build.py all
```
