import socket
import time
import threading
import random
from flask import Flask

# --- CONFIGURAÇÕES ---
SERVER = "irc.ptnet.org"
PORT = 6667
NICK = "TheOG"
CHANNEL = "#OG"

# --- LISTA DE FRASES PARA CUMPRIMENTOS (PT-PT) ---
SAUDACOES = [
    "Bem-vindo(a) ao #OG! Esperemos que te divirtas por cá. 😊",
    "Olha quem é! Boas, tudo bem?",
    "Mais um para a família #OG! Sente-te à vontade.",
    "Boas! Se precisares de algo, os OPs estão por aí.",
    "Bem-vindo ao canal mais original da PTnet! 🎧"
]

app = Flask(__name__)

@app.route('/')
def home():
    return "TheOG está acordado e a interagir com o canal!"

def run_web():
    app.run(host='0.0.0.0', port=10000)

def start_bot():
    while True:
        try:
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            irc.settimeout(240)
            
            print(f"Ligar a {SERVER}...")
            irc.connect((SERVER, PORT))
            
            irc.send(f"NICK {NICK}\r\n".encode())
            irc.send(f"USER {NICK} 8 * :Bot Oficial #OG\r\n".encode())
            
            while True:
                try:
                    data = irc.recv(2048).decode("utf-8", errors="ignore")
                    if not data: break
                    
                    if data.startswith("PING"):
                        irc.send(f"PONG {data.split()[1]}\r\n".encode())
                    
                    if "376" in data or "422" in data:
                        irc.send(f"JOIN {CHANNEL}\r\n".encode())

                    # --- DETETAR ENTRADA DE UTILIZADORES ---
                    if "JOIN" in data and NICK not in data:
                        # Extrai o nick de quem entrou
                        user_join = data.split('!')[0][1:]
                        saudacao = random.choice(SAUDACOES)
                        time.sleep(1) # Espera um pouco para não ser instantâneo
                        irc.send(f"PRIVMSG {CHANNEL} :{user_join}: {saudacao}\r\n".encode())

                    # --- COMANDOS ! ---
                    if "PRIVMSG" in data:
                        msg = data.lower()
                        parts = data.split()
                        
                        # Comando !noticias (Exemplo manual ou link)
                        if "!noticias" in msg:
                            # Aqui podes colocar um link ou as últimas de hoje
                            irc.send(f"PRIVMSG {CHANNEL} :📰 [NOTÍCIAS] Podes acompanhar as últimas notícias em: https://www.publico.pt ou https://www.rtp.pt/noticias\r\n".encode())

                        # Comando !ajuda
                        elif "!ajuda" in msg:
                            irc.send(f"PRIVMSG {CHANNEL} :Comandos disponíveis: !noticias, !site, !regras e !theog\r\n".encode())

                        # Comando !site
                        elif "!site" in msg:
                            irc.send(f"PRIVMSG {CHANNEL} :Visita o nosso cantinho na web: (insere aqui o teu link se tiveres)\r\n".encode())

                except socket.timeout:
                    break
        except Exception as e:
            print(f"Erro: {e}. Re-tentando...")
            time.sleep(15)

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    start_bot()
