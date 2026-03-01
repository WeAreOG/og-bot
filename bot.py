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

# Filtro para não interagir com serviços da rede
BOT_FILTER = ["nickserv", "chanserv", "memoserv", "operserv", "adamastor", "statserv", "secure"]

app = Flask(__name__)

# --- LISTAS DE FRASES (GÉNERO NEUTRO) ---
WELCOME_BASES = [
    "Boas-vindas ao antro, {user}!", "Olha quem é! Boas {user}.", "Puxa uma cadeira e bota sentido, {user}!",
    "Mais alguém para a festa! Viva {user}.", "Apareceste, {user}! Já pensava que tinhas ido às compras.",
    "Boas {user}! Ocupa aí um pixel vago.", "Ora vivas {user}, trazes bebidas?", 
    "Grande {user}! A casa é tua (mas não estragues nada).", "Alerta CM: {user} acaba de entrar!",
    "Saudações, {user}! Estávamos mesmo a falar de ti... brincadeira!",
    "{user}, chegaste a tempo do lanche virtual.", "Vejam só quem decidiu aparecer, boas {user}!",
    "Tudo calmo até {user} chegar! Boas-vindas.", "Dá cá cinco, {user}!", 
    "Boas-vindas {user}, limpa os pés ao entrar.", "Fica à vontade, {user}, o chat é teu.",
    "Uma lenda de nome {user} entrou no servidor!", "Boas {user}, conta lá as novidades.",
    "Olha {user}! Estás em boa forma, não? Boas-vindas.", "Finalmente, {user}! Já ias levar falta.",
    "Tudo bem por aí, {user}? Boas-vindas ao #TheOG.", "Boas-vindas {user}, ignora o barulho.",
    "Ora cá está {user}, a peça que faltava!", "Boas {user}, não ligues ao bot, é só código maluco.",
    "{user} na área! Cuidado com os pertences.", "Entra, {user}! Há espaço para toda a gente.",
    "Quanta alegria, {user} chegou!", "Mais alguém ilustre: boas-vindas {user}!", 
    "Boas {user}, vieste para a fofoca ou para o convívio?", "Saudações digitais, {user}!",
    "Boas-vindas {user}, a gerência agradece a visita.", "Olha {user}, a maior estrela da aldeia!",
    "Puxa um banco, {user}.", "Boas {user}, traz notícias frescas!",
    "{user}! Que bom ver-te por estas bandas.", "Entra com calma, {user}.",
    "Sempre bom ver {user} por aqui.", "Boas {user}! Estás em casa.",
    "Um brinde à entrada de {user}!", "Vivas {user}, tudo na paz?",
    "Chegou {user}, agora é que isto anima!", "Boas-vindas {user}, força aí!",
    "Tudo a postos? {user} entrou!", "Boas {user}, não te percas no chat.",
    "Aí está, grande {user}!", "Boas-vindas {user}, mais alguém para o grupo.",
    "Saudações {user}, espero que tragas boa vibe!", "Boas {user}, entra e não batas com a porta.",
    "Viva {user}, prazer em ver-te aqui!", "Olha quem voltou, grande {user}!"
]

POSITIVE_REINFORCEMENT = [
    "Este canal é o melhor spot!", "Orgulho nesta malta!", "Ambiente top por aqui.", 
    "A união faz a força!", "Energia incrível hoje.", "Melhor comunidade da PTnet.",
    "Continuem assim, gente fixe!", "É um prazer estar aqui.", "Grande vibe, sim senhor.",
    "Vocês são máquinas!", "Respeito máximo por este grupo.", "TheOG em grande!",
    "Sempre a somar neste canal!", "O convívio aqui é de elite.", "Só gente boa por estas bandas.",
    "A fofoca é boa, mas o respeito é melhor!", "Agradecimentos por animarem o meu CPU.",
    "Não há canal como o #TheOG!", "Viva a amizade virtual!", "Que dia fantástico para teclar.",
    "A vossa alegria é contagiante!", "O melhor chat de Portugal, sem dúvida.",
    "Sintam-se em casa, família!", "Mantenham o foco no positivo!", "União no chat e na vida.",
    "Só boas ondas por aqui hoje!", "TheOG: Onde a amizade acontece.", "Que conversa produtiva!",
    "É disto que o povo gosta!", "Agradeço a vossa companhia.", "Chat nota 1000!",
    "Cada pixel aqui brilha com vocês.", "Energia positiva atrai coisas boas!",
    "Grato por fazer parte deste grupo.", "A vossa presença é o meu melhor update.",
    "Vamos espalhar magia no chat!", "A malta mais fixe da rede está aqui.",
    "Um abraço virtual para toda a gente!", "TheOG sempre no topo!", "Respeito e amizade acima de tudo.",
    "Agradeço por serem pessoas fantásticas.", "O chat está on fire hoje!",
    "Vibe de ouro, malta!", "Felicidade é ter um canal assim.", "Vocês fazem a diferença!",
    "Mantenham essa chama viva!", "Melhor que este canal, só dois deste!",
    "Aqui ninguém fica sem companhia!", "Comunidade exemplar, sim senhor.", "Bravo malta, continuem!",
    "O espírito deste canal é único.", "TheOG até ao fim!", "Alegria total no servidor.",
    "Agradeço por partilharem o vosso tempo aqui.", "Sempre em frente com esta energia!",
    "Gente humilde e porreira é aqui.", "O #TheOG não para!", "Vocês são a alma deste bot.",
    "Que orgulho ver este movimento!", "Paz, amor e muitos bytes!", "TheOG, a nossa casa."
]

INVITE_MESSAGES = [
    "Olá! Gostavas de conhecer um espaço com boa vibe? A convite de {sender}, aparece no #TheOG!",
    "Saudações! No canal #TheOG valorizamos o bom convívio. {sender} sugeriu que passasses por lá!",
    "Boas! Procuras um lugar para teclar com respeito? {sender} convidou-te para o canal #TheOG.",
    "Tudo bem? Passava para convidar a tua presença no #TheOG (convite enviado por {sender})."
]

# --- CONTROLO DE FLOOD E ESTADO ---
last_invite_time = {}
irc_conn = None

# --- FUNÇÕES DE API ---
def get_advice():
    try:
        r = requests.get("https://api.adviceslip.com/advice", timeout=5)
        return r.json()['slip']['advice']
    except: return "A vida é feita de momentos, aproveita cada um com calma."

def get_useless_fact():
    try:
        r = requests.get("https://uselessfacts.jsph.pl/random.json?language=en", timeout=5)
        return r.json()['text']
    except: return "Sabias que o silêncio às vezes é a melhor resposta?"

# --- PROCESSADOR DE COMANDOS ---
def handle_commands(user, message, irc_socket):
    msg = message.lower()
    global last_invite_time

    if msg == "!comandos":
        help_text = [
            "--- Funções Disponíveis (TheOG) ---",
            "!comandos - Lista de funções em PVT.",
            "!conselho - Recebe um conselho aleatório.",
            "!facto    - Recebe uma curiosidade.",
            "!invite [nick] - Convida alguém em teu nome.",
            "-----------------------------------"
        ]
        for line in help_text:
            irc_socket.send(f"PRIVMSG {user} :{line}\r\n".encode())
        return True

    if msg.startswith("!invite "):
        current_time = time.time()
        if user in last_invite_time and current_time - last_invite_time[user] < 60:
            irc_socket.send(f"PRIVMSG {user} :Aguarda um minuto antes de outro convite.\r\n".encode())
            return True
        parts = message.split()
        if len(parts) > 1:
            target = parts[1]
            if target.lower() != NICK.lower():
                invite_txt = random.choice(INVITE_MESSAGES).format(sender=user)
                irc_socket.send(f"PRIVMSG {target} :{invite_txt}\r\n".encode())
                irc_socket.send(f"PRIVMSG {user} :Convite enviado a {target} em teu nome! 🌟\r\n".encode())
                last_invite_time[user] = current_time
        return True

    if msg.startswith("!conselho"):
        irc_socket.send(f"PRIVMSG {user} :Conselho: {get_advice()}\r\n".encode())
        return True

    if msg.startswith("!facto"):
        irc_socket.send(f"PRIVMSG {user} :Sabias que? {get_useless_fact()}\r\n".encode())
        return True

    return False

# --- CORE DO BOT IRC ---
def run_irc_bot():
    global irc_conn
    while True:
        try:
            print(f"Ligar a {SERVER}...")
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
                    time.sleep(3)
                    irc_conn.send(f"JOIN {CHANNEL}\r\n".encode())
                    irc_conn.send(f"PRIVMSG {CHANNEL} :TheOG ativo e a vigiar! Escrevam !comandos em PVT.\r\n".encode())

                if " JOIN " in line:
                    u = line.split('!')[0][1:]
                    if u.lower() not in BOT_FILTER and u.lower() != NICK.lower():
                        msg = random.choice(WELCOME_BASES).format(user=u)
                        irc_conn.send(f"PRIVMSG {CHANNEL} :{msg}\r\n".encode())

                if "PRIVMSG" in line:
                    user_nick = line.split('!')[0][1:]
                    if user_nick.lower() == NICK.lower() or user_nick.lower() in BOT_FILTER: continue
                    msg_content = line.split(" :", 1)[1].strip() if " :" in line else ""
                    handle_commands(user_nick, msg_content, irc_conn)

        except Exception as e:
            print(f"Erro IRC: {e}. Reconnect em 20s...")
            time.sleep(20)

# --- LOOP DE REFORÇO POSITIVO ---
def pos_loop():
    while True:
        time.sleep(1800) # De 30 em 30 minutos
        if irc_conn:
            try:
                phrase = random.choice(POSITIVE_REINFORCEMENT)
                irc_conn.send(f"PRIVMSG {CHANNEL} :🌟 {phrase}\r\n".encode())
            except: pass

@app.route('/')
def home():
    return "TheOG Bot está online."

if __name__ == "__main__":
    # Iniciar bot e reforço em threads separadas
    threading.Thread(target=run_irc_bot, daemon=True).start()
    threading.Thread(target=pos_loop, daemon=True).start()
    
    # Iniciar Flask (Porta obrigatória para o Render)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
