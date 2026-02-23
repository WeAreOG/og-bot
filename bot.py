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
        # Log para debug no Render
        print(f"[AI DEBUG] Enviando para HF: {prompt}")
        
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload = {
            "inputs": f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nÉs o TheOG, um assistente divertido do canal #TheOG. Responde sempre em português de Portugal. Sê breve e direto.<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
            "parameters": {
                "max_new_tokens": 100,
                "temperature": 0.7,
                "top_p": 0.9,
                "return_full_text": False
            }
        }
        
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=12)
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            text = result[0].get('generated_text', '').strip()
            # Limpeza básica de quebras de linha
            text = text.replace('\n', ' ')
            print(f"[AI DEBUG] Resposta recebida: {text}")
            return text if len(text) > 1 else "Estou sem ideias agora, mas estou aqui!"
        
        return "Os meus circuitos estão ocupados. Podes repetir?"
    except Exception as e:
        print(f"[ERRO AI]: {e}")
        return "Tive um pequeno precalço técnico. Diz de novo!"

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
                    
                    # Evitar que o bot responda a ele próprio
                    if user_talker.lower() == NICK.lower():
                        continue

                    msg_parts = data.split(f"PRIVMSG {CHANNEL} :", 1)
                    if len(msg_parts) > 1:
                        msg_content = msg_parts[1].strip()

                        # Comando !noticias
                        if msg_content.lower().startswith("!noticias"):
                            irc.send(f"PRIVMSG {CHANNEL} :📰 {get_last_news()}\r\n".encode())

                        # Interação com AI
                        elif NICK.lower() in msg_content.lower():
                            # Remove menções como <@TheOG>, TheOG:, TheOG, etc.
                            clean_prompt = re.sub(rf'[<@]?{NICK}[:>,]?\s*', '', msg_content, flags=re.IGNORECASE).strip()
                            
                            # Se sobrar apenas lixo ou estiver vazio, não vai à IA
                            if not clean_prompt or len(clean_prompt) < 2:
                                irc.send(f"PRIVMSG {CHANNEL} :{user_talker}: Sim? Se precisares de algo, diz-me. Ou usa !noticias\r\n".encode())
                            else:
                                resposta = get_ai_response(clean_prompt)
                                irc.send(f"PRIVMSG {CHANNEL} :{user_talker}: {resposta}\r\n".encode())

        except Exception as e:
            print(f"Erro de Conexão: {e}")
            time.sleep(20)

if __name__ == "__main__":
    threading.Thread(target=start_bot, daemon=True).start()
    # Porta padrão para o Render
    app.run(host='0.0.0.0', port=10000)
