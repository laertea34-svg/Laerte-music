from flask import Flask, request, jsonify, render_template_string
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#000000">
<title>Laerte Music</title>
<style>
body{background:#000;color:white;font-family:Arial;margin:0;padding:15px;padding-bottom:140px}
input{width:68%;padding:14px;border-radius:25px;border:none;background:#222;color:white;outline:none}
button{padding:14px 18px;border-radius:25px;border:none;background:#1DB954;color:white;font-weight:bold}
.card{display:flex;align-items:center;background:#181818;margin:10px 0;padding:10px;border-radius:10px}
.card img{width:55px;height:55px;border-radius:5px;margin-right:10px}
#playerBox{position:fixed;bottom:0;left:0;right:0;background:#181818;padding:12px;border-top:1px solid #333;display:none}
audio{width:100%;margin-top:8px}
</style>
</head>
<body>
<h2>🎵 Laerte Music</h2>
<div style="display:flex;gap:8px">
<input id="q" value="Felipe Rodrigues" placeholder="Buscar música">
<button onclick="buscar()">Buscar</button>
</div>
<div id="lista"></div>

<div id="playerBox">
<div style="display:flex;align-items:center;gap:10px">
<img id="capa" style="width:50px;height:50px;border-radius:5px">
<div style="flex:1"><b id="titulo">-</b><br><small id="artista">-</small><br><small id="status" style="color:#1DB954"></small></div>
</div>
<audio id="audio" controls controlsList="nodownload" playsinline></audio>
</div>

<script>
let musicas=[]
let atual=0
async function buscar(){
 document.getElementById('lista').innerHTML='<p>Buscando...</p>'
 let q=document.getElementById('q').value
 let r=await fetch('/search?q='+encodeURIComponent(q))
 musicas=await r.json()
 let h=''
 musicas.forEach((m,i)=>{
   h+=`<div class="card" onclick="tocar(${i})"><img src="${m.thumb}"><div><b>${m.title}</b><br><small>${m.artist}</small></div></div>`
 })
 document.getElementById('lista').innerHTML=h
}
async function tocar(i){
 atual=i
 let m=musicas[i]
 document.getElementById('playerBox').style.display='block'
 document.getElementById('capa').src=m.thumb
 document.getElementById('titulo').innerText=m.title
 document.getElementById('artista').innerText=m.artist
 document.getElementById('status').innerText='Carregando...'
 let audio=document.getElementById('audio')
 audio.pause()
 try{
  let r=await fetch('/play?url='+encodeURIComponent(m.id))
  let d=await r.json()
  if(d.error){ document.getElementById('status').innerText='Erro: '+d.error; return }
  audio.src=d.audio
  await audio.play()
  document.getElementById('status').innerText='Tocando'
  if('mediaSession' in navigator){
    navigator.mediaSession.metadata = new MediaMetadata({
      title: m.title,
      artist: m.artist,
      artwork: [{src: m.thumb, sizes:'512x512', type:'image/jpeg'}]
    })
    navigator.mediaSession.setActionHandler('play', ()=>audio.play())
    navigator.mediaSession.setActionHandler('pause', ()=>audio.pause())
    navigator.mediaSession.setActionHandler('nexttrack', ()=>{ if(atual+1<musicas.length) tocar(atual+1) })
    navigator.mediaSession.setActionHandler('previoustrack', ()=>{ if(atual-1>=0) tocar(atual-1) })
  }
 }catch(e){ document.getElementById('status').innerText='Erro ao carregar, tente outra música' }
}
buscar()
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/search')
def search():
    q = request.args.get('q')
    ydl_opts = {'quiet': True, 'extract_flat': True, 'skip_download': True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch8:{q}", download=False)
        res = []
        for e in info.get('entries', []):
            if not e: continue
            thumb = ''
            if e.get('thumbnails'):
                thumb = e['thumbnails'][-1]['url']
            res.append({
                'id': e.get('id'),
                'title': e.get('title'),
                'artist': e.get('uploader') or e.get('channel') or 'YouTube',
                'thumb': thumb
            })
        return jsonify(res)

@app.route('/play')
def play():
    video_id = request.args.get('url')
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'quiet': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'no_warnings': True,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info.get('url')
            if not audio_url and 'entries' in info:
                audio_url = info['entries'][0]['url']
            return jsonify({'audio': audio_url})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
