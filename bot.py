import socket
import time
import threading
from flask import Flask

# --- CONFIGURAÇÕES ---
SERVER = "irc.ptnet.org"
PORT = 6667
NICK = "TheOG"
CHANNEL = "#TheOG"

app = Flask(__name__)

@app.route('/')
def home():
    return "TheOG está acordado e a vigiar o canal!"

def run_web():
    # O Render precisa que o Flask corra na porta 10000
    app.run(host='0.0.0.0', port=10000)

def start_bot():
    while True:
        try:
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1) # Mantém a ligação ativa
            irc.settimeout(240) # Tempo máximo de espera antes de considerar "morto"
            
            print(f"Ligar a {SERVER}...")
            irc.connect((SERVER, PORT))
            
            irc.send(f"NICK {NICK}\r\n".encode())
            irc.send(f"USER {NICK} 8 * :Bot Oficial #OG\r\n".encode())
            
            while True:
                try:
                    data = irc.recv(2048).decode("utf-8", errors="ignore")
                    if not data: break
                    
                    # Responder ao PING imediatamente (Crucial para não levar Quit)
                    if data.startswith("PING"):
                        irc.send(f"PONG {data.split()[1]}\r\n".encode())
                    
                    # Entrar no canal e pedir OP se necessário
                    if "376" in data or "422" in data:
                        irc.send(f"JOIN {CHANNEL}\r\n".encode())
                        # Se o nick estiver registado, podes adicionar a linha de senha aqui
                        
                    # Auto-Rejoin se for expulso (Kick)
                    if f"KICK {CHANNEL} {NICK}" in data:
                        time.sleep(2)
                        irc.send(f"JOIN {CHANNEL}\r\n".encode())

                except socket.timeout:
                    print("Timeout! A reiniciar...")
                    break
        except Exception as e:
            print(f"Erro: {e}. A tentar novamente em 15s...")
            time.sleep(15)

if __name__ == "__main__":
    # Inicia o servidor Web primeiro para o Render ficar feliz
    threading.Thread(target=run_web, daemon=True).start()
    # Inicia o Bot no processo principal
    start_bot()
