"""Baut aus den geprüften Einzelclips den Audio-Sprite für die App: <out>/en.mp3 + en.json"""
import sys, os, json, subprocess, wave, tempfile
VOICE = sys.argv[1]; LANG = sys.argv[2] if len(sys.argv) > 2 else "en"
BASE = os.path.dirname(os.path.abspath(__file__))
CLIPS = os.path.join(BASE, "out_" + VOICE, "clips"); DEST = os.path.join(BASE, "out_" + VOICE)
SR = 24000; GAP = 0.3; TMP = tempfile.mkdtemp()
def ff(a): subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + a, check=True)
keys = sorted(f[:-4] for f in os.listdir(CLIPS) if f.endswith(".wav"))
index = {}; parts = []; t = GAP
sil = os.path.join(TMP, "sil.wav"); ff(["-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=mono", "-t", str(GAP), sil])
for k in keys:
    src = os.path.join(CLIPS, k + ".wav"); dst = os.path.join(TMP, k + ".wav")
    # Lautstärke angleichen, leichte Kompression, Spitzen begrenzen
    ff(["-i", src, "-af", "highpass=f=60,acompressor=threshold=-18dB:ratio=3:attack=5:release=120:makeup=2,loudnorm=I=-15:TP=-1.5:LRA=9,alimiter=limit=0.95", "-ar", str(SR), "-ac", "1", dst])
    with wave.open(dst) as w: d = w.getnframes() / w.getframerate()
    index[k] = [round(t, 4), round(d, 4)]; parts += [dst, sil]; t += d + GAP
if "s180" in index: index["n180"] = index["s180"]
lst = os.path.join(TMP, "l.txt")
with open(lst, "w") as fh:
    fh.write(f"file '{sil}'\n")
    for p in parts: fh.write(f"file '{p}'\n")
spr = os.path.join(TMP, "sprite.wav"); ff(["-f", "concat", "-safe", "0", "-i", lst, "-ar", str(SR), "-ac", "1", spr])
ff(["-i", spr, "-codec:a", "libmp3lame", "-b:a", "64k", os.path.join(DEST, LANG + ".mp3")])
json.dump(index, open(os.path.join(DEST, LANG + ".json"), "w"))
print(len(index), "Ansagen,", round(t, 1), "s")
