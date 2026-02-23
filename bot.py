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
    return "TheOG AI Status: Online e Operacional", 200

def get_ai_response(prompt):
    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        # Prompt mais robusto para evitar respostas de confusão
        payload = {
            "inputs": f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nÉs o assistente do canal IRC #TheOG. Responde de forma curta, prestável e sempre em português de Portugal.<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
            "parameters": {
                "max_new_tokens": 150,
                "temperature": 0.7,
                "top_p": 0.9,
                "return_full_text": False
            }
        }
        
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=15)
        result = response.json()
        
        if isinstance(result, dict) and "estimated_time" in result:
            return "Estou a processar... tenta de novo em 10 segundos!"

        if isinstance(result, list) and len(result) > 0:
            text = result[0].get('generated_text', '')
            res = text.replace('\n', ' ').strip()
            return res[:300] if len(res) > 2 else "Estou aqui! O que precisas?"
        
        return "Diz-me algo mais específico para eu te conseguir ajudar!"
    except Exception as e:
        print(f"Erro AI: {e}")
        return "Tive um soluço técnico. Podes repetir a pergunta?"

def get_last_news():
    try:
        feed = feedparser.parse("https://www.rtp.pt/noticias/rss")
        if feed.entries:
            top_3 = feed.entries[:3]
            noticias = [entry.title.strip() for entry in top_3]
            return " | ".join(noticias)
        return "Sem notícias de última hora."
    except Exception as e:
        print(f"Erro RSS: {e}")
        return "Não consegui aceder às notícias agora."

def start_bot():
    while True:
        try:
            print(f"A conectar a {SERVER}...")
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.settimeout(300)
            irc.connect((SERVER, PORT))
            
            irc.send(f"NICK {NICK}\r\n".encode())
            irc.send(f"USER {NICK} 8 * :Assistente AI #TheOG\r\n".encode())
            
            while True:
                try:
                    raw_data = irc.recv(2048)
                    if not raw_data: break
                    
                    data = raw_data.decode("utf-8", errors="ignore")
                    
                    if data.startswith("PING"):
                        irc.send(f"PONG {data.split()[1]}\r\n".encode())
                        continue

                    if "433" in data:
                        irc.send(f"PRIVMSG NickServ :GHOST {NICK} {PASS}\r\n".encode())
                        time.sleep(1)
                        irc.send(f"NICK {NICK}\r\n".encode())

                    if "376" in data or "422" in data:
                        irc.send(f"PRIVMSG NickServ :IDENTIFY {PASS}\r\n".encode())
                        time.sleep(2)
                        irc.send(f"JOIN {CHANNEL}\r\n".encode())

                    # Boas-vindas corrigidas
                    if " JOIN " in data:
                        user_nick = data.split('!')[0][1:]
                        if user_nick.lower() not in [NICK.lower(), "chanserv", "nickserv"]:
                            saudacao = random.choice(SAUDACOES)
                            time.sleep(2)
                            irc.send(f"PRIVMSG {CHANNEL} :{user_nick}: {saudacao}\r\n".encode())

                    # Mensagens e Comandos
                    if "PRIVMSG" in data:
                        user_talker = data.split('!')[0][1:]
                        msg_parts = data.split(f"PRIVMSG {CHANNEL} :", 1)
                        
                        if len(msg_parts) > 1:
                            msg_content = msg_parts[1].strip()

                            # Comando !noticias
                            if msg_content.lower().startswith("!noticias"):
                                news = get_last_news()
                                irc.send(f"PRIVMSG {CHANNEL} :📰 {news}\r\n".encode())

                            # Resposta AI (Limpeza de menções agressiva)
                            elif NICK.lower() in msg_content.lower():
                                # Remove tags de menção do tipo <@TheOG>, TheOG:, TheOG, etc.
                                clean_prompt = re.sub(rf'[<@]?{NICK}[:>,]?\s*', '', msg_content, flags=re.IGNORECASE).strip()
                                
                                if clean_prompt:
                                    resposta = get_ai_response(clean_prompt)
                                    irc.send(f"PRIVMSG {CHANNEL} :{user_talker}: {resposta}\r\n".encode())
                                else:
                                    # Se apenas chamarem o nome sem texto
                                    irc.send(f"PRIVMSG {CHANNEL} :{user_talker}: Sim? Se precisares de ajuda diz algo ou usa !noticias\r\n".encode())

                except socket.timeout:
                    irc.send(f"PING {SERVER}\r\n".encode())
                except Exception as e:
                    print(f"Erro no loop: {e}")
                    break

        except Exception as e:
            print(f"Erro de Conexão: {e}")
            time.sleep(20)

if __name__ == "__main__":
    # Inicia o bot
    threading.Thread(target=start_bot, daemon=True).start()
    # Flask para o Render
    app.run(host='0.0.0.0', port=10000)
