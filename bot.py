import socket
import time
import threading
import random
import feedparser
from flask import Flask

# --- CONFIGURAÇÕES DE TRABALHO ---
SERVER = "irc.ptnet.org"
PORT = 6667
NICK = "TheOG"
CHANNEL = "#TheOG"  # Atualizado para o canal correto
ADMIN_NICK = "Emergency112" # O teu nick de controlo

SAUDACOES = [
    "Bem-vindo(a) ao #TheOG! 😊",
    "Olha quem é! Boas, tudo bem?",
    "Sente-te à vontade no nosso canal! 🎧",
    "Boas! É um prazer ter-te por cá."
]

app = Flask(__name__)

@app.route('/')
def home():
    return "TheOG Operacional - Administrador: Emergency112"

def get_last_news():
    try:
        # Busca notícias reais da RTP (Última Hora)
        feed = feedparser.parse("https://www.rtp.pt/noticias/rss")
        if feed.entries:
            # Pegamos nas 3 notícias mais recentes
            top_3 = feed.entries[:3]
            noticias = []
            for entry in top_3:
                noticias.append(entry.title)
            return " | ".join(noticias)
        return "Sem notícias de momento."
    except Exception as e:
        return "Erro ao aceder ao serviço de notícias."

def start_bot():
    while True:
        try:
            print(f"A ligar a {SERVER}...")
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.settimeout(120)
            irc.connect((SERVER, PORT))
            
            irc.send(f"NICK {NICK}\r\n".encode())
            irc.send(f"USER {NICK} 8 * :Ferramenta de Gestao #TheOG\r\n".encode())
            
            while True:
                data = irc.recv(2048).decode("utf-8", errors="ignore")
                if not data: break
                
                # Responder ao PING para manter a ligação ativa
                if data.startswith("PING"):
                    irc.send(f"PONG {data.split()[1]}\r\n".encode())

                # Quando o servidor dá o sinal de prontidão
                if "376" in data or "422" in data:
                    irc.send(f"JOIN {CHANNEL}\r\n".encode())
                    time.sleep(1)
                    # Relatório de entrada para o Admin
                    irc.send(f"PRIVMSG {CHANNEL} :[SISTEMA] TheOG Online. Comandante {ADMIN_NICK}, estou ao seu dispor! 🚀\r\n".encode())

                # CUMPRIMENTOS: Deteta a entrada de utilizadores
                if " JOIN " in data:
                    # Extração precisa do nick
                    user_nick = data.split('!')[0][1:]
                    if user_nick.lower() != NICK.lower():
                        saudacao = random.choice(SAUDACOES)
                        time.sleep(1.5) # Pausa natural
                        irc.send(f"PRIVMSG {CHANNEL} :{user_nick}: {saudacao}\r\n".encode())

                # COMANDOS DE CHAT
                if "PRIVMSG" in data:
                    msg = data.lower()
                    
                    # Comando de Notícias em Tempo Real
                    if "!noticias" in msg:
                        txt_noticias = get_last_news()
                        irc.send(f"PRIVMSG {CHANNEL} :📰 [ÚLTIMA HORA]: {txt_noticias}\r\n".encode())
                    
                    # Comando de Ajuda
                    elif "!ajuda" in msg:
                        irc.send(f"PRIVMSG {CHANNEL} :Comandos ativos: !noticias | !ajuda | !status\r\n".encode())

                    # Comando de Status (para controlo)
                    elif "!status" in msg:
                        irc.send(f"PRIVMSG {CHANNEL} :[STATUS] Sistema estável em Frankfurt. Admin: {ADMIN_NICK}.\r\n".encode())

        except Exception as e:
            print(f"Erro de ligação: {e}. A reiniciar em 20s...")
            time.sleep(20)

if __name__ == "__main__":
    # Inicia o Flask para o Render não adormecer o bot
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    start_bot()
