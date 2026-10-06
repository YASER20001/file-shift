"""Assemble the final video. Usage: python3 build.py [shots|final|all] [--draft]"""
import json, os, subprocess, sys, math
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
VID = "/home/user/file-shift/videos"
SRC = {
    "D": (os.path.join(VID, "SDC - IDC Dashboard.mp4"), 22),   # (path, title-bar px to crop)
    "T": (os.path.join(VID, "SDC - IDC Tracker1.mp4"), 22),
    "P": (os.path.join(VID, "PIMx Transmittals.mp4"), 18),
}
W, H, FPS = 1920, 1080, 30
FW, FH, FX, FY = 1680, 884, 120, 98          # framed footage box
XF = 0.7                                      # transition length
DRAFT = "--draft" in sys.argv
SHOTS = os.path.join(HERE, "shots"); os.makedirs(SHOTS, exist_ok=True)
MG = os.path.join(HERE, "mg")
durs = json.load(open(os.path.join(HERE, "vo", "durations.json")))
cards = {}
for _n in os.listdir(MG):
    _d = os.path.join(MG, _n)
    if os.path.isdir(_d):
        cards[_n] = {"d": len([f for f in os.listdir(_d) if f.endswith(".png")]) / FPS}

# rounded-corner mask for framed footage
mask_path = os.path.join(HERE, "mask.png")
if not os.path.exists(mask_path):
    m = Image.new("L", (FW, FH), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, FW - 1, FH - 1], radius=20, fill=255)
    m.save(mask_path)

# ------------------------------------------------------------------ shot list
# kind: card | footage
# clips: list of (src, in, out, speed)  -> concatenated, then fitted to shot duration
# layout: framed | full (full = crop region (x,y,w,h) of source scaled to 1920x1080)
# vo: line id; pad: extra seconds after VO; overlays: list of (name, start, end, x, y)
def S(id, clips, vo=None, pad=0.6, layout="framed", crop=None, zoom=0.06, overlays=(), min_d=0, anchor="center"):
    d = max(min_d, (durs.get(vo, 0) if vo else 0) + pad)
    return dict(id=id, kind="footage", clips=clips, vo=vo, d=d, layout=layout, crop=crop, zoom=zoom, overlays=list(overlays), anchor=anchor)

def C(id, vo=None):
    return dict(id=id, kind="card", vo=vo, d=cards.get(id, {"d": 3.0})["d"], overlays=[])

LT_Y = None  # lower thirds use their own position in PNG? no -> we place at (120, 860)
shots = [
    C("intro1", "intro1"),
    C("intro2", "intro2"),
    C("title", "title"),
    S("hub1", [("D", 0.0, 1.0, 1.0)], "hub1", 0.5, overlays=[("lt_hub", 1.0, 6.5)]),
    S("hub2", [("D", 1.5, 3.0, 1.0)], "hub2", 0.5, overlays=[("lt_eth", 0.8, 8.0)]),
    C("ch1"),
    S("dash1", [("D", 20.4, 27.0, 1.0)], "dash1", 0.5, overlays=[("lt_dash", 1.0, 7.5)]),
    S("dash2", [("D", 21.0, 27.0, 1.0)], "dash2", 0.5, layout="full", crop=(440, 290, 1280, 720), zoom=0.08,
      overlays=[("co_wells", 0.6, 6.0, 1180, 26)]),
    S("dash3", [("D", 36.5, 46.0, 1.0)], "dash3", 0.5, overlays=[("lt_reg", 0.8, 6.5)]),
    S("dash4", [("D", 49.0, 57.5, 1.4), ("D", 75.5, 84.0, 1.6)], "dash4", 0.8, overlays=[("co_excel", 2.6, 5.4, 1180, 150)]),
    C("ch2"),
    S("trk1", [("T", 2.0, 21.0, 2.5)], "trk1", 0.4, overlays=[("lt_trk", 0.8, 6.0)]),
    S("trk2", [("T", 21.0, 30.0, 1.0)], "trk2", 0.4),
    S("trk3", [("T", 24.5, 30.6, 1.0)], "trk3", 0.6, layout="full", crop=(300, 150, 1600, 900), zoom=0.07,
      overlays=[("co_live", 8.5, 14.0, 1120, 120)]),
    C("ch3"),
    S("tx1", [("P", 3.6, 5.6, 1.0), ("P", 7.0, 8.6, 1.0), ("P", 9.4, 12.6, 1.4)], "tx1", 0.4, overlays=[("lt_tx", 0.8, 5.0)]),
    S("tx2", [("P", 14.6, 17.6, 1.0)], "tx2", 0.4),
    S("tx3", [("P", 21.0, 29.5, 1.0)], "tx3", 0.5, layout="full", crop=(790, 395, 1120, 630), zoom=0.05,
      overlays=[("co_ai", 1.0, 8.5, 90, 110)]),
    S("tx4", [("P", 33.0, 34.6, 1.0)], "tx4", 0.5),
    S("tx5", [("P", 36.0, 43.0, 1.2)], "tx5", 0.5),
    S("tx6", [("P", 45.5, 60.5, 1.5)], "tx6", 0.6, overlays=[("co_pw", 1.2, 8.5, 1180, 150)]),
    S("tx7", [("P", 62.8, 66.5, 1.0)], "tx7", 0.5, overlays=[("lt_wf", 0.8, 8.5)]),
    S("tx8", [("P", 71.4, 78.5, 1.0)], "tx8", 0.5, overlays=[("co_email", 3.5, 8.8, 1180, 150)]),
    S("tx9", [("P", 80.8, 86.5, 1.0)], "tx9", 0.5),
    S("tx10", [("P", 92.2, 94.6, 1.0)], "tx10", 0.5),
    S("tx11", [("P", 118.5, 127.0, 2.4)], "tx11", 0.4, overlays=[("co_sign", 0.4, 3.0, 1180, 150)]),
    S("tx12", [("P", 129.0, 132.0, 1.0)], "tx12", 0.5),
    S("tx13", [("P", 133.5, 136.4, 1.0)], "tx13", 0.6, layout="full", crop=(0, 300, 1280, 720), zoom=0.05, anchor="bottom",
      overlays=[("co_issue", 1.4, 7.0, 760, 120)]),
    S("tx14", [("P", 108.0, 111.4, 1.0)], "tx14", 0.5, overlays=[("lt_regtx", 0.8, 7.0)]),
    C("recap", "recap"),
    C("end", "end"),
]
CHAPTER_IDS = {"ch1", "ch2", "ch3", "title", "recap"}

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(" ".join(cmd)); print(r.stderr[-4000:]); sys.exit(1)

def render_footage(s):
    out = os.path.join(SHOTS, s["id"] + ".mp4")
    d = s["d"]
    # total source time after speed
    src_len = sum((o - i) / sp for _, i, o, sp in s["clips"])
    inputs, parts = [], []
    for k, (src, i, o, sp) in enumerate(s["clips"]):
        path, bar = SRC[src]
        inputs += ["-ss", f"{i:.3f}", "-t", f"{o - i:.3f}", "-i", path]
        parts.append(f"[{k}:v]crop=iw:ih-{bar}:0:{bar},setpts=PTS/{sp},fps={FPS},scale={W}:{round(W*1010/1920)}:flags=lanczos,setsar=1[v{k}]")
    n = len(s["clips"])
    cat = "".join(f"[v{k}]" for k in range(n)) + f"concat=n={n}:v=1:a=0[cat]"
    # fit: if source shorter -> clone last frame; if longer -> trim
    fit = f"[cat]tpad=stop_mode=clone:stop_duration={max(0, d - src_len) + 0.5:.3f},trim=duration={d:.3f},setpts=PTS-STARTPTS[fit]"
    z = s["zoom"]
    frames = max(1, round(d * FPS))
    if s["layout"] == "framed":
        # zoom via zoompan on 2x supersampled frame -> FWxFH
        # compose window on background, then slow push-in on the whole composite (no UI edges lost)
        z = min(z, 0.045)
        zp = (f"[fit]scale={FW}:{FH}:flags=lanczos,format=rgba[sc];[sc][{n}:v]alphamerge[fg];[{n+1}:v]scale={W}:{H}[bg];"
              f"[bg][fg]overlay={FX}:{FY}:format=auto,scale={W*2}:{H*2}:flags=lanczos,"
              f"zoompan=z='1+{z}*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},format=yuv420p[out]")
        extra = ["-loop", "1", "-i", mask_path, "-loop", "1", "-i", os.path.join(MG, "bg_frame.png")]
    else:
        cx, cy, cw, ch = s["crop"]
        # crop region in 1920x1010 space (source coords minus title bar). Shift y by title bar.
        cy = max(0, cy - SRC[s["clips"][0][0]][1])
        yexp = "ih-ih/zoom" if s.get("anchor") == "bottom" else "ih/2-(ih/zoom/2)"
        zp = (f"[fit]crop={cw}:{ch}:{cx}:{cy},scale={W*2}:{H*2}:flags=lanczos,"
              f"zoompan=z='1+{z}*on/{frames}':x='iw/2-(iw/zoom/2)':y='{yexp}':d=1:s={W}x{H}:fps={FPS},format=yuv420p[out]")
        extra = []
    fc = ";".join(parts + [cat, fit, zp])
    cmd = ["ffmpeg", "-v", "error", "-y"] + inputs + extra + ["-filter_complex", fc, "-map", "[out]",
           "-t", f"{d:.3f}", "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast" if DRAFT else "medium",
           "-crf", "20" if DRAFT else "16", "-pix_fmt", "yuv420p", out]
    run(cmd)
    return out

def render_card(s):
    out = os.path.join(SHOTS, s["id"] + ".mp4")
    run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(MG, s["id"], "f%04d.png"),
         "-t", f"{s['d']:.3f}", "-c:v", "libx264", "-preset", "veryfast" if DRAFT else "medium", "-crf", "16", "-pix_fmt", "yuv420p", out])
    return out

def build_shots(kind=None):
    for s in shots:
        if kind and s["kind"] != kind:
            continue
        p = render_card(s) if s["kind"] == "card" else render_footage(s)
        print("shot", s["id"], f"{s['d']:.2f}s")

def timeline():
    """start time of each shot in the final (xfade overlaps XF)."""
    t = 0.0; starts = []
    for i, s in enumerate(shots):
        starts.append(t)
        t += s["d"] - (XF if i < len(shots) - 1 else 0)
    return starts, t

def build_final():
    starts, total = timeline()
    print("final length", round(total, 1), "s")
    n = len(shots)
    inputs = []
    for s in shots:
        inputs += ["-i", os.path.join(SHOTS, s["id"] + ".mp4")]
    fc = []
    # ---- video: chained xfade
    trans = {"title": "fadeblack", "ch1": "slideleft", "ch2": "slideleft", "ch3": "slideleft", "recap": "fade", "end": "fadeblack"}
    prev = "[0:v]"
    off = 0.0
    for i in range(1, n):
        off += shots[i - 1]["d"] - XF
        tr = trans.get(shots[i]["id"], "fade" if shots[i - 1]["kind"] == "card" else "smoothleft" if i % 3 == 0 else "fade")
        if shots[i - 1]["kind"] == "card" and shots[i]["kind"] == "footage":
            tr = "circleopen" if shots[i-1]["id"].startswith("ch") else "fade"
        out = f"[x{i}]" if i < n - 1 else "[vx]"
        fc.append(f"{prev}[{i}:v]xfade=transition={tr}:duration={XF}:offset={off:.3f}{out}")
        prev = out
    # ---- overlays (lower thirds / callouts)
    ov_inputs = []
    cur = "[vx]"
    k = 0
    for s, st in zip(shots, starts):
        for ov in s["overlays"]:
            name, a, b = ov[0], ov[1], ov[2]
            x, y = (ov[3], ov[4]) if len(ov) > 3 else (120, 860)
            A, B = st + a, min(st + b, st + s["d"] - 0.3)
            idx = n + k
            ov_inputs += ["-loop", "1", "-framerate", str(FPS), "-i", os.path.join(MG, name + ".png")]
            # slide in 24px + fade in/out on alpha
            fc.append(f"[{idx}:v]format=rgba,trim=duration={B - A + 0.1:.3f},setpts=PTS-STARTPTS+{A:.3f}/TB,"
                      f"fade=t=in:st={A:.3f}:d=0.45:alpha=1,fade=t=out:st={B - 0.4:.3f}:d=0.4:alpha=1[o{k}]")
            xs = f"'{x}-28*max(0,1-(t-{A:.3f})/0.5)*max(0,1-(t-{A:.3f})/0.5)'" if name.startswith("lt_") else f"{x}"
            ys = f"{y}" if name.startswith("lt_") else f"'{y}+18*max(0,1-(t-{A:.3f})/0.5)*max(0,1-(t-{A:.3f})/0.5)'"
            fc.append(f"{cur}[o{k}]overlay=x={xs}:y={ys}:enable='between(t,{A:.3f},{B:.3f})':eof_action=pass[c{k}]")
            cur = f"[c{k}]"; k += 1
    fc.append(f"{cur}format=yuv420p[vout]")
    # ---- audio
    a_inputs = []; a_idx = n + k
    amix = []
    for s, st in zip(shots, starts):
        if s["vo"] and durs.get(s["vo"], 0) > 0:
            lead = 0.9 if s["kind"] == "card" else 0.35
            a_inputs += ["-i", os.path.join(HERE, "vo", s["vo"] + ".wav")]
            fc.append(f"[{a_idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,adelay={int((st + lead) * 1000)}|{int((st + lead) * 1000)}[a{a_idx}]")
            amix.append(f"[a{a_idx}]"); a_idx += 1
    fc.append("".join(amix) + f"amix=inputs={len(amix)}:normalize=0,dynaudnorm=f=250:g=15:p=0.8,alimiter=limit=0.9[vo]")
    # whoosh on chapter/title transitions, pop on callouts
    sfx = []
    for i, (s, st) in enumerate(zip(shots, starts)):
        if s["id"] in CHAPTER_IDS or s["id"] == "end":
            a_inputs += ["-i", os.path.join(HERE, "whoosh.wav")]
            fc.append(f"[{a_idx}:a]volume=0.55,adelay={int(max(0, st - 0.25) * 1000)}|{int(max(0, st - 0.25) * 1000)}[s{a_idx}]"); sfx.append(f"[s{a_idx}]"); a_idx += 1
        for ov in s["overlays"]:
            if ov[0].startswith("co_"):
                tt = st + ov[1]
                a_inputs += ["-i", os.path.join(HERE, "pop.wav")]
                fc.append(f"[{a_idx}:a]volume=0.5,adelay={int(tt * 1000)}|{int(tt * 1000)}[s{a_idx}]"); sfx.append(f"[s{a_idx}]"); a_idx += 1
    fc.append("".join(sfx) + f"amix=inputs={len(sfx)}:normalize=0[sfx]")
    a_inputs += ["-i", os.path.join(HERE, "music.wav")]
    fc.append(f"[{a_idx}:a]atrim=duration={total:.3f},afade=t=out:st={total - 4:.3f}:d=4,volume=0.9[mus0]")
    fc.append("[vo]asplit[vo1][vo2]")
    fc.append("[mus0][vo2]sidechaincompress=threshold=0.02:ratio=6:attack=80:release=600:makeup=1[mus]")
    fc.append("[mus]volume=-13dB[musq]")
    fc.append("[vo1][musq][sfx]amix=inputs=3:normalize=0:duration=first,loudnorm=I=-16:TP=-1.5:LRA=11[aout]")
    out = os.path.join(HERE, "PIMX_promo_draft.mp4" if DRAFT else "PIMX_promo.mp4")
    cmd = ["ffmpeg", "-v", "error", "-stats", "-y"] + inputs + ov_inputs + a_inputs + ["-filter_complex", ";".join(fc),
           "-map", "[vout]", "-map", "[aout]", "-t", f"{total:.3f}", "-r", str(FPS),
           "-c:v", "libx264", "-preset", "veryfast" if DRAFT else "slow", "-crf", "22" if DRAFT else "18", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
    open(os.path.join(HERE, "final_cmd.txt"), "w").write(" ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-6000:]); sys.exit(1)
    print("wrote", out)
    json.dump({s["id"]: round(st, 2) for s, st in zip(shots, starts)}, open(os.path.join(HERE, "starts.json"), "w"), indent=1)

if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "all"
    if what in ("shots", "all"):
        build_shots()
    if what in ("footage", "cards"):
        build_shots(what[:-1] if what == "cards" else what)
    if what in ("final", "all"):
        build_final()
    if what.startswith("shot:"):
        sid = what.split(":")[1]
        s = next(x for x in shots if x["id"] == sid)
        print(render_card(s) if s["kind"] == "card" else render_footage(s))
