import socket
import time
import threading
from flask import Flask

# --- CONFIGURAÇÕES DA PTNET ---
SERVER = "irc.ptnet.org"
PORT = 6667
NICK = "TheOG"
CHANNEL = "#TheOG"
USER = "TheOG 0 * :Bot oficial do Canal #OG"

# --- CONFIGURAÇÃO PARA O RENDER ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot TheOG Online na PTnet!"

def run_web():
    # O Render utiliza a porta 10000 por defeito
    app.run(host='0.0.0.0', port=10000)

# --- LÓGICA DO BOT IRC ---
def connect_irc():
    while True:
        try:
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.settimeout(300)
            print(f"A ligar a {SERVER} como {NICK}...")
            irc.connect((SERVER, PORT))
            
            irc.send(f"NICK {NICK}\r\n".encode())
            irc.send(f"USER {USER}\r\n".encode())
            return irc
        except Exception as e:
            print(f"Erro na conexão: {e}. A tentar novamente em 10s...")
            time.sleep(10)

def start_bot():
    irc = connect_irc()
    
    while True:
        try:
            data = irc.recv(2048).decode("utf-8", errors="ignore")
            if not data:
                irc = connect_irc()
                continue
            
            # Responder ao PING do servidor
            if data.startswith("PING"):
                irc.send(f"PONG {data.split()[1]}\r\n".encode())
            
            # Entrar no canal após o final do MOTD
            if "376" in data or "422" in data:
                irc.send(f"JOIN {CHANNEL}\r\n".encode())
                print(f"TheOG entrou com sucesso em {CHANNEL}")

            # COMANDOS NO CANAL
            if "PRIVMSG" in data:
                msg = data.lower()
                
                # Resposta ao comando !theog
                if "!theog" in msg:
                    irc.send(f"PRIVMSG {CHANNEL} :Olá! Eu sou o TheOG, o bot oficial deste canal. Respeita as regras e diverte-te!\r\n".encode())
                
                # Resposta ao comando !info
                elif "!info" in msg:
                    irc.send(f"PRIVMSG {CHANNEL} :Canal #OG - O som original da PTnet. Bot alojado na Cloud 24/7.\r\n".encode())

        except Exception as e:
            print(f"Erro no loop: {e}")
            irc = connect_irc()

if __name__ == "__main__":
    # Inicia o servidor web em background
    threading.Thread(target=run_web).start()
    # Inicia o Bot
    start_bot()
