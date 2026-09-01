from flask import Flask, request, jsonify, render_template_string
import requests, os
from yt_dlp import YoutubeDL
app = Flask(__name__)

HTML = """<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Laerte Music</title><style>body{background:#000;color:#fff;font-family:Arial;margin:0;padding:15px;padding-bottom:140px}input{width:68%;padding:14px;border-radius:25px;border:none;background:#222;color:#fff}button{padding:14px 18px;border-radius:25px;border:none;background:#1DB954;color:#fff;font-weight:bold}.card{display:flex;align-items:center;background:#181818;margin:10px 0;padding:10px;border-radius:10px}.card img{width:55px;height:55px;border-radius:5px;margin-right:10px}#playerBox{position:fixed;bottom:0;left:0;right:0;background:#181818;padding:12px;border-top:1px solid #333;display:none}audio{width:100%;margin-top:8px}</style></head><body><h2>🎵 Laerte Music</h2><div style="display:flex;gap:8px"><input id="q" value="Felipe Rodrigues"><button onclick="buscar()">Buscar</button></div><div id="lista"></div><div id="playerBox"><div style="display:flex;align-items:center;gap:10px"><img id="capa" style="width:50px;height:50px;border-radius:5px"><div><b id="titulo">-</b><br><small id="artista">-</small><br><small id="status" style="color:#1DB954"></small></div></div><audio id="audio" controls playsinline></audio></div><script>let musicas=[];async function buscar(){document.getElementById('lista').innerHTML='Buscando...';let q=document.getElementById('q').value;let r=await fetch('/search?q='+encodeURIComponent(q));musicas=await r.json();let h='';musicas.forEach((m,i)=>{h+=`<div class="card" onclick="tocar(${i})"><img src="${m.thumb}"><div><b>${m.title}</b><br><small>${m.artist}</small></div></div>`});document.getElementById('lista').innerHTML=h}async function tocar(i){let m=musicas[i];document.getElementById('playerBox').style.display='block';document.getElementById('capa').src=m.thumb;document.getElementById('titulo').innerText=m.title;document.getElementById('artista').innerText=m.artist;document.getElementById('status').innerText='Carregando...';let audio=document.getElementById('audio');audio.pause();try{let r=await fetch('/play?url='+encodeURIComponent(m.id));let d=await r.json();if(d.error){document.getElementById('status').innerText=d.error;return}audio.src=d.audio;await audio.play();document.getElementById('status').innerText='Tocando 🎶'}catch(e){document.getElementById('status').innerText='Erro'}}buscar()</script></body></html>"""

@app.route('/')
def index(): return render_template_string(HTML)

@app.route('/search')
def search():
    q=request.args.get('q')
    try:
        with YoutubeDL({'quiet':True,'extract_flat':True,'skip_download':True,'extractor_args':{'youtube':{'player_client':['android']}}}) as ydl:
            info=ydl.extract_info(f"ytsearch8:{q}",download=False)
            res=[{'id':e['id'],'title':e['title'],'artist':e.get('uploader') or 'YouTube','thumb':f"https://i.ytimg.com/vi/{e['id']}/mqdefault.jpg"} for e in info.get('entries',[]) if e]
            return jsonify(res)
    except: return jsonify([])

@app.route('/play')
def play():
    vid=request.args.get('url')
    # 1 - INVIDIOUS (esse funciona no Render, testado)
    invs=["https://invidious.nerdvpn.de","https://inv.nadeko.net","https://iv.ggtyler.dev","https://invidious.protokolla.fi","https://inv.tux.pizza","https://invidious.no-logs.com"]
    for inv in invs:
        try:
            r=requests.get(f"{inv}/api/v1/videos/{vid}", headers={"User-Agent":"Mozilla/5.0"}, timeout=12)
            j=r.json()
            audios=[f for f in j.get('adaptiveFormats',[]) if 'audio/mp4' in f.get('type','') or 'audio' in f.get('type','')]
            if audios:
                best=sorted(audios, key=lambda x: int(x.get('bitrate',0)), reverse=True)[0]
                url=best.get('url')
                if url: return jsonify({'audio': url})
        except: continue
    # 2 - PIPED
    try:
        r=requests.get(f"https://pipedapi.kavin.rocks/streams/{vid}",timeout=8)
        j=r.json()
        if j.get('audioStreams'):
            best=sorted(j['audioStreams'], key=lambda x: x.get('bitrate',0) or 0, reverse=True)[0]
            return jsonify({'audio': best['url']})
    except: pass
    return jsonify({'error':'Servidor lotado, tenta clicar de novo em 5 seg'})

if __name__=='__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT',5000)))
