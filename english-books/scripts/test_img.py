import os,sys,json,base64,urllib.request
key=os.environ['GEMINI_API_KEY']
model,prompt,out=sys.argv[1:4]
body={"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"responseModalities":["IMAGE"],"imageConfig":{"aspectRatio":sys.argv[4] if len(sys.argv)>4 else "1:1"}}}
req=urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",data=json.dumps(body).encode(),headers={"Content-Type":"application/json"})
d=json.load(urllib.request.urlopen(req,timeout=180))
for p in d['candidates'][0]['content']['parts']:
    if 'inlineData' in p: open(out,'wb').write(base64.b64decode(p['inlineData']['data'])); print('ok',out)
