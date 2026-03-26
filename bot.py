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

# --- CONFIGURAÇÃO DE LOGS PARA RENDER ---
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s [%(levelname)s] %(message)s', 
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("TheOG_Bot")

def force_log(msg):
    """Garante que o log aparece no Render imediatamente."""
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
users_online = []  # Lista de nicks no canal

# --- GESTÃO DE DADOS ---
def carregar_dados():
    global dados
    # Lista mestra de admins
    admins_lista = ["Emergency112", "Padre", "CutxiiiPoint"]
    
    try:
        if os.path.exists('frases.json'):
            with open('frases.json', 'r', encoding='utf-8') as f:
                dados = json.load(f)
                # Garante que os admins estão sempre atualizados no JSON
                dados["admins"] = admins_lista
                force_log("JSON carregado e admins atualizados.")
        else:
            force_log("A criar base de dados JSON com todos os admins...")
            dados = {
                "admins": admins_lista,
                "frases_entrada": ["TheOG online! Tudo operacional.", "Boas malta, o vosso bot favorito chegou."],
                "saudacoes": ["Olá {u}!", "Boas {u}, como vai isso?", "Bem-vindo ao #TheOG, {u}!"],
                "puxar_conversa": [
                    "Então {u}, como corre o teu dia?",
                    "Alguém aqui tem novidades tecnológicas? {u}?",
                    "{u}, andas muito calado hoje!",
                    "Quem aqui gosta de rádio? Digitem !radio para uma sugestão.",
                    "{u}, conta aí uma coisa boa que te aconteceu hoje!",
                    "Este canal #TheOG está com bom ambiente, não acham?",
                    "Alguma sugestão de música para agora, {u}?"
                ],
                "evasivas": ["Estou aqui a processar uns logs, mas diz lá!", "Um momento, estou a afinar os circuitos."],
                "convites_frases": ["Olá {u}, o canal #TheOG é o lugar ideal para estares. Aparece!"]
            }
            salvar_dados()
    except Exception as e:
        force_log(f"Erro ao carregar dados: {e}")
        # Fallback de segurança
        dados = {"admins": admins_lista}

def salvar_dados():
    try:
        with open('frases.json', 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    except Exception as e:
        force_log(f"Erro ao salvar JSON: {e}")

carregar_dados()

def get_uptime():
    delta = datetime.now() - START_TIME
    return str(delta).split('.')[0]

def send_raw(sock, msg):
    """Envia comandos com segurança anti-flood (1.5s)."""
    try:
        sock.send(f"{msg}\r\n".encode('utf-8'))
        time.sleep(1.5) 
    except:
        pass

# --- TAREFA SOCIAL (A CADA 20 MINUTOS) ---
def social_task(irc_conn):
    """Interage com o canal periodicamente."""
    while True:
        time.sleep(1200) # 20 minutos
        if users_online:
            outros = [u for u in users_online if u != NICK]
            if outros:
                alvo = random.choice(outros)
                frases = dados.get("puxar_conversa", ["Como vai isso, {u}?"])
                frase = random.choice(frases).format(u=alvo)
                send_raw(irc_conn, f"PRIVMSG {CHANNEL} :{frase}")
                force_log(f"SOCIAL: Interação automática com {alvo}")

# --- LÓGICA DE MENSAGENS E COMANDOS ---
def handle_msg(user, message, is_private, irc):
    msg = message.lower().strip()
    target = user if is_private else CHANNEL
    
    # Comandos de Admin
    if user in dados.get("admins", []):
        if msg.startswith("!admin test"):
            send_raw(irc, f"PRIVMSG {target} :✅ Olá {user}, o teu acesso de Admin está ativo!")

    # Comandos Gerais
    if msg.startswith("!uptime"):
        send_raw(irc, f"PRIVMSG {target} :🚀 Uptime: {get_uptime()}")
    
    elif msg.startswith("!convidar"):
        partes = msg.split()
        if len(partes) > 1:
            alvo = partes[1]
            frase = random.choice(dados.get("convites_frases", ["Vem ao #TheOG!"])).format(u=alvo)
            send_raw(irc, f"PRIVMSG {alvo} :{frase}")
            force_log(f"CONVITE: {user} enviou para {alvo}")

    elif NICK.lower() in msg:
        frase = random.choice(dados.get('evasivas', ['Sim?']))
        send_raw(irc, f"PRIVMSG {target} :{user}: {frase}")

# --- LOOP PRINCIPAL ---
app = Flask(__name__)
@app.route('/')
def home(): return f"TheOG Status: Online | Admins Ativos: {len(dados.get('admins', []))}"

def run_bot():
    global users_online
    while True:
        irc = None
        try:
            force_log("--- A LIGAR AO IRC ---")
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.settimeout(300)
            irc.connect((SERVER, PORT))
            
            send_raw(irc, f"PASS {PASS}")
            send_raw(irc, f"NICK {NICK}")
            send_raw(irc, f"USER {NICK} 8 * :TheOG Social Manager")
            
            threading.Thread(target=social_task, args=(irc,), daemon=True).start()

            while True:
                data = irc.recv(4096).decode("utf-8", errors="ignore")
                if not data: break
                
                for line in data.split("\r\n"):
                    if not line: continue
                    
                    if line.startswith("PING"):
                        irc.send(f"PONG {line.split()[1]}\r\n".encode())
                        continue

                    # Ghost / Nick Recovery
                    if " 433 " in line:
                        force_log("Nick em uso, a limpar fantasma...")
                        irc.send(f"NICK {NICK}_{random.randint(10,99)}\r\n".encode())
                        time.sleep(2)
                        send_raw(irc, f"PRIVMSG NickServ :GHOST {NICK} {PASS}")
                        time.sleep(5)
                        send_raw(irc, f"NICK {NICK}")
                        continue

                    # Entrada no Canal
                    if " 376 " in line or " 422 " in line:
                        force_log("Ligado com sucesso!")
                        send_raw(irc, f"PRIVMSG NickServ :IDENTIFY {PASS}")
                        time.sleep(2)
                        send_raw(irc, f"JOIN {CHANNEL}")
                        send_raw(irc, f"NAMES {CHANNEL}")
                        entrada = random.choice(dados.get('frases_entrada', ["Olá!"]))
                        send_raw(irc, f"PRIVMSG {CHANNEL} :{entrada}")

                    # Lista de Nicks
                    if " 353 " in line:
                        p_nomes = line.split(" :")[1].split()
                        users_online = [n.strip("@+ ") for n in p_nomes]
                        force_log(f"Utilizadores detetados: {len(users_online)}")

                    # Notificar Entradas e Saídas
                    if " JOIN " in line and CHANNEL in line:
                        u = line.split('!')[0][1:]
                        if u != NICK:
                            if u not in users_online: users_online.append(u)
                            msg = random.choice(dados.get('saudacoes')).format(u=u)
                            send_raw(irc, f"PRIVMSG {CHANNEL} :{msg}")
                            force_log(f"ENTRADA: {u}")

                    if " PART " in line or " QUIT " in line:
                        u = line.split('!')[0][1:]
                        if u in users_online: users_online.remove(u)
                        force_log(f"SAÍDA: {u}")

                    # Mensagens
                    if " PRIVMSG " in line:
                        u = line.split('!')[0][1:]
                        try:
                            t_msg = line.split(' PRIVMSG ')[1].split(' :')[0]
                            m_msg = line.split(' PRIVMSG ')[1].split(' :', 1)[1]
                            handle_msg(u, m_msg, t_msg == NICK, irc)
                        except: continue

        except Exception as e:
            force_log(f"ERRO: {e}")
        finally:
            if irc: irc.close()
            users_online = []
            time.sleep(30)

if __name__ == "__main__":
    p_web = int(os.environ.get("PORT", 5000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=p_web), daemon=True).start()
    run_bot()
