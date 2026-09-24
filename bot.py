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
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] [SISTEMA] {msg}", flush=True)
    sys.stdout.flush()

# --- CONFIGURAÇÃO IRC ---
SERVER = "irc.ptnet.org"
PORT = 6667
NICK = "TheOG"
PASS = "Nasomet112#"
CHANNEL = "#TheOG"

# --- INTERVALOS DAS NOVAS FUNCIONALIDADES (em segundos) ---
INTERVALO_ANEDOTAS = 40 * 60   # 40 em 40 minutos
INTERVALO_REFORCO = 90 * 60    # hora e meia em hora e meia

# --- ESTADO GLOBAL ---
START_TIME = datetime.now()
dados = {}
extras = {}
ultima_atividade = {}
irc_sock = None
JSON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frases.json')
EXTRAS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'extras.json')

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

def carregar_extras():
    global extras
    try:
        if os.path.exists(EXTRAS_FILE):
            with open(EXTRAS_FILE, 'r', encoding='utf-8') as f:
                extras = json.load(f)
            force_log("✅ extras.json carregado com sucesso.")
        else:
            force_log("❌ extras.json não encontrado!")
            extras = {}
    except Exception as e:
        force_log(f"🔥 Erro ao carregar extras.json: {e}")

def send_raw(msg):
    global irc_sock
    try:
        if irc_sock:
            irc_sock.send(f"{msg}\r\n".encode('utf-8'))
            safe = msg
            if msg.upper().startswith("PASS ") or "IDENTIFY" in msg.upper() or "GHOST" in msg.upper():
                safe = msg.split(" ", 1)[0] + " ***"
            force_log(f"→ {safe}")
    except Exception as e:
        force_log(f"❌ Erro ao enviar: {e}")

def saudacao_por_hora(user):
    """Devolve uma saudação neutra mas simpática, de acordo com a hora do dia."""
    hora = datetime.now().hour
    if 5 <= hora < 12:
        chave = "saudacoes_manha"
    elif 12 <= hora < 20:
        chave = "saudacoes_tarde"
    else:
        chave = "saudacoes_noite"

    pool = extras.get(chave, [])
    if not pool:
        return None
    return random.choice(pool).replace('{u}', user)

def tarefas_periodicas():
    """Keep-alive PING a cada 120s."""
    while True:
        time.sleep(120)
        if irc_sock:
            send_raw(f"PING {SERVER}")
            force_log("💓 Keep-alive PING enviado")

def tarefa_anedotas():
    """Envia uma anedota seca ao canal de 40 em 40 minutos."""
    while True:
        time.sleep(INTERVALO_ANEDOTAS)
        if irc_sock:
            anedotas = extras.get("anedotas", [])
            if anedotas:
                anedota = random.choice(anedotas)
                send_raw(f"PRIVMSG {CHANNEL} :😐 {anedota}")
                force_log("😐 Anedota seca enviada.")

def tarefa_reforco_positivo():
    """Envia uma mensagem de reforço positivo de hora e meia em hora e meia."""
    while True:
        time.sleep(INTERVALO_REFORCO)
        if irc_sock:
            pool = extras.get("reforco_positivo", [])
            if pool:
                mensagem = random.choice(pool)
                send_raw(f"PRIVMSG {CHANNEL} :{mensagem}")
                force_log("💪 Reforço positivo enviado.")

def handle_irc_event(line):
    global dados, ultima_atividade

    # Log de TUDO o que o servidor envia
    force_log(f"← {line}")

    if line.startswith("PING"):
        send_raw(f"PONG {line.split()[1]}")
        return

    if line.startswith("ERROR") or "Closing Link" in line:
        force_log(f"🛑 SERVIDOR FECHOU A LIGAÇÃO: {line}")
        return

    # Boas-vindas consoante a hora do dia
    if " JOIN " in line:
        m = re.match(r'^:([^! ]+)!.* JOIN :?#.*', line)
        if m:
            user_join = m.group(1)
            if user_join != NICK:
                ultima_atividade[user_join] = time.time()
                saudacao = saudacao_por_hora(user_join)
                if saudacao:
                    send_raw(f"PRIVMSG {CHANNEL} :{saudacao}")

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
            send_raw(f"PRIVMSG {user} :🛠️ !uptime, !historia, !prenda, !lapada, !radio, !anedota")
            return
        if cmd == "!radio":
            radios = dados.get("radios_online", [])
            msg_r = "📻 Rádios: " + ", ".join([f"{r['nome']} ({r['url']})" for r in radios])
            send_raw(f"PRIVMSG {user} :{msg_r}")
            return
        if cmd == "!anedota":
            anedotas = extras.get("anedotas", [])
            if anedotas:
                send_raw(f"PRIVMSG {reply_to} :😐 {random.choice(anedotas)}")
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

def run_bot():
    global irc_sock
    carregar_dados()
    carregar_extras()
    threading.Thread(target=tarefas_periodicas, daemon=True).start()
    threading.Thread(target=tarefa_anedotas, daemon=True).start()
    threading.Thread(target=tarefa_reforco_positivo, daemon=True).start()

    while True:
        try:
            force_log("=" * 60)
            force_log(f"🛰️  A ligar a {SERVER}:{PORT} ...")

            try:
                resolved_ip = socket.gethostbyname(SERVER)
                force_log(f"📍 {SERVER} → {resolved_ip}")
            except Exception as e:
                force_log(f"⚠️ DNS falhou: {e}")

            irc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc_sock.settimeout(240)
            irc_sock.connect((SERVER, PORT))
            force_log("✅ Socket ligado!")

            # NÃO enviar PASS aqui (é password de servidor, não do NickServ)
            send_raw(f"NICK {NICK}")
            send_raw(f"USER {NICK} 8 * :TheOG Bot")

            buffer = ""
            while True:
                data = irc_sock.recv(4096).decode("utf-8", errors="ignore")
                if not data:
                    force_log("🔌 Conexão fechada pelo servidor (recv vazio).")
                    break

                buffer += data
                while "\r\n" in buffer:
                    line, buffer = buffer.split("\r\n", 1)

                    if " 433 " in line:
                        force_log("⚠️ Nick ocupado → a tentar GHOST...")
                        send_raw(f"PRIVMSG NickServ :GHOST {NICK} {PASS}")
                        time.sleep(2)
                        send_raw(f"NICK {NICK}")
                        continue

                    if " 001 " in line:
                        force_log("🎉 WELCOME recebido (001) — estamos registados no servidor!")

                    if " 376 " in line or " 422 " in line:
                        force_log("✅ Fim do MOTD — a identificar no NickServ...")
                        send_raw(f"PRIVMSG NickServ :IDENTIFY {PASS}")
                        time.sleep(1.5)
                        force_log(f"🚪 A entrar no canal {CHANNEL}...")
                        send_raw(f"JOIN {CHANNEL}")
                        send_raw(f"PRIVMSG {CHANNEL} :[TheOG Online]")
                        force_log("✅ Comandos de JOIN enviados.")

                    handle_irc_event(line)

        except socket.timeout:
            force_log("⏰ Timeout.")
        except ConnectionRefusedError:
            force_log("❌ Ligação recusada.")
        except Exception as e:
            force_log(f"💥 Erro: {type(e).__name__}: {e}")

        if irc_sock:
            try:
                irc_sock.close()
            except:
                pass
            irc_sock = None

        force_log("⏳ Aguardar 180 segundos antes de nova tentativa...")
        time.sleep(180)

# --- FLASK ---
app = Flask(__name__)

@app.route('/')
def home():
    return "TheOG Bot Online", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port), daemon=True).start()
    force_log("🚀 Bot a iniciar...")
    run_bot()
