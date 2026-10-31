import sys,subprocess,numpy as np
from faster_whisper import WhisperModel
m=WhisperModel("base.en",device="cpu",compute_type="int8")
def load(f):
    raw=subprocess.run(["ffmpeg","-loglevel","error","-i",f,"-f","s16le","-ar","16000","-ac","1","-"],capture_output=True,check=True).stdout
    return np.frombuffer(raw,np.int16).astype(np.float32)/32768
def tr(f):
    segs,_=m.transcribe(load(f),vad_filter=False);return list(segs)
if __name__=="__main__":
    for f in sys.argv[1:]:
        print("==",f.split('/')[-1]);[print(f"  {s.start:5.1f}-{s.end:5.1f} {s.text}") for s in tr(f)]
