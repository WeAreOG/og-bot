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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    stream=sys.stdout
)

def force_log(msg):
    """Log imediato e visível nos logs da Render"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] [SISTEMA] {msg}", flush=True)
    sys.stdout.flush()

# --- CONFIGURAÇÃO IRC ---
SERVER = "irc.ptnet.org"          # Hostname oficial da PTnet (recomendado)
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
            force_log("✅ JSON carregado com sucesso.")
        else:
            force_log("❌ frases.json não encontrado!")
            dados = {}
    except Exception as e:
        force_log(f"🔥 Erro ao carregar JSON: {e}")

def send_raw(msg):
    global irc_sock
    try:
        if irc_sock:
            irc_sock.send(f"{msg}\r\n".encode('utf-8'))
            # Log de comandos importantes (sem mostrar a password)
            if not msg.startswith("PASS ") and not "IDENTIFY" in msg and not "GHOST" in msg:
                force_log(f"→ Enviado: {msg}")
    except Exception as e:
        force_log(f"❌ Erro ao enviar mensagem: {e}")

# --- TAREFAS AUTOMÁTICAS ---
def tarefas_periodicas():
    while True:
        time.sleep(120)
        if irc_sock:
            send_raw(f"PING {SERVER}")
            force_log("💓 Keep-alive PING enviado")

# --- PROCESSAMENTO IRC ---
def handle_irc_event(line):
    global dados, ultima_atividade

    # Log de todas as linhas importantes do servidor
    if any(x in line for x in [" 001 ", " 002 ", " 003 ", " 004 ", " 005 ", " 251 ", " 255 ", " 375 ", " 376 ", " 422 ", " 433 ", " JOIN ", " PRIVMSG "]):
        force_log(f"← {line[:200]}")

    if line.startswith("PING"):
        send_raw(f"PONG {line.split()[1]}")
        return

    # Boas-vindas (30%)
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

    # Comandos
    if " PRIVMSG " in line:
        m = re.match(r'^:([^! ]+)!.* PRIVMSG ([^ ]+) :(.*)$', line)
        if not m:
            return

        user, target, message = m.group(1), m.group(2), m.group(3)
        msg_clean = re.sub(r'\x03(?:\d{1,2}(?:,\d{1,2})?)?|[\x02\x0F\x16\x1D\x1F]', '', message).strip()
        msg_lower = msg_clean.lower()
        partes = msg_clean.split()
        if not partes:
            return

        ultima_atividade[user] = time.time()
        cmd = partes[0].lower()
        is_channel = target.startswith("#")
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
        elif cmd == "!prenda":
            alvo = partes[1] if len(partes) > 1 else user
            frase = random.choice(dados.get("prendas", ["prenda para {u}"]))
            send_raw(f"PRIVMSG {reply_to} :\x01ACTION {frase.replace('{u}', alvo)}\x01")
        elif cmd == "!lapada":
            alvo = partes[1] if len(partes) > 1 else user
            frase = random.choice(dados.get("lapadas", ["lapada em {u}"]))
            send_raw(f"PRIVMSG {reply_to} :\x01ACTION {frase.replace('{u}', alvo)}\x01")
        elif NICK.lower() in msg_lower:
            if random.random() < 0.40:
                pool = dados.get("saudacoes", []) + dados.get("evasivas", [])
                if pool:
                    send_raw(f"PRIVMSG {reply_to} :{random.choice(pool).replace('{u}', user)}")

# --- LOOP PRINCIPAL ---
def run_bot():
    global irc_sock
    carregar_dados()
    threading.Thread(target=tarefas_periodicas, daemon=True).start()

    while True:
        try:
            force_log("=" * 50)
            force_log(f"🛰️  A ligar a {SERVER}:{PORT} ...")
            
            # Resolve o hostname para IP (para log)
            try:
                resolved_ip = socket.gethostbyname(SERVER)
                force_log(f"📍 Hostname {SERVER} resolveu para IP: {resolved_ip}")
            except Exception as e:
                force_log(f"⚠️ Não foi possível resolver DNS: {e}")

            irc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc_sock.settimeout(240)
            irc_sock.connect((SERVER, PORT))   # ← Usa o hostname, não um IP fixo errado
            
            force_log("✅ Socket ligado com sucesso!")

            send_raw(f"PASS {PASS}")
            send_raw(f"NICK {NICK}")
            send_raw(f"USER {NICK} 8 * :TheOG Bot")

            buffer = ""
            while True:
                data = irc_sock.recv(4096).decode("utf-8", errors="ignore")
                if not data:
                    force_log("🔌 Conexão fechada pelo servidor remoto.")
                    break

                buffer += data
                while "\r\n" in buffer:
                    line, buffer = buffer.split("\r\n", 1)

                    # Nick em uso
                    if " 433 " in line:
                        force_log("⚠️ Nick ocupado. A tentar recuperar com GHOST...")
                        send_raw(f"PRIVMSG NickServ :GHOST {NICK} {PASS}")
                        time.sleep(2)
                        send_raw(f"NICK {NICK}")
                        continue

                    # Ligação bem sucedida (End of MOTD ou No MOTD)
                    if " 376 " in line or " 422 " in line:
                        force_log("🎉 REGISTADO COM SUCESSO NO SERVIDOR!")
                        force_log("🔑 A identificar no NickServ...")
                        send_raw(f"PRIVMSG NickServ :IDENTIFY {PASS}")
                        time.sleep(1)
                        force_log(f"🚪 A entrar no canal {CHANNEL}...")
                        send_raw(f"JOIN {CHANNEL}")
                        send_raw(f"PRIVMSG {CHANNEL} :[TheOG Online]")
                        force_log("✅ Bot deve estar agora online no canal!")

                    handle_irc_event(line)

        except socket.timeout:
            force_log("⏰ Timeout na ligação/receção.")
        except ConnectionRefusedError:
            force_log("❌ Ligação recusada pelo servidor.")
        except Exception as e:
            force_log(f"💥 Erro inesperado: {type(e).__name__}: {e}")

        # Limpeza
        if irc_sock:
            try:
                irc_sock.close()
            except:
                pass
            irc_sock = None

        force_log("⏳ Aguardando 180 segundos antes de tentar novamente...")
        time.sleep(180)

# --- FLASK (para a Render não matar o serviço) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "TheOG Bot Online", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port), daemon=True).start()
    force_log("🚀 Bot a iniciar...")
    run_bot()
