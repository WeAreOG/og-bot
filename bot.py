import socket
import time
import threading
import requests
import re
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask
import os
import feedparser

# --- CONFIGURAÇÕES ---
SERVER = "irc.ptnet.org"
PORT = 6667
NICK = "TheOG"
PASS = "Nasomet112#" 
CHANNEL = "#TheOG"

# --- IA MISTRAL ---
HF_TOKEN = "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"
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"

# --- SPOTIFY ---
SPOTIPY_CLIENT_ID = '049705e3011d4fec99378b4ccd01ff26'
SPOTIPY_CLIENT_SECRET = 'bbaa61b3216048728dd0e9d9942328a9'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:8888/callback'

SCOPE = "user-read-currently-playing user-modify-playback-state user-read-playback-state playlist-modify-public playlist-modify-private"

app = Flask(__name__)

@app.route('/')
def health_check():
    return "TheOG Online", 200

# --- FUNÇÕES ---

def get_ai_response(prompt):
    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload = {
            "inputs": f"<s>[INST] Tu és o TheOG no IRC. Responde curto em PT-PT: {prompt} [/INST]</s>", 
            "parameters": {"max_new_tokens": 60, "temperature": 0.7}
        }
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=8)
        if response.status_code == 200:
            res = response.json()[0].get('generated_text', '').strip()
            return re.sub(r'[\r\n\t]+', ' ', res)
    except: pass
    return "Estou sintonizado!"

def get_or_create_playlist(sp):
    try:
        user_id = sp.current_user()['id']
        playlists = sp.current_user_playlists()
        for pl in playlists['items']:
            if pl['name'] == "TheOG IRC Playlist": return pl['id']
        return sp.user_playlist_create(user_id, "TheOG IRC Playlist", public=True)['id']
    except: return None

# --- CORE DO BOT ---

def run_irc_bot():
    auth_manager = SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI, scope=SCOPE,
        cache_path=".cache-spotify", open_browser=False
    )
    sp = spotipy.Spotify(auth_manager=auth_manager)
    playlist_id = None

    while True:
        try:
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            irc.connect((SERVER, PORT))
            
            irc.send(f"NICK {NICK}\r\n".encode())
            irc.send(f"USER {NICK} 8 * :TheOG Assistant\r\n".encode())

            while True:
                data = irc.recv(2048).decode("utf-8", errors="ignore")
                if not data: break

                if data.startswith("PING"):
                    irc.send(f"PONG {data.split()[1]}\r\n".encode())
                    continue

                if "376" in data or "422" in data:
                    irc.send(f"PRIVMSG NickServ :IDENTIFY {PASS}\r\n".encode())
                    time.sleep(2)
                    irc.send(f"JOIN {CHANNEL}\r\n".encode())
                    if not playlist_id: playlist_id = get_or_create_playlist(sp)

                if "PRIVMSG" in data:
                    user = data.split('!')[0][1:]
                    
                    # CORREÇÃO DA LINHA 100:
                    if user.lower() == NICK.lower(): 
                        continue
                    
                    parts = data.split(f"PRIVMSG {CHANNEL} :", 1)
                    if len(parts) > 1:
                        msg = parts[1].strip()
                        cmd = msg.lower()

                        # --- COMANDOS ---
                        if cmd.startswith("!music "):
                            query = msg[7:].strip()
                            search = sp.search(q=query, limit=1, type='track')
                            if search['tracks']['items'] and playlist_id:
                                track = search['tracks']['items'][0]
                                sp.playlist_add_items(playlist_id, [track['id']])
                                irc.send(f"PRIVMSG {CHANNEL} :✅ Adicionada: {track['name']}\r\n".encode())

                        elif cmd == "!playlist":
                            try:
                                sp.start_playback(context_uri=f"spotify:playlist:{playlist_id}")
                                irc.send(f"PRIVMSG {CHANNEL} :▶️ Playlist iniciada!\r\n".encode())
                            except:
                                irc.send(f"PRIVMSG {CHANNEL} :Dispositivo não encontrado. Abre o Spotify.\r\n".encode())

                        elif cmd == "!skip":
                            try:
                                sp.next_track()
                                irc.send(f"PRIVMSG {CHANNEL} :⏭️ Música saltada!\r\n".encode())
                            except: pass

                        elif cmd == "!noticias":
                            feed = feedparser.parse("https://www.rtp.pt/noticias/rss")
                            news = " | ".join([e.title for e in feed.entries[:2]])
                            irc.send(f"PRIVMSG {CHANNEL} :📰 {news}\r\n".encode())

                        elif NICK.lower() in cmd:
                            prompt = re.sub(rf'{NICK}', '', msg, flags=re.IGNORECASE).strip()
                            if prompt:
                                response = get_ai_response(prompt)
                                irc.send(f"PRIVMSG {CHANNEL} :{user}: {response}\r\n".encode())

        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(15)

if __name__ == "__main__":
    threading.Thread(target=run_irc_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
