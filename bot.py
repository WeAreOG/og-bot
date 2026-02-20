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
PASS = "A_TUA_SENHA_AQUI"  # <--- SUBSTITUI PELA SENHA QUE DEFINISTE NO NICKSERV
CHANNEL = "#TheOG"
ADMIN_NICK = "Emergency112"

SAUDACOES = [
    "Bem-vindo(a) ao #TheOG! 😊",
    "Olha quem é! Boas, tudo bem?",
    "Sente-te à vontade no nosso canal! 🎧",
    "Boas! É um prazer ter-te por cá.",
    "Olá! Mais um membro para a equipa #TheOG!"
]

app = Flask(__name__)

@app.route('/')
def home():
    return f"TheOG Operacional - Admin: {ADMIN_NICK}"

def get_last_news():
    try:
        # Busca notícias reais da RTP (Última Hora)
        feed = feedparser.parse("https://www.rtp.pt/noticias/rss")
        if feed.entries:
            # Pegamos nas 3 notícias mais recentes
            top_3 = feed.entries[:3]
            noticias = []
            for entry in top_3:
                # Limpa o título de espaços extra
                noticias.append(entry.title.strip())
            return " | ".join(noticias)
        return "Sem notícias de momento."
    except Exception:
        return "Erro ao aceder ao serviço de notícias."

def start_bot():
    while True:
        try:
            print(f"A ligar a {SERVER}...")
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.settimeout(120)
            irc.connect((SERVER, PORT))
            
            # Login Inicial
            irc.send(f"NICK {NICK}\r\n".encode())
            irc.send(f"USER {NICK} 8 * :Ferramenta de Gestao #TheOG\r\n".encode())
            
            while True:
                data = irc.recv(2048).decode("utf-8", errors="ignore")
                if not data: break
                
                # Responder ao PING (Crucial para não cair)
                if data.startswith("PING"):
                    irc.send(f"PONG {data.split()[1]}\r\n".encode())

                # Quando o servidor está pronto (End of MOTD)
                if "376" in data or "422" in data:
                    # 1. Identificar com o NickServ
                    print("A identificar com o NickServ...")
                    irc.send(f"PRIVMSG NickServ :IDENTIFY {PASS}\r\n".encode())
                    time.sleep(3) # Pausa para o servidor processar a senha
                    
                    # 2. Entrar no Canal
                    irc.send(f"JOIN {CHANNEL}\r\n".encode())
                    time.sleep(1)
                    
                    # 3. Mensagem de Boas-vindas ao Admin
                    irc.send(f"PRIVMSG {CHANNEL} :[SISTEMA] TheOG Identificado e Online. Comandante {ADMIN_NICK}, estou ao seu dispor! 🚀\r\n".encode())

                # CUMPRIMENTOS: Deteta a entrada de utilizadores
                if " JOIN " in data:
                    user_nick = data.split('!')[0][1:]
                    # Evita que o bot se cumprimente a si próprio
                    if user_nick.lower() != NICK.lower():
                        saudacao = random.choice(SAUDACOES)
                        time.sleep(2) # Delay para parecer humano
                        irc.send(f"PRIVMSG {CHANNEL} :{user_nick}: {saudacao}\r\n".encode())

                # COMANDOS DE CHAT
                if "PRIVMSG" in data:
                    msg = data.lower()
                    
                    # Comando !noticias
                    if "!noticias" in msg:
                        txt_noticias = get_last_news()
                        irc.send(f"PRIVMSG {CHANNEL} :📰 [ÚLTIMA HORA]: {txt_noticias}\r\n".encode())
                    
                    # Comando !ajuda
                    elif "!ajuda" in msg:
                        irc.send(f"PRIVMSG {CHANNEL} :Comandos: !noticias | !status | !ajuda\r\n".encode())

                    # Comando !status
                    elif "!status" in msg:
                        irc.send(f"PRIVMSG {CHANNEL} :[STATUS] Ligado a {SERVER}. Admin: {ADMIN_NICK}. Servidor: Render Frankfurt.\r\n".encode())

        except Exception as e:
            print(f"Erro: {e}. A tentar reconectar em 20 segundos...")
            time.sleep(20)

if __name__ == "__main__":
    # Servidor Web para o Render e Cron-job não deixarem o bot dormir
    web_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True)
    web_thread.start()
    
    # Inicia o Bot
    start_bot()
