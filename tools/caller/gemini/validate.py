import os,sys
sys.argv=[sys.argv[0],"en-gb-concierge-10"]
import gen_full as G
bad=[]
for f in sorted(os.listdir(G.CLIPS)):
    k=f[:-4];h=G.whisper(os.path.join(G.CLIPS,f))
    if not G.matches(k,h): bad.append((k,h.strip())); os.remove(os.path.join(G.CLIPS,f))
print("entfernt:",bad);print("Stand:",len(G.done_keys()))
