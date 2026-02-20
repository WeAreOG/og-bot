import socket
import time
import threading
import random
import feedparser
import google.generativeai as genai
from flask import Flask

# --- CONFIGURAÇÕES ---
SERVER = "irc.ptnet.org"
PORT = 6667
NICK = "TheOG"
PASS = "Nasomet112#" 
CHANNEL = "#TheOG"
ADMIN_NICK = "Emergency112"
GEMINI_KEY = "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" # Obtém em aistudio.google.com

# Configurar a IA
genai.configure(api_key=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)
model = genai.GenerativeModel('gemini-1.5-flash')

SAUDACOES = [
    "Bem-vindo(a) ao #TheOG! 😊",
    "Olha quem é! Boas, tudo bem?",
    "Sente-te à vontade no nosso canal! 🎧",
    "Boas! É um prazer ter-te por cá.",
    "Hey! Bem-vindo ao ponto de encontro. 🚀",
    "Ora vivas! Que bom ver-te no canal."
]

app = Flask(__name__)

@app.route('/')
def home():
    return "TheOG AI Ativo"

def get_ai_response(prompt):
    try:
        # Instrução de personalidade para a IA
        full_prompt = f"És o assistente do canal #TheOG no IRC. Responde de forma curta e prestável: {prompt}"
        response = model.generate_content(full_prompt)
        return response.text.replace('\n', ' ').strip()[:300] # Limite de caracteres para IRC
    except:
        return "Estou a processar muita informação agora. Tenta daqui a pouco!"

def get_last_news():
    try:
        feed = feedparser.parse("https://www.rtp.pt/noticias/rss")
        if feed.entries:
            top_3 = feed.entries[:3]
            noticias = [entry.title.strip() for entry in top_3]
            return " | ".join(noticias)
        return "Sem notícias de momento."
    except:
        return "Erro ao aceder ao serviço de notícias."

def start_bot():
    while True:
        try:
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.settimeout(120)
            irc.connect((SERVER, PORT))
            
            irc.send(f"NICK {NICK}\r\n".encode())
            irc.send(f"USER {NICK} 8 * :Assistente AI #TheOG\r\n".encode())
            
            while True:
                data = irc.recv(2048).decode("utf-8", errors="ignore")
                if not data: break
                
                if data.startswith("PING"):
                    irc.send(f"PONG {data.split()[1]}\r\n".encode())

                if "433" in data:
                    irc.send(f"PRIVMSG NickServ :GHOST {NICK} {PASS}\r\n".encode())
                    time.sleep(2)
                    irc.send(f"NICK {NICK}\r\n".encode())

                if "376" in data or "422" in data:
                    irc.send(f"PRIVMSG NickServ :IDENTIFY {PASS}\r\n".encode())
                    time.sleep(3)
                    irc.send(f"JOIN {CHANNEL}\r\n".encode())

                # Cumprimentos
                if " JOIN " in data and f" JOIN {CHANNEL}" in data:
                    user_nick = data.split('!')[0][1:]
                    ignore = [NICK.lower(), "adamastor", "chanserv", "nickserv", "memoserv"]
                    if user_nick.lower() not in ignore:
                        saudacao = random.choice(SAUDACOES)
                        time.sleep(2)
                        irc.send(f"PRIVMSG {CHANNEL} :{user_nick}: {saudacao}\r\n".encode())

                # Comandos e Inteligência Artificial
                if "PRIVMSG" in data:
                    msg_full = data.split(f"PRIVMSG {CHANNEL} :")[1] if f"PRIVMSG {CHANNEL} :" in data else ""
                    user_talker = data.split('!')[0][1:]
                    
                    if "!noticias" in msg_full.lower():
                        irc.send(f"PRIVMSG {CHANNEL} :📰 [ÚLTIMA HORA]: {get_last_news()}\r\n".encode())
                    
                    # Se alguém chamar o bot pelo nome (IA)
                    elif NICK.lower() in msg_full.lower():
                        pergunta = msg_full.lower().replace(NICK.lower(), "").strip()
                        if pergunta:
                            resposta_ia = get_ai_response(pergunta)
                            irc.send(f"PRIVMSG {CHANNEL} :{user_talker}: {resposta_ia}\r\n".encode())

        except Exception:
            time.sleep(20)

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    start_bot()
