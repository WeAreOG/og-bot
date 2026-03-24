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

# --- CONFIGURAÇÃO ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("TheOG_Bot")

SERVER = "irc.ptnet.org"
PORT = 6667
NICK = "TheOG"
PASS = "Nasomet112#"
CHANNEL = "#TheOG"
BOT_FILTER = ["nickserv", "chanserv", "memoserv", "operserv", "adamastor", "statserv", "secure", "authserv", "irc", "theog", "bot"]
HF_TOKEN = "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"
API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
ICECAST_STATS = "http://teu-servidor-icecast:8000/status-json.xsl"

# --- ESTADO E DADOS ---
START_TIME = datetime.now()
STALKER_DATA = {}
STALKER_REQUESTS = {}
CHANNEL_USERS = set()

def carregar_dados():
    try:
        with open('frases.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar frases.json: {e}")
        return {}

dados = carregar_dados()
FRASES_ENTRADA = dados.get("frases_entrada", ["Olá!"])
HISTORIA_THEOG = dados.get("historia_theog", [])
PRENDAS = dados.get("prendas", [])
LAPADAS = dados.get("lapadas", [])
OG_EVASIVE = dados.get("evasivas", [])
PUXAR_CONVERSA = dados.get("puxar_conversa", [])
REFORCO_POSITIVO = dados.get("reforco_positivo", [])
USER_GREETINGS = dados.get("saudacoes", [])

# --- FUNÇÕES ---

app = Flask(__name__)

def get_uptime():
    delta = datetime.now() - START_TIME
    days, hours = divmod(delta.days * 24 + delta.seconds // 3600, 24)
    minutes, seconds = divmod((delta.seconds % 3600) // 60, 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"

def send_raw(sock, msg):
    try: sock.send(f"{msg}\r\n".encode('utf-8'))
    except: pass

def get_radio_status():
    try:
        r = requests.get(ICECAST_STATS, timeout=3).json()
        source = r['icestats']['source']
        if isinstance(source, list): source = source[0]
        return source.get('title', 'Rádio Online')
    except: return "Rádio #TheOG Online"

def ask_ia(question):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    prompt = f"Tu és o TheOG, bot do canal #TheOG. Responde curto em PT-PT: {question}"
    try:
        res = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=15).json()
        return res[0]['generated_text'].split(":")[-1].strip()
    except: return "A central da IA está a tomar café."

def parse_whois(line, irc):
    partes = line.split()
    if len(partes) < 4: return
    alvo = partes[3].lower()
    if alvo not in STALKER_REQUESTS: return
    solicitante = STALKER_REQUESTS[alvo]
    
    if alvo not in STALKER_DATA: STALKER_DATA[alvo] = {"nick": partes[3]}
    if " 311 " in line:
        STALKER_DATA[alvo]["host"] = f"{partes[4]}@{partes[5]}"
        STALKER_DATA[alvo]["name"] = line.split(" :", 1)[1]
    elif " 319 " in line: STALKER_DATA[alvo]["channels"] = line.split(" :", 1)[1]
    elif " 317 " in line:
        STALKER_DATA[alvo]["idle"] = str(timedelta(seconds=int(partes[4])))
        STALKER_DATA[alvo]["since"] = datetime.fromtimestamp(int(partes[5])).strftime('%d/%m %H:%M')
    elif " 318 " in line:
        d = STALKER_DATA[alvo]
        rep = [f"🕵️ REPORT [{d['nick']}]:", f"👤 Nome: {d.get('name','?')}", f"🌐 Host: {d.get('host','?')}", f"⏳ Idle: {d.get('idle','0s')}", f"📅 On: {d.get('since','?')}", f"🏠 Canais: {d.get('channels','Privados')}"]
        for r in rep: send_raw(irc, f"PRIVMSG {solicitante} :{r}")
        del STALKER_DATA[alvo], STALKER_REQUESTS[alvo]

def handle_msg(user, message, is_private, irc):
    msg = message.lower().strip()
    target = user if is_private else CHANNEL
    
    if msg.startswith("!"):
        if msg == "!uptime": send_raw(irc, f"PRIVMSG {target} :🚀 Ligado há: {get_uptime()}")
        elif msg == "!comandos": send_raw(irc, f"PRIVMSG {user} :!historia, !musica, !pergunta, !lapada, !prenda, !stalker, !uptime")
        elif msg == "!historia":
            for l in HISTORIA_THEOG: send_raw(irc, f"PRIVMSG {user} :{l}"); time.sleep(1)
        elif msg.startswith("!stalker"):
            partes = msg.split()
            if len(partes) > 1:
                alvo = partes[1]
                STALKER_REQUESTS[alvo.lower()] = user
                send_raw(irc, f"WHOIS {alvo} {alvo}")
                if not is_private: send_raw(irc, f"PRIVMSG {user} :🔎 Investigação silenciosa iniciada sobre {alvo}.")
        elif msg.startswith("!lapada"):
            u = msg.split()[1] if len(msg.split()) > 1 else user
            send_raw(irc, f"PRIVMSG {CHANNEL} :\x01ACTION {random.choice(LAPADAS).format(u=u)}\x01")
        elif msg.startswith("!prenda"):
            u = msg.split()[1] if len(msg.split()) > 1 else user
            send_raw(irc, f"PRIVMSG {CHANNEL} :\x01ACTION {random.choice(PRENDAS).format(u=u)}\x01")
        elif msg.startswith("!pergunta"):
            threading.Thread(target=lambda: send_raw(irc, f"PRIVMSG {target} :{user}: {ask_ia(message[10:])}")).start()

    elif NICK.lower() in msg: send_raw(irc, f"PRIVMSG {target} :{user}: {random.choice(OG_EVASIVE)}")

def loops(sock):
    while True:
        time.sleep(1800)
        ativos = [n for n in list(CHANNEL_USERS) if n.lower() not in BOT_FILTER]
        if ativos:
            if random.random() < 0.4: send_raw(sock, f"PRIVMSG {CHANNEL} :{random.choice(REFORCO_POSITIVO)}")
            else: send_raw(sock, f"PRIVMSG {CHANNEL} :{random.choice(PUXAR_CONVERSA).format(u=random.choice(ativos))}")

def run_bot():
    while True:
        try:
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.connect((SERVER, PORT))
            send_raw(irc, f"NICK {NICK}"); send_raw(irc, f"USER {NICK} 8 * :TheOG Bot")
            
            threads_ok = False
            while True:
                data = irc.recv(4096).decode("utf-8", errors="ignore")
                for line in data.split("\r\n"):
                    if not line: continue
                    if line.startswith("PING"): send_raw(irc, f"PONG {line.split()[1]}")
                    if any(x in line for x in [" 311 ", " 317 ", " 318 ", " 319 "]): parse_whois(line, irc)
                    if "376" in line:
                        send_raw(irc, f"PRIVMSG NickServ :IDENTIFY {PASS}")
                        send_raw(irc, f"JOIN {CHANNEL}")
                        send_raw(irc, f"PRIVMSG {CHANNEL} :{random.choice(FRASES_ENTRADA)}")
                        if not threads_ok: threading.Thread(target=loops, args=(irc,), daemon=True).start(); threads_ok = True
                    if " JOIN " in line:
                        u = line.split('!')[0][1:]
                        if u != NICK: CHANNEL_USERS.add(u); send_raw(irc, f"PRIVMSG {CHANNEL} :{random.choice(USER_GREETINGS).format(u=u)}")
                    if " PRIVMSG " in line:
                        u = line.split('!')[0][1:]; t = line.split(' PRIVMSG ')[1].split(' :')[0]
                        m = line.split(' PRIVMSG ')[1].split(' :', 1)[1]
                        handle_msg(u, m, t == NICK, irc)
        except: time.sleep(15)

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000))), daemon=True).start()
    run_bot()
