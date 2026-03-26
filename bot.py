import socket
import time
import threading
import os
import random
import logging
import sys
import json
from datetime import datetime
from flask import Flask, Response

# --- CONFIGURAÇÃO DE LOGS ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("TheOG_Bot")

LOG_FILE = "chat_log.txt"

def force_log(msg):
    """Log detalhado para o painel do Render e para o ficheiro local."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"{timestamp} [RENDER_DEBUG] {msg}"
    print(log_line)
    sys.stdout.flush()
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")
    except:
        pass

def log_chat(user, channel, message):
    """Regista conversas do canal no ficheiro de log."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] [{channel}] {user}: {message}"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")
    except:
        pass

# --- CONFIGURAÇÃO IRC ---
SERVER = "irc.ptnet.org"
PORT = 6667
NICK = "TheOG"
PASS = "Nasomet112#"
CHANNEL = "#TheOG"

# --- ESTADO GLOBAL ---
START_TIME = datetime.now()
STALKER_DATA = {}
STALKER_REQUESTS = {}
dados = {}

# --- GESTÃO DE DADOS (JSON) ---
def carregar_dados():
    global dados
    try:
        if os.path.exists('frases.json'):
            with open('frases.json', 'r', encoding='utf-8') as f:
                dados = json.load(f)
                n_prendas = len(dados.get("prendas", []))
                n_lapadas = len(dados.get("lapadas", []))
                force_log(f"✅ JSON Carregado: {n_prendas} prendas e {n_lapadas} lapadas detetadas.")
        else:
            force_log("❌ ERRO: frases.json não encontrado no GitHub/Render!")
            criar_base_emergencia()
    except Exception as e:
        force_log(f"🔥 ERRO AO LER JSON: {e}")
        criar_base_emergencia()

def salvar_dados():
    """Guarda o estado atual no JSON (Nota: No Render isto é temporário até ao restart)."""
    try:
        with open('frases.json', 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    except Exception as e:
        force_log(f"Erro ao salvar JSON: {e}")

def criar_base_emergencia():
    global dados
    dados = {
        "admins": ["Emergency112", "Padre", "CutxiiiPoint"],
        "stalker_config": {"alvos_ativos": {}, "avisos_pro": ["🕵️ Alvo {u} online!"]},
        "radios_online": [],
        "frases_entrada": ["TheOG Online!"],
        "saudacoes": ["Olá {u}!"],
        "lapadas": ["dá uma lapada em {u}!"],
        "prendas": ["oferece um café a {u}!"],
        "evasivas": ["Estou ocupado."],
        "historia_theog": ["O canal #TheOG foi criado para reunir amigos."]
    }

carregar_dados()

# --- UTILITÁRIOS ---
def get_uptime():
    delta = datetime.now() - START_TIME
    days = delta.days
    hours, rem = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"

def send_raw(sock, msg):
    try:
        sock.send(f"{msg}\r\n".encode('utf-8'))
    except:
        pass

# --- LÓGICA DE MENSAGENS E COMANDOS ---
def handle_msg(user, message, is_private, irc):
    global dados
    msg_original = message.strip()
    msg_lower = msg_original.lower()
    partes = msg_lower.split()
    if not partes: return
    comando = partes[0]
    target = user if is_private else CHANNEL

    log_chat(user, "PVT" if is_private else CHANNEL, msg_original)

    if comando == "!comandos":
        lista = ["--- 📜 MENU THEOG ---", "!uptime, !radio, !historia, !stalker <nick>", "!lapada <nick>, !prenda <nick>"]
        if user in dados.get("admins", []):
            lista.append("--- 🔐 ADMIN (STALKER-PRO) ---")
            lista.append("!stalkerpro [+ / - / list] [nick]")
        for c in lista:
            send_raw(irc, f"PRIVMSG {user} :{c}")
            time.sleep(0.4)
        return

    if comando == "!stalkerpro":
        if user not in dados.get("admins", []):
            if is_private: send_raw(irc, f"PRIVMSG {user} :❌ Acesso negado.")
            return
        if len(partes) < 2:
            send_raw(irc, f"PRIVMSG {user} :💡 Uso: !stalkerpro [+ / - / list] [nick]")
            return
        acao = partes[1]
        if acao == "list":
            vigia = dados.get("stalker_config", {}).get("alvos_ativos", {})
            if not vigia: send_raw(irc, f"PRIVMSG {user} :📂 Lista de vigia vazia.")
            else:
                for alvo, adm in vigia.items():
                    send_raw(irc, f"PRIVMSG {user} :🕵️ Alvo: {alvo} (Vigiado por: {adm})")
            return
        if len(partes) > 2:
            alvo = partes[2].lower()
            if acao == "+":
                dados.setdefault("stalker_config", {}).setdefault("alvos_ativos", {})[alvo] = user
                send_raw(irc, f"WATCH +{alvo}")
                send_raw(irc, f"PRIVMSG {user} :🎯 Alvo '{alvo}' adicionado à vigia.")
            elif acao == "-":
                if alvo in dados.get("stalker_config", {}).get("alvos_ativos", {}):
                    del dados["stalker_config"]["alvos_ativos"][alvo]
                    send_raw(irc, f"WATCH -{alvo}")
                    send_raw(irc, f"PRIVMSG {user} :🗑️ Alvo '{alvo}' removido.")
            salvar_dados()

    elif comando == "!stalker":
        if len(partes) > 1:
            alvo = partes[1].lower()
            STALKER_REQUESTS[alvo] = user
            send_raw(irc, f"WHOIS {alvo} {alvo}")
            send_raw(irc, f"PRIVMSG {target} :🔎 Investigando '{alvo}'...")

    elif comando == "!prenda":
        alvo = partes[1] if len(partes) > 1 else user
        frase = random.choice(dados.get("prendas", ["oferece um café a {u}!"]))
        send_raw(irc, f"PRIVMSG {CHANNEL} :\x01ACTION {frase.format(u=alvo)}\x01")

    elif comando == "!lapada":
        alvo = partes[1] if len(partes) > 1 else user
        frase = random.choice(dados.get("lapadas", ["dá uma lapada em {u}!"]))
        send_raw(irc, f"PRIVMSG {CHANNEL} :\x01ACTION {frase.format(u=alvo)}\x01")

    elif comando == "!uptime":
        send_raw(irc, f"PRIVMSG {target} :🚀 Uptime: {get_uptime()}")

    elif comando == "!radio":
        radios = dados.get("radios_online", [])
        if radios:
            r = random.choice(radios)
            send_raw(irc, f"PRIVMSG {target} :📻 Sugestão: {r['nome']} - {r['url']}")

    elif comando == "!historia":
        for linha in dados.get("historia_theog", []):
            send_raw(irc, f"PRIVMSG {user} :{linha}")
            time.sleep(0.8)

    elif NICK.lower() in msg_lower:
        send_raw(irc, f"PRIVMSG {target} :{user}: {random.choice(dados.get('evasivas', ['Estou ocupado!']))}")

# --- PROCESSAMENTO IRC ---
def parse_irc_lines(line, irc):
    global dados
    partes = line.split()
    if not partes: return

    # Resposta ao WHOIS
    if any(x in line for x in [" 311 ", " 317 ", " 318 ", " 319 "]):
        try:
            alvo = partes[3].lower()
            if alvo in STALKER_REQUESTS:
                if alvo not in STALKER_DATA: STALKER_DATA[alvo] = {"nick": partes[3]}
                if " 311 " in line: STALKER_DATA[alvo]["info"] = f"{partes[4]}@{partes[5]}"
                elif " 319 " in line: STALKER_DATA[alvo]["canais"] = line.split(" :", 1)[1]
                elif " 318 " in line:
                    d = STALKER_DATA[alvo]
                    send_raw(irc, f"PRIVMSG {STALKER_REQUESTS[alvo]} :🕵️ REPORT: {d['nick']} | Host: {d.get('info','?')} | Canais: {d.get('canais','?')}")
                    STALKER_DATA.pop(alvo, None)
                    STALKER_REQUESTS.pop(alvo, None)
        except: pass

    # Notificação do WATCH (StalkerPro)
    if " 600 " in line and len(partes) > 3:
        u_alvo = partes[3].lower()
        vigia = dados.get("stalker_config", {}).get("alvos_ativos", {})
        if u_alvo in vigia:
            adm = vigia[u_alvo]
            send_raw(irc, f"PRIVMSG {adm} :🕵️ ALERTA: O teu alvo '{u_alvo}' acabou de entrar no IRC!")

    # 353 Lista de utilizadores (RPL_NAMREPLY)
    if " 353 " in line:
        users_list = line.split(" :")[-1]
        force_log(f"👥 UTILIZADORES NO CANAL: {users_list}")

    # Confirmação de entrada (JOIN)
    if f":{NICK}!" in line and " JOIN " in line:
        force_log(f"🚩 SUCESSO: O bot entrou no canal {CHANNEL}")
        send_raw(irc, f"NAMES {CHANNEL}")

# --- SERVIDOR WEB ---
app = Flask(__name__)
@app.route('/')
def home(): return f"<h1>TheOG Online</h1><p>Uptime: {get_uptime()}</p><a href='/logs'>Ver Logs</a>"

@app.route('/logs')
def view_logs():
    if not os.path.exists(LOG_FILE): return "Sem logs."
    with open(LOG_FILE, "r", encoding="utf-8") as f: content = f.read()
    return Response(content, mimetype='text/plain')

# --- LOOP PRINCIPAL ---
def run_bot():
    while True:
        irc = None
        try:
            force_log(f"🛰️ Conectando a {SERVER}...")
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.settimeout(240)
            irc.connect((SERVER, PORT))
            
            send_raw(irc, f"PASS {PASS}")
            send_raw(irc, f"NICK {NICK}")
            send_raw(irc, f"USER {NICK} 8 * :TheOG Bot")
            
            while True:
                data = irc.recv(4096).decode("utf-8", errors="ignore")
                if not data: break
                
                for line in data.split("\r\n"):
                    if not line: continue
                    if line.startswith("PING"): 
                        send_raw(irc, f"PONG {line.split()[1]}")
                        continue
                    
                    parse_irc_lines(line, irc)
                    
                    if " 376 " in line or " 422 " in line:
                        send_raw(irc, f"PRIVMSG NickServ :IDENTIFY {PASS}")
                        time.sleep(2)
                        send_raw(irc, f"JOIN {CHANNEL}")
                        # WATCH para os alvos ativos ao ligar
                        for a in dados.get("stalker_config", {}).get("alvos_ativos", {}):
                            send_raw(irc, f"WATCH +{a}")
                        
                        entradas = dados.get('frases_entrada', ['TheOG Online!'])
                        send_raw(irc, f"PRIVMSG {CHANNEL} :{random.choice(entradas)}")

                    if " JOIN " in line and f" :{CHANNEL}" in line:
                        u = line.split('!')[0][1:]
                        if u != NICK:
                            saudacoes = dados.get('saudacoes', ['Olá {u}!'])
                            send_raw(irc, f"PRIVMSG {CHANNEL} :{random.choice(saudacoes).format(u=u)}")

                    if " PRIVMSG " in line:
                        try:
                            u_from = line.split('!')[0][1:]
                            t_dest = line.split(' PRIVMSG ')[1].split(' :')[0]
                            m_text = line.split(' PRIVMSG ')[1].split(' :', 1)[1]
                            handle_msg(u_from, m_text, t_dest == NICK, irc)
                        except: continue
        except Exception as e:
            force_log(f"💥 ERRO: {e}")
        finally:
            if irc: irc.close()
            time.sleep(60)

if __name__ == "__main__":
    port_render = int(os.environ.get("PORT", 5000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port_render), daemon=True).start()
    run_bot()
