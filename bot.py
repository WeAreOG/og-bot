import socket
import time
import threading
import random
import feedparser
import requests
import re
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask
import os

# --- CONFIGURAÇÕES IRC ---
SERVER = "irc.ptnet.org"
PORT = 6667
NICK = "TheOG"
PASS = "Nasomet112#" 
CHANNEL = "#TheOG"

# --- CONFIGURAÇÕES IA (Hugging Face / Mistral) ---
HF_TOKEN = "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"
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"

# --- CONFIGURAÇÕES SPOTIFY ---
SPOTIPY_CLIENT_ID = '049705e3011d4fec99378b4ccd01ff26'
SPOTIPY_CLIENT_SECRET = 'bbaa61b3216048728dd0e9d9942328a9'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:8888/callback'

SCOPE = (
    "user-read-currently-playing "
    "user-modify-playback-state "
    "user-read-playback-state "
    "playlist-modify-public "
    "playlist-modify-private"
)

app = Flask(__name__)

@app.route('/')
def home(): 
    return "TheOG Bot Online - IRC + IA + Spotify", 200

# --- FUNÇÕES DE LÓGICA ---

def get_ai_response(prompt):
    """Comunicação com a Mistral-7B via API do Hugging Face"""
    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        full_prompt = f"<s>[INST] Tu és o TheOG no IRC #TheOG. Responde muito curto e natural em PT-PT: {prompt} [/INST]</s>"
        payload = {"inputs": full_prompt, "parameters": {"max_new_tokens": 60, "temperature": 0.7}}
        
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            res = response.json()[0].get('generated_text', '').strip()
            return re.sub(r'[\r\n\t]+', ' ', res) # Limpeza para o IRC
    except: pass
    return "Estou sintonizado na música, repete lá!"

def get_meteo(cidade):
    """Obtém meteorologia em tempo real"""
    try:
        geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={cidade}&count=1").json()
        if not geo.get('results'): return "Cidade não encontrada."
        d = geo['results'][0]
        w = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={d['latitude']}&longitude={d['longitude']}&current_weather=true").json()
        return f"Meteo em {d['name']}: {w['current_weather']['temperature']}°C | Vento: {w['current_weather']['windspeed']}km/h"
    except: return "Erro ao consultar o tempo."

def get_or_create_playlist(sp):
    """Garante a existência da playlist 'TheOG IRC Playlist'"""
    try:
        user_id = sp.current_user()['id']
        playlists = sp.current_user_playlists()
        for pl in playlists['items']:
            if pl['name'] == "TheOG IRC Playlist":
                return pl['id']
        new_pl = sp.user_playlist_create(user_id, "TheOG IRC Playlist", public=True)
        return new_pl['id']
    except: return None

# --- CORE DO BOT ---

def start_bot():
    # Inicialização Spotipy (Spotify SDK)
    auth_manager = SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SCOPE,
        cache_path=".cache-spotify",
        open_browser=False # Crucial para servidores (Render)
    )
    sp = spotipy.Spotify(auth_manager=auth_manager)
    target_playlist_id = None

    while True:
        try:
            print(f"A ligar ao servidor {SERVER}...")
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.settimeout(60)
            irc.connect((SERVER, PORT))
            
            irc.send(f"NICK {NICK}\r\n".encode())
            irc.send(f"USER {NICK} 8 * :Assistente TheOG\r\n".encode())
            
            # Tentar capturar a playlist no arranque
            if not target_playlist_id:
                target_playlist_id = get_or_create_playlist(sp)

            while True:
                raw = irc.recv(2048).decode("utf-8", errors="ignore")
                if not raw: break
                
                # Manter a ligação ativa (Responder ao Servidor)
                if raw.startswith("PING"):
                    irc.send(f"PONG {raw.split()[1]}\r\n".encode())
                    continue
                
                # Autenticação e Entrada no Canal
                if "376" in raw or "422" in raw:
                    irc.send(f"PRIVMSG NickServ :IDENTIFY {PASS}\r\n".encode())
                    time.sleep(2)
                    irc.send(f"JOIN {CHANNEL}\r\n".encode())
                    irc.send(f"PRIVMSG {CHANNEL} :TheOG Online! 🎶 !music <nome>, !playlist, !meteo <cidade>, !noticias\r\n".encode())

                # Processamento de Mensagens
                if "PRIVMSG" in raw:
                    user = raw.split('!')[0][1:]
                    if user.lower() in [NICK.lower(), "emergency112"]: continue
                    
                    m = raw.split(f"PRIVMSG {CHANNEL} :", 1)
                    if len(m) > 1:
                        content = m[1].strip()
                        cmd_parts = content.split(' ', 1)
                        cmd = cmd_parts[0].lower()

                        # --- COMANDOS ---
                        if cmd == "!music":
                            if len(cmd_parts) > 1:
                                query = cmd_parts[1]
                                search = sp.search(q=query, limit=1, type='track')
                                if search['tracks']['items'] and target_playlist_id:
                                    track = search['tracks']['items'][0]
                                    sp.playlist_add_items(target_playlist_id, [track['id']])
                                    irc.send(f"PRIVMSG {CHANNEL} :✅ {user}: '{track['name']}' adicionada!\r\n".encode())
                                else:
                                    irc.send(f"PRIVMSG {CHANNEL} :Música não encontrada.\r\n".encode())
                            else:
                                curr = sp.currently_playing()
                                if curr and curr['is_playing']:
                                    irc.send(f"PRIVMSG {CHANNEL} :🎶 {curr['item']['name']} - {curr['item']['artists'][0]['name']}\r\n".encode())

                        elif cmd == "!playlist" and target_playlist_id:
                            try:
                                sp.start_playback(context_uri=f"spotify:playlist:{target_playlist_id}")
                                irc.send(f"PRIVMSG {CHANNEL} :▶️ A tocar a playlist do canal!\r\n".encode())
                            except:
                                irc.send(f"PRIVMSG {CHANNEL} :Erro: Abre o Spotify e põe em 'Play' primeiro.\r\n".encode())

                        elif cmd == "!skip":
                            try:
                                sp.next_track()
                                irc.send(f"PRIVMSG {CHANNEL} :⏭️ Música saltada.\r\n".encode())
                            except: pass

                        elif cmd.startswith("!meteo"):
                            cidade = content[7:].strip()
                            if cidade: irc.send(f"PRIVMSG {CHANNEL} :{user}: {get_meteo(cidade)}\r\n".encode())

                        elif cmd == "!noticias":
                            feed = feedparser.parse("https://www.rtp.pt/noticias/rss")
                            news = " | ".join([e.title for e in feed.entries[:2]])
                            irc.send(f"PRIVMSG {CHANNEL} :📰 {news}\r\n".encode())

                        # --- IA (Conversa) ---
                        elif NICK.lower() in content.lower():
                            prompt = re.sub(rf'[<@]?{NICK}[:>,]?\s*', '', content, flags=re.IGNORECASE).strip()
                            if prompt:
                                response = get_ai_response(prompt)
                                irc.send(f"PRIVMSG {CHANNEL} :{user}: {response}\r\n".encode())

        except Exception as e:
            print(f"Erro: {e}. A reiniciar em 20s...")
            time.sleep(20)

if __name__ == "__main__":
    # Thread do Bot IRC
    threading.Thread(target=start_bot, daemon=True).start()
    # Flask para Deploy (Render/Railway)
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
