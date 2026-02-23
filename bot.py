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
    # O Render precisa que esta rota responda 200 OK para manter o bot vivo
    return "TheOG AI Status: Online e Operacional", 200

def get_ai_response(prompt):
    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload = {
            "inputs": f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nÉs o assistente do canal #TheOG. Responde de forma curta e amigável em português.<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
            "parameters": {
                "max_new_tokens": 150,
                "temperature": 0.7,
                "top_p": 0.9,
                "return_full_text": False
            }
        }
        
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=10)
        result = response.json()
        
        if isinstance(result, dict) and "estimated_time" in result:
            return "Estou a carregar os meus módulos... tenta de novo em breve!"

        if isinstance(result, list) and len(result) > 0:
            text = result[0].get('generated_text', '')
            return text.replace('\n', ' ').strip()[:300]
        
        return "Estou um pouco confuso, podes repetir?"
    except:
        return "Tive um pequeno soluço técnico. Tenta outra vez!"

def get_last_news():
    try:
        # User-agent ajuda a evitar bloqueios de bots no RSS
        feed = feedparser.parse("https://www.rtp.pt/noticias/rss")
        if feed.entries:
            top_3 = feed.entries[:3]
            noticias = [entry.title.strip() for entry in top_3]
            return " | ".join(noticias)
        return "Não consegui encontrar notícias frescas agora."
    except Exception as e:
        print(f"Erro RSS: {e}")
        return "O serviço de notícias está temporariamente indisponível."

def start_bot():
    while True:
        try:
            print(f"A conectar a {SERVER}...")
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.settimeout(240) # Aumentado o timeout
            irc.connect((SERVER, PORT))
            
            irc.send(f"NICK {NICK}\r\n".encode())
            irc.send(f"USER {NICK} 8 * :Assistente AI #TheOG\r\n".encode())
            
            while True:
                try:
                    raw_data = irc.recv(2048)
                    if not raw_data:
                        break
                    
                    data = raw_data.decode("utf-8", errors="ignore")
                    
                    # Responder ao PING imediatamente para não cair
                    if data.startswith("PING"):
                        irc.send(f"PONG {data.split()[1]}\r\n".encode())
                        continue

                    # Mensagens do sistema e NickServ
                    if "433" in data: # Nick em uso
                        irc.send(f"PRIVMSG NickServ :GHOST {NICK} {PASS}\r\n".encode())
                        time.sleep(1)
                        irc.send(f"NICK {NICK}\r\n".encode())

                    if "376" in data or "422" in data: # Fim do MOTD
                        irc.send(f"PRIVMSG NickServ :IDENTIFY {PASS}\r\n".encode())
                        time.sleep(2)
                        irc.send(f"JOIN {CHANNEL}\r\n".encode())

                    # Lógica de SAUDAÇÃO (Corrigida para ser mais sensível ao JOIN)
                    if " JOIN " in data:
                        # Extrair nick: :Nick!User@Host JOIN #Canal
                        try:
                            user_nick = data.split('!')[0][1:]
                            if user_nick.lower() not in [NICK.lower(), "adamastor", "chanserv", "nickserv"]:
                                saudacao = random.choice(SAUDACOES)
                                time.sleep(1) # Pequena pausa para parecer natural
                                irc.send(f"PRIVMSG {CHANNEL} :{user_nick}: {saudacao}\r\n".encode())
                        except:
                            pass

                    # Lógica de COMANDOS e AI
                    if "PRIVMSG" in data:
                        # Verifica se a mensagem é para o canal ou para o bot
                        if f"PRIVMSG {CHANNEL}" in data:
                            parts = data.split(f"PRIVMSG {CHANNEL} :", 1)
                            user_talker = data.split('!')[0][1:]
                            msg_content = parts[1].strip() if len(parts) > 1 else ""

                            # Comando Notícias
                            if msg_content.lower().startswith("!noticias"):
                                news = get_last_news()
                                irc.send(f"PRIVMSG {CHANNEL} :📰 [RTP NOTÍCIAS]: {news}\r\n".encode())

                            # Resposta AI (se chamarem o nome do bot)
                            elif NICK.lower() in msg_content.lower():
                                prompt = msg_content.lower().replace(NICK.lower(), "").strip()
                                if prompt:
                                    resposta = get_ai_response(prompt)
                                    irc.send(f"PRIVMSG {CHANNEL} :{user_talker}: {resposta}\r\n".encode())

                except socket.timeout:
                    print("Timeout da conexão, a tentar manter vivo...")
                    irc.send(f"PING {SERVER}\r\n".encode())
                except Exception as e:
                    print(f"Erro no processamento de dados: {e}")
                    break

        except Exception as e:
            print(f"Erro de Conexão: {e}")
            time.sleep(15) # Espera antes de tentar reconectar

if __name__ == "__main__":
    # 1. Iniciamos o Bot de IRC numa Thread separada
    irc_thread = threading.Thread(target=start_bot, daemon=True)
    irc_thread.start()
    
    # 2. Iniciamos o Flask no processo principal
    # O Render exige que o processo principal escute na porta definida
    port = int(random.randint(10000, 10100)) # O Render geralmente fornece a porta na env PORT
    # Em produção no Render, usa: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
    app.run(host='0.0.0.0', port=10000)
