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
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s [%(levelname)s] %(message)s', 
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("TheOG_Bot")

def force_log(msg):
    logger.info(msg)
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

# --- GESTÃO DE DADOS ---
def carregar_dados():
    global dados
    try:
        if os.path.exists('frases.json'):
            with open('frases.json', 'r', encoding='utf-8') as f:
                dados = json.load(f)
        else:
            dados = {
                "admins": ["Emergency112"],
                "frases_entrada": ["TheOG Online e Estável!"],
                "saudacoes": ["Olá {u}!", "Boas {u}, tudo bem?"],
                "evasivas": ["Estou aqui a processar dados..."],
                "convites_frases": ["Olá {u}, aparece no canal #TheOG quando puderes!"]
            }
    except Exception as e:
        force_log(f"Erro no JSON: {e}")

carregar_dados()

def get_uptime():
    delta = datetime.now() - START_TIME
    return str(delta).split('.')[0] # Formato simples: Dias, HH:MM:SS

def send_raw(sock, msg):
    """Envia comandos com atraso de 1.5s para evitar ser banido por flood."""
    try:
        sock.send(f"{msg}\r\n".encode('utf-8'))
        time.sleep(1.5) 
    except:
        pass

# --- LÓGICA DE MENSAGENS ---
def handle_msg(user, message, is_private, irc):
    msg = message.lower().strip()
    target = user if is_private else CHANNEL
    
    if msg.startswith("!uptime"):
        send_raw(irc, f"PRIVMSG {target} :🚀 Uptime: {get_uptime()}")
    
    elif msg.startswith("!convidar"):
        partes = msg.split()
        if len(partes) > 1:
            alvo = partes[1]
            frase = random.choice(dados.get("convites_frases", ["Vem ao #TheOG!"])).format(u=alvo)
            send_raw(irc, f"PRIVMSG {alvo} :{frase}")
            force_log(f"Convite enviado para {alvo}")

    elif NICK.lower() in msg:
        send_raw(irc, f"PRIVMSG {target} :{user}: {random.choice(dados.get('evasivas'))}")

# --- LOOP PRINCIPAL ---
app = Flask(__name__)
@app.route('/')
def home(): return f"TheOG Bot Ativo - {get_uptime()}"

def run_bot():
    while True:
        irc = None
        try:
            force_log("--- A INICIAR CONEXÃO ---")
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.settimeout(240)
            irc.connect((SERVER, PORT))
            
            # 1. Identificação Inicial
            send_raw(irc, f"PASS {PASS}")
            send_raw(irc, f"NICK {NICK}")
            send_raw(irc, f"USER {NICK} 8 * :TheOG Manager")
            
            while True:
                data = irc.recv(4096).decode("utf-8", errors="ignore")
                if not data: break
                
                for line in data.split("\r\n"):
                    if not line: continue
                    
                    # Responder ao PING imediatamente
                    if line.startswith("PING"):
                        irc.send(f"PONG {line.split()[1]}\r\n".encode())
                        continue

                    # Erro 433: Nick em uso (O "Bot fantasma")
                    if " 433 " in line:
                        force_log(f"AVISO: O nick {NICK} está preso. A tentar GHOST...")
                        # Usa um nick temporário para dar o comando GHOST
                        irc.send(f"NICK {NICK}_{random.randint(10,99)}\r\n".encode())
                        time.sleep(2)
                        send_raw(irc, f"PRIVMSG NickServ :GHOST {NICK} {PASS}")
                        time.sleep(5) # Espera o servidor derrubar o antigo
                        send_raw(irc, f"NICK {NICK}")
                        continue

                    # 376 ou 422: Fim do MOTD (Ligado com sucesso)
                    if " 376 " in line or " 422 " in line:
                        force_log("CONECTADO: A entrar no canal...")
                        send_raw(irc, f"PRIVMSG NickServ :IDENTIFY {PASS}")
                        time.sleep(3)
                        send_raw(irc, f"JOIN {CHANNEL}")
                        send_raw(irc, f"PRIVMSG {CHANNEL} :{random.choice(dados.get('frases_entrada'))}")

                    # Monitorizar Entradas e Saídas
                    if " JOIN " in line and CHANNEL in line:
                        u = line.split('!')[0][1:]
                        if u != NICK:
                            force_log(f"ENTROU: {u}")
                            msg = random.choice(dados.get('saudacoes')).format(u=u)
                            send_raw(irc, f"PRIVMSG {CHANNEL} :{msg}")

                    if " PART " in line or " QUIT " in line:
                        u = line.split('!')[0][1:]
                        if u != NICK:
                            force_log(f"SAIU: {u} (Motivo: {line[-15:]})")

                    # Processar Mensagens
                    if " PRIVMSG " in line:
                        u = line.split('!')[0][1:]
                        try:
                            t = line.split(' PRIVMSG ')[1].split(' :')[0]
                            m = line.split(' PRIVMSG ')[1].split(' :', 1)[1]
                            handle_msg(u, m, t == NICK, irc)
                        except: continue

        except Exception as e:
            force_log(f"ERRO DE SOCKET: {e}")
        finally:
            if irc:
                force_log("A fechar socket e aguardar 30 segundos para limpar fantasmas...")
                irc.close()
            time.sleep(30) # Espera longa para o servidor limpar a sessão anterior

if __name__ == "__main__":
    # Flask para manter o Render feliz
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000))), daemon=True).start()
    run_bot()
