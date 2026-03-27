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
NICK = "TheOG"  # Nick fixo e obrigatório
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
            force_log(f"✅ JSON carregado: {len(dados.get('saudacoes', []))} saudações.")
        else:
            force_log("❌ frases.json não encontrado!")
    except Exception as e:
        force_log(f"🔥 Erro no JSON: {e}")

def send_raw(msg):
    global irc_sock
    try:
        if irc_sock:
            irc_sock.send(f"{msg}\r\n".encode('utf-8'))
    except:
        pass

# --- TAREFAS AUTOMÁTICAS (20 MIN) ---
def tarefas_periodicas():
    while True:
        time.sleep(1200)
        if not dados or not irc_sock: continue
        
        # Reforço Positivo
        reforcos = dados.get("reforco_positivo", [])
        if reforcos:
            send_raw(f"PRIVMSG {CHANNEL} :{random.choice(reforcos)}")
        
        # Puxar Conversa
        now = time.time()
        puxar = dados.get("puxar_conversa", [])
        if puxar and ultima_atividade:
            inativos = [n for n, t in ultima_atividade.items() if (now - t) > 1200 and n != NICK]
            if inativos:
                alvo = random.choice(inativos)
                send_raw(f"PRIVMSG {CHANNEL} :{random.choice(puxar).replace('{u}', alvo)}")

# --- PROCESSAMENTO IRC ---
def handle_irc_event(line):
    global dados, ultima_atividade
    
    if line.startswith("PING"):
        send_raw(f"PONG {line.split()[1]}")
        return

    # Boas-vindas a quem entra (JOIN)
    if " JOIN " in line:
        m = re.match(r'^:([^! ]+)!.* JOIN :?#.*', line)
        if m:
            user_join = m.group(1)
            if user_join != NICK:
                saudacoes = dados.get("saudacoes", [])
                if saudacoes:
                    send_raw(f"PRIVMSG {CHANNEL} :{random.choice(saudacoes).replace('{u}', user_join)}")
                ultima_atividade[user_join] = time.time()

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
        is_admin = user in dados.get("admins", [])
        reply_to = target if is_channel else user

        if cmd == "!comandos":
            send_raw(f"PRIVMSG {user} :🛠️ !uptime, !historia, !prenda, !lapada, !radio")
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
                time.sleep(0.8)

        elif cmd == "!prenda":
            alvo = partes[1] if len(partes) > 1 else user
            frase = random.choice(dados.get("prendas", ["prenda para {u}"]))
            send_raw(f"PRIVMSG {reply_to} :\x01ACTION {frase.replace('{u}', alvo)}\x01")

        elif cmd == "!lapada":
            alvo = partes[1] if len(partes) > 1 else user
            frase = random.choice(dados.get("lapadas", ["lapada em {u}"]))
            send_raw(f"PRIVMSG {reply_to} :\x01ACTION {frase.replace('{u}', alvo)}\x01")

        elif NICK.lower() in msg_lower:
            pool = dados.get("saudacoes", []) + dados.get("evasivas", [])
            if pool:
                send_raw(f"PRIVMSG {reply_to} :{random.choice(pool).replace('{u}', user)}")

# --- LOOP DE LIGAÇÃO ---
def run_bot():
    global irc_sock
    carregar_dados()
    threading.Thread(target=tarefas_periodicas, daemon=True).start()

    while True:
        try:
            force_log(f"🛰️ Tentando ligar como {NICK}...")
            irc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc_sock.settimeout(300)
            irc_sock.connect((SERVER, PORT))
            
            send_raw(f"PASS {PASS}")
            send_raw(f"NICK {NICK}")
            send_raw(f"USER {NICK} 8 * :TheOG Bot")
            
            buffer = ""
            while True:
                data = irc_sock.recv(4096).decode("utf-8", errors="ignore")
                if not data: break
                buffer += data
                while "\r\n" in buffer:
                    line, buffer = buffer.split("\r\n", 1)
                    force_log(f"RAW: {line}")

                    # Se o nick estiver em uso, o bot não muda, apenas espera e tenta de novo
                    if " 433 " in line:
                        force_log(f"⚠️ O nick {NICK} está ocupado. Tentando novamente...")
                        irc_sock.close()
                        time.sleep(30)
                        break

                    # Sucesso no Registo
                    if " 376 " in line or " 422 " in line:
                        force_log(f"✅ Registado como {NICK}!")
                        send_raw(f"PRIVMSG NickServ :IDENTIFY {PASS}")
                        time.sleep(2)
                        send_raw(f"JOIN {CHANNEL}")
                        entrada = random.choice(dados.get("frases_entrada", ["TheOG está na área!"]))
                        send_raw(f"PRIVMSG {CHANNEL} :{entrada}")

                    handle_irc_event(line)
                else:
                    continue
                break # Sai do loop interno se houver erro de nick

        except Exception as e:
            force_log(f"💥 Erro: {e}. Re-tentando em 15s...")
            time.sleep(15)

# --- FLASK ---
app = Flask(__name__)
@app.route('/')
def home(): return "TheOG Bot Online", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port), daemon=True).start()
    run_bot()
