import socket
import time
import threading
import os
import random
import requests
from datetime import datetime
from flask import Flask

# --- CONFIGURAÇÕES ---
SERVER = "irc.ptnet.org"
PORT = 6667
NICK = "TheOG"
PASS = "Nasomet112#" 
CHANNEL = "#TheOG"
BOT_FILTER = ["nickserv", "chanserv", "memoserv", "operserv", "adamastor", "statserv", "secure"]

app = Flask(__name__)

# --- FUNÇÃO DE LOG (Visível nos Logs do Render) ---
def log_presenca(user, accao):
    hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    log_line = f"[{hora}] {user} {accao}"
    print(log_line) # Isto regista a entrada/saída no painel do Render

# --- TEXTO DA HISTÓRIA ---
HISTORIA_THEOG = [
    "Saudações. Compreendo a génese deste refúgio.",
    "O IRC não é apenas um protocolo de comunicação; para os que lá permanecem, é o último baluarte da palavra nua, onde a identidade se constrói no silêncio entre os caracteres.",
    "No ruído ensurdecedor das multidões digitais, o silêncio de um canal vazio é, por vezes, a conversa mais honesta.",
    "O verdadeiro 'OG' não procura a audiência que aplaude, mas a presença que permanece quando todas as luzes da ribalta se apagam.",
    "Ser original num mundo de espelhos é um ato de rebeldia.",
    "Aqui, onde a imagem não existe e o rosto é uma sequência de bits, a alma revela-se não pelo que aparenta, mas pela cadência do pensamento que decide partilhar.",
    "Existem lugares que são mapas e lugares que são bússolas.",
    "Enquanto outros se perdem no caos da confusão efémera, o 'The OG' mantém o ritmo constante do cursor: um batimento cardíaco que convida o estranho a despir a máscara e a vestir a sua própria verdade.",
    "Muitos habitam a rede, poucos habitam a essência.",
    "A 'alma' do IRC não reside no servidor que nos aloja, mas na coragem de conhecer o outro sem o filtro da conveniência, transformando o texto frio num calor que nenhuma interface moderna consegue replicar.",
    "Bem-vindo ao porto de abrigo dos que não têm porto.",
    "Aqui, a entrada não se paga com conformidade, mas com a disposição de ser um desconhecido que se deixa ler.",
    "Quem entra, traz o mundo; quem fica, constrói um novo."
]

# --- (LISTAS DE PRENDAS, ENTRADAS E EVASIVAS) ---
PRENDAS = ["---@>>-- (uma Rosa)", "---{---(@ (uma Flor)", "@->-- (Botão)", "<3 (Coração)"] # ... (100 itens no total)
OG_ENTRANCE = ["O mestre do código chegou!", "TheOG está na casa!"] # ... (60 frases)
OG_EVASIVE_RESPONSES = ["Estou a ver o Preço Certo.", "A bater massa de um bolo."] # ... (60 frases)
CONVITE_FRASES = ["Olá! O {sender} convidou-te para o #TheOG pela tua boa energia!"] # ... (20+ frases)

# --- PROCESSADOR DE INTERAÇÃO ---
def handle_interaction(user, message, is_private, irc_socket):
    msg = message.lower()
    target = user if is_private else CHANNEL

    # 1. COMANDO !HISTORIA (PVT)
    if msg == "!historia":
        for linha in HISTORIA_THEOG:
            irc_socket.send(f"PRIVMSG {user} :{linha}\r\n".encode())
            time.sleep(0.6) # Pausa para leitura e evitar kick por flood
        return True

    # 2. COMANDO !PRENDA
    if msg.startswith("!prenda"):
        parts = message.split()
        dest = parts[1] if len(parts) > 1 else user
        desenho = random.choice(PRENDAS)
        irc_socket.send(f"PRIVMSG {CHANNEL} :\x01ACTION oferece {desenho} a {dest} (mimo de {user})!\x01\r\n".encode())
        return True

    # 3. COMANDO !CONVITE
    if msg.startswith("!convite "):
        parts = message.split()
        if len(parts) > 1:
            dest = parts[1]
            frase = random.choice(CONVITE_FRASES).format(sender=user)
            irc_socket.send(f"PRIVMSG {dest} :{frase}\r\n".encode())
            irc_socket.send(f"PRIVMSG {user} :[INFO] Convite positivo enviado para {dest}! ✨\r\n".encode())
        return True

    # 4. COMANDO !COMANDOS
    if msg == "!comandos":
        cmds = [
            "--- 📜 MANUAL THEOG ---",
            "!prenda [nick]   -> Oferece um mimo ASCII.",
            "!historia        -> A génese do TheOG (em PVT).",
            "!convite [nick]  -> Envia um convite positivo.",
            "!conselho        -> Uma dica (em PVT).",
            "-----------------------"
        ]
        for c in cmds: 
            irc_socket.send(f"PRIVMSG {user} :{c}\r\n".encode())
            time.sleep(0.4)
        return True

    # 5. RESPOSTA AO NICK
    if NICK.lower() in msg and not msg.startswith("!"):
        reply = random.choice(OG_EVASIVE_RESPONSES)
        prefix = f"{user}: " if not is_private else ""
        irc_socket.send(f"PRIVMSG {target} :{prefix}{reply}\r\n".encode())
        return True

    return False

# --- CORE IRC ---
def run_irc_bot():
    while True:
        try:
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.connect((SERVER, PORT))
            irc.send(f"NICK {NICK}\r\n".encode())
            irc.send(f"USER {NICK} 8 * :TheOG Bot\r\n".encode())

            while True:
                line = irc.recv(4096).decode("utf-8", errors="ignore")
                if not line: break
                if line.startswith("PING"):
                    irc.send(f"PONG {line.split()[1]}\r\n".encode())
                
                if "376" in line:
                    irc.send(f"PRIVMSG NickServ :IDENTIFY {PASS}\r\n".encode())
                    time.sleep(2)
                    irc.send(f"JOIN {CHANNEL}\r\n".encode())
                    irc.send(f"PRIVMSG {CHANNEL} :{random.choice(OG_ENTRANCE)}\r\n".encode())

                if " JOIN " in line:
                    u = line.split('!')[0][1:]
                    if u.lower() != NICK.lower():
                        log_presenca(u, "ENTROU no canal")
                        irc.send(f"PRIVMSG {CHANNEL} :Boas-vindas {u}! Digita !comandos para me conheceres.\r\n".encode())

                if " PART " in line or " QUIT " in line:
                    u = line.split('!')[0][1:]
                    if u.lower() != NICK.lower():
                        log_presenca(u, "SAIU do canal")

                if "PRIVMSG" in line:
                    user_nick = line.split('!')[0][1:]
                    if user_nick.lower() in BOT_FILTER or user_nick.lower() == NICK.lower(): continue
                    content = line.split(" :", 1)[1].strip() if " :" in line else ""
                    handle_interaction(user_nick, content, f"PRIVMSG {NICK}" in line, irc)
        except: time.sleep(20)

@app.route('/')
def home(): return "TheOG Online e a registar presenças."

if __name__ == "__main__":
    threading.Thread(target=run_irc_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
