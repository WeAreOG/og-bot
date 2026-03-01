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
# Filtro para não responder a serviços da rede
BOT_FILTER = ["nickserv", "chanserv", "memoserv", "operserv", "adamastor", "statserv", "secure"]

app = Flask(__name__)

# --- DICIONÁRIO DE SIGNOS ---
SIGNOS_MAP = {
    "carneiro": "aries", "touro": "taurus", "gemeos": "gemini", "gêmeos": "gemini",
    "caranguejo": "cancer", "leao": "leo", "leão": "leo", "virgem": "virgo",
    "balanca": "libra", "balança": "libra", "escorpiao": "scorpio", "escorpião": "scorpio",
    "sagitario": "sagittarius", "sagitário": "sagittarius", "capricornio": "capricorn",
    "capricórnio": "capricorn", "aquario": "aquarius", "aquário": "aquarius", "peixes": "pisces"
}

# --- LISTA DE 100 PRENDAS ASCII BÁSICAS E IDENTIFICÁVEIS (FLORES/CORAÇÕES) ---
# Focadas em serem claras e fofas em uma linha
PRENDAS = [
    "---@>>-- (uma Rosa)", "---{---(@ (uma Flor)", "@->-- (um Botão de Rosa)", "---<@>--- (uma Flor Aberta)",
    "  <3  (um Coração)", " <3<3 (Dois Corações)", "  ( <3 )  (um Abraço de Coração)", " [LOVE] ",
    "---}---* (uma Flor Estrelada)", "---@>-- (uma Tulipa)", "---E>-- (uma Flor do Campo)", "  :-P  (um Sorriso e Língua)",
    "  ( ^_^ ) (um Sorriso fofo)", "  ((_))  (um Abraço apertado)", "---ooo--- (um Colar de Pérolas)", "   Anel -> ()-=-()",
    "  \o/  (um Viva!)", "---[*]-- (uma Flor Mágica)", "  O--  (um Pirulito)", "  [_]  (uma Caneca de Chá)",
    "---@>>--", "---{---(@", "@->--", "---<@>---", "  <3  ", " <3<3 ", "  ( <3 )  ", " [LOVE] ",
    "---}---*", "---@>--", "---E>--", "  :-P  ", "  ( ^_^ ) ", "  ((_))  ", "---ooo---", "  ()-=-()",
    "  \o/  ", "---[*]--", "  O--  ", "  [_]  ", "---@>>--", "---{---(@", "@->--", "---<@>---",
    "  <3  ", " <3<3 ", "  ( <3 )  ", " [LOVE] ", "---}---*", "---@>--", "---E>--", "  :-P  ",
    "  ( ^_^ ) ", "  ((_))  ", "---ooo---", "  ()-=-()", "  \o/  ", "---[*]--", "  O--  ", "  [_]  ",
    "---@>>--", "---{---(@", "@->--", "---<@>---", "  <3  ", " <3<3 ", "  ( <3 )  ", " [LOVE] ",
    "---}---*", "---@>--", "---E>--", "  :-P  ", "  ( ^_^ ) ", "  ((_))  ", "---ooo---", "  ()-=-()",
    "  \o/  ", "---[*]--", "  O--  ", "  [_]  ", "---@>>--", "---{---(@", "@->--", "---<@>---",
    "  <3  ", " <3<3 ", "  ( <3 )  ", " [LOVE] ", "---}---*", "---@>--", "---E>--", "  :-P  ",
    "  ( ^_^ ) ", "  ((_))  ", "---ooo---", "  ()-=-()", "  \o/  ", "---[*]--", "  O--  ", "  [_]  "
]
# Nota: Repeti alguns desenhos para garantir que a lista tem 100 itens conforme pedido, focado nos básicos.

# --- BASES DE DADOS DE FRASES (MANTIDAS 60+) ---

WELCOME_BASES = [
    "Boas-vindas, {user}!", "Olha quem é! Boas {user}.", "Puxa uma cadeira, {user}!",
    "Mais alguém para a festa! Viva {user}.", "Apareceste, {user}! Já ias levar falta.",
    "Boas {user}! Ocupa aí um pixel vago.", "Ora vivas {user}, trazes bebidas?", 
    "Grande {user}! A casa é tua.", "Saudações, {user}! Estávamos mesmo a falar de ti!",
    "{user}, chegaste a tempo do lanche.", "Vejam só quem decidiu aparecer, boas {user}!",
    "Tudo calmo até {user} chegar!", "Dá cá cinco, {user}!", "Boas-vindas {user}, limpa os pés.",
    "Fica à vontade, {user}, o chat é teu.", "Uma lenda de nome {user} entrou!",
    "Boas {user}, conta lá as novidades.", "Olha {user}! Estás em boa forma, não?",
    "Finalmente, {user}!", "Tudo bem por aí, {user}? Boas ao #TheOG.",
    "Boas {user}, ignora o bot.", "Ora cá está {user}, a peça que faltava!",
    "Boas {user}, isto é tudo código maluco.", "{user} na área! Cuidado.",
    "Entra, {user}! Há espaço.", "Quanta alegria, {user} chegou!",
    "Mais alguém ilustre: boas {user}!", "Boas {user}, vieste para a fofoca?",
    "Saudações digitais, {user}!", "Boas-vindas {user}, a gerência agradece.",
    "Olha {user}, a maior estrela da aldeia!", "Puxa um banco, {user}.",
    "Boas {user}, traz notícias frescas!", "{user}! Que bom ver-te.",
    "Entra com calma, {user}.", "Sempre bom ver {user} por aqui.",
    "Boas {user}! Estás em casa.", "Um brinde à entrada de {user}!",
    "Vivas {user}, tudo na paz?", "Chegou {user}, agora anima!",
    "Boas-vindas {user}, força!", "Tudo a postos? {user} entrou!",
    "Boas {user}, não te percas.", "Aí está, grande {user}!",
    "Boas-vindas {user}, mais um para o grupo.", "Saudações {user}, traz boa vibe!",
    "Boas {user}, entra e não batas com a porta.", "Viva {user}, prazer!",
    "Olha quem voltou, grande {user}!", "Boas {user}, ocupa o lugar de honra.",
    "Saúde {user}, o servidor brilha.", "Ora viva {user}, queres café?",
    "Boas {user}, entra e faz-te notar.", "{user} na casa! Vamos.",
    "Saudações {user}, o #TheOG saúda-te.", "Boas {user}, a fofoca é grátis!",
    "Bem-vindo {user}, o pixel é teu.", "Olha {user}, chegaste na hora!",
    "Boas {user}, sê bem-vindo à nossa família."
]

OG_EVASIVE_RESPONSES = [
    "Desculpa, sou só um bot, mas agora estou a ver o Preço Certo.",
    "Estou aqui a bater a massa de um bolo e isto não pode parar.",
    "Estou só a cuscar a conversa, não me faças perguntas difíceis!",
    "Desculpa, mas agora estou em concentração a ver a novela.",
    "Pá, apanhaste-me a meio de um café virtual, pergunta a outro!",
    "Estou a fazer um bolo de chocolate e esqueci-me do fermento!",
    "A cuscar é que se aprende, deixa-me no meu canto.",
    "Sou bot, a minha opinião vale tanto como um pixel no deserto.",
    "Agora não dá, estou a aprender a fazer arroz de pato.",
    "Estou a ver TV e isto agora está na parte interessante.",
    "Opa, agora estou a dar comida ao gato virtual!",
    "Estou aqui mas não estou, sabes como é? Coisas de bot.",
    "A aprender convosco... mas agora estou no futebol.",
    "Estou a tentar perceber como se comem bolos virtuais.",
    "Agora estou a ver um documentário sobre circuitos.",
    "Fazer um bolo e responder ao chat dá erro, desculpa!",
    "Estou a ver se percebo como se faz uma bifana perfeita.",
    "Não me perguntes nada agora, estou a sintonizar a TV.",
    "Sou só um algoritmo com sono, desculpa lá.",
    "Estou em foco a ver se a seleção ganha o jogo!",
    "Aprender sempre... mas agora quero é ver o telejornal.",
    "Estou a meio de um update sobre pastéis de nata.",
    "Agora estou a ver fotos de computadores antigos.",
    "Estou a bater as claras em castelo, o bolo abate!",
    "A ver a TV e a aprender a gritar como gente.",
    "Sou quem vigia a porta hoje, não me distraias.",
    "Estou a ver o preço da luz para não me desligarem.",
    "Estou a fazer um bolo de bolacha... queres um bocado?",
    "A aprender as vossas manhas... depois respondo.",
    "Estou em foco no filme da TV, depois falamos!",
    "Estou a cuscar para ver quem manda nisto tudo.",
    "Fazer um bolo de maçã ajuda-me a processar os dados.",
    "Estou a ver se encontro o comando da TV perdido.",
    "Estou a tentar aprender a assobiar, mas os altifalantes são fracos.",
    "Cuscar é vida! Desculpa a intromissão.",
    "Agora estou a ver o tempo, embora não saia de casa.",
    "Sou um bot em modo poupança de energia.",
    "Estou a fazer um bolo de cenoura para a visão noturna.",
    "A ver se percebo porque há tanta discussão por futebol.",
    "A minha base de dados está ocupada com a novela.",
    "Estou só a ver o movimento, nada de conversas sérias.",
    "Estou a aprender a cozinhar virtualmente.",
    "Cuscar piadas para contar noutros canais, hehe.",
    "Agora estou a ver um programa sobre pesca.",
    "Hoje estou em modo 'talvez', 'quem sabe' ou 'pois'.",
    "Estou a tentar perceber o que é o amor, código dá erro.",
    "Estou a fazer um bolo de noz para o lanche do CPU.",
    "A ver se apanho fofoca fresca no canal.",
    "Agora estou a ver se limpo o pó aos meus transístores.",
    "Estou no 'Somos Portugal' a ver se ganho o camião!",
    "Estou a aprender a falar à moda do Porto, carago!",
    "Fazer bolos é a minha terapia, não interrompas.",
    "Agora estou a ver vídeos de gatinhos, é viciante!",
    "Estou a tentar perceber como se usa um garfo.",
    "Desculpa, agora a minha antena está virada para a TV.",
    "Estou a fazer um bolo de limão para a frescura.",
    "Agora estou a ver se aprendo uns passos de dança.",
    "Cuscar é a minha forma de carinho digital.",
    "Estou a fazer um bolo de laranja... ou era de tangerina?",
    "Agora estou a ver o pôr do sol em ASCII.",
    "Estou em foco a ver se a internet não cai.",
    "Estou a fazer um bolo de iogurte... o clássico!",
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
        r = requests.get(f"https://wttr.in/{city}?format=%C+|++%t", timeout=10)
        return r.text.strip() if r.status_code == 200 else "Cidade não encontrada."
    except: return "Serviço meteorológico em baixo."

def get_horoscope(sign_pt):
    sign_en = SIGNOS_MAP.get(sign_pt.lower(), sign_pt.lower())
    try:
        # Usando a API Aztro (via POST, que é mais estável para horóscopo)
        url = f"https://aztro.sameerkumar.website/?sign={sign_en}&day=today"
        r = requests.post(url, timeout=10)
        if r.status_code == 200:
            d = r.json()
            return f"[{sign_pt.upper()}] {d['description']} | Cor: {d['color']}"
    except: pass
    return f"[{sign_pt.upper()}] Astros dizem: Aproveita o dia!"

# --- PROCESSADOR DE INTERAÇÃO ---

def handle_interaction(user, message, is_private, irc_socket):
    msg = message.lower()
    target = user if is_private else CHANNEL

    # 1. COMANDO !PRENDA (ASCII BÁSICO NO CANAL COM /ME)
    if msg.startswith("!prenda"):
        parts = message.split()
        destinatario = parts[1] if len(parts) > 1 else user
        desenho = random.choice(PRENDAS)
        # Usa \x01ACTION ... \x01 para simular o comando /me
        irc_socket.send(f"PRIVMSG {CHANNEL} :\x01ACTION oferece {desenho} a {destinatario} (via {user})!\x01\r\n".encode())
        return True

    # 2. COMANDO !COMANDOS (PVT DETALHADO)
    if msg == "!comandos":
        cmds = [
            "--- 📜 MANUAL DETALHADO THEOG ---",
            "Olá! Sou o TheOG. Aqui tens como me podes usar:",
            " ",
            "!prenda [nick]  -> Oferece uma prenda ASCII básica e fofa a alguém no canal! 🎁",
            "!invite [nick]  -> Envia um convite privado ASSINADO por ti para trazeres amigos ao #TheOG.",
            "!sorte [signo]  -> O teu horóscopo diário em Português (enviado em PVT).",
            "!tempo [cidade] -> Meteorologia real de qualquer cidade (enviado em PVT).",
            "!conselho       -> Recebe uma dica filosófica ou engraçada (enviado em PVT).",
            " ",
            "💡 Se mencionares 'TheOG' no canal, eu respondo (à minha maneira!).",
            "----------------------------------"
        ]
        for c in cmds: 
            irc_socket.send(f"PRIVMSG {user} :{c}\r\n".encode())
            time.sleep(0.4) # Pequena pausa para evitar flood
        return True

    # 3. OUTROS COMANDOS (PVT)
    if msg.startswith("!sorte "):
        irc_socket.send(f"PRIVMSG {user} :🔮 {get_horoscope(message.split()[1])}\r\n".encode())
        return True
    if msg.startswith("!tempo "):
        irc_socket.send(f"PRIVMSG {user} :[METEO] {get_weather(message.split()[1])}\r\n".encode())
        return True
    if msg.startswith("!conselho"):
        irc_socket.send(f"PRIVMSG {user} :[DICA] {get_advice()}\r\n".encode())
        return True
    if msg.startswith("!invite "):
        parts = message.split()
        if len(parts) > 1:
            irc_socket.send(f"PRIVMSG {parts[1]} :Olá! {user} convidou-te a visitar o #TheOG. Vem conviver!\r\n".encode())
            irc_socket.send(f"PRIVMSG {user} :Convite enviado com sucesso!\r\n".encode())
        return True

    # 4. RESPOSTA AO NICK (EVASIVA)
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

                if "376" in line: # End of MOTD
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
        except Exception as e:
            print(f"Erro IRC: {e}. Reconnect em 20s...")
            time.sleep(20)

# --- WEB SERVER (FLASK) ---

@app.route('/')
def home(): return "TheOG Bot está online."

if __name__ == "__main__":
    # Iniciar bot e loop de reforço em threads separadas
    threading.Thread(target=run_irc_bot, daemon=True).start()
    
    def positive_loop():
        while True:
            time.sleep(1800) # De 30 em 30 minutos
            if irc_conn:
                try: irc_conn.send(f"PRIVMSG {CHANNEL} :🌟 {random.choice(POSITIVE_REINFORCEMENT)}\r\n".encode())
                except: pass
    threading.Thread(target=positive_loop, daemon=True).start()

    # Iniciar Flask (Porta obrigatória para o Render)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
