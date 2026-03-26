import socket
import time
import threading
import os
import random
import logging
import sys
import json
from datetime import datetime
from flask import Flask

# --- CONFIGURAÇÃO DE LOGS ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
def force_log(msg):
    print(msg)
    sys.stdout.flush()

# --- CONFIGURAÇÃO ---
SERVER = "irc.ptnet.org"
PORT = 6667
NICK = "TheOG"
PASS = "Nasomet112#"
CHANNEL = "#TheOG"
ADMINS = ["Emergency112", "Padre", "CutxiiiPoint"]

# --- ESTADO ---
START_TIME = datetime.now()
users_online = []
dados = {
    "saudacoes_comuns": ["Olá {u}!", "Boas {u}!", "Viva {u}!"],
    "saudacoes_admins": ["Grande {u}! Bem-vindo, Chefe!", "Viva {u}! O canal é teu."],
    "puxar_conversa": ["Como corre isso, {u}?", "{u}: novidades?", "Tudo calmo, {u}?"],
    "respostas_gerais": ["Diz lá, {u}!", "Estou a ouvir, {u}.", "Fala comigo!", "Tudo operacional por aqui."],
    "frases_entrada": ["TheOG Online e atento!"],
}

def get_uptime():
    return str(datetime.now() - START_TIME).split('.')[0]

# --- MOTOR DE ENVIO (CADÊNCIA DE 1.5s - Equilibrado) ---
def send(irc, msg):
    try:
        irc.send(f"{msg}\r\n".encode('utf-8'))
        time.sleep(1.5) 
    except:
        pass

# --- TAREFA SOCIAL (20 MINUTOS) ---
def social_cycle(irc):
    while True:
        time.sleep(1200)
        if users_online:
            outros = [u for u in users_online if u != NICK and len(u) > 1]
            if outros:
                alvo = random.choice(outros)
                frase = random.choice(dados["puxar_conversa"]).format(u=alvo)
                send(irc, f"PRIVMSG {CHANNEL} :{frase}")

# --- RECEPTOR E RESPOSTA (O CORAÇÃO DO BOT) ---
def handle_msg(user, message, is_private, irc):
    msg = message.lower().strip()
    target = user if is_private else CHANNEL
    
    force_log(f"MENSAGEM DE {user}: {message}")

    # 1. Resposta a Comandos
    if msg == "!uptime":
        send(irc, f"PRIVMSG {target} :🚀 Uptime: {get_uptime()}")
        return

    # 2. Resposta quando o chamam pelo nome ou falam em privado
    if NICK.lower() in msg or is_private:
        # Se for um admin, ele pode ser mais respeitoso
        if user in ADMINS:
            resposta = f"Com certeza, Chefe {user}. Em que posso ajudar?"
        else:
            resposta = random.choice(dados["respostas_gerais"]).format(u=user)
        
        send(irc, f"PRIVMSG {target} :{resposta}")
        force_log(f"RESPONDIDO A {user}: {resposta}")

# --- WEB SERVER ---
app = Flask(__name__)
@app.route('/')
def home(): return "TheOG Bot Ativo"

# --- BOT CORE ---
def run_bot():
    global users_online
    while True:
        try:
            force_log("--- A LIGAR ---")
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.settimeout(240)
            irc.connect((SERVER, PORT))
            
            # Login
            irc.send(f"PASS {PASS}\r\n".encode())
            irc.send(f"NICK {NICK}\r\n".encode())
            irc.send(f"USER {NICK} 8 * :TheOG Manager\r\n".encode())
            
            threading.Thread(target=social_cycle, args=(irc,), daemon=True).start()

            while True:
                buffer = irc.recv(4096).decode("utf-8", errors="ignore")
                if not buffer: break
                
                for line in buffer.split("\r\n"):
                    if not line: continue
                    
                    if line.startswith("PING"):
                        irc.send(f"PONG {line.split()[1]}\r\n".encode())
                        continue

                    # Recuperação de Nick
                    if " 433 " in line:
                        irc.send(f"NICK {NICK}_{random.randint(10,99)}\r\n".encode())
                        time.sleep(2)
                        send(irc, f"PRIVMSG NickServ :GHOST {NICK} {PASS}")
                        time.sleep(2)
                        irc.send(f"NICK {NICK}\r\n".encode())

                    # Entrar no canal após MOTD
                    if " 376 " in line or " 422 " in line:
                        send(irc, f"PRIVMSG NickServ :IDENTIFY {PASS}")
                        send(irc, f"JOIN {CHANNEL}")
                        send(irc, f"NAMES {CHANNEL}")

                    # Lista de Users
                    if " 353 " in line:
                        nicks = line.split(" :")[1].split()
                        users_online = [n.strip("@+ ") for n in nicks]

                    # Entradas
                    if " JOIN " in line and CHANNEL in line:
                        u = line.split('!')[0][1:]
                        if u != NICK:
                            if u not in users_online: users_online.append(u)
                            if u != "Emergency112": # Silêncio para ti
                                msg_s = random.choice(dados["saudacoes_admins" if u in ADMINS else "saudacoes_comuns"]).format(u=u)
                                send(irc, f"PRIVMSG {CHANNEL} :{msg_s}")

                    # MENSAGENS (PRIVMSG) - Processamento Reforçado
                    if " PRIVMSG " in line:
                        try:
                            # Extrair o nick: :Nick!user@host PRIVMSG target :message
                            user_nick = line.split('!')[0][1:]
                            target = line.split(' PRIVMSG ')[1].split(' :')[0]
                            content = line.split(' PRIVMSG ')[1].split(' :', 1)[1]
                            
                            handle_msg(user_nick, content, target == NICK, irc)
                        except Exception as e:
                            force_log(f"Erro ao processar linha: {e}")

        except Exception as e:
            force_log(f"ERRO: {e}")
        finally:
            if irc: irc.close()
            time.sleep(15)

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000))), daemon=True).start()
    run_bot()
