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
                force_log(f"✅ JSON CARREGADO: {len(dados.get('admins', []))} admins encontrados.")
        else:
            force_log("⚠️ frases.json NÃO ENCONTRADO! Criando estrutura básica...")
            dados = {
                "admins": ["Emergency112"], 
                "stalker_config": {"alvos_ativos": {}}, 
                "prendas": ["oferece um café a {u}"], 
                "lapadas": ["dá uma lapada em {u}"], 
                "historia_theog": ["História padrão do bot."]
            }
            salvar_dados()
    except Exception as e:
        force_log(f"🔥 Erro ao ler JSON: {e}")

def salvar_dados():
    try:
        with open('frases.json', 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    except Exception as e:
        force_log(f"🔥 Erro ao salvar JSON: {e}")

carregar_dados()

def get_uptime():
    delta = datetime.now() - START_TIME
    days = delta.days
    hours, rem = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{days}d {hours}h {minutes}m"

def strip_irc_codes(text):
    return re.sub(r'\x03(?:\d{1,2}(?:,\d{1,2})?)?|[\x02\x0F\x16\x1D\x1F]', '', text)

def send_raw(sock, msg):
    try:
        if sock:
            sock.send(f"{msg}\r\n".encode('utf-8'))
    except: pass

# --- LÓGICA DE COMANDOS IRC ---
def handle_irc_msg(user, message, target, irc):
    global dados
    msg_clean = strip_irc_codes(message).strip()
    partes = msg_clean.split()
    if not partes: return
    
    cmd = partes[0].lower()
    is_private = (target.lower() == NICK.lower())
    reply_to = user if is_private else CHANNEL
    
    # Verifica se o utilizador é ADMIN (pelo JSON)
    lista_admins = dados.get("admins", [])
    is_admin = user in lista_admins

    # --- COMANDO !COMANDOS (DINÂMICO) ---
    if cmd == "!comandos":
        # Comandos para todos
        base_cmds = "!comandos, !uptime, !historia, !prenda <nick>, !lapada <nick>"
        # Adiciona stalker apenas se for Admin no JSON
        if is_admin:
            msg_final = f"🛠️ [ADMIN] Comandos: {base_cmds}, !stalkerpro <+ / - / list> <nick>"
        else:
            msg_final = f"🛠️ Comandos: {base_cmds}"
        
        send_raw(irc, f"PRIVMSG {reply_to} :{msg_final}")

    elif cmd == "!uptime":
        send_raw(irc, f"PRIVMSG {reply_to} :🚀 Uptime: {get_uptime()}")

    elif cmd == "!historia":
        # Puxa as linhas diretamente do JSON
        linhas = dados.get("historia_theog", ["História não configurada no JSON."])
        for linha in linhas:
            send_raw(irc, f"PRIVMSG {reply_to} :{linha}")
            time.sleep(1)

    elif cmd == "!prenda":
        alvo = partes[1] if len(partes) > 1 else user
        # Puxa frases do JSON
        frases_prenda = dados.get("prendas", ["oferece um café a {u}"])
        f = random.choice(frases_prenda)
        send_raw(irc, f"PRIVMSG {CHANNEL} :\x01ACTION {f.replace('{u}', alvo)}\x01")

    elif cmd == "!lapada":
        alvo = partes[1] if len(partes) > 1 else user
        # Puxa frases do JSON
        frases_lapada = dados.get("lapadas", ["dá uma lapada em {u}"])
        f = random.choice(frases_lapada)
        send_raw(irc, f"PRIVMSG {CHANNEL} :\x01ACTION {f.replace('{u}', alvo)}\x01")

    # --- COMANDO STALKER (RESTRITO PELO JSON) ---
    elif cmd == "!stalkerpro":
        if not is_admin:
            send_raw(irc, f"PRIVMSG {reply_to} :❌ Erro: Comando restrito a Administradores.")
            return
            
        if len(partes) < 2: return
        acao = partes[1]
        
        if acao == "list":
            vigia = dados.get("stalker_config", {}).get("alvos_ativos", {})
            if not vigia:
                send_raw(irc, f"PRIVMSG {user} :🕵️ Nenhum alvo em vigilância.")
            else:
                for a, adm in vigia.items(): 
                    send_raw(irc, f"PRIVMSG {user} :🕵️ Alvo: {a} (Vigiado por: {adm})")
        
        elif len(partes) > 2:
            alvo = partes[2].lower()
            if acao == "+":
                dados.setdefault("stalker_config", {}).setdefault("alvos_ativos", {})[alvo] = user
                send_raw(irc, f"WATCH +{alvo}")
                send_raw(irc, f"PRIVMSG {user} :🎯 {alvo} adicionado à lista de vigilância.")
            elif acao == "-":
                if alvo in dados.get("stalker_config", {}).get("alvos_ativos", {}):
                    del dados["stalker_config"]["alvos_ativos"][alvo]
                    send_raw(irc, f"WATCH -{alvo}")
                    send_raw(irc, f"PRIVMSG {user} :❌ {alvo} removido.")
            salvar_dados()

# --- LOOP PRINCIPAL ---
def run_bot():
    while True:
        try:
            force_log(f"🛰️ Conectando a {SERVER}...")
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.settimeout(600)
            irc.connect((SERVER, PORT))
            
            send_raw(irc, f"PASS {PASS}")
            send_raw(irc, f"NICK {NICK}")
            send_raw(irc, f"USER {NICK} 8 * :TheOG Bot")
            
            buffer = ""
            while True:
                try:
                    data = irc.recv(4096).decode("utf-8", errors="ignore")
                except: break
                
                if not data: break
                buffer += data
                while "\r\n" in buffer:
                    line, buffer = buffer.split("\r\n", 1)
                    
                    if line.startswith("PING"):
                        send_raw(irc, f"PONG {line.split(':')[1] if ':' in line else line.split()[1]}")
                        continue

                    if " 376 " in line or " 422 " in line:
                        send_raw(irc, f"PRIVMSG NickServ :IDENTIFY {PASS}")
                        time.sleep(2)
                        send_raw(irc, f"JOIN {CHANNEL}")
                        # Reativa o WATCH para os alvos guardados no JSON
                        for a in dados.get("stalker_config", {}).get("alvos_ativos", {}):
                            send_raw(irc, f"WATCH +{a}")
                        force_log(f"🚩 Online em {CHANNEL}")

                    if " PRIVMSG " in line:
                        m = re.match(r'^:([^! ]+)!.* PRIVMSG ([^ ]+) :(.*)$', line)
                        if m:
                            u_nick = m.group(1)
                            u_dest = m.group(2)
                            u_msg = m.group(3)
                            handle_irc_msg(u_nick, u_msg, u_dest, irc)

        except Exception as e:
            force_log(f"💥 Erro: {e}")
            time.sleep(10)

# --- SERVIDOR WEB ---
app = Flask(__name__)
@app.route('/')
def home(): return "TheOG Bot Online com integração JSON."

if __name__ == "__main__":
    p = int(os.environ.get("PORT", 5000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=p), daemon=True).start()
    run_bot()
