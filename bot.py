import socket
import time
import threading
import os
import random
import requests
import logging
import sys
import json
from datetime import datetime, timedelta
from flask import Flask

# --- CONFIGURAÇÃO DE LOGS (Essencial para ver no Render) ---
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s [%(levelname)s] %(message)s', 
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("TheOG_Bot")

SERVER = "irc.ptnet.org"
PORT = 6667
NICK = "TheOG"
PASS = "Nasomet112#"
CHANNEL = "#TheOG"
BOT_FILTER = ["nickserv", "chanserv", "memoserv", "operserv", "adamastor", "statserv", "secure", "authserv", "irc", "theog", "bot"]
HF_TOKEN = "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"
API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"

# --- ESTADO E DADOS ---
START_TIME = datetime.now()
STALKER_DATA = {}
STALKER_REQUESTS = {}
CHANNEL_USERS = set()

def carregar_dados():
    try:
        # Verifica se o ficheiro existe antes de abrir
        if os.path.exists('frases.json'):
            with open('frases.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logger.error("ERRO: Ficheiro frases.json não encontrado no diretório!")
            return {}
    except Exception as e:
        logger.error(f"Erro ao ler frases.json: {e}")
        return {}

# Carregar as frases do JSON
dados = carregar_dados()
FRASES_ENTRADA = dados.get("frases_entrada", ["Olá canal!"])
HISTORIA_THEOG = dados.get("historia_theog", [])
PRENDAS = dados.get("prendas", [])
LAPADAS = dados.get("lapadas", [])
OG_EVASIVE = dados.get("evasivas", [])
PUXAR_CONVERSA = dados.get("puxar_conversa", [])
REFORCO_POSITIVO = dados.get("reforco_positivo", [])
USER_GREETINGS = dados.get("saudacoes", [])

# --- FUNÇÕES ---
app = Flask(__name__)

def send_raw(sock, msg):
    try:
        sock.send(f"{msg}\r\n".encode('utf-8'))
    except Exception as e:
        logger.error(f"Erro no envio de dados: {e}")

def parse_whois(line, irc):
    partes = line.split()
    if len(partes) < 4: return
    alvo = partes[3].lower()
    if alvo not in STALKER_REQUESTS: return
    solicitante = STALKER_REQUESTS[alvo]
    
    if alvo not in STALKER_DATA: STALKER_DATA[alvo] = {"nick": partes[3]}
    if " 311 " in line:
        STALKER_DATA[alvo]["host"] = f"{partes[4]}@{partes[5]}"
        STALKER_DATA[alvo]["name"] = line.split(" :", 1)[1]
    elif " 319 " in line: STALKER_DATA[alvo]["channels"] = line.split(" :", 1)[1]
    elif " 317 " in line:
        STALKER_DATA[alvo]["idle"] = str(timedelta(seconds=int(partes[4])))
        STALKER_DATA[alvo]["since"] = datetime.fromtimestamp(int(partes[5])).strftime('%d/%m %H:%M')
    elif " 318 " in line:
        d = STALKER_DATA[alvo]
        rep = [f"🕵️ REPORT [{d['nick']}]:", f"👤 Nome: {d.get('name','?')}", f"🌐 Host: {d.get('host','?')}", f"⏳ Idle: {d.get('idle','0s')}", f"📅 On: {d.get('since','?')}", f"🏠 Canais: {d.get('channels','Privados')}"]
        for r in rep: send_raw(irc, f"PRIVMSG {solicitante} :{r}")
        logger.info(f"Stalker: Relatório enviado para {solicitante} sobre {d['nick']}")
        del STALKER_DATA[alvo], STALKER_REQUESTS[alvo]

def run_bot():
    while True:
        try:
            logger.info(f"A ligar ao servidor {SERVER}...")
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.connect((SERVER, PORT))
            
            send_raw(irc, f"NICK {NICK}")
            send_raw(irc, f"USER {NICK} 8 * :TheOG Bot")
            
            while True:
                data = irc.recv(4096).decode("utf-8", errors="ignore")
                for line in data.split("\r\n"):
                    if not line: continue
                    
                    if line.startswith("PING"):
                        send_raw(irc, f"PONG {line.split()[1]}")
                    
                    if any(x in line for x in [" 311 ", " 317 ", " 318 ", " 319 "]):
                        parse_whois(line, irc)
                    
                    # 376 é o código de fim do MOTD (Bot está oficialmente ligado)
                    if "376" in line:
                        logger.info("Ligação efetuada com sucesso! A identificar...")
                        send_raw(irc, f"PRIVMSG NickServ :IDENTIFY {PASS}")
                        time.sleep(2)
                        logger.info(f"A entrar no canal {CHANNEL}...")
                        send_raw(irc, f"JOIN {CHANNEL}")
                        # Frase de entrada aleatória do JSON
                        frase = random.choice(FRASES_ENTRADA)
                        send_raw(irc, f"PRIVMSG {CHANNEL} :{frase}")

                    if " JOIN " in line:
                        u = line.split('!')[0][1:]
                        if u == NICK:
                            logger.info(f"O Bot está agora dentro do canal {CHANNEL}")
                        else:
                            CHANNEL_USERS.add(u)
                    
                    if " PRIVMSG " in line:
                        # Processar comandos... (lógica do handle_msg)
                        pass

        except Exception as e:
            logger.error(f"Caiu! Erro: {e}. A tentar reconectar em 15s...")
            time.sleep(15)

if __name__ == "__main__":
    # Servidor Flask para o Render não dar erro de Port
    port = int(os.environ.get("PORT", 5000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port), daemon=True).start()
    run_bot()
