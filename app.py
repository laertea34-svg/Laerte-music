from flask import Flask, request, jsonify, render_template_string
import requests, os
from yt_dlp import YoutubeDL
app = Flask(__name__)

HTML = """<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Laerte Music</title><style>body{background:#000;color:#fff;font-family:Arial;margin:0;padding:15px;padding-bottom:140px}input{width:68%;padding:14px;border-radius:25px;border:none;background:#222;color:#fff}button{padding:14px 18px;border-radius:25px;border:none;background:#1DB954;color:#fff;font-weight:bold}.card{display:flex;align-items:center;background:#181818;margin:10px 0;padding:10px;border-radius:10px}.card img{width:55px;height:55px;border-radius:5px;margin-right:10px}#playerBox{position:fixed;bottom:0;left:0;right:0;background:#181818;padding:12px;border-top:1px solid #333;display:none}audio{width:100%;margin-top:8px}</style></head><body><h2>🎵 Laerte Music</h2><div style="display:flex;gap:8px"><input id="q" value="Felipe Rodrigues"><button onclick="buscar()">Buscar</button></div><div id="lista"></div><div id="playerBox"><div style="display:flex;align-items:center;gap:10px"><img id="capa" style="width:50px;height:50px;border-radius:5px"><div><b id="titulo">-</b><br><small id="artista">-</small><br><small id="status" style="color:#1DB954"></small></div></div><audio id="audio" controls playsinline></audio></div><script>let musicas=[],atual=0;async function buscar(){document.getElementById('lista').innerHTML='Buscando...';let q=document.getElementById('q').value;let r=await fetch('/search?q='+encodeURIComponent(q));musicas=await r.json();let h='';musicas.forEach((m,i)=>{h+=`<div class="card" onclick="tocar(${i})"><img src="${m.thumb}"><div><b>${m.title}</b><br><small>${m.artist}</small></div></div>`});document.getElementById('lista').innerHTML=h||'Nada encontrado'}async function tocar(i){atual=i;let m=musicas[i];document.getElementById('playerBox').style.display='block';document.getElementById('capa').src=m.thumb;document.getElementById('titulo').innerText=m.title;document.getElementById('artista').innerText=m.artist;document.getElementById('status').innerText='Carregando...';let audio=document.getElementById('audio');audio.pause();try{let r=await fetch('/play?url='+encodeURIComponent(m.id));let d=await r.json();if(d.error){document.getElementById('status').innerText=d.error;return}audio.src=d.audio;await audio.play();document.getElementById('status').innerText='Tocando 🎶'}catch(e){document.getElementById('status').innerText='Erro'}}buscar()</script></body></html>"""

@app.route('/')
def index(): return render_template_string(HTML)

@app.route('/search')
def search():
    q=request.args.get('q')
    try:
        ydl_opts={'quiet':True,'extract_flat':True,'skip_download':True,'extractor_args':{'youtube':{'player_client':['android']}}}
        with YoutubeDL(ydl_opts) as ydl:
            info=ydl.extract_info(f"ytsearch10:{q}",download=False)
            res=[]
            for e in info.get('entries',[]):
                if not e: continue
                thumb=f"https://i.ytimg.com/vi/{e.get('id')}/mqdefault.jpg"
                if e.get('thumbnails'):
                    try: thumb=e['thumbnails'][-1]['url']
                    except: pass
                res.append({'id':e.get('id'),'title':e.get('title'),'artist':e.get('uploader') or 'YouTube','thumb':thumb})
            return jsonify(res)
    except Exception as e:
        return jsonify([])

@app.route('/play')
def play():
    vid=request.args.get('url')
    # 1 - Tenta Cobalt (nunca da bot)
    for api in ["https://api.cobalt.tools","https://co.wuk.sh/api/json"]:
        try:
            r=requests.post(api, json={"url":f"https://www.youtube.com/watch?v={vid}","isAudioOnly":True,"aFormat":"mp3"}, headers={"Accept":"application/json","Content-Type":"application/json"}, timeout=12)
            j=r.json()
            if j.get('url'): return jsonify({'audio': j.get('url')})
        except: continue
    # 2 - Tenta Piped como backup
    try:
        r=requests.get(f"https://pipedapi.kavin.rocks/streams/{vid}",timeout=10)
        j=r.json()
        if j.get('audioStreams'):
            best=sorted(j['audioStreams'], key=lambda x: x.get('bitrate',0), reverse=True)[0]
            return jsonify({'audio': best['url']})
    except: pass
    return jsonify({'error':'Tente outra musica'})

if __name__=='__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT',5000)))
