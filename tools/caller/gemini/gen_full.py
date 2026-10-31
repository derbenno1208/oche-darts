"""Erzeugt alle Caller-Ansagen mit Gemini TTS, schneidet sie, prüft sie per Whisper und baut den Audio-Sprite.
Aufruf: ../venv/bin/python gen_full.py <voice> [lang=en]"""
import sys, os, json, re, subprocess, time, wave, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tts2 import tts2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

VOICE = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_" + VOICE)
CLIPS = os.path.join(OUT, "clips"); os.makedirs(CLIPS, exist_ok=True)
ARENA = "a professional darts match referee announcing into the microphone to a packed, roaring arena"
ST_SCORE = f"{ARENA}; loud, crisp and clear, with the classic rising arena delivery"
ST_BIG = f"{ARENA}; loud and excited, building up, stretching the last word"
ST_180 = f"{ARENA}; shouting at full volume, with a huge, long, drawn-out, rising roar on the final word that lasts about two seconds"
ST_CALM = f"{ARENA}; calm, measured and authoritative"
ST_WIN = f"{ARENA}; loud, triumphant, drawing out the last word"

def en_num(n):
    ones = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
    if n < 20: return ones[n]
    if n < 100: return tens[n // 10] + ("-" + ones[n % 10] if n % 10 else "")
    return "one hundred" + (" and " + en_num(n % 100) if n % 100 else "")

ITEMS = {}  # key -> (text, style, expected words for check)
for n in range(1, 180):
    ITEMS[f"n{n}"] = (en_num(n).capitalize() + ("!" if n >= 100 else "."), ST_BIG if n >= 100 else ST_SCORE)
ITEMS["s180"] = ("One hundred and eighty!", ST_180)
ITEMS["n180"] = ITEMS["s180"]
for k, t, s in [("noscore", "No score.", ST_SCORE), ("bust", "Bust!", ST_SCORE), ("require", "You require", ST_CALM),
                ("gameon", "Game on!", ST_WIN), ("gs_leg", "Game shot, and the leg!", ST_WIN), ("gs_set", "Game shot, and the set!", ST_WIN),
                ("gs_match", "Game shot, and the match!", ST_WIN), ("shanghai", "Shanghai!", ST_WIN), ("halved", "Halved!", ST_SCORE),
                ("gotcha", "Gotcha!", ST_WIN), ("killer", "Killer!", ST_WIN), ("out", "Out!", ST_SCORE), ("checkout", "Checkout!", ST_WIN),
                ("draw", "It's a draw!", ST_SCORE), ("next", "Next attempt.", ST_CALM), ("scram", "Change over!", ST_SCORE)]:
    ITEMS[k] = (t, s)

W2N = {}
for n in range(0, 181): W2N[re.sub(r"[^a-z]", "", en_num(n))] = n
def norm(t):
    t = t.lower().replace("-", " ")
    t = re.sub(r"[^a-z0-9 ]", "", t)
    return re.sub(r"\s+", " ", t).strip()
def matches(key, heard):
    text = ITEMS[key][0]
    h = norm(heard)
    if key.startswith("n") and key[1:].isdigit() or key == "s180":
        n = 180 if key == "s180" else int(key[1:])
        digits = re.findall(r"\d+", h)
        if digits: return len(digits) == 1 and int(digits[0]) == n
        return W2N.get(re.sub(r"[^a-z]", "", h.replace("and", "")) or "", None) == n or re.sub(r"[^a-z]", "", h) == re.sub(r"[^a-z]", "", en_num(n))
    a, b = set(norm(text).split()), set(h.split())
    return len(a & b) >= max(1, len(a) - 1)

_wm = None
def whisper(path):
    global _wm
    from faster_whisper import WhisperModel
    if _wm is None: _wm = WhisperModel("base.en", device="cpu", compute_type="int8")
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "s16le", "-ar", "16000", "-ac", "1", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    pad = np.zeros(8000, np.float32); a = np.concatenate([pad, a, pad])
    segs, _ = _wm.transcribe(a, vad_filter=False, language="en")
    return " ".join(s.text for s in segs)

def read_wav(p):
    with wave.open(p) as w: sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)
    return a, sr
def write_wav(p, a, sr):
    with wave.open(p, "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(np.clip(a, -32768, 32767).astype(np.int16).tobytes())

def split(path, k):
    """Teilt eine Aufnahme an den k-1 längsten Pausen."""
    a, sr = read_wav(path); hop = int(sr * 0.01)
    env = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a) - hop, hop)])
    thr = max(80, np.percentile(env, 95) * 0.04); quiet = env < thr
    runs = []; i = 0
    while i < len(quiet):
        if quiet[i]:
            j = i
            while j < len(quiet) and quiet[j]: j += 1
            runs.append((i, j)); i = j
        else: i += 1
    inner = [r for r in runs if r[0] > 0 and r[1] < len(quiet)]
    inner = sorted(sorted(inner, key=lambda r: r[1] - r[0], reverse=True)[:k - 1])
    if len(inner) < k - 1: return None
    cuts = [0] + [((s + e) // 2) * hop for s, e in inner] + [len(a)]
    out = []
    for s, e in zip(cuts, cuts[1:]):
        seg = a[s:e]; env2 = np.array([np.sqrt(np.mean(seg[i:i + hop] ** 2)) for i in range(0, max(1, len(seg) - hop), hop)])
        loud = np.where(env2 >= thr)[0]
        if not len(loud): return None
        s2 = max(0, loud[0] * hop - int(.04 * sr)); e2 = min(len(seg), (loud[-1] + 1) * hop + int(.12 * sr))
        out.append(seg[s2:e2])
    return out, sr

MODEL = "gemini-3.8-flash-lite-tts"

def segments(path, min_gap=0.55):
    """Zerlegt eine Aufnahme an allen Pausen ab min_gap Sekunden."""
    a, sr = read_wav(path); hop = int(sr * 0.01)
    env = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a) - hop, hop)])
    thr = max(80, np.percentile(env, 95) * 0.04); loud = env >= thr
    segs = []; i = 0; n = len(loud); gap = int(min_gap / 0.01)
    while i < n:
        if not loud[i]: i += 1; continue
        s = i; last = i
        while i < n:
            if loud[i]: last = i; i += 1
            elif i - last > gap: break
            else: i += 1
        if (last - s) * 0.01 > 0.15:
            s2 = max(0, s * hop - int(.05 * sr)); e2 = min(len(a), (last + 1) * hop + int(.15 * sr))
            segs.append(a[s2:e2])
    return segs, sr

def gen_batch(keys):
    items = [((("<long pause> " if i else "") + ITEMS[k][0]), ITEMS[k][1]) for i, k in enumerate(keys)]
    p = os.path.join(OUT, f"batch_{int(time.time())}.wav")
    tts2(items, VOICE, p, model=MODEL, retries=2)
    segs, sr = segments(p)
    print(f"  {len(segs)} Abschnitte für {len(keys)} Ansagen", flush=True)
    return assign(segs, sr, keys)

def assign(segs, sr, keys):
    """Ordnet jeden Abschnitt der passenden noch fehlenden Ansage zu (Suche über alle Schlüssel)."""
    ok = []
    for seg in segs:
        tmp = os.path.join(OUT, "seg.wav"); write_wav(tmp, seg, sr); heard = whisper(tmp)
        cand = [k for k in keys if k not in ok and k not in done_keys() and matches(k, heard)]
        if cand:
            os.replace(tmp, os.path.join(CLIPS, cand[0] + ".wav")); ok.append(cand[0])
        else:
            print(f"  ? nicht zugeordnet: '{heard.strip()}'", flush=True)
    return ok

def done_keys(): return {f[:-4] for f in os.listdir(CLIPS) if f.endswith(".wav")}

if __name__ == "__main__" and os.environ.get("REPROCESS"):
    keys = [k for k in ITEMS if k != "n180"]
    for f in sorted(x for x in os.listdir(OUT) if x.startswith("batch_")):
        segs, sr = segments(os.path.join(OUT, f)); got = assign(segs, sr, [k for k in keys if k not in done_keys()])
        print(f, "neu zugeordnet:", " ".join(got), flush=True)
    print("Stand:", len(done_keys()), "/", len(keys), flush=True); sys.exit(0)

if __name__ == "__main__":
    keys = [k for k in ITEMS if k != "n180"]
    B = int(os.environ.get("BATCH", "33")); maxcalls = int(os.environ.get("MAXCALLS", "9")); calls = 0
    while calls < maxcalls:
        todo = [k for k in keys if k not in done_keys()]
        if not todo: break
        import random; random.shuffle(todo); batch = todo[:B]
        try: ok = gen_batch(batch)
        except Exception as e:
            print("Fehler:", str(e)[:300], flush=True)
            if "per day" in str(e) or "rate limited" in str(e) or "failed" in str(e): break
            time.sleep(30); calls += 1; continue
        calls += 1
        miss = [k for k in batch if k not in ok]
        print(f"[{len(done_keys())}/{len(keys)}] Anfrage {calls}: ok {len(ok)}/{len(batch)}" + (f" · fehlt: {' '.join(miss)}" if miss else ""), flush=True)
        time.sleep(22)
    print("FERTIG, fehlend:", [k for k in keys if k not in done_keys()], flush=True)
