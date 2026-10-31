"""Erzeugt die Profi-Caller-Ansagen für Oche Darts mit Piper (offline, neuronal).
Ausgabe: out/<lang>.mp3 (Audio-Sprite) + out/<lang>.json (Startzeit/Dauer je Ansage)."""
import json, os, subprocess, sys, wave, tempfile
from piper import PiperVoice, SynthesisConfig

HERE = os.path.dirname(os.path.abspath(__file__))
M = lambda n: os.path.join(HERE, "models", n + ".onnx")
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
TMP = tempfile.mkdtemp()
SR = 22050

def en_num(n):
    ones = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
    if n < 20: return ones[n]
    if n < 100: return tens[n // 10] + ("-" + ones[n % 10] if n % 10 else "")
    return "one hundred" + (" and " + en_num(n % 100) if n % 100 else "")

def de_num(n):
    o = "null eins zwei drei vier fünf sechs sieben acht neun zehn elf zwölf dreizehn vierzehn fünfzehn sechzehn siebzehn achtzehn neunzehn".split()
    t = ["", "", "zwanzig", "dreißig", "vierzig", "fünfzig", "sechzig", "siebzig", "achtzig", "neunzig"]
    if n < 20: return o[n]
    if n < 100: return (("ein" if n % 10 == 1 else o[n % 10]) + "und" if n % 10 else "") + t[n // 10]
    return "hundert" + (de_num(n % 100) if n % 100 else "")

voices = {}
def voice(name):
    if name not in voices: voices[name] = PiperVoice.load(M(name))
    return voices[name]

def synth(model, text, path, length=1.0, speaker=None, noise=0.6, noise_w=0.7):
    v = voice(model)
    cfg = SynthesisConfig(length_scale=length, noise_scale=noise, noise_w_scale=noise_w, speaker_id=speaker)
    with wave.open(path, "wb") as w:
        v.synthesize_wav(text, w, syn_config=cfg)

def ff(args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + args, check=True)

# Hall-Klang wie in einer Arena, kräftig komprimiert
ARENA = "highpass=f=90,acompressor=threshold=-20dB:ratio=5:attack=4:release=90:makeup=3,aecho=0.85:0.55:45|85:0.10|0.06,alimiter=limit=0.95"

def fx(src, dst, pitch=1.0, gain_db=0.0, chain=ARENA):
    f = []
    if pitch != 1.0:
        f.append(f"asetrate={int(SR*pitch)},aresample={SR},atempo={1/pitch:.5f}")
    f.append(chain)
    if gain_db: f.append(f"volume={gain_db}dB")
    f.append("silenceremove=start_periods=1:start_threshold=-45dB:stop_periods=-1:stop_threshold=-45dB:stop_duration=0.25")
    ff(["-i", src, "-af", ",".join(f), "-ar", str(SR), "-ac", "1", dst])

def concat(parts, dst, gap=0.06):
    lst = os.path.join(TMP, "l.txt")
    sil = os.path.join(TMP, f"sil{gap}.wav")
    ff(["-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=mono", "-t", str(gap), sil])
    with open(lst, "w") as fh:
        for i, p in enumerate(parts):
            if i: fh.write(f"file '{sil}'\n")
            fh.write(f"file '{p}'\n")
    ff(["-f", "concat", "-safe", "0", "-i", lst, "-ar", str(SR), "-ac", "1", dst])

def clip(lang, key, model, text, length=1.0, pitch=1.0, speaker=None, gain=0.0):
    raw = os.path.join(TMP, f"{lang}_{key}_raw.wav")
    out = os.path.join(TMP, f"{lang}_{key}.wav")
    synth(model, text, raw, length=length, speaker=speaker)
    fx(raw, out, pitch=pitch, gain_db=gain)
    return out

def build(lang):
    if lang == "en":
        V = "en_GB-northern_english_male-medium"; num = en_num
        P = dict(model=V)
        clips = {}
        for n in range(1, 181):
            if n == 180: continue
            clips[f"n{n}"] = clip(lang, f"n{n}", V, num(n) + ("!" if n >= 100 else "."), length=1.12 if n >= 100 else 1.05, pitch=1.04 if n >= 100 else 1.0)
        a = clip(lang, "s180a", V, "One hundred and", length=1.15, pitch=1.03)
        b = clip(lang, "s180b", V, "eighty!", length=2.9, pitch=1.22, gain=3)
        s = os.path.join(TMP, "en_s180.wav"); concat([a, b], s, gap=0.08); clips["s180"] = s
        clips["n180"] = s
        phrases = {
            "noscore": ("No score.", 1.1, 1.0), "bust": ("Bust!", 1.15, 1.03), "require": ("You require", 1.08, 1.0),
            "gameon": ("Game on!", 1.25, 1.06), "gs_leg": ("Game shot, and the leg!", 1.12, 1.06),
            "gs_match": ("Game shot, and the match!", 1.18, 1.08), "gs_set": ("Game shot, and the set!", 1.15, 1.07),
            "shanghai": ("Shanghai!", 1.3, 1.08), "halved": ("Halved!", 1.15, 1.03), "gotcha": ("Gotcha!", 1.15, 1.05),
            "killer": ("Killer!", 1.2, 1.05), "out": ("Out!", 1.1, 1.0), "checkout": ("Checkout!", 1.15, 1.05),
            "draw": ("It's a draw!", 1.1, 1.0), "next": ("Next attempt.", 1.05, 1.0), "scram": ("Change over!", 1.1, 1.03),
        }
    else:
        V = "de_DE-thorsten-high"; E = "de_DE-thorsten_emotional-medium"; num = de_num
        clips = {}
        for n in range(1, 181):
            if n == 180: continue
            clips[f"n{n}"] = clip(lang, f"n{n}", V, num(n) + ("!" if n >= 100 else "."), length=1.05 if n >= 100 else 1.0, pitch=1.03 if n >= 100 else 1.0)
        a = clip(lang, "s180a", V, "Hundert", length=1.15, pitch=1.03)
        b = clip(lang, "s180b", E, "achtzig!", length=2.7, pitch=1.18, speaker=6, gain=3)
        s = os.path.join(TMP, "de_s180.wav"); concat([a, b], s, gap=0.08); clips["s180"] = s
        clips["n180"] = s
        phrases = {
            "noscore": ("Kein Skor.", 1.05, 1.0), "bust": ("Überworfen!", 1.1, 1.02), "require": ("Du brauchst", 1.05, 1.0),
            "gameon": ("Gehm onn!", 1.2, 1.05), "gs_leg": ("Gehm schott, und das Leg!", 1.08, 1.05),
            "gs_match": ("Gehm schott, und das Match!", 1.12, 1.06), "gs_set": ("Gehm schott, und das Set!", 1.1, 1.05),
            "shanghai": ("Schanghai!", 1.25, 1.06), "halved": ("Halbiert!", 1.1, 1.02), "gotcha": ("Erwischt!", 1.1, 1.04),
            "killer": ("Killer!", 1.15, 1.04), "out": ("Raus!", 1.1, 1.0), "checkout": ("Tschekaut!", 1.1, 1.04),
            "draw": ("Unentschieden!", 1.05, 1.0), "next": ("Nächster Versuch.", 1.0, 1.0), "scram": ("Seitenwechsel!", 1.08, 1.02),
        }
    for k, (t, l, p) in phrases.items():
        clips[k] = clip(lang, k, V, t, length=l, pitch=p)
    # Sprite zusammensetzen: jede Ansage mit 0,3 s Stille dazwischen
    order = sorted(clips.keys(), key=lambda k: (not k.startswith("n"), int(k[1:]) if k[1:].isdigit() and k.startswith("n") else 0, k))
    gap = 0.3; t = gap; index = {}; parts = []
    for k in order:
        with wave.open(clips[k]) as w: d = w.getnframes() / w.getframerate()
        index[k] = [round(t, 4), round(d, 4)]; parts.append(clips[k]); t += d + gap
    sprite = os.path.join(TMP, f"{lang}_sprite.wav")
    concat(parts, sprite, gap=gap)
    # führende Stille ergänzen, damit die Zeiten stimmen
    lead = os.path.join(TMP, f"{lang}_lead.wav")
    ff(["-f", "lavfi", "-t", str(gap), "-i", f"anullsrc=r={SR}:cl=mono", "-i", sprite, "-filter_complex", "[0][1]concat=n=2:v=0:a=1", lead])
    ff(["-i", lead, "-codec:a", "libmp3lame", "-b:a", "48k", "-ar", str(SR), "-ac", "1", os.path.join(OUT, f"{lang}.mp3")])
    json.dump(index, open(os.path.join(OUT, f"{lang}.json"), "w"))
    print(lang, len(index), "clips", round(t, 1), "s")

for lang in sys.argv[1:] or ["en", "de"]:
    build(lang)
