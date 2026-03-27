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
ultima_atividade = {} # Guarda o timestamp da última mensagem de cada nick
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

def send_raw(sock, msg):
    try:
        sock.send(f"{msg}\r\n".encode('utf-8'))
    except:
        pass

# --- TAREFAS TEMPORIZADAS ---
def tarefas_periodicas(irc):
    """Executa reforço positivo a cada 20 min e puxa conversa com inativos."""
    while True:
        time.sleep(1200) # 20 minutos
        if not dados: continue
        
        # 1. Reforço Positivo no Canal
        reforcos = dados.get("reforco_positivo", [])
        if reforcos:
            msg = random.choice(reforcos)
            send_raw(irc, f"PRIVMSG {CHANNEL} :{msg}")
        
        # 2. Interagir com quem menos fala (Puxar Conversa)
        now = time.time()
        puxar_frases = dados.get("puxar_conversa", [])
        if puxar_frases and ultima_atividade:
            # Filtra nicks que não falaram nos últimos 20 min (excluindo o bot)
            inativos = [n for n, t in ultima_atividade.items() if (now - t) > 1200 and n != NICK]
            if inativos:
                alvo = random.choice(inativos)
                frase = random.choice(puxar_frases).replace("{u}", alvo)
                send_raw(irc, f"PRIVMSG {CHANNEL} :{frase}")

# --- LÓGICA DE MENSAGENS ---
def handle_irc_msg(user, message, target, irc):
    global dados, ultima_atividade
    msg_clean = re.sub(r'\x03(?:\d{1,2}(?:,\d{1,2})?)?|[\x02\x0F\x16\x1D\x1F]', '', message).strip()
    if not msg_clean: return
    
    # Atualiza última atividade do utilizador
    ultima_atividade[user] = time.time()
    
    msg_lower = msg_clean.lower()
    partes = msg_clean.split()
    cmd = partes[0].lower()
    is_channel = target.startswith("#")
    is_admin = user in dados.get("admins", [])

    # --- COMANDOS EM PVT (Sempre em PVT como pedido) ---
    if cmd == "!comandos":
        lista = "!comandos, !uptime, !historia, !prenda, !lapada, !radio"
        if is_admin: lista += ", !stalkerpro"
        send_raw(irc, f"PRIVMSG {user} :🛠️ Comandos: {lista}")
        return

    # --- COMANDOS GERAIS ---
    if cmd == "!uptime":
        delta = datetime.now() - START_TIME
        uptime_str = f"{delta.days}d {delta.seconds//3600}h {(delta.seconds//60)%60}m"
        send_raw(irc, f"PRIVMSG {target if is_channel else user} :🚀 Uptime: {uptime_str}")

    elif cmd == "!historia":
        for linha in dados.get("historia_theog", []):
            send_raw(irc, f"PRIVMSG {target if is_channel else user} :{linha}")
            time.sleep(0.8)

    elif cmd == "!radio":
        radios = dados.get("radios_online", [])
        msg_radio = "📻 Rádios: " + ", ".join([f"{r['nome']} ({r['url']})" for r in radios])
        send_raw(irc, f"PRIVMSG {user} :{msg_radio}")

    elif cmd == "!prenda":
        alvo = partes[1] if len(partes) > 1 else user
        frase = random.choice(dados.get("prendas", ["dá um presente a {u}"]))
        send_raw(irc, f"PRIVMSG {target if is_channel else user} :\x01ACTION {frase.replace('{u}', alvo)}\x01")

    elif cmd == "!lapada":
        alvo = partes[1] if len(partes) > 1 else user
        frase = random.choice(dados.get("lapadas", ["dá uma lapada em {u}"]))
        send_raw(irc, f"PRIVMSG {target if is_channel else user} :\x01ACTION {frase.replace('{u}', alvo)}\x01")

    # --- STALKER PRO (ADMIN) ---
    elif cmd == "!stalkerpro" and is_admin:
        if len(partes) > 2:
            acao, alvo = partes[1], partes[2].lower()
            if acao == "+":
                dados.setdefault("stalker_config", {}).setdefault("alvos_ativos", {})[alvo] = user
                send_raw(irc, f"WATCH +{alvo}")
                send_raw(irc, f"PRIVMSG {user} :🎯 {alvo} vigiado.")
            elif acao == "-":
                dados.get("stalker_config", {}).get("alvos_ativos", {}).pop(alvo, None)
                send_raw(irc, f"WATCH -{alvo}")
                send_raw(irc, f"PRIVMSG {user} :❌ {alvo} removido.")
            salvar_dados()

    # --- MENÇÃO / INTERAÇÃO ---
    elif NICK.lower() in msg_lower:
        # Se alguém falar com o bot, ele pode responder com evasivas ou saudações
        pool = dados.get("saudacoes", []) + dados.get("evasivas", [])
        if pool:
            escolha = random.choice(pool).replace("{u}", user)
            send_raw(irc, f"PRIVMSG {target if is_channel else user} :{escolha}")

# --- LOOP PRINCIPAL ---
def run_bot():
    carregar_dados()
    while True:
        try:
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.connect((SERVER, PORT))
            send_raw(irc, f"PASS {PASS}")
            send_raw(irc, f"NICK {NICK}")
            send_raw(irc, f"USER {NICK} 8 * :TheOG Bot")
            
            # Inicia thread de tarefas automáticas (20 em 20 min)
            threading.Thread(target=tarefas_periodicas, args=(irc,), daemon=True).start()
            
            buffer = ""
            while True:
                data = irc.recv(4096).decode("utf-8", errors="ignore")
                if not data: break
                buffer += data
                while "\r\n" in buffer:
                    line, buffer = buffer.split("\r\n", 1)
                    if line.startswith("PING"):
                        send_raw(irc, f"PONG {line.split()[1]}")
                    
                    # Ao entrar no canal
                    elif " 376 " in line:
                        send_raw(irc, f"JOIN {CHANNEL}")
                        time.sleep(1)
                        # Frase de entrada aleatória
                        entrada = random.choice(dados.get("frases_entrada", ["Olá!"]))
                        send_raw(irc, f"PRIVMSG {CHANNEL} :{entrada}")
                        # Reativa WATCH
                        for a in dados.get("stalker_config", {}).get("alvos_ativos", {}):
                            send_raw(irc, f"WATCH +{a}")

                    # Detectar entrada de alvos (WATCH)
                    elif " 604 " in line or " 600 " in line: # Numerics para WATCH online
                        partes = line.split()
                        alvo_detectado = partes[3].lower()
                        avisos = dados.get("stalker_config", {}).get("avisos_pro", [])
                        if avisos:
                            msg_aviso = random.choice(avisos).replace("{u}", alvo_detectado)
                            # Avisa o admin que adicionou
                            admin = dados["stalker_config"]["alvos_ativos"].get(alvo_detectado)
                            if admin: send_raw(irc, f"PRIVMSG {admin} :{msg_aviso}")

                    elif " PRIVMSG " in line:
                        m = re.match(r'^:([^! ]+)!.* PRIVMSG ([^ ]+) :(.*)$', line)
                        if m: handle_irc_msg(m.group(1), m.group(3), m.group(2), irc)

        except Exception as e:
            force_log(f"💥 Erro: {e}")
            time.sleep(10)

# --- WEB SERVER ---
app = Flask(__name__)
@app.route('/')
def home(): return "TheOG Online"

if __name__ == "__main__":
    t = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000))), daemon=True)
    t.start()
    run_bot()
