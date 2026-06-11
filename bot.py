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
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

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
            force_log("❌ frases.json não encontrado!")
            dados = {}
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
            # Envia um PING ao servidor a cada 2 minutos para evitar fecho por inatividade
            time.sleep(120)
            if irc_sock:
                send_raw(f"PING {SERVER}")
                
            # Lógica de Reforço Positivo (2 Horas)
            if dados and irc_sock:
                pass
        except:
            pass

# --- PROCESSAMENTO IRC ---
def handle_irc_event(line):
    global dados, ultima_atividade
    
    if line.startswith("PING"):
        send_raw(f"PONG {line.split()[1]}")
        return

    # Boas-vindas (Probabilidade de 30%)
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

    # Comandos e Interações
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
            send_raw(f"PRIVMSG {user} :🌐 Fórum do Grupo (Acede às discussões da nossa comunidade): https://weareog.forumeiros.com")
            return

        elif cmd == "!family":
            send_raw(f"PRIVMSG {user} :🖼️ Stickers Family (Vê aqui a nossa coleção de stickers): https://drive.proton.me/urls/45Z42X27F0#XPfr61gxlrsQ")
            return

        # Resposta ao nick (Probabilidade 40%)
        elif NICK.lower() in msg_lower:
            if random.random() < 0.40:
                pool = dados.get("saudacoes", []) + dados.get("evasivas", [])
                if pool:
                    send_raw(f"PRIVMSG {reply_to} :{random.choice(pool).replace('{u}', user)}")

# --- LOOP DE LIGAÇÃO PRINCIPAL ---
def run_bot():
    global irc_sock
    carregar_dados()

    while True:
        try:
            force_log(f"🛰️ Conectando...")
            irc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc_sock.settimeout(240)
            irc_sock.connect((SERVER, PORT))
            
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
            force_log(f"💥 Erro inesperado: {e}")
        
        # Limpeza segura do socket antigo antes de tentar ligar outra vez
        if irc_sock:
            try:
                irc_sock.close()
            except:
                pass
            irc_sock = None
        
        # Reduzido de 180s para 15s para evitar adormecimento no Render
        force_log("⏳ Aguardando 15 segundos para reconectar...")
        time.sleep(15) 

# --- FLASK ---
app = Flask(__name__)
@app.route('/')
def home(): return "TheOG Bot Online", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Inicializa as threads apenas uma vez no arranque da app
    threading.Thread(target=tarefas_periodicas, daemon=True).start()
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port), daemon=True).start()
    run_bot()
