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

# --- CONFIGURAÇÃO DE LOGS (PARA RENDER) ---
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
# Lista de Operadores/Admins
ADMINS = ["Emergency112", "Padre", "CutxiiiPoint"]

# --- ESTADO ---
START_TIME = datetime.now()
users_online = []
dados = {
    "saudacoes_comuns": ["Olá {u}!", "Boas {u}, bem-vindo!", "Viva {u}!"],
    "saudacoes_admins": [
        "Grande {u}! O canal está agora em boas mãos. Bem-vindo, Chefe!",
        "Olha quem chegou para por ordem nisto: Viva {u}!",
        "Boas, {u}! Estávamos à tua espera para animar o #TheOG!"
    ],
    "puxar_conversa": ["Como corre isso, {u}?", "{u}: novidades?", "Tudo calmo por aqui, {u}?"],
    "frases_entrada": ["TheOG Online!", "Pronto para a ação."],
    "convites": ["Ei {u}, junta-te a nós no #TheOG!"]
}

def get_uptime():
    return str(datetime.now() - START_TIME).split('.')[0]

# --- MOTOR DE ENVIO (EQUILIBRADO - 2s) ---
def send(irc, msg):
    try:
        irc.send(f"{msg}\r\n".encode('utf-8'))
        time.sleep(2.0) 
    except:
        pass

# --- TAREFA SOCIAL (A CADA 20 MINUTOS) ---
def social_cycle(irc):
    while True:
        time.sleep(1200)
        if users_online:
            outros = [u for u in users_online if u != NICK and len(u) > 1]
            if outros:
                alvo = random.choice(outros)
                frase = random.choice(dados["puxar_conversa"]).format(u=alvo)
                send(irc, f"PRIVMSG {CHANNEL} :{frase}")
                force_log(f"SOCIAL: Interação com {alvo}")

# --- COMANDOS ---
def handle_msg(user, message, is_private, irc):
    msg = message.lower().strip()
    target = user if is_private else CHANNEL
    
    if msg == "!uptime":
        send(irc, f"PRIVMSG {target} :🚀 Online há: {get_uptime()}")
    
    elif msg.startswith("!convidar "):
        partes = msg.split()
        if len(partes) > 1:
            alvo = partes[1]
            frase = random.choice(dados["convites"]).format(u=alvo)
            send(irc, f"PRIVMSG {alvo} :{frase}")
            force_log(f"CONVITE: {user} convidou {alvo}")

# --- WEB SERVER (PARA O RENDER) ---
app = Flask(__name__)
@app.route('/')
def home(): return f"TheOG Ativo | Admins: Padre, CutxiiiPoint, Emergency112"

# --- BOT CORE ---
def run_bot():
    global users_online
    while True:
        try:
            force_log("--- A LIGAR AO SERVIDOR (EQUILIBRADO) ---")
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.settimeout(240)
            irc.connect((SERVER, PORT))
            
            # Login Faseado para evitar Flood
            irc.send(f"PASS {PASS}\r\n".encode())
            time.sleep(1)
            irc.send(f"NICK {NICK}\r\n".encode())
            time.sleep(1)
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

                    # Recuperação de Nick (Ghost)
                    if " 433 " in line:
                        force_log("AVISO: Nick ocupado. Recuperando...")
                        irc.send(f"NICK {NICK}_{random.randint(10,99)}\r\n".encode())
                        time.sleep(2)
                        send(irc, f"PRIVMSG NickServ :GHOST {NICK} {PASS}")
                        time.sleep(3)
                        irc.send(f"NICK {NICK}\r\n".encode())

                    # Fim do MOTD - Entrar no Canal
                    if " 376 " in line or " 422 " in line:
                        force_log("CONECTADO. Entrando no canal...")
                        send(irc, f"PRIVMSG NickServ :IDENTIFY {PASS}")
                        send(irc, f"JOIN {CHANNEL}")
                        send(irc, f"NAMES {CHANNEL}")
                        entrada = random.choice(dados["frases_entrada"])
                        send(irc, f"PRIVMSG {CHANNEL} :{entrada}")

                    # Lista de Utilizadores
                    if " 353 " in line:
                        nicks = line.split(" :")[1].split()
                        users_online = [n.strip("@+ ") for n in nicks]
                        force_log(f"Utilizadores no canal: {len(users_online)}")

                    # GESTÃO DE ENTRADAS (JOIN)
                    if " JOIN " in line and CHANNEL in line:
                        u = line.split('!')[0][1:]
                        if u != NICK:
                            if u not in users_online: users_online.append(u)
                            
                            # Lógica Personalizada de Boas-Vindas
                            if u == "Emergency112":
                                force_log(f"O Chefe {u} entrou. Mantendo silêncio conforme pedido.")
                            elif u in ["Padre", "CutxiiiPoint"]:
                                msg = random.choice(dados["saudacoes_admins"]).format(u=u)
                                send(irc, f"PRIVMSG {CHANNEL} :{msg}")
                                force_log(f"ADMIN ENTROU: {u} (Saudação especial enviada)")
                            else:
                                msg = random.choice(dados["saudacoes_comuns"]).format(u=u)
                                send(irc, f"PRIVMSG {CHANNEL} :{msg}")
                                force_log(f"UTILIZADOR ENTROU: {u}")

                    # Saídas
                    if " PART " in line or " QUIT " in line:
                        u = line.split('!')[0][1:]
                        if u in users_online: users_online.remove(u)
                        force_log(f"SAIU: {u}")

                    # Mensagens
                    if " PRIVMSG " in line:
                        u = line.split('!')[0][1:]
                        try:
                            t_msg = line.split(' PRIVMSG ')[1].split(' :')[0]
                            m_msg = line.split(' PRIVMSG ')[1].split(' :', 1)[1]
                            handle_msg(u, m_msg, t_msg == NICK, irc)
                        except: continue

        except Exception as e:
            force_log(f"ERRO: {e}")
        finally:
            if irc: irc.close()
            users_online = []
            time.sleep(20)

if __name__ == "__main__":
    port_r = int(os.environ.get("PORT", 5000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port_r), daemon=True).start()
    run_bot()
