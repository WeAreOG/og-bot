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

# --- CONFIGURAÇÃO DE LOGS PARA RENDER (FORÇADOS) ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("TheOG_Bot")

def force_log(msg):
    """Garante que o log aparece no painel do Render imediatamente."""
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
                force_log("Ficheiro frases.json carregado com sucesso.")
        else:
            force_log("AVISO: frases.json não encontrado! A criar base de emergência...")
            criar_base_emergencia()
    except Exception as e:
        force_log(f"ERRO AO CARREGAR JSON: {e}")
        criar_base_emergencia()

def salvar_dados():
    try:
        with open('frases.json', 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    except Exception as e:
        force_log(f"Erro ao guardar JSON: {e}")

def criar_base_emergencia():
    global dados
    dados = {
        "admins": ["Emergency112", "Padre", "CutxiiiPoint"],
        "stalker_config": {"alvos_ativos": {}, "avisos_pro": ["🕵️ Alvo {u} detetado!"]},
        "radios_online": [],
        "frases_entrada": ["TheOG de volta ao serviço!", "Sistema carregado. Olá a todos!"],
        "saudacoes": ["Olá {u}, bem-vindo ao #TheOG!", "Boas {u}! Como vai isso?"],
        "lapadas": ["dá uma lapada valente em {u}!"],
        "prendas": ["oferece uma imperial gelada a {u}!"],
        "evasivas": ["Agora não posso, estou a configurar uns kernels...", "Diz lá, estou a ouvir com um ouvido."],
        "convites_frases": [
            "Ei {u}, junta-te a nós no #TheOG, a melhor malta da PTNet!",
            "Olá {u}, se procuras um canal descontraído, passa no #TheOG!"
        ],
        "historia_theog": ["O canal #TheOG nasceu da vontade de unir tecnologia e amizade."]
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
    """Envia comandos de forma lenta para evitar expulsão por flood."""
    try:
        sock.send(f"{msg}\r\n".encode('utf-8'))
        time.sleep(1.0) # Abrandamento forçado entre comandos
    except Exception as e:
        force_log(f"Falha ao enviar: {msg} | Erro: {e}")

# --- LÓGICA DE MENSAGENS E COMANDOS ---
def handle_msg(user, message, is_private, irc):
    global dados
    msg = message.lower().strip()
    partes = msg.split()
    if not partes: return
    comando = partes[0]
    target = user if is_private else CHANNEL

    if comando == "!comandos":
        cmds = ["!uptime", "!stalker <nick>", "!radio", "!historia", "!lapada", "!prenda", "!convidar <nick>"]
        send_raw(irc, f"PRIVMSG {user} :📜 Comandos disponíveis: {', '.join(cmds)}")
        return

    if comando == "!convidar" and len(partes) > 1:
        alvo = partes[1]
        frase = random.choice(dados.get("convites_frases")).format(u=alvo)
        send_raw(irc, f"PRIVMSG {alvo} :{frase}")
        force_log(f"CONVITE: {user} pediu para convidar {alvo}")
        return

    if comando == "!uptime":
        send_raw(irc, f"PRIVMSG {target} :🚀 Estou online há: {get_uptime()}")

    elif NICK.lower() in msg:
        frase = random.choice(dados.get('evasivas', ['Sim?']))
        send_raw(irc, f"PRIVMSG {target} :{user}: {frase}")

# --- PROCESSAMENTO IRC ---
def parse_irc_lines(line, irc):
    global dados
    partes = line.split()
    if not partes: return

    # Gestão de Nick em uso
    if " 433 " in line:
        force_log(f"Nick {NICK} em uso. A recuperar...")
        send_raw(irc, f"NICK {NICK}_{random.randint(100,999)}")
        send_raw(irc, f"PRIVMSG NickServ :GHOST {NICK} {PASS}")
        time.sleep(2)
        send_raw(irc, f"NICK {NICK}")

    # Notificação de Stalker Pro (Watch list)
    if " 600 " in line and len(partes) > 3:
        u_alvo = partes[3].lower()
        vigia = dados.get("stalker_config", {}).get("alvos_ativos", {})
        if u_alvo in vigia:
            adm = vigia[u_alvo]
            aviso = random.choice(dados["stalker_config"]["avisos_pro"]).format(u=u_alvo)
            send_raw(irc, f"PRIVMSG {adm} :{aviso}")
            force_log(f"STALKER: Alvo {u_alvo} detetado para {adm}")

# --- SERVIDOR WEB (PARA RENDER) ---
app = Flask(__name__)
@app.route('/')
def home(): return f"TheOG Bot Ativo - Uptime: {get_uptime()}"

# --- LOOP PRINCIPAL DO BOT ---
def run_bot():
    while True:
        irc = None
        try:
            force_log(f"A ligar a {SERVER}...")
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.settimeout(300)
            irc.connect((SERVER, PORT))
            
            # Login faseado (lento)
            send_raw(irc, f"PASS {PASS}")
            send_raw(irc, f"NICK {NICK}")
            send_raw(irc, f"USER {NICK} 8 * :TheOG Bot v2")
            
            while True:
                try:
                    data = irc.recv(4096).decode("utf-8", errors="ignore")
                except socket.timeout:
                    force_log("Timeout de rede. A reiniciar...")
                    break
                
                if not data:
                    force_log("Ligação encerrada pelo servidor.")
                    break
                
                for line in data.split("\r\n"):
                    if not line: continue
                    
                    if line.startswith("PING"): 
                        send_raw(irc, f"PONG {line.split()[1]}")
                    
                    parse_irc_lines(line, irc)
                    
                    # Após o MOTD, entrar no canal
                    if " 376 " in line:
                        force_log("MOTD recebido. A entrar no canal principal...")
                        send_raw(irc, f"PRIVMSG NickServ :IDENTIFY {PASS}")
                        time.sleep(2)
                        send_raw(irc, f"JOIN {CHANNEL}")
                        entrada = random.choice(dados.get('frases_entrada', ['Olá!']))
                        send_raw(irc, f"PRIVMSG {CHANNEL} :{entrada}")
                        
                        # Reativar WATCH para admins
                        for a in dados.get("stalker_config", {}).get("alvos_ativos", {}):
                            send_raw(irc, f"WATCH +{a}")

                    # Logs de entrada/saída de utilizadores no canal
                    if " JOIN " in line and CHANNEL in line:
                        u = line.split('!')[0][1:]
                        if u != NICK:
                            msg = random.choice(dados.get('saudacoes')).format(u=u)
                            send_raw(irc, f"PRIVMSG {CHANNEL} :{msg}")
                            force_log(f"ENTRADA: {u} entrou no canal.")

                    if " PART " in line or " QUIT " in line:
                        u = line.split('!')[0][1:]
                        if u != NICK:
                            force_log(f"SAÍDA: {u} saiu da rede/canal.")

                    # Processar mensagens
                    if " PRIVMSG " in line:
                        u = line.split('!')[0][1:]
                        try:
                            t = line.split(' PRIVMSG ')[1].split(' :')[0]
                            m = line.split(' PRIVMSG ')[1].split(' :', 1)[1]
                            handle_msg(u, m, t == NICK, irc)
                        except: continue

        except Exception as e:
            force_log(f"ERRO CRÍTICO: {e}. A tentar reconectar em 15 segundos...")
        finally:
            if irc: irc.close()
            time.sleep(15)

if __name__ == "__main__":
    # Inicia servidor Web em background
    port = int(os.environ.get("PORT", 5000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port), daemon=True).start()
    run_bot()
