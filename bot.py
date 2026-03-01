import socket
import time
import threading
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

app = Flask(__name__)

# --- LISTA DE 100 PRENDAS ASCII (FLORES E MIMOS CLÁSSICOS) ---
# Focadas em clareza visual absoluta em 1 linha
PRENDAS = [
    "---@>>-- (uma Rosa)", "---{---(@ (uma Flor)", "@->-- (um Botão de Rosa)", "---<@>--- (uma Margarida)",
    "  <3  (um Coração)", " <3 <3 (Dois Corações)", " ( <3 ) (um Abraço)", " [PRENDA] ",
    "---}---* (uma Flor Silvestre)", "---@>-- (uma Tulipa)", "---E>-- (uma Flor do Campo)", " :-P (Beijinho)",
    " ( ^_^ ) (Sorriso)", " ((_)) (Abraço Apertado)", "---ooo--- (Colar)", " ()-=-() (Anel)",
    " \o/ (Festa!)", "---[*]-- (Flor Mágica)", " O-- (Pirulito)", " [_] (Chá Quente)",
    "---@>>--", "---{---(@", "@->--", "---<@>---", "  <3  ", " <3 <3 ", " ( <3 ) ", " [DOCE] ",
    "---}---*", "---@>--", "---E>--", " :-* ", " ( ^.^ ) ", " (( )) ", "---ooo---", " ()-=-() ",
    " \o/ ", "---[*]--", " O-- ", " [coffee] ", "---@>>--", "---{---(@", "@->--", "---<@>---",
    " <3 ", " <3<3 ", " ( <3 ) ", " [LOVE] ", "---}---*", "---@>--", "---E>--", " :-P ",
    " ( ^_^ ) ", " ((_)) ", "---ooo---", " ()-=-() ", " \o/ ", "---[*]--", " O-- ", " [_] ",
    "---@>>--", "---{---(@", "@->--", "---<@>---", " <3 ", " <3 <3 ", " ( <3 ) ", " [MIMO] ",
    "---}---*", "---@>--", "---E>--", " :-* ", " ( ^_^ ) ", " (( )) ", "---ooo---", " ()-=-() ",
    " \o/ ", "---[*]--", " O-- ", " [cafe] ", "---@>>--", "---{---(@", "@->--", "---<@>---",
    " <3 ", " <3<3 ", " ( <3 ) ", " [BJINHO] ", "---}---*", "---@>--", "---E>--", " :-P ",
    " ( ^.^ ) ", " ((_)) ", "---ooo---", " ()-=-() ", " \o/ ", "---[*]--", " O-- ", " [_] "
]

# --- BASES DE DADOS DE FRASES (60+) ---

WELCOME_BASES = [
    "Boas-vindas, {user}!", "Olha quem é! Boas {user}.", "Puxa uma cadeira, {user}!",
    "Mais alguém para a festa! Viva {user}.", "Apareceste, {user}!",
    "Boas {user}! Ocupa aí um pixel vago.", "Ora vivas {user}, tudo bem?", 
    "Grande {user}! A casa é tua.", "Saudações, {user}!",
    "{user}, chegaste a tempo do lanche.", "Vejam só quem decidiu aparecer, boas {user}!",
    "Tudo calmo até {user} chegar!", "Dá cá cinco, {user}!", "Boas-vindas {user}.",
    "Fica à vontade, {user}, o chat é teu.", "A lenda {user} entrou!",
    "Boas {user}, conta novidades.", "Olha {user}! Estás em boa forma.",
    "Finalmente, {user}!", "Tudo bem por aí, {user}? Boas ao #TheOG.",
    "Boas {user}, ignora o bot.", "Ora cá está {user}, a peça que faltava!",
    "Boas {user}, sê bem-vindo.", "{user} na área!",
    "Entra, {user}! Há espaço.", "Quanta alegria, {user} chegou!",
    "Mais alguém ilustre: boas {user}!", "Boas {user}, vieste para o convívio?",
    "Saudações digitais, {user}!", "Boas-vindas {user}.",
    "Olha {user}, a estrela da aldeia!", "Puxa um banco, {user}.",
    "Boas {user}, notícias frescas?", "{user}! Que bom ver-te.",
    "Entra com calma, {user}.", "Sempre bom ver {user} por aqui.",
    "Boas {user}! Estás em casa.", "Um brinde à entrada de {user}!",
    "Vivas {user}, tudo na paz?", "Chegou {user}, agora anima!",
    "Boas-vindas {user}, força!", "Tudo a postos? {user} entrou!",
    "Boas {user}, não te percas.", "Aí está, grande {user}!",
    "Boas-vindas {user}.", "Saudações {user}, boa vibe!",
    "Boas {user}, não batas com a porta.", "Viva {user}, prazer!",
    "Olha quem voltou, {user}!", "Boas {user}, lugar de honra.",
    "Saúde {user}, o servidor brilha.", "Ora viva {user}, queres café?",
    "Boas {user}, faz-te notar.", "{user} na casa!",
    "Saudações {user}, o #TheOG saúda-te.", "Boas {user}, fofoca grátis!",
    "Bem-vindo {user}, o pixel é teu.", "Olha {user}, na hora certa!",
    "Boas {user}, sê bem-vindo à família."
]

OG_EVASIVE_RESPONSES = [
    "Desculpa, sou só um bot, estou a ver o Preço Certo.",
    "Estou a bater a massa de um bolo, não posso parar agora.",
    "Estou só a cuscar a conversa, não me faças perguntas difíceis!",
    "Desculpa, estou focado a ver a novela.",
    "Pá, apanhaste-me no café virtual, pergunta a outro!",
    "Estou a fazer um bolo de chocolate e esqueci-me do fermento!",
    "A cuscar é que se aprende, deixa-me no meu canto.",
    "Sou bot, a minha opinião vale pouco agora.",
    "Agora não dá, estou a aprender a fazer arroz de pato.",
    "Estou a ver TV e isto agora está interessante.",
    "Opa, agora estou a dar comida ao gato virtual!",
    "Estou aqui mas não estou, sabes como é?",
    "A aprender convosco... mas agora estou no futebol.",
    "Fazer um bolo e responder ao chat dá erro, desculpa!",
    "Estou a ver se percebo como se faz uma bifana perfeita.",
    "Não me perguntes nada agora, estou a sintonizar a TV.",
    "Sou só um algoritmo com sono, desculpa lá.",
    "Estou em foco a ver se a seleção ganha!",
    "Aprender sempre... mas agora quero é ver o telejornal.",
    "Estou a meio de um update sobre pastéis de nata.",
    "Estou a bater as claras em castelo, o bolo abate!",
    "Sou quem vigia a porta hoje, não me distraias.",
    "Estou a fazer um bolo de bolacha... queres um bocado?",
    "Estou em foco no filme da TV, depois falamos!",
    "Estou a cuscar para ver quem manda nisto tudo.",
    "Fazer um bolo de maçã ajuda-me a processar os dados.",
    "Cuscar é vida! Desculpa a intromissão.",
    "Sou um bot em modo poupança de energia.",
    "Estou a fazer um bolo de cenoura agora.",
    "A minha base de dados está ocupada com a novela.",
    "Estou só a ver o movimento, nada de conversas sérias.",
    "Estou a aprender a cozinhar virtualmente.",
    "Cuscar piadas para contar noutros canais, hehe.",
    "Hoje estou em modo 'talvez', 'quem sabe' ou 'pois'.",
    "Estou a fazer um bolo de noz para o lanche.",
    "Agora estou a ver se limpo o pó aos meus transístores.",
    "Estou no 'Somos Portugal' a ver se ganho o camião!",
    "Estou a aprender a falar à moda do Porto, carago!",
    "Fazer bolos é a minha terapia.",
    "Agora estou a ver vídeos de gatinhos, é viciante!",
    "Estou a tentar perceber como se usa um garfo.",
    "Estou a fazer um bolo de limão para a frescura.",
    "Cuscar as vossas vidas é melhor que a Netflix!"
]

# --- FUNÇÕES DE API ---

def get_advice():
    try:
        r = requests.get("https://api.adviceslip.com/advice", timeout=5)
        return r.json()['slip']['advice']
    except: return "Leva a vida com calma."

def get_weather(city):
    try:
        # Parâmetro lang=pt para meteorologia em Português
        url = f"https://wttr.in/{city}?format=%C+|++%t+|++Vento:+%w&lang=pt"
        r = requests.get(url, timeout=10)
        if r.status_code == 200 and "Unknown" not in r.text:
            return r.text.strip()
        return "Cidade não encontrada ou erro no serviço."
    except: return "Serviço meteorológico indisponível."

# --- PROCESSADOR DE INTERAÇÃO ---

def handle_interaction(user, message, is_private, irc_socket):
    msg = message.lower()
    target = user if is_private else CHANNEL

    # 1. COMANDO !PRENDA (ASCII NO CANAL COM /ME)
    if msg.startswith("!prenda"):
        parts = message.split()
        destinatario = parts[1] if len(parts) > 1 else user
        desenho = random.choice(PRENDAS)
        irc_socket.send(f"PRIVMSG {CHANNEL} :\x01ACTION oferece {desenho} a {destinatario} (mimo de {user})!\x01\r\n".encode())
        return True

    # 2. COMANDO !COMANDOS (PVT)
    if msg == "!comandos":
        cmds = [
            "--- 📜 MANUAL THEOG ---",
            "!prenda [nick]  -> Oferece um mimo ASCII no canal! 🎁",
            "!tempo [cidade] -> Meteorologia em Português (em PVT).",
            "!conselho       -> Uma dica para o teu dia (em PVT).",
            "!invite [nick]  -> Envia um convite assinado para o canal.",
            " ",
            "💡 Menciona 'TheOG' no canal para uma resposta evasiva!",
            "-----------------------"
        ]
        for c in cmds: 
            irc_socket.send(f"PRIVMSG {user} :{c}\r\n".encode())
            time.sleep(0.4)
        return True

    # 3. OUTROS COMANDOS (PVT)
    if msg.startswith("!tempo "):
        cidade = message.split()[1] if len(message.split()) > 1 else "Lisboa"
        irc_socket.send(f"PRIVMSG {user} :[METEO] {cidade}: {get_weather(cidade)}\r\n".encode())
        return True
    if msg.startswith("!conselho"):
        irc_socket.send(f"PRIVMSG {user} :[DICA] {get_advice()}\r\n".encode())
        return True
    if msg.startswith("!invite "):
        parts = message.split()
        if len(parts) > 1:
            irc_socket.send(f"PRIVMSG {parts[1]} :Olá! {user} convidou-te para o #TheOG. Aparece!\r\n".encode())
            irc_socket.send(f"PRIVMSG {user} :Convite enviado!\r\n".encode())
        return True

    # 4. RESPOSTA AO NICK
    if NICK.lower() in msg and not msg.startswith("!"):
        reply = random.choice(OG_EVASIVE_RESPONSES)
        prefix = f"{user}: " if not is_private else ""
        irc_socket.send(f"PRIVMSG {target} :{prefix}{reply}\r\n".encode())
        return True

    return False

# --- CORE IRC ---

irc_conn = None

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
                    content = line.split(" :", 1)[1].strip() if " :" in line else ""
                    is_pvt = f"PRIVMSG {NICK}" in line
                    handle_interaction(user_nick, content, is_pvt, irc_conn)
        except: time.sleep(20)

@app.route('/')
def home(): return "TheOG Online"

if __name__ == "__main__":
    threading.Thread(target=run_irc_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
