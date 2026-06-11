import socket
import ssl  # Suporte a conexão segura (SSL)
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
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def force_log(msg):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] [SISTEMA] {msg}")
    sys.stdout.flush()

# --- CONFIGURAÇÃO IRC (Pool de servidores oficiais da PTNet) ---
SERVIDORES_POOL = ["irc.ptnet.org", "luna.ptnet.org"]
PORT = 6697  
NICK = "TheOG"  
PASS = "Nasomet112#"
CHANNEL = "#TheOG"

# --- ESTADO GLOBAL ---
START_TIME = datetime.now()
dados = {}
ultima_atividade = {} 
irc_sock = None
JSON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frases.json')

def carregar_dados():
    global dados
    try:
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            force_log(f"✅ JSON carregado.")
        else:
            force_log("❌ frases.json não encontrado! A usar dados base.")
            dados = {
                "saudacoes": ["Olá {u}!", "Bem-vindo {u}!"],
                "evasivas": ["Estou ocupado agora, {u}.", "Diz, {u}?"],
                "prendas": ["deu uma prenda a {u}"],
                "lapadas": ["deu uma lapada em {u}"],
                "radios_online": [{"nome": "Rádio Comercial", "url": "https://radiocomercial.iol.pt"}],
                "historia_theog": ["Linha 1 da história dos OG", "Linha 2 da história dos OG"]
            }
    except Exception as e:
        force_log(f"🔥 Erro no JSON: {e}")

def send_raw(msg):
    global irc_sock
    try:
        if irc_sock:
            irc_sock.send(f"{msg}\r\n".encode('utf-8'))
    except:
        pass

# --- TAREFAS AUTOMÁTICAS ---
def tarefas_periodicas():
    global irc_sock
    while True:
        try:
            time.sleep(120)
            if irc_sock:
                irc_sock.send(f"PING :ping\r\n".encode('utf-8'))
        except:
            pass

# --- PROCESSAMENTO IRC ---
def handle_irc_event(line):
    global dados, ultima_atividade
    
    if line.startswith("PING"):
        send_raw(f"PONG {line.split()[1]}")
        return

    if " JOIN " in line:
        m = re.match(r'^:([^! ]+)!.* JOIN :?#.*', line)
        if m:
            user_join = m.group(1)
            if user_join != NICK:
                ultima_atividade[user_join] = time.time()
                if random.random() < 0.30: 
                    saudacoes = dados.get("saudacoes", [])
                    if saudacoes:
                        send_raw(f"PRIVMSG {CHANNEL} :{random.choice(saudacoes).replace('{u}', user_join)}")

    if " PRIVMSG " in line:
        m = re.match(r'^:([^! ]+)!.* PRIVMSG ([^ ]+) :(.*)$', line)
        if not m: return
        
        user, target, message = m.group(1), m.group(2), m.group(3)
        msg_clean = re.sub(r'\x03(?:\d{1,2}(?:,\d{1,2})?)?|[\x02\x0F\x16\x1D\x1F]', '', message).strip()
        msg_lower = msg_clean.lower()
        partes = msg_clean.split()
        if not partes: return

        ultima_atividade[user] = time.time()
        cmd = partes[0].lower()
        is_channel = target.startswith("#")
        reply_to = target if is_channel else user

        if cmd == "!comandos":
            send_raw(f"PRIVMSG {user} :🛠️ !uptime, !historia, !prenda, !lapada, !radio, !forum, !family")
            return

        if cmd == "!radio":
            radios = dados.get("radios_online", [])
            msg_r = "📻 Rádios: " + ", ".join([f"{r['nome']} ({r['url']})" for r in radios])
            send_raw(f"PRIVMSG {user} :{msg_r}")
            return

        if cmd == "!uptime":
            delta = datetime.now() - START_TIME
            send_raw(f"PRIVMSG {reply_to} :🚀 Online há {delta.days}d {delta.seconds//3600}h")

        elif cmd == "!historia":
            for linha in dados.get("historia_theog", []):
                send_raw(f"PRIVMSG {reply_to} :{linha}")

        elif cmd == "!prenda":
            alvo = partes[1] if len(partes) > 1 else user
            frase = random.choice(dados.get("prendas", ["prenda para {u}"]))
            send_raw(f"PRIVMSG {reply_to} :\x01ACTION {frase.replace('{u}', alvo)}\x01")

        elif cmd == "!lapada":
            alvo = partes[1] if len(partes) > 1 else user
            frase = random.choice(dados.get("lapadas", ["lapada em {u}"]))
            send_raw(f"PRIVMSG {reply_to} :\x01ACTION {frase.replace('{u}', alvo)}\x01")

        elif cmd == "!forum":
            send_raw(f"PRIVMSG {user} :🌐 Fórum do Grupo: https://weareog.forumeiros.com")
            return

        elif cmd == "!family":
            send_raw(f"PRIVMSG {user} :🖼️ Stickers Family: https://drive.proton.me/urls/45Z42X27F0#XPfr61gxlrsQ")
            return

        elif NICK.lower() in msg_lower:
            if random.random() < 0.40:
                pool = dados.get("saudacoes", []) + dados.get("evasivas", [])
                if pool:
                    send_raw(f"PRIVMSG {reply_to} :{random.choice(pool).replace('{u}', user)}")

# --- LOOP DE LIGAÇÃO PRINCIPAL ---
def run_bot():
    global irc_sock
    carregar_dados()
    
    servidor_atual_index = 0

    while True:
        server_alvo = SERVIDORES_POOL[servidor_atual_index]
        try:
            force_log(f"🛰️ Conectando via SSL a {server_alvo}:{PORT}...")
            
            base_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            base_sock.settimeout(15)  # Timeout mais curto para não ficar preso caso barrem a rota
            
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            irc_sock = context.wrap_socket(base_sock, server_hostname=server_alvo)
            irc_sock.connect((server_alvo, PORT))
            irc_sock.settimeout(240)
            
            send_raw(f"PASS {PASS}")
            send_raw(f"NICK {NICK}")
            send_raw(f"USER {NICK} 8 * :TheOG Bot")
            
            buffer = ""
            while True:
                data = irc_sock.recv(4096).decode("utf-8", errors="ignore")
                if not data: 
                    force_log("🔌 Conexão interrompida pelo host remoto.")
                    break
                
                buffer += data
                while "\r\n" in buffer:
                    line, buffer = buffer.split("\r\n", 1)

                    if " 433 " in line:
                        force_log(f"⚠️ Nick ocupado. Recuperando...")
                        send_raw(f"PRIVMSG NickServ :GHOST {NICK} {PASS}")
                        send_raw(f"NICK {NICK}")
                        time.sleep(2)
                        continue

                    if " 376 " in line or " 422 " in line:
                        force_log(f"✅ Registado!")
                        send_raw(f"PRIVMSG NickServ :IDENTIFY {PASS}")
                        send_raw(f"JOIN {CHANNEL}")
                        send_raw(f"PRIVMSG {CHANNEL} :[TheOG Online]")

                    handle_irc_event(line)

        except Exception as e:
            force_log(f"💥 Erro de conexão com {server_alvo}: {e}")
        
        # Rotaciona para o próximo servidor se a ligação cair ou for recusada
        servidor_atual_index = (servidor_atual_index + 1) % len(SERVIDORES_POOL)
        
        if irc_sock:
            try: irc_sock.close()
            except: pass
            irc_sock = None
        
        # Reduzido o tempo de espera para forçar a reconexão imediata por outra rota
        force_log("⏳ Alternando rota de ligação em 10 segundos...")
        time.sleep(10) 

# --- FLASK ---
app = Flask(__name__)
@app.route('/')
def home(): 
    return "TheOG Bot Ativo", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    threading.Thread(target=tarefas_periodicas, daemon=True).start()
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port), daemon=True).start()
    run_bot()
