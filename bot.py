import socket
import time
import threading
import os
import random
import requests
import logging
import sys
import json
from datetime import datetime, timedelta
from flask import Flask

# --- CONFIGURAÇÃO DE LOGS ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("TheOG_Bot")

# --- CONFIGURAÇÃO IRC ---
SERVER = "irc.ptnet.org"
PORT = 6667
NICK = "TheOG"
PASS = "Nasomet112#"
CHANNEL = "#TheOG"
BOT_FILTER = ["nickserv", "chanserv", "memoserv", "theog", "bot", "irc"]

# --- ESTADO GLOBAL ---
START_TIME = datetime.now()
STALKER_DATA = {}
STALKER_REQUESTS = {}
CHANNEL_USERS = set()
dados = {}

# --- CARREGAMENTO DE DADOS ---
def carregar_dados():
    global dados
    try:
        if os.path.exists('frases.json'):
            with open('frases.json', 'r', encoding='utf-8') as f:
                dados = json.load(f)
                logger.info("Ficheiro frases.json carregado com sucesso.")
        else:
            logger.error("ERRO: frases.json não encontrado!")
            dados = {"admins": [], "stalker_config": {"alvos_ativos": {}}}
    except Exception as e:
        logger.error(f"Erro ao carregar JSON: {e}")

carregar_dados()

# --- UTILITÁRIOS ---
def get_uptime():
    delta = datetime.now() - START_TIME
    days = delta.days
    hours, rem = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"

def send_raw(sock, msg):
    try: sock.send(f"{msg}\r\n".encode('utf-8'))
    except: pass

# --- LOGICA DE COMANDOS ---
def handle_msg(user, message, is_private, irc):
    msg = message.lower().strip()
    partes = msg.split()
    if not partes: return
    comando = partes[0]
    target = user if is_private else CHANNEL

    # 1. COMANDO !STALKERPRO (Apenas PVT + Admins)
    if comando == "!stalkerpro":
        if not is_private: return
        admins = dados.get("admins", [])
        if user not in admins:
            send_raw(irc, f"PRIVMSG {user} :❓ Comando desconhecido.")
            return
        
        if len(partes) < 2:
            send_raw(irc, f"PRIVMSG {user} :💡 Uso: !stalkerpro [+ / - / list] [nick]")
            return
        
        acao = partes[1]
        
        if acao == "list":
            vigia = dados.get("stalker_config", {}).get("alvos_ativos", {})
            if not vigia: send_raw(irc, f"PRIVMSG {user} :📂 Lista de vigia vazia.")
            else:
                for alvo, adm in vigia.items():
                    send_raw(irc, f"PRIVMSG {user} :🕵️ Alvo: {alvo} | Por: {adm}")
            return

        if len(partes) > 2:
            alvo = partes[2].lower()
            if acao == "+":
                dados["stalker_config"]["alvos_ativos"][alvo] = user
                send_raw(irc, f"WATCH +{alvo}")
                send_raw(irc, f"PRIVMSG {user} :🎯 Alvo '{alvo}' adicionado à vigilância.")
            elif acao == "-":
                if alvo in dados["stalker_config"]["alvos_ativos"]:
                    del dados["stalker_config"]["alvos_ativos"][alvo]
                    send_raw(irc, f"WATCH -{alvo}")
                    send_raw(irc, f"PRIVMSG {user} :🗑️ Alvo '{alvo}' removido.")
            
            with open('frases.json', 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2)

    # 2. COMANDOS PÚBLICOS
    elif comando == "!stalker":
        if len(partes) > 1:
            alvo = partes[1].lower()
            STALKER_REQUESTS[alvo] = user
            send_raw(irc, f"WHOIS {alvo} {alvo}")
            send_raw(irc, f"PRIVMSG {target} :🔎 Investigação sobre '{alvo}' iniciada. Relatório no teu PVT.")

    elif comando == "!uptime":
        send_raw(irc, f"PRIVMSG {target} :🚀 TheOG online há: {get_uptime()}")

    elif comando == "!radio":
        radios = dados.get("radios_online", [])
        if radios:
            r = random.choice(radios)
            send_raw(irc, f"PRIVMSG {target} :📻 Sugestão: {r['nome']} - {r['url']}")

    elif comando == "!historia":
        for linha in dados.get("historia_theog", []):
            send_raw(irc, f"PRIVMSG {user} :{linha}")
            time.sleep(1)

    elif comando == "!lapada":
        alvo = partes[1] if len(partes) > 1 else user
        frase = random.choice(dados.get("lapadas", ["dá uma lapada em {u}!"]))
        send_raw(irc, f"PRIVMSG {CHANNEL} :\x01ACTION {frase.format(u=alvo)}\x01")

    elif comando == "!prenda":
        alvo = partes[1] if len(partes) > 1 else user
        frase = random.choice(dados.get("prendas", ["oferece um café a {u}!"]))
        send_raw(irc, f"PRIVMSG {CHANNEL} :\x01ACTION {frase.format(u=alvo)}\x01")

    # Resposta por menção
    elif NICK.lower() in msg:
        send_raw(irc, f"PRIVMSG {target} :{user}: {random.choice(dados.get('evasivas', ['Estou ocupado!']))}")

# --- PROCESSAMENTO DE RESPOSTAS DO SERVIDOR ---
def parse_irc_lines(line, irc):
    global dados
    partes = line.split()
    
    # WATCH: Alvo entrou (600)
    if " 600 " in line and len(partes) > 3:
        u_alvo = partes[3].lower()
        vigia = dados.get("stalker_config", {}).get("alvos_ativos", {})
        if u_alvo in alvos:
            adm = alvos[u_alvo]
            aviso = random.choice(dados["stalker_config"]["avisos_pro"]).format(u=u_alvo)
            send_raw(irc, f"PRIVMSG {adm} :{aviso}")

    # WHOIS: Dados do Stalker
    if any(x in line for x in [" 311 ", " 317 ", " 318 ", " 319 "]):
        alvo_whois = partes[3].lower()
        if alvo_whois in STALKER_REQUESTS:
            solicitante = STALKER_REQUESTS[alvo_whois]
            if alvo_whois not in STALKER_DATA: STALKER_DATA[alvo_whois] = {"nick": partes[3]}
            if " 311 " in line: STALKER_DATA[alvo_whois]["info"] = f"{partes[4]}@{partes[5]} ({line.split(' :',1)[1]})"
            elif " 319 " in line: STALKER_DATA[alvo_whois]["canais"] = line.split(" :", 1)[1]
            elif " 318 " in line:
                d = STALKER_DATA[alvo_whois]
                res = [f"🕵️ REPORT: {d['nick']}", f"🌐 Host: {d.get('info','?')}", f"🏠 Canais: {d.get('canais','Privados')}"]
                for r in res: send_raw(irc, f"PRIVMSG {solicitante} :{r}")
                del STALKER_DATA[alvo_whois], STALKER_REQUESTS[alvo_whois]

# --- SERVIDOR WEB (RENDER) ---
app = Flask(__name__)
@app.route('/')
def home(): return "TheOG Bot Online!"

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# --- LOOP PRINCIPAL DO BOT ---
def run_bot():
    while True:
        try:
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.connect((SERVER, PORT))
            send_raw(irc, f"NICK {NICK}")
            send_raw(irc, f"USER {NICK} 8 * :TheOG Bot")
            
            while True:
                data = irc.recv(4096).decode("utf-8", errors="ignore")
                for line in data.split("\r\n"):
                    if not line: continue
                    if line.startswith("PING"): send_raw(irc, f"PONG {line.split()[1]}")
                    
                    parse_irc_lines(line, irc)
                    
                    if " 376 " in line: # Fim do MOTD
                        send_raw(irc, f"PRIVMSG NickServ :IDENTIFY {PASS}")
                        time.sleep(2)
                        send_raw(irc, f"JOIN {CHANNEL}")
                        send_raw(irc, f"PRIVMSG {CHANNEL} :{random.choice(dados.get('frases_entrada', ['Olá!']))}")
                        # Reativar WATCH
                        for a in dados.get("stalker_config", {}).get("alvos_ativos", {}):
                            send_raw(irc, f"WATCH +{a}")

                    if " JOIN " in line:
                        u = line.split('!')[0][1:]
                        if u != NICK:
                            CHANNEL_USERS.add(u)
                            send_raw(irc, f"PRIVMSG {CHANNEL} :{random.choice(dados.get('saudacoes', ['Olá!'])).format(u=u)}")

                    if " PRIVMSG " in line:
                        u = line.split('!')[0][1:]
                        t = line.split(' PRIVMSG ')[1].split(' :')[0]
                        m = line.split(' PRIVMSG ')[1].split(' :', 1)[1]
                        handle_msg(u, m, t == NICK, irc)
        except Exception as e:
            logger.error(f"Erro: {e}. Reconectando...")
            time.sleep(15)

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    run_bot()
