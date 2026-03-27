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
# Garante que o caminho do ficheiro é relativo ao script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, 'frases.json')

def carregar_dados():
    global dados
    try:
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                # Logs de verificação para sabermos o que foi lido
                n_reforcos = len(dados.get("reforcos_positivos", []))
                n_prendas = len(dados.get("prendas", []))
                force_log(f"✅ JSON CARREGADO: {n_reforcos} reforços e {n_prendas} prendas encontradas.")
        else:
            force_log("⚠️ frases.json NÃO ENCONTRADO! Criando estrutura padrão...")
            dados = {
                "admins": ["Emergency112"], 
                "stalker_config": {"alvos_ativos": {}}, 
                "prendas": ["oferece um café a {u}"], 
                "lapadas": ["dá uma lapada em {u}"], 
                "reforcos_positivos": ["És o maior, {u}!", "Bom trabalho, {u}!", "Continua assim!"],
                "respostas_mencao": ["Diz lá, {u}?", "Estou aqui!"],
                "historia_theog": ["História base no JSON."]
            }
            salvar_dados()
    except Exception as e:
        force_log(f"🔥 Erro ao ler JSON: {e}")

def salvar_dados():
    try:
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    except Exception as e:
        force_log(f"🔥 Erro ao salvar JSON: {e}")

# Inicializa os dados antes de começar
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

# --- LÓGICA DE COMANDOS E INTERAÇÃO ---
def handle_irc_msg(user, message, target, irc):
    global dados
    msg_clean = strip_irc_codes(message).strip()
    partes = msg_clean.split()
    if not partes: return
    
    msg_lower = msg_clean.lower()
    cmd = partes[0].lower()
    is_channel = target.startswith("#")
    reply_to = target if is_channel else user
    
    lista_admins = dados.get("admins", [])
    is_admin = user in lista_admins

    # --- 1. COMANDO !COMANDOS ---
    if cmd == "!comandos":
        base = "!comandos, !uptime, !historia, !prenda <nick>, !lapada <nick>"
        if is_admin:
            msg_pvt = f"🛠️ [ADMIN] {base}, !stalkerpro <+ / - / list>"
        else:
            msg_pvt = f"🛠️ {base}"
        send_raw(irc, f"PRIVMSG {user} :{msg_pvt}")
        return

    # --- 2. COMANDOS DIRETOS ---
    if cmd == "!uptime":
        send_raw(irc, f"PRIVMSG {reply_to} :🚀 Uptime: {get_uptime()}")
    
    elif cmd == "!historia":
        linhas = dados.get("historia_theog", ["Sem história disponível."])
        for linha in linhas:
            send_raw(irc, f"PRIVMSG {reply_to} :{linha}")
            time.sleep(0.8)

    elif cmd == "!prenda":
        alvo = partes[1] if len(partes) > 1 else user
        pool = dados.get("prendas", ["oferece um café a {u}"])
        f = random.choice(pool)
        send_raw(irc, f"PRIVMSG {reply_to} :\x01ACTION {f.replace('{u}', alvo)}\x01")

    elif cmd == "!lapada":
        alvo = partes[1] if len(partes) > 1 else user
        pool = dados.get("lapadas", ["dá uma lapada em {u}"])
        f = random.choice(pool)
        send_raw(irc, f"PRIVMSG {reply_to} :\x01ACTION {f.replace('{u}', alvo)}\x01")

    elif cmd == "!stalkerpro" and is_admin:
        if len(partes) < 2: return
        acao = partes[1]
        if acao == "list":
            vigia = dados.get("stalker_config", {}).get("alvos_ativos", {})
            send_raw(irc, f"PRIVMSG {user} :🕵️ Alvos: {list(vigia.keys())}")
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
                send_raw(irc, f"PRIVMSG {user} :❌ {alvo} removido.")
            salvar_dados()

    # --- 3. MENÇÃO AO BOT (REFORÇOS POSITIVOS) ---
    elif NICK.lower() in msg_lower:
        # Puxa as listas atualizadas do dicionário 'dados' que veio do JSON
        respostas = dados.get("respostas_mencao", ["Diz lá, {u}?"])
        reforcos = dados.get("reforcos_positivos", ["És o maior, {u}!"])
        pool_respostas = respostas + reforcos
        
        escolha = random.choice(pool_respostas)
        send_raw(irc, f"PRIVMSG {reply_to} :{escolha.replace('{u}', user)}")

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
                        # Reativa o WATCH para alvos salvos
                        for a in dados.get("stalker_config", {}).get("alvos_ativos", {}):
                            send_raw(irc, f"WATCH +{a}")
                        force_log(f"🚩 Online em {CHANNEL}")

                    if " PRIVMSG " in line:
                        m = re.match(r'^:([^! ]+)!.* PRIVMSG ([^ ]+) :(.*)$', line)
                        if m:
                            u_nick, u_target, u_msg = m.group(1), m.group(2), m.group(3)
                            handle_irc_msg(u_nick, u_msg, u_target, irc)

        except Exception as e:
            force_log(f"💥 Erro na conexão: {e}")
            time.sleep(10)

# --- SERVIDOR WEB (PARA MANTER VIVO NO RENDER/HEROKU) ---
app = Flask(__name__)
@app.route('/')
def home(): return "TheOG Bot Online."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Inicia Flask numa thread separada
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port), daemon=True).start()
    run_bot()
