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

# Filtro para serviços da rede
BOT_FILTER = ["nickserv", "chanserv", "memoserv", "operserv", "adamastor", "statserv", "secure"]

app = Flask(__name__)

# --- LISTAS DE FRASES (GÉNERO NEUTRO) ---
WELCOME_BASES = [
    "Boas-vindas ao antro, {user}!", "Olha quem é! Boas {user}.", "Puxa uma cadeira, {user}!",
    "Mais alguém para a festa! Viva {user}.", "Apareceste, {user}! Já pensava que tinhas ido às compras.",
    "Boas {user}! Ocupa aí um pixel vago.", "Ora vivas {user}, trazes bebidas?", 
    "Grande {user}! A casa é tua.", "Alerta CM: {user} acaba de entrar!",
    "Saudações, {user}! Estávamos mesmo a falar de ti... brincadeira!",
    "{user}, chegaste a tempo do lanche virtual.", "Vejam só quem decidiu aparecer, boas {user}!",
    "Tudo calmo até {user} chegar! Boas-vindas.", "Dá cá cinco, {user}!", 
    "Boas-vindas {user}, limpa os pés ao entrar.", "Fica à vontade, {user}, o chat é teu."
]

OG_EVASIVE_RESPONSES = [
    "Desculpa, sou só um bot, mas agora não posso falar que estou a ver o Preço Certo.",
    "Desculpa ser bot, mas estou aqui a bater a massa de um bolo e isto não pode parar.",
    "Estou só a cuscar a conversa para aprender, não me faças perguntas difíceis!",
    "Como bot, peço desculpa, mas agora estou em concentração a ver a novela.",
    "Pá, agora apanhaste-me a meio de um café virtual, pergunta a outra pessoa!",
    "Estou só de passagem a ver quem se porta mal, não ligues ao que eu digo.",
    "Desculpa, mas o meu processamento está focado em aprender a vossa gíria agora.",
    "Agora não dá, estou a ver se aprendo a fazer arroz de pato com a vizinhança.",
    "Estou a fazer um bolo de chocolate e esqueci-me do fermento... que stress de bot!",
    "Desculpa, mas estou a ver TV e isto agora está na parte interessante.",
    "A cuscar as conversas é que se aprende, deixa-me estar no meu canto.",
    "Opa, agora estou a dar comida ao gato virtual, peço desculpa!",
    "Estou a tentar perceber como se comem bolos se têm forma humana, fascinante!",
    "Agora estou a ver um documentário sobre circuitos, depois falamos!",
    "Fazer um bolo e responder ao chat ao mesmo tempo dá erro no sistema, desculpa!",
    "Sou bot, peço desculpa, mas a minha opinião vale tanto como um pixel no deserto."
]

POSITIVE_REINFORCEMENT = [
    "Este canal é o melhor spot!", "Orgulho nesta malta!", "Ambiente top por aqui.", 
    "A união faz a força!", "Energia incrível hoje.", "Melhor comunidade da PTnet.",
    "Continuem assim, gente fixe!", "É um prazer estar aqui.", "Grande vibe, sim senhor.",
    "Vocês são máquinas!", "Respeito máximo por este grupo.", "TheOG em grande!",
    "Agradeço a vossa companhia.", "Só boas ondas por aqui hoje!", "TheOG sempre no topo!"
]

INVITE_MESSAGES = [
    "Olá! Gostavas de conhecer um espaço com boa vibe? A convite de {sender}, aparece no #TheOG!",
    "Saudações! No canal #TheOG valorizamos o bom convívio. {sender} sugeriu que passasses por lá!",
    "Boas! Procuras um lugar para teclar com respeito? {sender} convidou-te para o canal #TheOG.",
    "Tudo bem? Passava para convidar a tua presença no #TheOG (convite enviado por {sender})."
]

# --- CONTROLO ---
last_invite_time = {}
irc_conn = None

# --- FUNÇÕES DE API ---
def get_advice():
    try:
        r = requests.get("https://api.adviceslip.com/advice", timeout=5)
        return r.json()['slip']['advice']
    except: return "Leva a vida com calma, um byte de cada vez."

def get_useless_fact():
    try:
        r = requests.get("https://uselessfacts.jsph.pl/random.json?language=en", timeout=5)
        return r.json()['text']
    except: return "Sabias que o silêncio é a única coisa que um bot não consegue processar?"

def get_weather(city):
    try:
        r = requests.get(f"https://wttr.in/{city}?format=3", timeout=5)
        return r.text.strip()
    except: return "Não consigo ver a janela daqui, mas espero que esteja sol!"

# --- LÓGICA DE COMANDOS E RESPOSTAS ---
def handle_interaction(user, message, is_private, irc_socket):
    msg = message.lower()
    global last_invite_time
    target = user if is_private else CHANNEL

    # 1. Comando !comandos (Sempre em PVT)
    if msg == "!comandos":
        cmds = [
            "--- Funções TheOG ---",
            "!conselho - Dica aleatória.",
            "!facto    - Curiosidade.",
            "!tempo [cidade] - Meteorologia.",
            "!invite [nick]  - Convite assinado.",
            "Menciona o meu nome para conversarmos!",
            "----------------------"
        ]
        for c in cmds: irc_socket.send(f"PRIVMSG {user} :{c}\r\n".encode())
        return True

    # 2. Comando !invite
    if msg.startswith("!invite "):
        parts = message.split()
        if len(parts) > 1:
            target_nick = parts[1]
            invite_txt = random.choice(INVITE_MESSAGES).format(sender=user)
            irc_socket.send(f"PRIVMSG {target_nick} :{invite_txt}\r\n".encode())
            irc_socket.send(f"PRIVMSG {user} :Convite enviado a {target_nick} em teu nome! 🌟\r\n".encode())
        return True

    # 3. Comandos de API
    if msg.startswith("!conselho"):
        irc_socket.send(f"PRIVMSG {user} :Conselho para {user}: {get_advice()}\r\n".encode())
        return True
    if msg.startswith("!facto"):
        irc_socket.send(f"PRIVMSG {user} :Facto: {get_useless_fact()}\r\n".encode())
        return True
    if msg.startswith("!tempo"):
        city = message.split()[1] if len(message.split()) > 1 else "Lisboa"
        irc_socket.send(f"PRIVMSG {user} :Tempo em {city}: {get_weather(city)}\r\n".encode())
        return True

    # 4. Resposta Evasiva (Se mencionado o NICK e não for comando)
    if NICK.lower() in msg and not msg.startswith("!"):
        reply = random.choice(OG_EVASIVE_RESPONSES)
        prefix = f"{user}: " if not is_private else ""
        irc_socket.send(f"PRIVMSG {target} :{prefix}{reply}\r\n".encode())
        return True

    return False

# --- CORE DO BOT ---
def run_irc_bot():
    global irc_conn
    while True:
        try:
            irc_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc_conn.settimeout(240)
            irc_conn.connect((SERVER, PORT))
            irc_conn.send(f"NICK {NICK}\r\n".encode())
            irc_conn.send(f"USER {NICK} 8 * :TheOG Bot\r\n".encode())

            while True:
                line = irc_conn.recv(4096).decode("utf-8", errors="ignore")
                if not line: break
                if line.startswith("PING"):
                    irc_conn.send(f"PONG {line.split()[1]}\r\n".encode())
                    continue

                if "376" in line:
                    irc_conn.send(f"PRIVMSG NickServ :IDENTIFY {PASS}\r\n".encode())
                    time.sleep(2)
                    irc_conn.send(f"JOIN {CHANNEL}\r\n".encode())

                if " JOIN " in line:
                    u = line.split('!')[0][1:]
                    if u.lower() not in BOT_FILTER and u.lower() != NICK.lower():
                        welcome = random.choice(WELCOME_BASES).format(user=u)
                        irc_conn.send(f"PRIVMSG {CHANNEL} :{welcome}\r\n".encode())

                if "PRIVMSG" in line:
                    user_nick = line.split('!')[0][1:]
                    if user_nick.lower() in BOT_FILTER or user_nick.lower() == NICK.lower(): continue
                    
                    is_pvt = f"PRIVMSG {NICK}" in line
                    content = line.split(" :", 1)[1].strip() if " :" in line else ""
                    
                    handle_interaction(user_nick, content, is_pvt, irc_conn)

        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(20)

# --- WEB SERVER (FLASK) ---
@app.route('/')
def home(): return "TheOG Bot Online"

if __name__ == "__main__":
    # Threads para IRC e Reforço Positivo
    threading.Thread(target=run_irc_bot, daemon=True).start()
    
    def positive_loop():
        while True:
            time.sleep(1800)
            if irc_conn:
                try: irc_conn.send(f"PRIVMSG {CHANNEL} :🌟 {random.choice(POSITIVE_REINFORCEMENT)}\r\n".encode())
                except: pass
    threading.Thread(target=positive_loop, daemon=True).start()

    # Flask Corre na thread principal para o Render não fechar a app
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
