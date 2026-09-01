from flask import Flask, request, jsonify, render_template_string
import requests
import os
app = Flask(__name__)

HTML = """<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Laerte Music</title><style>body{background:#000;color:#fff;font-family:Arial;margin:0;padding:15px;padding-bottom:140px}input{width:68%;padding:14px;border-radius:25px;border:none;background:#222;color:#fff}button{padding:14px 18px;border-radius:25px;border:none;background:#1DB954;color:#fff;font-weight:bold}.card{display:flex;align-items:center;background:#181818;margin:10px 0;padding:10px;border-radius:10px}.card img{width:55px;height:55px;border-radius:5px;margin-right:10px}#playerBox{position:fixed;bottom:0;left:0;right:0;background:#181818;padding:12px;border-top:1px solid #333;display:none}audio{width:100%;margin-top:8px}</style></head><body><h2>🎵 Laerte Music</h2><div style="display:flex;gap:8px"><input id="q" value="Felipe Rodrigues"><button onclick="buscar()">Buscar</button></div><div id="lista"></div><div id="playerBox"><div style="display:flex;align-items:center;gap:10px"><img id="capa" style="width:50px;height:50px;border-radius:5px"><div><b id="titulo">-</b><br><small id="artista">-</small><br><small id="status" style="color:#1DB954"></small></div></div><audio id="audio" controls playsinline></audio></div><script>let musicas=[],atual=0;async function buscar(){document.getElementById('lista').innerHTML='Buscando...';let q=document.getElementById('q').value;let r=await fetch('/search?q='+encodeURIComponent(q));musicas=await r.json();let h='';musicas.forEach((m,i)=>{h+=`<div class="card" onclick="tocar(${i})"><img src="${m.thumb}"><div><b>${m.title}</b><br><small>${m.artist}</small></div></div>`});document.getElementById('lista').innerHTML=h}async function tocar(i){atual=i;let m=musicas[i];document.getElementById('playerBox').style.display='block';document.getElementById('capa').src=m.thumb;document.getElementById('titulo').innerText=m.title;document.getElementById('artista').innerText=m.artist;document.getElementById('status').innerText='Carregando...';let audio=document.getElementById('audio');audio.pause();try{let r=await fetch('/play?url='+encodeURIComponent(m.id));let d=await r.json();if(d.error){document.getElementById('status').innerText=d.error;return}audio.src=d.audio;await audio.play();document.getElementById('status').innerText='Tocando';if('mediaSession' in navigator){navigator.mediaSession.metadata=new MediaMetadata({title:m.title,artist:m.artist,artwork:[{src:m.thumb,sizes:'512x512',type:'image/jpeg'}]});}}catch(e){document.getElementById('status').innerText='Tente outra musica'}}buscar()</script></body></html>"""

@app.route('/')
def index(): return render_template_string(HTML)

@app.route('/search')
def search():
    q = request.args.get('q')
    # Busca via Invidious - nunca bloqueia
    try:
        r = requests.get(f"https://invidious.nerdvpn.de/api/v1/search?q={q}&type=video", timeout=10, headers={"User-Agent":"Mozilla/5.0"})
        data = r.json()
        res=[]
        for item in data[:8]:
            vid = item.get('videoId')
            if not vid: continue
            res.append({
                'id': vid,
                'title': item.get('title'),
                'artist': item.get('author') or 'YouTube',
                'thumb': f"https://i.ytimg.com/vi/{vid}/mqdefault.jpg"
            })
        if res: return jsonify(res)
    except: pass
    # fallback Piped
    try:
        r = requests.get(f"https://pipedapi.kavin.rocks/search?q={q}&filter=music_songs", timeout=8)
        j = r.json()
        res=[]
        for item in (j.get('items') or [])[:8]:
            url = item.get('url','')
            vid = url.split('v=')[-1].split('&')[0].replace('/watch?v=','')
            res.append({'id':vid,'title':item.get('title'),'artist':item.get('uploaderName'),'thumb':item.get('thumbnail')})
        if res: return jsonify(res)
    except: pass
    return jsonify([])

@app.route('/play')
def play():
    vid = request.args.get('url')
    # METODO 1 - Cobalt (mais forte contra bot)
    cobalt_instances = ["https://api.cobalt.tools","https://co.wuk.sh/api/json","https://cobalt-api.kavin.rocks"]
    for api in cobalt_instances:
        try:
            r = requests.post(api, json={"url": f"https://www.youtube.com/watch?v={vid}", "isAudioOnly": True, "aFormat": "mp3"}, headers={"Accept":"application/json","Content-Type":"application/json"}, timeout=15)
            j = r.json()
            url = j.get('url')
            if url: return jsonify({'audio': url})
        except: continue

    # METODO 2 - Invidious direto
    inv_instances = ["https://invidious.nerdvpn.de","https://iv.ggtyler.dev","https://inv.nadeko.net"]
    for inv in inv_instances:
        try:
            r = requests.get(f"{inv}/latest_version?id={vid}&itag=140", timeout=10, allow_redirects=False)
            # Invidious retorna redirect pro audio
            if r.status_code in [302,303,307]:
                loc = r.headers.get('Location')
                if loc: return jsonify({'audio': loc})
            # tenta API de streams
            r2 = requests.get(f"{inv}/api/v1/videos/{vid}", timeout=10)
            j = r2.json()
            streams = j.get('adaptiveFormats',[])
            audio = [s for s in streams if 'audio' in s.get('type','')]
            if audio:
                best = sorted(audio, key=lambda x: x.get('bitrate',0), reverse=True)[0]
                return jsonify({'audio': best['url']})
        except: continue

    return jsonify({'error': 'Servidor cheio, tente tocar outra da lista'})

if __name__=='__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5000)))
