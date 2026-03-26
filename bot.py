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

# --- LOGS ---
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

# --- CARREGAR JSON (Prioridade Máxima) ---
dados = {}
def carregar_dados():
    global dados
    if os.path.exists('frases.json'):
        try:
            with open('frases.json', 'r', encoding='utf-8') as f:
                dados = json.load(f)
            force_log("✅ JSON DETETADO: A usar a tua história e frases.")
        except:
            force_log("❌ ERRO AO LER JSON.")
    else:
        force_log("⚠️ JSON NÃO ENCONTRADO. Usando base de emergência.")
        dados = {"historia": "História no JSON não encontrada.", "admins": ADMINS}

carregar_dados()

# --- ESTADO ---
START_TIME = datetime.now()
users_online = []
stalker_list = []

def get_uptime():
    return str(datetime.now() - START_TIME).split('.')[0]

def send(irc, msg):
    try:
        irc.send(f"{msg}\r\n".encode('utf-8'))
        time.sleep(2.0) # Delay de 2s para estabilidade total
    except: pass

# --- TAREFA SOCIAL (20 MIN) ---
def social_cycle(irc):
    while True:
        time.sleep(1200)
        if users_online:
            outros = [u for u in users_online if u != NICK and len(u) > 1]
            if outros:
                alvo = random.choice(outros)
                frases = dados.get("puxar_conversa", ["Tudo bem, {u}?"])
                send(irc, f"PRIVMSG {CHANNEL} :{random.choice(frases).format(u=alvo)}")

# --- PROCESSADOR ---
def handle_msg(user, message, is_private, irc):
    msg = message.lower().strip()
    partes = msg.split()
    cmd = partes[0] if partes else ""
    target = user if is_private else CHANNEL
    
    if cmd == "!uptime":
        send(irc, f"PRIVMSG {target} :🚀 Uptime: {get_uptime()}")
    
    elif cmd == "!historia":
        hist = dados.get("historia", "Sem história no JSON.")
        send(irc, f"PRIVMSG {target} :📖 {hist}")

    elif cmd == "!radio":
        radios = dados.get("radios", ["Rádio Comercial"])
        send(irc, f"PRIVMSG {target} :📻 Sugestão: {random.choice(radios)}")

    elif cmd in ["!stalker", "!watch"] and len(partes) > 1 and user in ADMINS:
        alvo = partes[1]
        if alvo not in stalker_list:
            stalker_list.append(alvo)
            send(irc, f"WATCH +{alvo}")
            send(irc, f"PRIVMSG {target} :🕵️ [STALKER] {alvo} sob vigilância.")

# --- FLASK ---
app = Flask(__name__)
@app.route('/')
def home(): return f"TheOG Ativo - {get_uptime()}"

# --- BOT CORE ---
def run_bot():
    global users_online
    while True:
        try:
            force_log("--- A LIGAR (ANTI-DUPLICAÇÃO ATIVO) ---")
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.settimeout(240)
            irc.connect((SERVER, PORT))
            
            # EXPULSAR FANTASMA ANTES DE TUDO
            irc.send(f"PASS {PASS}\r\n".encode())
            # Entra com nick temporário para dar o GHOST
            temp_nick = f"OG_{random.randint(100,999)}"
            irc.send(f"NICK {temp_nick}\r\n".encode())
            irc.send(f"USER {NICK} 8 * :TheOG Manager\r\n".encode())
            
            time.sleep(2)
            # Mata o bot antigo que ficou preso
            irc.send(f"PRIVMSG NickServ :GHOST {NICK} {PASS}\r\n".encode())
            force_log(f"Comando GHOST enviado para libertar o nick {NICK}")
            time.sleep(3)
            
            # Agora sim, assume o nick real
            irc.send(f"NICK {NICK}\r\n".encode())
            
            threading.Thread(target=social_cycle, args=(irc,), daemon=True).start()

            while True:
                buffer = irc.recv(4096).decode("utf-8", errors="ignore")
                if not buffer: break
                
                for line in buffer.split("\r\n"):
                    if not line: continue
                    if line.startswith("PING"):
                        irc.send(f"PONG {line.split()[1]}\r\n".encode())
                        continue

                    # Se mesmo assim der erro de nick ocupado
                    if " 433 " in line:
                        force_log("Nick ainda ocupado, tentando GHOST novamente...")
                        irc.send(f"PRIVMSG NickServ :GHOST {NICK} {PASS}\r\n".encode())
                        time.sleep(5)
                        irc.send(f"NICK {NICK}\r\n".encode())

                    if " 376 " in line or " 422 " in line:
                        send(irc, f"PRIVMSG NickServ :IDENTIFY {PASS}")
                        send(irc, f"JOIN {CHANNEL}")
                        send(irc, f"NAMES {CHANNEL}")
                        for a in stalker_list: send(irc, f"WATCH +{a}")

                    # Alertas Stalker
                    if " 600 " in line:
                        send(irc, f"PRIVMSG {CHANNEL} :🕵️ [STALKER] ONLINE: {line.split()[3]}")
                    if " 601 " in line:
                        send(irc, f"PRIVMSG {CHANNEL} :🕵️ [STALKER] OFFLINE: {line.split()[3]}")

                    if " 353 " in line:
                        nicks = line.split(" :")[1].split()
                        users_online = [n.strip("@+ ") for n in nicks]

                    if " JOIN " in line and CHANNEL in line:
                        u = line.split('!')[0][1:]
                        if u != NICK:
                            if u not in users_online: users_online.append(u)
                            if u != "Emergency112":
                                tipo = "saudacoes_admins" if u in ADMINS else "saudacoes_comuns"
                                frases = dados.get(tipo, ["Olá {u}"])
                                send(irc, f"PRIVMSG {CHANNEL} :{random.choice(frases).format(u=u)}")

                    if " PRIVMSG " in line:
                        try:
                            u_nick = line.split('!')[0][1:]
                            u_target = line.split(' PRIVMSG ')[1].split(' :')[0]
                            u_content = line.split(' PRIVMSG ')[1].split(' :', 1)[1]
                            handle_msg(u_nick, u_content, u_target == NICK, irc)
                        except: continue

        except Exception as e:
            force_log(f"ERRO: {e}")
        finally:
            if irc: irc.close()
            users_online = []
            # ESPERA LONGA PARA EVITAR DUPLICADOS NO RENDER
            force_log("Aguardando 45s para limpeza de sessão...")
            time.sleep(45)

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000))), daemon=True).start()
    run_bot()
