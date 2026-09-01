from flask import Flask, request, jsonify, render_template_string
import yt_dlp

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html><head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Laerte Music</title>
<style>
body{background:#121212;color:white;font-family:sans-serif;margin:0;padding:15px}
input{width:70%;padding:15px;border-radius:25px;border:none;background:#2a2a2a;color:white}
button{padding:15px 20px;border-radius:25px;border:none;background:#1db954;color:white;font-weight:bold}
.card{display:flex;gap:12px;background:#1e1e1e;padding:10px;border-radius:12px;margin-top:10px;align-items:center}
.card img{width:60px;height:60px;border-radius:8px}
#player{position:fixed;bottom:0;left:0;right:0;background:#000;padding:15px;border-top:1px solid #333}
audio{width:100%}
</style>
</head>
<body>
<h2>🎵 Laerte Music</h2>
<input id="q" value="Filipe Rodrigues"><button onclick="search()">Buscar</button>
<div id="list"></div>
<div style="height:120px"></div>
<div id="player"><div id="now">Escolha uma música</div><audio id="audio" controls autoplay></audio></div>
<script>
let queue=[], current=0;
async function search(){
 let q=document.getElementById('q').value;
 document.getElementById('list').innerHTML='Buscando...';
 let r=await fetch('/search?q='+encodeURIComponent(q));
 let data=await r.json();
 queue=data; let html='';
 data.forEach((v,i)=>{
   html+=`<div class="card" onclick="play(${i})"><img src="${v.thumb}"><div><b>${v.title}</b><br><small>${v.author}</small></div></div>`;
 });
 document.getElementById('list').innerHTML=html;
}
async function play(i){
 current=i; let v=queue[i];
 document.getElementById('now').innerText='Carregando: '+v.title;
 let r=await fetch('/stream?id='+v.id);
 let d=await r.json();
 document.getElementById('audio').src=d.url;
 document.getElementById('now').innerText='Tocando: '+v.title;
 document.getElementById('audio').onended=()=>{ if(current+1<queue.length) play(current+1); };
}
search();
</script>
</body></html>
"""
@app.route('/')
def home(): return render_template_string(HTML)
@app.route('/search')
def search():
    q=request.args.get('q')
    ydl_opts={'quiet':True,'skip_download':True,'extract_flat':True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info=ydl.extract_info(f"ytsearch10:{q}", download=False)
        out=[]
        for e in info['entries']:
            out.append({'id':e['id'],'title':e['title'],'author':e.get('uploader',''),'thumb':f"https://i.ytimg.com/vi/{e['id']}/mqdefault.jpg"})
        return jsonify(out)
@app.route('/stream')
def stream():
    vid=request.args.get('id')
    ydl_opts={'quiet':True,'format':'bestaudio[ext=m4a]/bestaudio','noplaylist':True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info=ydl.extract_info(f"https://www.youtube.com/watch?v={vid}", download=False)
        return jsonify({'url':info['url'],'title':info['title']})
if __name__=='__main__':
    app.run(host='0.0.0.0',port=10000)
