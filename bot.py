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
    return "TheOG AI Status: Online e Operacional", 200

def get_ai_response(prompt):
    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        # Melhoria no System Prompt para ser mais direto
        payload = {
            "inputs": f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nÉs o assistente amigável do canal #TheOG. Responde sempre em português de Portugal de forma breve.<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
            "parameters": {
                "max_new_tokens": 150,
                "temperature": 0.8,
                "top_p": 0.9,
                "return_full_text": False
            }
        }
        
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=12)
        result = response.json()
        
        if isinstance(result, dict) and "estimated_time" in result:
            return "Estou a processar muita informação... pergunta-me outra vez em 10 segundos!"

        if isinstance(result, list) and len(result) > 0:
            text = result[0].get('generated_text', '')
            res = text.replace('\n', ' ').strip()
            return res[:300] if res else "Diz-me mais sobre isso!"
        
        return "Não percebi bem, podes reformular?"
    except Exception as e:
        print(f"Erro AI: {e}")
        return "Tive um pequeno curto-circuito cerebral. Tenta de novo!"

def get_last_news():
    try:
        feed = feedparser.parse("https://www.rtp.pt/noticias/rss")
        if feed.entries:
            top_3 = feed.entries[:3]
            noticias = [entry.title.strip() for entry in top_3]
            return " | ".join(noticias)
        return "Sem notícias frescas por agora."
    except Exception as e:
        print(f"Erro RSS: {e}")
        return "O feed de notícias está temporariamente offline."

def start_bot():
    while True:
        try:
            print(f"A ligar a {SERVER}...")
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.settimeout(300) 
            irc.connect((SERVER, PORT))
            
            irc.send(f"NICK {NICK}\r\n".encode())
            irc.send(f"USER {NICK} 8 * :Assistente AI #TheOG\r\n".encode())
            
            while True:
                try:
                    raw_data = irc.recv(2048)
                    if not raw_data:
                        break
                    
                    data = raw_data.decode("utf-8", errors="ignore")
                    
                    # Keep-alive PING/PONG
                    if data.startswith("PING"):
                        irc.send(f"PONG {data.split()[1]}\r\n".encode())
                        continue

                    # Autenticação e Entrada
                    if "433" in data:
                        irc.send(f"PRIVMSG NickServ :GHOST {NICK} {PASS}\r\n".encode())
                        time.sleep(1)
                        irc.send(f"NICK {NICK}\r\n".encode())

                    if "376" in data or "422" in data:
                        irc.send(f"PRIVMSG NickServ :IDENTIFY {PASS}\r\n".encode())
                        time.sleep(2)
                        irc.send(f"JOIN {CHANNEL}\r\n".encode())

                    # Boas-vindas a novos membros
                    if " JOIN " in data:
                        user_nick = data.split('!')[0][1:]
                        if user_nick.lower() not in [NICK.lower(), "chanserv", "nickserv"]:
                            print(f"Novo utilizador detetado: {user_nick}")
                            saudacao = random.choice(SAUDACOES)
                            time.sleep(2)
                            irc.send(f"PRIVMSG {CHANNEL} :{user_nick}: {saudacao}\r\n".encode())

                    # Processamento de Mensagens
                    if "PRIVMSG" in data:
                        user_talker = data.split('!')[0][1:]
                        # Extrair o conteúdo da mensagem após o segundo ':'
                        msg_parts = data.split(f"PRIVMSG {CHANNEL} :", 1)
                        
                        if len(msg_parts) > 1:
                            msg_content = msg_parts[1].strip()
                            print(f"Mensagem de {user_talker}: {msg_content}")

                            # 1. Comando Notícias
                            if msg_content.lower().startswith("!noticias"):
                                news = get_last_news()
                                irc.send(f"PRIVMSG {CHANNEL} :📰 [RTP]: {news}\r\n".encode())

                            # 2. Interação com AI
                            elif NICK.lower() in msg_content.lower():
                                # Remove o nome do bot e pontuação comum para limpar o prompt
                                clean_prompt = msg_content.lower().replace(NICK.lower(), "").strip()
                                clean_prompt = clean_prompt.lstrip(':').lstrip(',').strip()
                                
                                if clean_prompt:
                                    resposta = get_ai_response(clean_prompt)
                                    irc.send(f"PRIVMSG {CHANNEL} :{user_talker}: {resposta}\r\n".encode())
                                else:
                                    irc.send(f"PRIVMSG {CHANNEL} :{user_talker}: Olá! Em que posso ajudar? Podes usar !noticias ou falar comigo.\r\n".encode())

                except socket.timeout:
                    irc.send(f"PING {SERVER}\r\n".encode())
                except Exception as e:
                    print(f"Erro interno: {e}")
                    break

        except Exception as e:
            print(f"Erro de Conexão: {e}")
            time.sleep(20)

if __name__ == "__main__":
    # Inicia o bot em segundo plano
    threading.Thread(target=start_bot, daemon=True).start()
    
    # O Render precisa que o Flask rode no host 0.0.0.0 e porta 10000 (padrão)
    print("A iniciar servidor Health Check...")
    app.run(host='0.0.0.0', port=10000)
