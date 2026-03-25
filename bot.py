import socket
import time
import threading
import os
import random
import logging
import sys
import json
from datetime import datetime
from flask import Flask

# --- CONFIGURAÇÃO DE LOGS ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("TheOG_Bot")

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
                logger.info("Ficheiro frases.json carregado com sucesso.")
        else:
            logger.error("ERRO: frases.json não encontrado! A criar base...")
            criar_base_emergencia()
    except json.JSONDecodeError as e:
        logger.error(f"ERRO CRÍTICO NO JSON: {e}. Verifique as vírgulas!")
        # Carrega estrutura mínima para evitar crash total
        dados = {"admins": ["Emergency112"], "stalker_config": {"alvos_ativos": {}}}

def salvar_dados():
    try:
        with open('frases.json', 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Erro ao guardar JSON: {e}")

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
        "evasivas": ["Estou ocupado."]
    }
    salvar_dados()

carregar_dados()

# --- UTILITÁRIOS ---
def get_uptime():
    delta = datetime.now() - START_TIME
    days = delta.days
    hours, rem = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"

def send_raw(sock, msg):
    try: sock.send(f"{msg}\r\n".encode('utf-8'))
    except: pass

# --- LÓGICA DE MENSAGENS E COMANDOS ---
def handle_msg(user, message, is_private, irc):
    global dados
    msg = message.lower().strip()
    partes = msg.split()
    if not partes: return
    comando = partes[0]
    target = user if is_private else CHANNEL

    # --- COMANDO !COMANDOS (INTELIGENTE & DINÂMICO) ---
    if comando == "!comandos":
        lista_pode_ver = [
            "--- 📜 MENU THEOG ---",
            "!comandos - Esta lista (em PVT).",
            "!uptime   - Tempo de atividade.",
            "!stalker <nick> - Relatório WHOIS (PVT).",
            "!radio    - Sugestão de rádio.",
            "!historia - A história do canal (PVT).",
            "!lapada <nick> - Ação no canal.",
            "!prenda <nick> - Ação no canal."
        ]
        
        # Se for ADMIN, adiciona os comandos secretos
        if user in dados.get("admins", []):
            lista_pode_ver.append("--- 🔐 ADMIN (STALKER-PRO) ---")
            lista_pode_ver.append("!stalkerpro + <nick> - Vigiar entrada.")
            lista_pode_ver.append("!stalkerpro - <nick> - Parar vigia.")
            lista_pode_ver.append("!stalkerpro list     - Ver alvos.")

        lista_pode_ver.append("----------------------")

        for c in lista_pode_ver:
            send_raw(irc, f"PRIVMSG {user} :{c}")
            time.sleep(0.4)
        return

    # --- COMANDO !STALKERPRO (APENAS ADMINS) ---
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
                dados["stalker_config"]["alvos_ativos"][alvo] = user
                send_raw(irc, f"WATCH +{alvo}")
                send_raw(irc, f"PRIVMSG {user} :🎯 Alvo '{alvo}' adicionado com sucesso.")
            elif acao == "-":
                if alvo in dados["stalker_config"]["alvos_ativos"]:
                    del dados["stalker_config"]["alvos_ativos"][alvo]
                    send_raw(irc, f"WATCH -{alvo}")
                    send_raw(irc, f"PRIVMSG {user} :🗑️ Alvo '{alvo}' removido.")
            salvar_dados()

    # --- OUTROS COMANDOS ---
    elif comando == "!stalker":
        if len(partes) > 1:
            alvo = partes[1].lower()
            STALKER_REQUESTS[alvo] = user
            send_raw(irc, f"WHOIS {alvo} {alvo}")
            send_raw(irc, f"PRIVMSG {target} :🔎 Investigação sobre '{alvo}' iniciada...")

    elif comando == "!uptime":
        send_raw(irc, f"PRIVMSG {target} :🚀 {NICK} online há: {get_uptime()}")

    elif comando == "!radio":
        radios = dados.get("radios_online", [])
        if radios:
            r = random.choice(radios)
            send_raw(irc, f"PRIVMSG {target} :📻 Sugestão: {r['nome']} - {r['url']}")

    elif comando == "!historia":
        for linha in dados.get("historia_theog", ["História não configurada."]):
            send_raw(irc, f"PRIVMSG {user} :{linha}")
            time.sleep(1)

    elif comando == "!lapada":
        alvo = partes[1] if len(partes) > 1 else user
        frase = random.choice(dados.get("lapadas", ["lapada em {u}!"]))
        send_raw(irc, f"PRIVMSG {CHANNEL} :\x01ACTION {frase.format(u=alvo)}\x01")

    elif comando == "!prenda":
        alvo = partes[1] if len(partes) > 1 else user
        frase = random.choice(dados.get("prendas", ["oferece algo a {u}!"]))
        send_raw(irc, f"PRIVMSG {CHANNEL} :\x01ACTION {frase.format(u=alvo)}\x01")

    # Resposta por menção
    elif NICK.lower() in msg:
        send_raw(irc, f"PRIVMSG {target} :{user}: {random.choice(dados.get('evasivas', ['Estou ocupado!']))}")

# --- PROCESSAMENTO IRC ---
def parse_irc_lines(line, irc):
    global dados
    partes = line.split()
    
    # Notificação de WATCH (Alvo entrou)
    if " 600 " in line and len(partes) > 3:
        u_alvo = partes[3].lower()
        vigia = dados.get("stalker_config", {}).get("alvos_ativos", {})
        if u_alvo in vigia:
            adm = vigia[u_alvo]
            avisos = dados.get("stalker_config", {}).get("avisos_pro", ["🕵️ Alvo {u} entrou!"])
            aviso = random.choice(avisos).format(u=u_alvo)
            send_raw(irc, f"PRIVMSG {adm} :{aviso}")

    # WHOIS Logic
    if any(x in line for x in [" 311 ", " 317 ", " 318 ", " 319 "]):
        try:
            alvo = partes[3].lower()
            if alvo in STALKER_REQUESTS:
                solicitante = STALKER_REQUESTS[alvo]
                if alvo not in STALKER_DATA: STALKER_DATA[alvo] = {"nick": partes[3]}
                if " 311 " in line: STALKER_DATA[alvo]["info"] = f"{partes[4]}@{partes[5]}"
                elif " 319 " in line: STALKER_DATA[alvo]["canais"] = line.split(" :", 1)[1]
                elif " 318 " in line:
                    d = STALKER_DATA[alvo]
                    send_raw(irc, f"PRIVMSG {solicitante} :🕵️ REPORT: {d['nick']} | Host: {d.get('info','?')} | Canais: {d.get('canais','?')}")
                    del STALKER_DATA[alvo], STALKER_REQUESTS[alvo]
        except: pass

# --- SERVIDOR WEB (Keep Alive) ---
app = Flask(__name__)
@app.route('/')
def home(): return "TheOG Bot Online!"

# --- LOOP PRINCIPAL ---
def run_bot():
    while True:
        try:
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.connect((SERVER, PORT))
            send_raw(irc, f"NICK {NICK}")
            send_raw(irc, f"USER {NICK} 8 * :TheOG Bot")
            
            while True:
                data = irc.recv(4096).decode("utf-8", errors="ignore")
                if not data: break
                for line in data.split("\r\n"):
                    if not line: continue
                    if line.startswith("PING"): send_raw(irc, f"PONG {line.split()[1]}")
                    parse_irc_lines(line, irc)
                    
                    if " 376 " in line: # Fim do MOTD
                        send_raw(irc, f"PRIVMSG NickServ :IDENTIFY {PASS}")
                        time.sleep(2)
                        send_raw(irc, f"JOIN {CHANNEL}")
                        send_raw(irc, f"PRIVMSG {CHANNEL} :{random.choice(dados.get('frases_entrada', ['Olá!']))}")
                        # Re-ligar WATCH para alvos ativos
                        for a in dados.get("stalker_config", {}).get("alvos_ativos", {}):
                            send_raw(irc, f"WATCH +{a}")

                    if " JOIN " in line:
                        u = line.split('!')[0][1:]
                        if u != NICK:
                            msg = random.choice(dados.get('saudacoes', ['Olá {u}!'])).format(u=u)
                            send_raw(irc, f"PRIVMSG {CHANNEL} :{msg}")

                    if " PRIVMSG " in line:
                        u = line.split('!')[0][1:]
                        try:
                            t = line.split(' PRIVMSG ')[1].split(' :')[0]
                            m = line.split(' PRIVMSG ')[1].split(' :', 1)[1]
                            handle_msg(u, m, t == NICK, irc)
                        except: continue
        except Exception as e:
            logger.error(f"Erro na ligação: {e}. Reconectando em 15s...")
            time.sleep(15)

if __name__ == "__main__":
    # Inicia Web server em background
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000))), daemon=True).start()
    run_bot()
