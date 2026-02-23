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
ADMIN_NICK = "Emergency112"

# API HUGGING FACE
HF_TOKEN = "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"
# Modelo alterado para uma versão mais estável caso a outra esteja em manutenção
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
    return "TheOG AI Status: Online", 200

def get_ai_response(prompt):
    try:
        print(f"[DEBUG] Prompt enviado: {prompt}")
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        
        # Payload simplificado para evitar erros de parsing
        payload = {
            "inputs": f"Pergunta: {prompt}\nResposta curta em português:",
            "parameters": {
                "max_new_tokens": 80,
                "temperature": 0.7,
                "return_full_text": False
            }
        }
        
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=10)
        
        # Log do status code para debug no Render
        print(f"[DEBUG] Status Code: {response.status_code}")
        
        result = response.json()
        
        if response.status_code != 200:
            print(f"[ERRO API] {result}")
            return "Estou a reconfigurar o meu cérebro. Tenta daqui a pouco!"

        if isinstance(result, list) and len(result) > 0:
            text = result[0].get('generated_text', '').strip()
            # Remover repetições da pergunta que o modelo às vezes faz
            text = text.replace(f"Pergunta: {prompt}", "").strip()
            return text if text else "Estou sem palavras, mas estou atento!"
            
        return "A ligação à minha base de dados falhou. Repetes?"
        
    except Exception as e:
        print(f"[EXCEPÇÃO AI]: {e}")
        return "Tive um soluço técnico nos meus servidores."

def get_last_news():
    try:
        feed = feedparser.parse("https://www.rtp.pt/noticias/rss")
        if feed.entries:
            top_3 = feed.entries[:3]
            noticias = [entry.title.strip() for entry in top_3]
            return " | ".join(noticias)
        return "Sem notícias por agora."
    except:
        return "Não consegui ler as notícias."

def start_bot():
    while True:
        try:
            print(f"A ligar a {SERVER}...")
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.settimeout(300)
            irc.connect((SERVER, PORT))
            
            irc.send(f"NICK {NICK}\r\n".encode())
            irc.send(f"USER {NICK} 8 * :Assistente #TheOG\r\n".encode())
            
            while True:
                raw_data = irc.recv(2048)
                if not raw_data: break
                
                data = raw_data.decode("utf-8", errors="ignore")
                
                if data.startswith("PING"):
                    irc.send(f"PONG {data.split()[1]}\r\n".encode())
                    continue

                if "376" in data or "422" in data:
                    irc.send(f"PRIVMSG NickServ :IDENTIFY {PASS}\r\n".encode())
                    time.sleep(2)
                    irc.send(f"JOIN {CHANNEL}\r\n".encode())

                if " JOIN " in data:
                    user_nick = data.split('!')[0][1:]
                    if user_nick.lower() not in [NICK.lower(), "nickserv", "chanserv"]:
                        irc.send(f"PRIVMSG {CHANNEL} :{user_nick}: {random.choice(SAUDACOES)}\r\n".encode())

                if "PRIVMSG" in data:
                    user_talker = data.split('!')[0][1:]
                    if user_talker.lower() == NICK.lower(): continue

                    msg_parts = data.split(f"PRIVMSG {CHANNEL} :", 1)
                    if len(msg_parts) > 1:
                        msg_content = msg_parts[1].strip()

                        if msg_content.lower().startswith("!noticias"):
                            irc.send(f"PRIVMSG {CHANNEL} :📰 {get_last_news()}\r\n".encode())

                        elif NICK.lower() in msg_content.lower():
                            # Limpeza de menções
                            clean_prompt = re.sub(rf'[<@]?{NICK}[:>,]?\s*', '', msg_content, flags=re.IGNORECASE).strip()
                            
                            if not clean_prompt:
                                irc.send(f"PRIVMSG {CHANNEL} :{user_talker}: Diz lá, estou a ouvir!\r\n".encode())
                            else:
                                resposta = get_ai_response(clean_prompt)
                                irc.send(f"PRIVMSG {CHANNEL} :{user_talker}: {resposta}\r\n".encode())

        except Exception as e:
            print(f"Erro de Conexão: {e}")
            time.sleep(20)

if __name__ == "__main__":
    # Inicia o bot em background
    threading.Thread(target=start_bot, daemon=True).start()
    # Flask para o Render não matar o processo
    app.run(host='0.0.0.0', port=10000)
