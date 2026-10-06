"""Procedural ambient/corporate music bed + whoosh SFX (numpy only)."""
import os, sys
import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
LENGTH = float(sys.argv[1]) if len(sys.argv) > 1 else 200.0
BPM = 96
BEAT = 60 / BPM
rng = np.random.default_rng(7)


def note(n):  # midi -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)


def env_adsr(n, a, d, s, r, total):
    t = np.arange(n) / SR
    e = np.ones(n) * s
    e[t < a] = t[t < a] / a
    m = (t >= a) & (t < a + d)
    e[m] = 1 - (1 - s) * (t[m] - a) / d
    rel = t > total - r
    e[rel] *= np.clip((total - t[rel]) / r, 0, 1)
    return e


def lowpass(x, cutoff):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x))


def reverb(x, secs=2.2, mix=0.35):
    n = int(secs * SR)
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / (SR * secs / 4))
    ir = lowpass(ir, 4000)
    ir /= np.sqrt((ir ** 2).sum())
    wet = np.fft.irfft(np.fft.rfft(x, len(x) + n) * np.fft.rfft(ir, len(x) + n))[: len(x)]
    return x * (1 - mix) + wet * mix


# chord progression (D minor): Dm9 - Bbmaj7 - F(add9) - C(add9)/E
chords = [
    [50, 57, 60, 64, 69],   # D F A C E
    [46, 53, 57, 60, 65],   # Bb D F A C
    [41, 48, 53, 57, 60],   # F C F A C? -> F A C G
    [40, 48, 55, 60, 62],   # E (bass) C G C D
]
chords[2] = [41, 48, 53, 57, 67]
bar = BEAT * 4
chord_len = bar * 2
N = int(LENGTH * SR)
pad = np.zeros(N)
bass = np.zeros(N)
pluck = np.zeros(N)
perc = np.zeros(N)

t_chord = 0.0
ci = 0
while t_chord < LENGTH:
    ch = chords[ci % len(chords)]
    n0 = int(t_chord * SR)
    n1 = min(N, int((t_chord + chord_len) * SR))
    n = n1 - n0
    if n <= 0:
        break
    tt = np.arange(n) / SR
    e = env_adsr(n, 1.2, 0.5, 0.8, 1.5, chord_len)
    seg = np.zeros(n)
    for midi in ch[1:]:
        f = note(midi)
        for det in (-0.4, 0.3):
            fd = f * 2 ** (det / 1200)
            # soft saw via few harmonics
            s = sum(np.sin(2 * np.pi * fd * k * tt + rng.uniform(0, 6.28)) / k for k in range(1, 6))
            seg += s
    seg = lowpass(seg * e, 1800) * 0.06
    pad[n0:n1] += seg
    # bass (sine + bit of 2nd harmonic), pulsing on beats 1 and 3
    fb = note(ch[0] - 12)
    b = (np.sin(2 * np.pi * fb * tt) + 0.3 * np.sin(2 * np.pi * fb * 2 * tt))
    pulse = np.ones(n)
    for k in range(int(chord_len / (BEAT * 2)) + 1):
        st = int(k * BEAT * 2 * SR)
        if st < n:
            L = min(n - st, int(BEAT * 1.6 * SR))
            pulse[st:st + L] = np.linspace(1, 0.35, L)
    bass[n0:n1] += b * e * pulse * 0.12
    # plucks: arpeggio on 8ths, random subset
    for k in range(int(chord_len / (BEAT / 2))):
        if rng.random() < 0.45:
            st = n0 + int(k * BEAT / 2 * SR)
            midi = ch[1 + (k * 3) % 4] + 12 * rng.integers(0, 2)
            f = note(midi)
            L = int(1.2 * SR)
            if st + L > N:
                L = N - st
            if L <= 0:
                continue
            ttp = np.arange(L) / SR
            p = (np.sin(2 * np.pi * f * ttp) + 0.4 * np.sin(2 * np.pi * 2 * f * ttp) * np.exp(-ttp * 9)) * np.exp(-ttp * 3.2)
            pluck[st:st + L] += p * 0.07
    t_chord += chord_len
    ci += 1

# percussion: soft kick on 1 & 3, hat ticks on 8ths (very quiet)
nb = int(LENGTH / BEAT)
for b in range(nb):
    st = int(b * BEAT * SR)
    if b % 2 == 0:
        L = int(0.25 * SR)
        tt = np.arange(L) / SR
        kick = np.sin(2 * np.pi * (50 + 80 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 14)
        perc[st:st + L] += kick[: max(0, min(L, N - st))] * 0.35 if st < N else 0
    for h in (0, 0.5):
        s2 = int((b + h) * BEAT * SR)
        L = int(0.05 * SR)
        if s2 + L < N:
            hat = rng.standard_normal(L) * np.exp(-np.arange(L) / (SR * 0.012))
            hat = hat - lowpass(hat, 6000)
            perc[s2:s2 + L] += hat * (0.05 if h == 0 else 0.035)

mix = reverb(pad + pluck, 2.4, 0.4) + bass + reverb(perc, 0.6, 0.15)
mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.7
# gentle intro/outro
fade = int(2.0 * SR)
mix[:fade] *= np.linspace(0, 1, fade)
mix[-fade:] *= np.linspace(1, 0, fade)
stereo = np.stack([mix, np.roll(mix, int(0.0004 * SR))], axis=1)
sf.write(os.path.join(HERE, "music.wav"), stereo, SR)
print("music", LENGTH, "s")

# ---- whoosh SFX ----
L = int(1.1 * SR)
tt = np.arange(L) / SR
noise = rng.standard_normal(L)
env = np.exp(-((tt - 0.55) / 0.22) ** 2)
w = noise * env
# sweep: filter in chunks with rising then falling cutoff
out = np.zeros(L)
chunk = 2048
for i in range(0, L, chunk):
    seg = w[i:i + chunk]
    c = 300 + 3500 * np.sin(np.pi * min(1, i / L))
    out[i:i + chunk] = lowpass(seg, c) - lowpass(seg, c * 0.15)
out = out / (np.max(np.abs(out)) + 1e-9) * 0.5
sf.write(os.path.join(HERE, "whoosh.wav"), np.stack([out, out], 1), SR)

# ---- soft "pop" for callouts ----
L = int(0.35 * SR)
tt = np.arange(L) / SR
pop = np.sin(2 * np.pi * (900 - 400 * tt) * tt) * np.exp(-tt * 22)
pop = pop / np.max(np.abs(pop)) * 0.35
sf.write(os.path.join(HERE, "pop.wav"), np.stack([pop, pop], 1), SR)
print("sfx done")
