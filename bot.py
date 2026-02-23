import socket
import time
import threading
import random
import feedparser
import requests
import re
from flask import Flask

# --- CONFIGURAÇÕES ---
SERVER = "irc.ptnet.org"
PORT = 6667
NICK = "TheOG"
PASS = "Nasomet112#" 
CHANNEL = "#TheOG"
HF_TOKEN = "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"
HF_API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-3B-Instruct"

# --- BANCO DE DADOS LOCAL ---
# Lista de nicks que o bot viu falar (para as frases aleatórias)
nicks_ativos = set()

FRASES_ALEATORIAS = [
    "Sinto-me incrivelmente bem hoje no #TheOG!",
    "Alguém já disse ao {nick} que ele é uma lenda?",
    "A vida no IRC é melhor com amigos como vocês.",
    "O {nick} anda muito calado... tudo bem por aí?",
    "Sabiam que o #TheOG é o melhor canal da PTNet?",
    "Estou aqui a processar dados e a pensar como o {nick} é porreiro.",
    "Beber café virtual e ver o chat passar... que paz!",
    "Se o {nick} fosse um comando, seria o !top.",
    # ... Adiciona aqui as tuas 200 frases ...
    "Sinto que hoje vai ser um grande dia para o {nick}!",
    "Olá malta! Estou só a passar para dizer que adoro este canal."
]

SAUDACOES = ["Bem-vindo(a)!", "Boas! Tudo bem?", "Olha quem é! Senta-te e relaxa."]

app = Flask(__name__)

@app.route('/')
def home(): return "TheOG AI Online", 200

# --- FUNÇÕES DE SUPORTE ---

def get_ai_response(prompt):
    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload = {"inputs": f"Pergunta: {prompt}\nResposta curta:", "parameters": {"max_new_tokens": 50}}
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            res = response.json()[0].get('generated_text', '')
            return res.split("Resposta curta:")[-1].strip()
        return "Estou a pensar... mas o cérebro falhou."
    except: return "Erro nos meus neurónios!"

def get_meteo(cidade):
    try:
        # 1. Obter coordenadas da cidade/concelho
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={cidade}&count=1&language=pt"
        geo_res = requests.get(geo_url).json()
        if not geo_res.get('results'): return "Concelho não encontrado."
        
        lat = geo_res['results'][0]['latitude']
        lon = geo_res['results'][0]['longitude']
        nome = geo_res['results'][0]['name']

        # 2. Obter meteorologia
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        w_res = requests.get(w_url).json()
        temp = w_res['current_weather']['temperature']
        wind = w_res['current_weather']['windspeed']
        
        return f"Meteo em {nome}: {temp}°C | Vento: {wind}km/h"
    except: return "Erro ao consultar meteorologia."

def get_last_news():
    try:
        feed = feedparser.parse("https://www.rtp.pt/noticias/rss")
        return " | ".join([e.title for e in feed.entries[:2]])
    except: return "Sem notícias."

# --- LÓGICA DO BOT ---

def start_bot():
    while True:
        try:
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.settimeout(300)
            irc.connect((SERVER, PORT))
            irc.send(f"NICK {NICK}\r\n".encode())
            irc.send(f"USER {NICK} 8 * :Assistente #TheOG\r\n".encode())
            
            # Thread para frases aleatórias de 15 em 15 minutos
            def auto_talk():
                while True:
                    time.sleep(900) # 15 minutos
                    if nicks_ativos:
                        target = random.choice(list(nicks_ativos))
                        frase = random.choice(FRASES_ALEATORIAS).format(nick=target)
                        try: irc.send(f"PRIVMSG {CHANNEL} :{frase}\r\n".encode())
                        except: break

            threading.Thread(target=auto_talk, daemon=True).start()

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

                if "PRIVMSG" in data:
                    user = data.split('!')[0][1:]
                    nicks_ativos.add(user) # Adiciona à lista de nicks vistos
                    
                    msg_parts = data.split(f"PRIVMSG {CHANNEL} :", 1)
                    if len(msg_parts) > 1:
                        cmd = msg_parts[1].strip().lower()

                        # COMANDOS
                        if cmd == "!comandos":
                            irc.send(f"PRIVMSG {CHANNEL} :Comandos: !noticias, !meteo <concelho>, !comandos ou fala comigo mencionando {NICK}\r\n".encode())
                        
                        elif cmd.startswith("!meteo"):
                            cidade = cmd.replace("!meteo", "").strip()
                            if cidade:
                                res = get_meteo(cidade)
                                irc.send(f"PRIVMSG {CHANNEL} :{user}: {res}\r\n".encode())
                            else:
                                irc.send(f"PRIVMSG {CHANNEL} :{user}: Indica um concelho. Ex: !meteo Lisboa\r\n".encode())

                        elif cmd.startswith("!noticias"):
                            irc.send(f"PRIVMSG {CHANNEL} :📰 {get_last_news()}\r\n".encode())

                        elif NICK.lower() in cmd:
                            prompt = re.sub(rf'[<@]?{NICK}[:>,]?\s*', '', cmd, flags=re.IGNORECASE).strip()
                            if prompt:
                                resp = get_ai_response(prompt)
                                irc.send(f"PRIVMSG {CHANNEL} :{user}: {resp}\r\n".encode())

        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(20)

if __name__ == "__main__":
    threading.Thread(target=start_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
