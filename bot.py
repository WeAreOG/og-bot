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

# --- CONFIGURAÇÕES IRC ---
SERVER = "irc.ptnet.org"
PORT = 6667
NICK = "TheOG"
PASS = "Nasomet112#" 
CHANNEL = "#TheOG"

# --- CONFIGURAÇÕES IA (Hugging Face) ---
HF_TOKEN = "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"
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"

# --- CONFIGURAÇÕES SPOTIFY ---
SPOTIPY_CLIENT_ID = '049705e3011d4fec99378b4ccd01ff26'
SPOTIPY_CLIENT_SECRET = 'bbaa61b3216048728dd0e9d9942328a9'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:8888/callback'

# Escopos expandidos para gerir playlists e procurar músicas
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
    return "TheOG Online - Playlist Mode Active", 200

# --- FUNÇÕES AUXILIARES ---

def get_ai_response(prompt):
    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        full_prompt = f"<s>[INST] Tu és o TheOG no IRC #TheOG. Responde curto em PT-PT: {prompt} [/INST]</s>"
        payload = {"inputs": full_prompt, "parameters": {"max_new_tokens": 80}}
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json()[0].get('generated_text', '').strip().replace('\n', ' ')
    except: pass
    return "Estou aqui para ajudar!"

def get_or_create_playlist(sp):
    """Encontra ou cria a playlist do canal"""
    user_id = sp.current_user()['id']
    playlists = sp.current_user_playlists()
    for pl in playlists['items']:
        if pl['name'] == "TheOG IRC Playlist":
            return pl['id']
    
    # Se não existir, cria
    new_pl = sp.user_playlist_create(user_id, "TheOG IRC Playlist", public=True, description="Músicas adicionadas pelo chat IRC")
    return new_pl['id']

# --- BOT CORE ---

def start_bot():
    auth_manager = SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SCOPE,
        cache_path=".cache-spotify"
    )
    sp = spotipy.Spotify(auth_manager=auth_manager)
    
    # Identifica a playlist alvo no arranque
    try:
        target_playlist_id = get_or_create_playlist(sp)
    except:
        target_playlist_id = None

    while True:
        try:
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.connect((SERVER, PORT))
            irc.send(f"NICK {NICK}\r\n".encode())
            irc.send(f"USER {NICK} 8 * :TheOG Playlist Bot\r\n".encode())
            
            while True:
                raw = irc.recv(2048).decode("utf-8", errors="ignore")
                if not raw: break
                if raw.startswith("PING"):
                    irc.send(f"PONG {raw.split()[1]}\r\n".encode())
                
                if "376" in raw or "422" in raw:
                    irc.send(f"PRIVMSG NickServ :IDENTIFY {PASS}\r\n".encode())
                    time.sleep(2)
                    irc.send(f"JOIN {CHANNEL}\r\n".encode())

                if "PRIVMSG" in raw:
                    user = raw.split('!')[0][1:]
                    if user.lower() in [NICK.lower(), "emergency112"]: continue
                    
                    m = raw.split(f"PRIVMSG {CHANNEL} :", 1)
                    if len(m) > 1:
                        content = m[1].strip()
                        cmd_parts = content.split(' ', 1)
                        cmd = cmd_parts[0].lower()

                        # --- COMANDOS SPOTIFY ATUALIZADOS ---
                        
                        # !music <nome da musica> - Adiciona à playlist
                        if cmd == "!music":
                            if len(cmd_parts) > 1:
                                query = cmd_parts[1]
                                search = sp.search(q=query, limit=1, type='track')
                                if search['tracks']['items']:
                                    track = search['tracks']['items'][0]
                                    sp.playlist_add_items(target_playlist_id, [track['id']])
                                    irc.send(f"PRIVMSG {CHANNEL} :✅ Adicionada: {track['artists'][0]['name']} - {track['name']} à playlist!\r\n".encode())
                                else:
                                    irc.send(f"PRIVMSG {CHANNEL} :Não encontrei essa música.\r\n".encode())
                            else:
                                # Se usado sem argumentos, mostra a música atual
                                current = sp.currently_playing()
                                if current and current['is_playing']:
                                    irc.send(f"PRIVMSG {CHANNEL} :🎶 A tocar agora: {current['item']['name']}\r\n".encode())

                        # !playlist - Começa a tocar a playlist do canal
                        elif cmd == "!playlist":
                            try:
                                devices = sp.devices()
                                if devices['devices']:
                                    device_id = devices['devices'][0]['id']
                                    sp.start_playback(device_id=device_id, context_uri=f"spotify:playlist:{target_playlist_id}")
                                    irc.send(f"PRIVMSG {CHANNEL} :▶️ A carregar a playlist do canal no Spotify!\r\n".encode())
                                else:
                                    irc.send(f"PRIVMSG {CHANNEL} :Erro: Nenhum dispositivo Spotify ativo encontrado.\r\n".encode())
                            except Exception as e:
                                irc.send(f"PRIVMSG {CHANNEL} :Ativa o teu Spotify primeiro.\r\n".encode())

                        elif cmd == "!skip":
                            try:
                                sp.next_track()
                                irc.send(f"PRIVMSG {CHANNEL} :⏭️ Próxima!\r\n".encode())
                            except: pass

                        # --- OUTROS ---
                        elif NICK.lower() in content.lower():
                            prompt = re.sub(rf'[<@]?{NICK}[:>,]?\s*', '', content, flags=re.IGNORECASE).strip()
                            if prompt:
                                irc.send(f"PRIVMSG {CHANNEL} :{user}: {get_ai_response(prompt)}\r\n".encode())

        except Exception as e:
            time.sleep(15)

if __name__ == "__main__":
    threading.Thread(target=start_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
