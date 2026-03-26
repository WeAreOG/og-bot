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
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', handlers=[logging.StreamHandler(sys.stdout)])

def force_log(msg):
    """Imprime mensagens diretamente no painel de Logs do Render."""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] [SISTEMA] {msg}")
    sys.stdout.flush()

# --- CONFIGURAÇÃO IRC ---
SERVER = "irc.ptnet.org"
PORT = 6667
NICK = "TheOG"
PASS = "Nasomet112#"
CHANNEL = "#TheOG"

# --- ESTADO GLOBAL ---
START_TIME = datetime.now()
dados = {}

def carregar_dados():
    global dados
    try:
        if os.path.exists('frases.json'):
            with open('frases.json', 'r', encoding='utf-8') as f:
                dados = json.load(f)
                force_log(f"✅ JSON OK: {len(dados.get('prendas',[]))} prendas e {len(dados.get('historia_theog',[]))} linhas de história.")
        else:
            force_log("⚠️ frases.json não encontrado! Usando base de emergência.")
            dados = {"admins": ["Emergency112"], "stalker_config": {"alvos_ativos": {}}, "prendas": ["oferece um café"], "historia_theog": ["Sem história no JSON."]}
    except Exception as e:
        force_log(f"🔥 Erro ao ler JSON: {e}")

def salvar_dados():
    try:
        with open('frases.json', 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    except: pass

carregar_dados()

def get_uptime():
    delta = datetime.now() - START_TIME
    days = delta.days
    hours, rem = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{days}d {hours}h {minutes}m"

def send_raw(sock, msg):
    try:
        if sock: sock.send(f"{msg}\r\n".encode('utf-8'))
    except: pass

# --- LÓGICA DE COMANDOS IRC ---
def handle_irc_msg(user, message, is_private, irc):
    global dados
    msg_low = message.lower().strip()
    partes = msg_low.split()
    if not partes: return
    cmd = partes[0]
    target = user if is_private else CHANNEL

    # STALKER PRO
    if cmd == "!stalkerpro":
        if user not in dados.get("admins", []): return
        if len(partes) < 2: return
        acao = partes[1]
        if acao == "list":
            vigia = dados.get("stalker_config", {}).get("alvos_ativos", {})
            for a, adm in vigia.items(): send_raw(irc, f"PRIVMSG {user} :🕵️ {a} (por {adm})")
        elif len(partes) > 2:
            alvo = partes[2].lower()
            if acao == "+":
                dados.setdefault("stalker_config", {}).setdefault("alvos_ativos", {})[alvo] = user
                send_raw(irc, f"WATCH +{alvo}")
                send_raw(irc, f"PRIVMSG {user} :🎯 {alvo} vigiado.")
            elif acao == "-":
                if alvo in dados.get("stalker_config", {}).get("alvos_ativos", {}):
                    del dados["stalker_config"]["alvos_ativos"][alvo]
                    send_raw(irc, f"WATCH -{alvo}")
            salvar_dados()

    # COMANDO HISTÓRIA (VEM DO JSON)
    elif cmd == "!historia":
        linhas = dados.get("historia_theog", ["História não configurada no JSON."])
        for linha in linhas:
            send_raw(irc, f"PRIVMSG {target} :{linha}")
            time.sleep(0.8) # Pausa para evitar kick por flood

    # PRENDAS E LAPADAS (CENTENAS DE FRASES DO JSON)
    elif cmd == "!prenda":
        alvo = partes[1] if len(partes) > 1 else user
        f = random.choice(dados.get("prendas", ["oferece um café a {u}"]))
        send_raw(irc, f"PRIVMSG {CHANNEL} :\x01ACTION {f.format(u=alvo)}\x01")

    elif cmd == "!lapada":
        alvo = partes[1] if len(partes) > 1 else user
        f = random.choice(dados.get("lapadas", ["dá uma lapada em {u}"]))
        send_raw(irc, f"PRIVMSG {CHANNEL} :\x01ACTION {f.format(u=alvo)}\x01")

    elif cmd == "!uptime":
        send_raw(irc, f"PRIVMSG {target} :🚀 Uptime: {get_uptime()}")

# --- LOOP PRINCIPAL ---
def run_bot():
    while True:
        try:
            force_log(f"🛰️ Conectando a {SERVER}...")
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.settimeout(240)
            irc.connect((SERVER, PORT))
            
            send_raw(irc, f"PASS {PASS}")
            send_raw(irc, f"NICK {NICK}")
            send_raw(irc, f"USER {NICK} 8 * :TheOG Bot")
            
            while True:
                data = irc.recv(4096).decode("utf-8", errors="ignore")
                if not data: break
                for line in data.split("\r\n"):
                    if not line: continue
                    if line.startswith("PING"): send_raw(irc, f"PONG {line.split()[1]}")
                    
                    if " 353 " in line:
                        force_log(f"👥 UTILIZADORES NO CANAL: {line.split(' :')[-1]}")
                    
                    if " PRIVMSG " in line:
                        u = line.split('!')[0][1:]
                        t = line.split(' PRIVMSG ')[1].split(' :', 1)[1]
                        d = line.split(' PRIVMSG ')[1].split(' :')[0]
                        force_log(f"CHAT: <{u}> {t}")
                        handle_irc_msg(u, t, d == NICK, irc)
                    
                    if " 376 " in line or " 422 " in line:
                        send_raw(irc, f"PRIVMSG NickServ :IDENTIFY {PASS}")
                        time.sleep(2)
                        send_raw(irc, f"JOIN {CHANNEL}")
                        for a in dados.get("stalker_config", {}).get("alvos_ativos", {}):
                            send_raw(irc, f"WATCH +{a}")
                        force_log(f"🚩 O bot entrou em {CHANNEL}")
                        send_raw(irc, f"NAMES {CHANNEL}")

        except Exception as e:
            force_log(f"💥 Erro: {e}")
            time.sleep(30)

# --- SERVIDOR WEB ---
app = Flask(__name__)
@app.route('/')
def home(): return "TheOG Bot Online. Verifique os Logs no Render."

if __name__ == "__main__":
    p = int(os.environ.get("PORT", 5000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=p), daemon=True).start()
    run_bot()
