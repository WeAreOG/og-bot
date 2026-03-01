import socket
import time
import threading
import re
import os
import random
import requests
from flask import Flask

# --- CONFIGURAÇÕES ---
SERVER = "irc.ptnet.org"
PORT = 6667
NICK = "TheOG"
PASS = "Nasomet112#" 
CHANNEL = "#TheOG"

BOT_FILTER = ["nickserv", "chanserv", "memoserv", "operserv", "adamastor", "statserv", "secure"]
HF_API_URL = "https://api-inference.huggingface.co/models/deepseek-ai/DeepSeek-V3"
HF_TOKEN = "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"

app = Flask(__name__)

# --- MENSAGENS DE CONVITE (GÉNERO NEUTRO E ASSINADAS) ---
INVITE_MESSAGES = [
    "Olá! Gostavas de conhecer um espaço com boa vibe e gente fixe? A convite de {sender}, aparece no #TheOG!",
    "Saudações! No canal #TheOG valorizamos o bom convívio. {sender} sugeriu que passasses por lá para conhecer a malta!",
    "Boas! Procuras um lugar para teclar com respeito? {sender} convidou-te para o canal #TheOG. Esperamos por ti!",
    "Tudo bem? Passava para convidar a tua presença no canal #TheOG (convite enviado por {sender}). Temos uma comunidade fantástica!"
]

# --- DICIONÁRIO PARA CONTROLO DE FLOOD ---
last_invite_time = {}

# --- FUNÇÕES DE APOIO ---

def get_advice():
    try:
        r = requests.get("https://api.adviceslip.com/advice", timeout=5)
        return r.json()['slip']['advice']
    except: return "Olha, não tenhas pressa na vida. É o melhor que te digo agora."

def get_useless_fact():
    try:
        r = requests.get("https://uselessfacts.jsph.pl/random.json?language=en", timeout=5)
        return r.json()['text']
    except: return "Sabias que... os bots também se esquecem das coisas? Pois é."

# --- LÓGICA DE COMANDOS ---

def handle_commands(user, message, irc_socket):
    msg = message.lower()
    global last_invite_time

    # 1. Comando !comandos
    if msg == "!comandos":
        help_text = [
            "--- Funções Disponíveis (TheOG) ---",
            "!comandos - Mostra esta lista em PVT.",
            "!conselho - Recebe um conselho aleatório.",
            "!facto    - Recebe uma curiosidade.",
            "!tempo [cidade] - Consulta o clima.",
            "!invite [nick]  - Convida alguém para o #TheOG em teu nome.",
            "-----------------------------------"
        ]
        for line in help_text:
            irc_socket.send(f"PRIVMSG {user} :{line}\r\n".encode())
        return True

    # 2. Comando !invite [nick] - COM ASSINATURA E COOLDOWN
    if msg.startswith("!invite "):
        current_time = time.time()
        # Cooldown de 30 segundos por utilizador para evitar abusos
        if user in last_invite_time and current_time - last_invite_time[user] < 30:
            irc_socket.send(f"PRIVMSG {user} :Aguarda um pouco antes de enviar outro convite. Não queremos parecer chatice!\r\n".encode())
            return True

        parts = message.split()
        if len(parts) > 1:
            target_nick = parts[1]
            if target_nick.lower() == NICK.lower():
                irc_socket.send(f"PRIVMSG {user} :Convidar-me a mim mesmo? Eu já moro aqui!\r\n".encode())
                return True
            
            invite_text = random.choice(INVITE_MESSAGES).format(sender=user)
            # Tenta enviar para a rede. Se o nick não existir, a rede IRC apenas descarta ou devolve erro 401.
            irc_socket.send(f"PRIVMSG {target_nick} :{invite_text}\r\n".encode())
            
            # Confirmação ao autor
            irc_socket.send(f"PRIVMSG {user} :Convite enviado a {target_nick} com a tua assinatura. 🌟\r\n".encode())
            last_invite_time[user] = current_time
        else:
            irc_socket.send(f"PRIVMSG {user} :Escreve !invite [nick] para convidares alguém.\r\n".encode())
        return True

    # 3. Restantes comandos de API
    if msg.startswith("!conselho"):
        irc_socket.send(f"PRIVMSG {user} :Conselho: {get_advice()}\r\n".encode())
        return True
    
    if msg.startswith("!facto"):
        irc_socket.send(f"PRIVMSG {user} :Sabias que? {get_useless_fact()}\r\n".encode())
        return True

    return False

# --- CORE DO BOT (RECONEXÃO E PING/PONG) ---
irc_conn = None

def run_irc_bot():
    global irc_conn
    # (O restante código de conexão permanece igual ao anterior para manter a estabilidade)
    while True:
        try:
            irc_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc_conn.settimeout(240)
            irc_conn.connect((SERVER, PORT))
            irc_conn.send(f"NICK {NICK}\r\n".encode())
            irc_conn.send(f"USER {NICK} 8 * :TheOG Evasive Bot\r\n".encode())

            while True:
                line = irc_conn.recv(4096).decode("utf-8", errors="ignore")
                if not line: break
                if line.startswith("PING"):
                    irc_conn.send(f"PONG {line.split()[1]}\r\n".encode())
                    continue

                if "376" in line or "422" in line:
                    irc_conn.send(f"PRIVMSG NickServ :IDENTIFY {PASS}\r\n".encode())
                    time.sleep(5)
                    irc_conn.send(f"JOIN {CHANNEL}\r\n".encode())

                if "PRIVMSG" in line:
                    user_nick = line.split('!')[0][1:]
                    if user_nick.lower() == NICK.lower(): continue
                    msg_content = line.split(" :", 1)[1].strip() if " :" in line else ""

                    if handle_commands(user_nick, msg_content, irc_conn):
                        continue
        except:
            time.sleep(15)

# (Flask e loops de reforço positivo mantêm-se aqui...)
