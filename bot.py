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
irc_sock = None # Socket global para as threads acederem
JSON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frases.json')

def carregar_dados():
    global dados
    try:
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            force_log("✅ JSON carregado com sucesso!")
        else:
            force_log("❌ ERRO: frases.json não encontrado!")
    except Exception as e:
        force_log(f"🔥 Erro ao ler JSON: {e}")

def salvar_dados():
    try:
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    except Exception as e:
        force_log(f"🔥 Erro ao salvar JSON: {e}")

def send_raw(msg):
    global irc_sock
    try:
        if irc_sock:
            irc_sock.send(f"{msg}\r\n".encode('utf-8'))
    except:
        pass

# --- TAREFAS TEMPORIZADAS (20 MINUTOS) ---
def tarefas_periodicas():
    """Reforço positivo e Puxar conversa a cada 20 min."""
    while True:
        time.sleep(1200) # 20 minutos
        if not dados or not irc_sock: continue
        
        # 1. Reforço Positivo
        reforcos = dados.get("reforco_positivo", [])
        if reforcos:
            msg = random.choice(reforcos)
            send_raw(f"PRIVMSG {CHANNEL} :{msg}")
        
        # 2. Puxar Conversa com Inativos
        now = time.time()
        puxar_frases = dados.get("puxar_conversa", [])
        if puxar_frases and ultima_atividade:
            # Nicks que não falam há mais de 20 min
            inativos = [n for n, t in ultima_atividade.items() if (now - t) > 1200 and n != NICK]
            if inativos:
                alvo = random.choice(inativos)
                frase = random.choice(puxar_frases).replace("{u}", alvo)
                send_raw(f"PRIVMSG {CHANNEL} :{frase}")

# --- PROCESSAMENTO DE EVENTOS IRC ---
def handle_irc_event(line):
    global dados, ultima_atividade
    
    # 1. TRATAR PING
    if line.startswith("PING"):
        send_raw(f"PONG {line.split()[1]}")
        return

    # 2. ALGUÉM ENTROU NO CANAL (JOIN)
    if " JOIN " in line:
        m = re.match(r'^:([^! ]+)!.* JOIN :?#.*', line)
        if m:
            user_join = m.group(1)
            if user_join != NICK: # Não cumprimentar a si próprio
                saudacoes = dados.get("saudacoes", [])
                if saudacoes:
                    saudacao = random.choice(saudacoes).replace("{u}", user_join)
                    send_raw(f"PRIVMSG {CHANNEL} :{saudacao}")
                # Regista atividade inicial para não ser logo marcado como inativo
                ultima_atividade[user_join] = time.time()
        return

    # 3. MENSAGENS (PRIVMSG)
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

        # COMANDOS EM PVT
        if cmd == "!comandos":
            lista = "!comandos, !uptime, !historia, !prenda, !lapada, !radio"
            if is_admin: lista += ", !stalkerpro"
            send_raw(f"PRIVMSG {user} :🛠️ Comandos: {lista}")
            return

        if cmd == "!radio":
            radios = dados.get("radios_online", [])
            msg_r = "📻 Rádios: " + ", ".join([f"{r['nome']} ({r['url']})" for r in radios])
            send_raw(f"PRIVMSG {user} :{msg_r}")
            return

        # COMANDOS NO CANAL/PVT
        reply_to = target if is_channel else user

        if cmd == "!uptime":
            delta = datetime.now() - START_TIME
            uptime_str = f"{delta.days}d {delta.seconds//3600}h {(delta.seconds//60)%60}m"
            send_raw(f"PRIVMSG {reply_to} :🚀 Uptime: {uptime_str}")

        elif cmd == "!historia":
            for linha in dados.get("historia_theog", []):
                send_raw(f"PRIVMSG {reply_to} :{linha}")
                time.sleep(0.7)

        elif cmd == "!prenda":
            alvo = partes[1] if len(partes) > 1 else user
            frase = random.choice(dados.get("prendas", ["oferece algo a {u}"]))
            send_raw(f"PRIVMSG {reply_to} :\x01ACTION {frase.replace('{u}', alvo)}\x01")

        elif cmd == "!lapada":
            alvo = partes[1] if len(partes) > 1 else user
            frase = random.choice(dados.get("lapadas", ["dá uma lapada em {u}"]))
            send_raw(f"PRIVMSG {reply_to} :\x01ACTION {frase.replace('{u}', alvo)}\x01")

        # STALKER PRO
        elif cmd == "!stalkerpro" and is_admin:
            if len(partes) > 2:
                acao, alvo = partes[1], partes[2].lower()
                if acao == "+":
                    dados.setdefault("stalker_config", {}).setdefault("alvos_ativos", {})[alvo] = user
                    send_raw(f"WATCH +{alvo}")
                    send_raw(f"PRIVMSG {user} :🎯 {alvo} vigiado.")
                elif acao == "-":
                    dados.get("stalker_config", {}).get("alvos_ativos", {}).pop(alvo, None)
                    send_raw(f"WATCH -{alvo}")
                    send_raw(f"PRIVMSG {user} :❌ {alvo} removido.")
                salvar_dados()

        # MENÇÃO AO BOT
        elif NICK.lower() in msg_lower:
            pool = dados.get("saudacoes", []) + dados.get("evasivas", [])
            if pool:
                res = random.choice(pool).replace("{u}", user)
                send_raw(f"PRIVMSG {reply_to} :{res}")

    # 4. EVENTOS DE WATCH (STALKER)
    elif " 604 " in line or " 600 " in line:
        partes = line.split()
        alvo_detectado = partes[3].lower()
        admin = dados.get("stalker_config", {}).get("alvos_ativos", {}).get(alvo_detectado)
        if admin:
            aviso = random.choice(dados["stalker_config"].get("avisos_pro", ["Alvo online!"]))
            send_raw(f"PRIVMSG {admin} :{aviso.replace('{u}', alvo_detectado)}")

# --- LOOP PRINCIPAL ---
def run_bot():
    global irc_sock
    carregar_dados()
    
    # Inicia thread de tarefas (reforço/puxar conversa)
    threading.Thread(target=tarefas_periodicas, daemon=True).start()

    while True:
        try:
            irc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
                    
                    # Conectado com sucesso
                    if " 376 " in line or " 422 " in line:
                        send_raw(f"PRIVMSG NickServ :IDENTIFY {PASS}")
                        time.sleep(1)
                        send_raw(f"JOIN {CHANNEL}")
                        entrada = random.choice(dados.get("frases_entrada", ["Olá!"]))
                        send_raw(f"PRIVMSG {CHANNEL} :{entrada}")
                        for a in dados.get("stalker_config", {}).get("alvos_ativos", {}):
                            send_raw(f"WATCH +{a}")

                    handle_irc_event(line)

        except Exception as e:
            force_log(f"💥 Erro: {e}")
            time.sleep(10)

# --- WEB SERVER ---
app = Flask(__name__)
@app.route('/')
def home(): return "TheOG Bot Online"

if __name__ == "__main__":
    t = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000))), daemon=True)
    t.start()
    run_bot()
