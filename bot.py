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

# --- BASE DE DADOS E FRASES ---
nicks_ativos = set()

# Exemplo de lista (podes expandir até 200)
FRASES_ALEATORIAS = [
    "Sinto-me incrivelmente bem hoje por aqui!",
    "O {nick} é claramente a alma deste canal.",
    "IRC no #TheOG é outro nível, não acham?",
    "Alguém deu comida ao {nick} hoje? Parece-me muito calado.",
    "A processar algoritmos e a concluir que o {nick} é 5 estrelas.",
    "O que seria de mim sem o {nick} para animar o chat?",
    "Adoro o cheiro a bytes logo pela manhã!",
    "Sinto que o {nick} vai ganhar a lotaria hoje.",
    "A felicidade é um canal de IRC chamado #TheOG.",
    "O {nick} é o meu humano preferido (não digam aos outros)."
]

SAUDACOES = ["Bem-vindo(a)!", "Boas! Como vais?", "Ora vivas! Sente-te em casa."]

app = Flask(__name__)

@app.route('/')
def home(): return "TheOG Online", 200

# --- FUNÇÕES DE RESPOSTA ---

def get_ai_response(prompt):
    """Tenta obter resposta da AI. Se falhar, usa resposta genérica divertida."""
    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        # Prompt ultra-simplificado para garantir resposta
        payload = {
            "inputs": f"Conversa rápida em português:\nHumano: {prompt}\nAssistente:",
            "parameters": {"max_new_tokens": 60, "temperature": 0.7}
        }
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=8)
        
        if response.status_code == 200:
            result = response.json()
            full_text = result[0].get('generated_text', '')
            # Extrair apenas o que vem depois de 'Assistente:'
            if "Assistente:" in full_text:
                return full_text.split("Assistente:")[-1].strip().split('\n')[0]
            return full_text.strip()
    except Exception as e:
        print(f"Erro AI: {e}")
    
    # Fallback caso a AI falhe
    respostas_backup = [
        "Interessante... conta-me mais sobre isso!",
        "Estou a processar, mas os meus cabos estão um pouco baralhados.",
        "Essa é uma excelente pergunta. O que achas tu?",
        "Às vezes prefiro só ouvir e aprender convosco.",
        "Os meus sensores dizem que és uma pessoa curiosa!"
    ]
    return random.choice(respostas_backup)

def get_meteo(cidade):
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={cidade}&count=1&language=pt"
        geo_res = requests.get(geo_url).json()
        if not geo_res.get('results'): return "Concelho não encontrado."
        
        data = geo_res['results'][0]
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={data['latitude']}&longitude={data['longitude']}&current_weather=true"
        w_res = requests.get(w_url).json()
        temp = w_res['current_weather']['temperature']
        return f"Meteo em {data['name']}: {temp}°C | Vento: {w_res['current_weather']['windspeed']}km/h"
    except: return "Erro ao obter meteorologia."

def get_last_news():
    try:
        feed = feedparser.parse("https://www.rtp.pt/noticias/rss")
        return " | ".join([e.title for e in feed.entries[:3]])
    except: return "Sem notícias disponíveis."

# --- BOT CORE ---

def start_bot():
    while True:
        try:
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.settimeout(300)
            irc.connect((SERVER, PORT))
            irc.send(f"NICK {NICK}\r\n".encode())
            irc.send(f"USER {NICK} 8 * :Assistente #TheOG\r\n".encode())
            
            # Loop de frases automáticas (15 min)
            def auto_talk():
                while True:
                    time.sleep(900)
                    if nicks_ativos:
                        target = random.choice(list(nicks_ativos))
                        frase = random.choice(FRASES_ALEATORIAS).format(nick=target)
                        try: irc.send(f"PRIVMSG {CHANNEL} :{frase}\r\n".encode())
                        except: break
            
            threading.Thread(target=auto_talk, daemon=True).start()

            while True:
                raw = irc.recv(2048).decode("utf-8", errors="ignore")
                if not raw: break
                
                # Resposta ao PING (Obrigatório)
                if raw.startswith("PING"):
                    irc.send(f"PONG {raw.split()[1]}\r\n".encode())
                    continue

                # Entrar no canal
                if "376" in raw or "422" in raw:
                    irc.send(f"PRIVMSG NickServ :IDENTIFY {PASS}\r\n".encode())
                    time.sleep(2)
                    irc.send(f"JOIN {CHANNEL}\r\n".encode())

                if "PRIVMSG" in raw:
                    user = raw.split('!')[0][1:]
                    if user.lower() == NICK.lower(): continue
                    
                    nicks_ativos.add(user)
                    
                    msg_content = raw.split(f"PRIVMSG {CHANNEL} :", 1)
                    if len(msg_content) > 1:
                        content = msg_content[1].strip()
                        cmd = content.lower()

                        # COMANDOS EM PVT (PRIVMSG para o utilizador, não para o canal)
                        if cmd == "!comandos":
                            irc.send(f"PRIVMSG {user} :Comandos: !noticias, !meteo <concelho>, !comandos ou chama por {NICK}\r\n".encode())
                        
                        elif cmd.startswith("!meteo"):
                            cidade = content[7:].strip()
                            res = get_meteo(cidade) if cidade else "Uso: !meteo <concelho>"
                            irc.send(f"PRIVMSG {user} :{res}\r\n".encode())

                        elif cmd.startswith("!noticias"):
                            news = get_last_news()
                            irc.send(f"PRIVMSG {user} :📰 {news}\r\n".encode())

                        # RESPOSTA AI (No Canal)
                        elif NICK.lower() in cmd:
                            prompt = re.sub(rf'[<@]?{NICK}[:>,]?\s*', '', content, flags=re.IGNORECASE).strip()
                            if prompt:
                                resposta = get_ai_response(prompt)
                                irc.send(f"PRIVMSG {CHANNEL} :{user}: {resposta}\r\n".encode())

        except Exception as e:
            print(f"Erro Conexão: {e}")
            time.sleep(20)

if __name__ == "__main__":
    threading.Thread(target=start_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
