from flask import Flask, request, jsonify, render_template_string
from yt_dlp import YoutubeDL
import os
app = Flask(__name__)

HTML = """
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Laerte Music</title>
<style>body{background:#000;color:#fff;font-family:Arial;margin:0;padding:15px;padding-bottom:170px}input{width:68%;padding:14px;border-radius:25px;border:none;background:#222;color:#fff}button{padding:14px 18px;border-radius:25px;border:none;background:#1DB954;color:#fff;font-weight:bold}.card{display:flex;align-items:center;background:#181818;margin:10px 0;padding:10px;border-radius:10px}.card img{width:55px;height:55px;border-radius:5px;margin-right:10px}#playerBox{position:fixed;bottom:0;left:0;right:0;background:#181818;padding:12px;border-top:1px solid #333;display:none}iframe{width:100%;height:80px;border:none;border-radius:10px}</style>
</head><body>
<h2>🎵 Laerte Music - FINAL</h2>
<div style="display:flex;gap:8px"><input id="q" value="Felipe Rodrigues"><button onclick="buscar()">Buscar</button></div>
<div id="lista"></div>
<div id="playerBox">
<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px"><img id="capa" style="width:50px;height:50px;border-radius:5px"><div><b id="titulo">-</b><br><small id="artista">-</small><br><small style="color:#1DB954">Tocando no seu celular 🎶</small></div></div>
<div id="ytplayer"></div>
</div>
<script>
let musicas=[];
async function buscar(){
 document.getElementById('lista').innerHTML='Buscando...';
 let q=document.getElementById('q').value;
 let r=await fetch('/search?q='+encodeURIComponent(q));
 musicas=await r.json();
 let h='';
 musicas.forEach((m,i)=>{
  h+=`<div class="card" onclick="tocar(${i})"><img src="${m.thumb}"><div><b>${m.title}</b><br><small>${m.artist}</small></div></div>`;
 });
 document.getElementById('lista').innerHTML=h||'Nada encontrado';
}
function tocar(i){
 let m=musicas[i];
 document.getElementById('playerBox').style.display='block';
 document.getElementById('capa').src=m.thumb;
 document.getElementById('titulo').innerText=m.title;
 document.getElementById('artista').innerText=m.artist;
 // Player que toca direto no celular - sem passar pelo Render (nunca bloqueia)
 document.getElementById('ytplayer').innerHTML=`<iframe src="https://www.youtube.com/embed/${m.id}?autoplay=1&playsinline=1&controls=1" allow="autoplay; encrypted-media" allowfullscreen></iframe>`;
 window.scrollTo(0,document.body.scrollHeight);
}
buscar();
</script>
</body></html>
"""

@app.route('/')
def index(): return render_template_string(HTML)

@app.route('/search')
def search():
    q=request.args.get('q')
    try:
        opts={'quiet':True,'extract_flat':True,'skip_download':True,'extractor_args':{'youtube':{'player_client':['android']}}}
        with YoutubeDL(opts) as ydl:
            info=ydl.extract_info(f"ytsearch10:{q}",download=False)
            res=[{'id':e['id'],'title':e['title'],'artist':e.get('uploader') or 'Felipe Rodrigues','thumb':f"https://i.ytimg.com/vi/{e['id']}/mqdefault.jpg"} for e in info.get('entries',[]) if e]
            return jsonify(res)
    except Exception as e:
        return jsonify([])

if __name__=='__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT',5000)))
</script>
