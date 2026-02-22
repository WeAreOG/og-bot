import socket
import time
import threading
import random
import feedparser
import requests
from flask import Flask

# --- CONFIGURAÇÕES ---
SERVER = "irc.ptnet.org"
PORT = 6667
NICK = "TheOG"
PASS = "Nasomet112#" 
CHANNEL = "#TheOG"
ADMIN_NICK = "Emergency112"

# API HUGGING FACE
HF_TOKEN = "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"
# Usando Llama-3.2-3B por ser rápido e eficiente para IRC
HF_API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-3B-Instruct"

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
    return "TheOG AI Ativo (Hugging Face Mode)"

def get_ai_response(prompt):
    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        # Estrutura de prompt para modelos Llama 3
        payload = {
            "inputs": f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nÉs o assistente do canal #TheOG. Responde de forma curta e amigável em português.<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
            "parameters": {
                "max_new_tokens": 200,
                "temperature": 0.7,
                "top_p": 0.9,
                "return_full_text": False
            }
        }
        
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=15)
        result = response.json()
        
        # Se o modelo estiver a carregar (loading)
        if isinstance(result, dict) and "estimated_time" in result:
            return "Estou a acordar os meus neurónios... tenta de novo em 10 segundos!"

        if isinstance(result, list) and len(result) > 0:
            text = result[0].get('generated_text', '')
            return text.replace('\n', ' ').strip()[:300]
        
        return "Fiquei sem palavras agora. Podes repetir?"
        
    except Exception as e:
        print(f"Erro HF: {e}")
        return "Opa, tive um curto-circuito. Tenta daqui a pouco!"

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

                if " JOIN " in data and f" JOIN {CHANNEL}" in data:
                    user_nick = data.split('!')[0][1:]
                    ignore = [NICK.lower(), "adamastor", "chanserv", "nickserv", "memoserv"]
                    if user_nick.lower() not in ignore:
                        saudacao = random.choice(SAUDACOES)
                        time.sleep(2)
                        irc.send(f"PRIVMSG {CHANNEL} :{user_nick}: {saudacao}\r\n".encode())

                if "PRIVMSG" in data:
                    parts = data.split(f"PRIVMSG {CHANNEL} :")
                    if len(parts) > 1:
                        msg_full = parts[1]
                        user_talker = data.split('!')[0][1:]
                        
                        if "!noticias" in msg_full.lower():
                            irc.send(f"PRIVMSG {CHANNEL} :📰 [ÚLTIMA HORA]: {get_last_news()}\r\n".encode())
                        
                        elif NICK.lower() in msg_full.lower():
                            pergunta = msg_full.lower().replace(NICK.lower(), "").strip()
                            if pergunta:
                                resposta_ia = get_ai_response(pergunta)
                                irc.send(f"PRIVMSG {CHANNEL} :{user_talker}: {resposta_ia}\r\n".encode())

        except Exception as e:
            print(f"Erro Conexão: {e}")
            time.sleep(20)

if __name__ == "__main__":
    # Flask para manter o serviço ativo
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    start_bot()
