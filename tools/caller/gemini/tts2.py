import json,base64,subprocess,sys,urllib.request,urllib.error,time,os
KEY=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'.key')).read().strip()
def tts2(items,voice,out,model="gemini-3.8-flash-tts",retries=6):
    """items: [(text, style)]"""
    body={"model":model,"input":[{"type":"user_input","content":[{"type":"text","text":t,"annotations":[{"type":"speech_metadata","style":s}]} for t,s in items]}],
          "response_format":{"type":"audio"},"generation_config":{"speech_config":[{"voice":voice}]}}
    for a in range(retries):
        req=urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/interactions",data=json.dumps(body).encode(),headers={"Content-Type":"application/json","x-goog-api-key":KEY})
        try:
            d=json.load(urllib.request.urlopen(req,timeout=240))
        except urllib.error.HTTPError as e:
            msg=e.read().decode();print("HTTP",e.code,msg[:400].replace("\n"," "),file=sys.stderr,flush=True)
            if e.code in (429,500,503): time.sleep(35*(a+1));continue
            raise
        auds=[c for st in d.get("steps",[]) if st.get("type")=="model_output" for c in st.get("content",[]) if c.get("type")=="audio"]
        if not auds: print("no audio",json.dumps(d)[:300],file=sys.stderr);time.sleep(10);continue
        a0=auds[-1];raw=base64.b64decode(a0["data"]);mime=a0.get("mime_type") or a0.get("mimeType") or ""
        tmp=out+".raw"
        open(tmp,"wb").write(raw)
        if raw[:4]==b"RIFF": os.replace(tmp,out)
        else:
            rate=int(mime.split("rate=")[1].split(";")[0]) if "rate=" in mime else 24000
            subprocess.run(["ffmpeg","-y","-loglevel","error","-f","s16le","-ar",str(rate),"-ac","1","-i",tmp,out],check=True);os.remove(tmp)
        return out
    raise RuntimeError("failed")
