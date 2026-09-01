@app.route('/play')
def play():
    vid=request.args.get('url')
    # 1 - Cobalt (4 instancias)
    for api in ["https://api.cobalt.tools","https://co.wuk.sh/api/json","https://api.cobalt.tools/api/json","https://cobalt-api.kavin.rocks"]:
        try:
            r=requests.post(api, json={"url":f"https://www.youtube.com/watch?v={vid}","isAudioOnly":True,"aFormat":"mp3","isNoTTWatermark":True}, headers={"Accept":"application/json","Content-Type":"application/json"}, timeout=15)
            j=r.json()
            if j.get('url'): return jsonify({'audio': j.get('url')})
            if j.get('status')=='redirect' and j.get('url'): return jsonify({'audio': j.get('url')})
        except: continue
    # 2 - Piped
    for piped in ["https://pipedapi.kavin.rocks","https://api.piped.privacy.com.de"]:
        try:
            r=requests.get(f"{piped}/streams/{vid}",timeout=10)
            j=r.json()
            if j.get('audioStreams'):
                best=sorted(j['audioStreams'], key=lambda x: x.get('bitrate',0) or 0, reverse=True)[0]
                if best.get('url'): return jsonify({'audio': best['url']})
        except: continue
    # 3 - Ultimo recurso yt-dlp android (funciona pra musica curta)
    try:
        ydl_opts={'format':'bestaudio/best','quiet':True,'extractor_args':{'youtube':{'player_client':['android','ios','mweb']}}}
        with YoutubeDL(ydl_opts) as ydl:
            info=ydl.extract_info(f"https://www.youtube.com/watch?v={vid}",download=False)
            if info.get('url'): return jsonify({'audio': info.get('url')})
    except Exception as e:
        pass
    return jsonify({'error':'Essa de 1h e muito grande, tenta uma menor (Tudo e Perda)'})
