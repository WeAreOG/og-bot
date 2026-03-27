import socket
import time
import threading
import os
import random
import logging
import sys
import json
import re
from datetime import datetime
from flask import Flask

# --- CONFIGURAÇÃO DE LOGS ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', handlers=[logging.StreamHandler(sys.stdout)])

def force_log(msg):
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
                force_log(f"✅ JSON OK: {len(dados.get('prendas',[]))} prendas.")
        else:
            force_log("⚠️ frases.json não encontrado! Usando base de emergência.")
            dados = {
                "admins": ["Emergency112"], 
                "stalker_config": {"alvos_ativos": {}}, 
                "prendas": ["oferece um café a {u}"], 
                "lapadas": ["dá uma lapada em {u}"], 
                "historia_theog": ["Sem história no JSON."]
            }
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

def strip_irc_codes(text):
    """Remove cores e formatação do IRC que podem quebrar o reconhecimento de comandos."""
    return re.sub(r'\x03(?:\d{1,2}(?:,\d{1,2})?)?|[\x02\x0F\x16\x1D\x1F]', '', text)

def send_raw(sock, msg):
    try:
        if sock:
            sock.send(f"{msg}\r\n".encode('utf-8'))
    except: pass

# --- LÓGICA DE COMANDOS IRC ---
def handle_irc_msg(user, message, target, irc):
    global dados
    # Limpa a mensagem de códigos de cores e espaços extras
    msg_clean = strip_irc_codes(message).strip()
    partes = msg_clean.split()
    if not partes: return
    
    cmd = partes[0].lower()
    is_private = (target.lower() == NICK.lower())
    reply_to = user if is_private else CHANNEL

    force_log(f"DEBUG: Comando detetado: {cmd} vindo de {user}")

    if cmd == "!uptime":
        send_raw(irc, f"PRIVMSG {reply_to} :🚀 Uptime: {get_uptime()}")

    elif cmd == "!historia":
        linhas = dados.get("historia_theog", ["História não configurada."])
        for linha in linhas:
            send_raw(irc, f"PRIVMSG {reply_to} :{linha}")
            time.sleep(1)

    elif cmd == "!prenda":
        alvo = partes[1] if len(partes) > 1 else user
        f = random.choice(dados.get("prendas", ["oferece um café a {u}"]))
        send_raw(irc, f"PRIVMSG {CHANNEL} :\x01ACTION {f.replace('{u}', alvo)}\x01")

    elif cmd == "!lapada":
        alvo = partes[1] if len(partes) > 1 else user
        f = random.choice(dados.get("lapadas", ["dá uma lapada em {u}"]))
        send_raw(irc, f"PRIVMSG {CHANNEL} :\x01ACTION {f.replace('{u}', alvo)}\x01")

    elif cmd == "!stalkerpro":
        if user not in dados.get("admins", []): return
        if len(partes) < 2: return
        acao = partes[1]
        if acao == "+":
            alvo = partes[2].lower()
            dados.setdefault("stalker_config", {}).setdefault("alvos_ativos", {})[alvo] = user
            send_raw(irc, f"WATCH +{alvo}")
            send_raw(irc, f"PRIVMSG {user} :🎯 {alvo} vigiado.")
            salvar_dados()

# --- LOOP PRINCIPAL ---
def run_bot():
    while True:
        try:
            force_log(f"🛰️ Conectando a {SERVER}...")
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.settimeout(300) # Evita que o bot fique pendurado
            irc.connect((SERVER, PORT))
            
            send_raw(irc, f"PASS {PASS}")
            send_raw(irc, f"NICK {NICK}")
            send_raw(irc, f"USER {NICK} 8 * :TheOG Bot")
            
            buffer = ""
            while True:
                try:
                    data = irc.recv(4096).decode("utf-8", errors="ignore")
                except socket.timeout:
                    send_raw(irc, "PING :keepalive")
                    continue
                
                if not data: break
                
                buffer += data
                while "\r\n" in buffer:
                    line, buffer = buffer.split("\r\n", 1)
                    if not line: continue
                    
                    # Resposta PING (Vital)
                    if line.startswith("PING"):
                        send_raw(irc, f"PONG {line.split(':')[1] if ':' in line else line.split()[1]}")
                        continue

                    # LOGIN / JOIN
                    if " 376 " in line or " 422 " in line:
                        send_raw(irc, f"PRIVMSG NickServ :IDENTIFY {PASS}")
                        time.sleep(2)
                        send_raw(irc, f"JOIN {CHANNEL}")
                        force_log(f"🚩 Online em {CHANNEL}")

                    # PROCESSAMENTO DE CHAT
                    if " PRIVMSG " in line:
                        # Parsing ultra-seguro usando Regex
                        match = re.match(r'^:([^!]+)!.* PRIVMSG ([^ ]+) :(.*)$', line)
                        if match:
                            user_nick = match.group(1)
                            target_dest = match.group(2)
                            message_text = match.group(3)
                            
                            force_log(f"LOG: [{target_dest}] <{user_nick}> {message_text}")
                            handle_irc_msg(user_nick, message_text, target_dest, irc)

        except Exception as e:
            force_log(f"💥 Erro Geral: {e}")
            time.sleep(15)

# --- SERVIDOR WEB ---
app = Flask(__name__)
@app.route('/')
def home(): return "TheOG Bot Online."

if __name__ == "__main__":
    p = int(os.environ.get("PORT", 5000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=p), daemon=True).start()
    run_bot()
