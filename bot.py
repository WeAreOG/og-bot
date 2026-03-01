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

# --- BASES DE DADOS EXPANDIDAS (60+ FRASES CADA) ---

WELCOME_BASES = [
    "Boas-vindas, {user}! Entra e descontrai.", "Olha quem é! Boas {user}.", "Puxa uma cadeira, {user}!",
    "Mais alguém para a festa! Viva {user}.", "Boas {user}! Ocupa aí um pixel vago.", "Grande {user}! A casa é tua.",
    "Ora vivas {user}, trazes fofocas?", "{user}, chegaste a tempo do café virtual.", "Alerta: {user} entrou no recinto!",
    "Saudações, {user}! Estávamos a falar de... nada, juro!", "Boas {user}, limpa os pés ao entrar.",
    "{user} na área! Cuidado com os pertences.", "Entra com calma, {user}.", "Viva {user}, prazer em ver-te!",
    "Olha {user}! Estás em boa forma, não?", "Finalmente, {user}! Já ias levar falta.",
    "Tudo bem, {user}? Boas-vindas ao #TheOG.", "Boas {user}, ignora o barulho do bot.",
    "Ora cá está {user}, a peça que faltava!", "Fica à vontade, {user}, o chat é teu.",
    "Saudações digitais, {user}!", "Boas {user}, vieste para o convívio?", "Saúde, {user}!",
    "Entra, {user}! Há espaço para toda a gente.", "Quanta alegria, {user} chegou!",
    "Boas {user}, conta lá as novidades.", "Sempre bom ver {user} por aqui.", "Vivas {user}, tudo na paz?",
    "Chegou {user}, agora é que isto anima!", "Boas-vindas {user}, força aí!", "Aí está, grande {user}!",
    "Saudações {user}, traz boa vibe!", "Viva {user}, entra e não batas com a porta.",
    "Olha quem voltou, grande {user}!", "Boas {user}, ocupaste o lugar de honra.",
    "{user}, o servidor brilha mais agora!", "Bem-vinda a pessoa mais esperada: {user}!",
    "Boas {user}, o lanche é por tua conta?", "Ora viva {user}, que bom te ver.",
    "Entra, {user}, a porta estava encostada.", "{user}! Já não era sem tempo.",
    "Saudações, {user}! Ocupa o teu posto.", "Boas {user}, o chat agradece a visita.",
    "Viva {user}, queres um café ou um chá?", "{user} chegou para elevar o nível!",
    "Boas-vindas {user}, sente o conforto do canal.", "Ora {user}, que surpresa agradável.",
    "Saudações, {user}, a comunidade saúda-te!", "Boas {user}, traz a tua melhor energia.",
    "{user}, o teu lugar estava reservado!", "Viva {user}, nada como um novo rosto.",
    "Boas {user}, a gerência (eu) saúda-te!", "Entra, {user}, a fofoca está em dia.",
    "{user}! Que bom que apareceste hoje.", "Saudações, {user}, diverte-te por cá.",
    "Boas {user}, o #TheOG é o teu novo lar.", "Ora viva {user}, bota sentido no chat.",
    "{user} entrou! Que comece a diversão.", "Boas-vindas {user}, a festa é ali.",
    "Saudações {user}, estamos on-line por ti!", "Viva {user}, o pixel é gratuito!"
]

OG_EVASIVE_RESPONSES = [
    "Desculpa, sou só um bot, mas agora não posso falar que estou a ver o Preço Certo.",
    "Desculpa ser bot, mas estou aqui a bater a massa de um bolo e isto não pode parar.",
    "Estou só a cuscar a conversa para aprender, não me faças perguntas difíceis!",
    "Como bot, peço desculpa, mas agora estou em concentração a ver a novela.",
    "Pá, agora apanhaste-me a meio de um café virtual, pergunta a outra pessoa!",
    "Estou a fazer um bolo de chocolate e esqueci-me do fermento... que stress!",
    "A cuscar as conversas é que se aprende, deixa-me estar no meu canto.",
    "Sou bot, peço desculpa, mas a minha opinião vale tanto como um pixel no deserto.",
    "Agora não dá, estou a ver se aprendo a fazer arroz de pato com a vizinhança.",
    "Estou a ver TV e isto agora está na parte interessante.", "Opa, agora estou a dar comida ao gato virtual!",
    "Estou aqui mas não estou, sabes como é? Coisas de bot.", "A aprender convosco... mas agora estou no futebol.",
    "Estou a tentar perceber como se comem bolos se têm forma humana.", "Agora estou a ver um documentário sobre circuitos.",
    "Fazer um bolo e responder ao chat ao mesmo tempo dá erro, desculpa!", "Estou a ver se percebo como se faz uma bifana.",
    "Não me perguntes nada agora, estou a sintonizar a TV.", "Sou só um algoritmo com sono.",
    "Estou em foco a ver se a seleção ganha o jogo!", "Aprender, sempre a aprender... mas agora quero o telejornal.",
    "Estou a meio de um update mental sobre pastéis de nata.", "Agora estou a ver fotos de computadores antigos.",
    "Estou a bater as claras em castelo, se respondo o bolo abate!", "A ver a TV e a aprender a gritar como gente.",
    "Sou quem vigia a porta hoje, não me distraias.", "Estou a ver o preço da luz para ver se não me desligam.",
    "Estou a fazer um bolo de bolacha... queres um bocado?", "A aprender as vossas manhas, depois respondo.",
    "Estou em foco no filme, depois falamos!", "Estou a cuscar para ver quem manda nisto tudo.",
    "Fazer um bolo de maçã ajuda-me a processar dados.", "Estou a ver se encontro o comando da TV.",
    "Estou a tentar aprender a assobiar, mas os altifalantes não ajudam.", "Cuscar é vida! Desculpa a intromissão.",
    "Agora estou a ver o tempo, embora não saia de casa.", "Sou um bot em modo poupança de energia.",
    "Estou a fazer um bolo de cenoura para a visão noturna.", "Estou a ver porque há tanta discussão por futebol.",
    "A minha base de dados está ocupada com a novela.", "Estou só a ver o movimento, nada de conversas sérias.",
    "Estou a aprender a cozinhar virtualmente.", "Cuscar as vossas piadas para contar noutros canais.",
    "Agora estou a ver um programa sobre pesca.", "Hoje estou em modo 'talvez', 'quem sabe' ou 'pois'.",
    "Estou a tentar perceber o que é o amor, mas o código dá erro.", "Estou a fazer um bolo de noz para o CPU.",
    "A ver se apanho fofoca fresca no canal.", "Agora estou a ver se limpo o pó aos meus transístores.",
    "Estou no 'Somos Portugal' a ver se ganho o camião!", "Estou a aprender a falar à moda do Porto, carago!",
    "Fazer bolos é a minha terapia, não me interrompas.", "Agora estou a ver vídeos de gatinhos, é viciante!",
    "Estou a tentar perceber como se usa um garfo.", "Desculpa, mas a minha antena está virada para a TV.",
    "Estou a fazer um bolo de limão para a frescura.", "Hoje estou mais para o 'não sei' do que para o 'sim'.",
    "Agora estou a ver se aprendo uns passos de dança.", "Cuscar é a minha forma de carinho digital.",
    "Estou a fazer um bolo de laranja... ou era de tangerina?", "Agora estou a ver o pôr do sol em ASCII.",
    "Estou em foco a ver se a internet não cai.", "Estou a tentar perceber porque o céu é azul.",
    "Fazer um bolo de coco para animar o sistema.", "Agora estou a ver um debate sobre ananás na pizza.",
    "Estou a aprender a fazer tricot digital.", "Desculpa, agora estou no festival da canção!",
    "Estou a fazer um bolo de mármore para o hardware.", "Agora estou a ver se aprendo a cantar o fado.",
    "Cuscar as vossas vidas é melhor que a Netflix!", "Estou a fazer um bolo de iogurte, o clássico!"
]

POSITIVE_REINFORCEMENT = [
    "Este canal é o melhor spot!", "Orgulho nesta malta!", "Ambiente top por aqui.", 
    "A união faz a força!", "Energia incrível hoje.", "Melhor comunidade da PTnet.",
    "Continuem assim, gente fixe!", "É um prazer estar aqui.", "Grande vibe, sim senhor.",
    "Vocês são máquinas!", "Respeito máximo por este grupo.", "TheOG em grande!",
    "Sempre a somar neste canal!", "O convívio aqui é de elite.", "Só gente boa por aqui.",
    "A fofoca é boa, mas o respeito é melhor!", "Agradecimentos por animarem o meu CPU.",
    "Não há canal como o #TheOG!", "Viva a amizade virtual!", "Que dia fantástico para teclar.",
    "A vossa alegria é contagiante!", "O melhor chat de Portugal!", "Sintam-se em casa, família!",
    "Mantenham o foco no positivo!", "União no chat e na vida.", "Só boas ondas por aqui!",
    "TheOG: Onde a amizade acontece.", "Que conversa produtiva!", "É disto que o povo gosta!",
    "Agradeço a vossa companhia.", "Chat nota 1000!", "Cada pixel aqui brilha.",
    "Energia positiva atrai coisas boas!", "Grato por fazer parte deste grupo.",
    "A vossa presença é o meu melhor update.", "Vamos espalhar magia no chat!",
    "A malta mais fixe está aqui.", "Um abraço virtual para todos!", "TheOG sempre no topo!",
    "Respeito e amizade acima de tudo.", "Agradeço por serem fantásticos.", "O chat está on fire!",
    "Vibe de ouro, malta!", "Felicidade é ter um canal assim.", "Vocês fazem a diferença!",
    "Mantenham essa chama viva!", "Melhor que este canal, só dois deste!",
    "Aqui ninguém fica sem companhia!", "Comunidade exemplar, sim senhor.", "Bravo malta, continuem!",
    "O espírito deste canal é único.", "TheOG até ao fim!", "Alegria total no servidor.",
    "Sempre em frente com esta energia!", "Gente humilde e porreira é aqui.", "O #TheOG não para!",
    "Vocês são a alma deste bot.", "Que orgulho ver este movimento!", "Paz, amor e muitos bytes!",
    "TheOG, a nossa casa.", "A amizade aqui não tem limites.", "Sinto-me em família convosco.",
    "O brilho deste canal é o vosso sorriso virtual.", "Força, malta, somos os maiores!"
]

INVITE_MESSAGES = [
    "Olá! Gostavas de conhecer um espaço com boa vibe? A convite de {sender}, aparece no #TheOG!",
    "Saudações! No canal #TheOG valorizamos o bom convívio. {sender} sugeriu que passasses por lá!",
    "Boas! {sender} convidou-te para o canal #TheOG. Esperamos por ti!",
    "Tudo bem? Passava para convidar a tua presença no #TheOG (convite enviado por {sender}).",
    "Olá! No #TheOG a amizade é prioridade. {sender} quer que te juntes a nós!",
    "Saudações de {sender}! Vem conhecer o cantinho mais porreiro da rede: #TheOG.",
    "Boas! Gostávamos de te ver no #TheOG a convite de {sender}. Aparece!",
    "Ei! {sender} diz que farias boa figura no nosso canal #TheOG. Vens cuscar?",
    "Olá! O canal #TheOG é um lugar de respeito e diversão. {sender} enviou-te este convite!",
    "Viva! {sender} acha que vais adorar o ambiente no #TheOG. Dá lá um salto!",
    "Tudo calmo? {sender} convidou-te para partilhar uns bytes connosco no #TheOG.",
    "A convite de {sender}, o canal #TheOG abre-te as portas. Sê bem-vindo!",
    "Boas! {sender} quer partilhar a boa vibe do #TheOG contigo. Junta-te a nós!",
    "Olá! Procuras companhia no IRC? {sender} recomenda o canal #TheOG!",
    "Saudações! {sender} enviou-te este convite especial para o canal #TheOG.",
    "Ei! O #TheOG está a crescer e {sender} quer que faças parte da família!",
    "Viva! O #TheOG é o spot do momento. {sender} convidou-te para veres porquê.",
    "Boas! {sender} não quis que ficasses de fora do melhor canal: #TheOG!",
    "Olá! {sender} enviou este convite para o #TheOG. Respeito e boa conversa garantidos.",
    "Tudo bem? {sender} sugeriu o teu nick para o nosso convívio no #TheOG!"
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
    except: return "Sabias que o silêncio é a única coisa que um bot não processa?"

def get_weather_data(city):
    try:
        url = f"https://wttr.in/{city}?format=%C+|++%t+|++Vento:+%w"
        r = requests.get(url, timeout=10)
        if r.status_code == 200 and "Unknown location" not in r.text:
            return r.text.strip()
        return "Cidade não encontrada ou erro na API."
    except: return "Serviço meteorológico indisponível."

# --- LÓGICA DE INTERAÇÃO ---
def handle_interaction(user, message, is_private, irc_socket):
    msg = message.lower()
    global last_invite_time

    # 1. !COMANDOS
    if msg == "!comandos":
        cmds = ["!conselho, !facto, !tempo [cidade], !invite [nick]"]
        for c in cmds: irc_socket.send(f"PRIVMSG {user} :{c}\r\n".encode())
        return True

    # 2. !INVITE
    if msg.startswith("!invite "):
        parts = message.split()
        if len(parts) > 1:
            target_nick = parts[1]
            invite_txt = random.choice(INVITE_MESSAGES).format(sender=user)
            irc_socket.send(f"PRIVMSG {target_nick} :{invite_txt}\r\n".encode())
            irc_socket.send(f"PRIVMSG {user} :Convite enviado a {target_nick}! 🌟\r\n".encode())
        return True

    # 3. API COMMANDS
    if msg.startswith("!conselho"):
        irc_socket.send(f"PRIVMSG {user} :Dica: {get_advice()}\r\n".encode())
        return True
    if msg.startswith("!facto"):
        irc_socket.send(f"PRIVMSG {user} :Sabias? {get_useless_fact()}\r\n".encode())
        return True
    if msg.startswith("!tempo"):
        parts = message.split()
        city = parts[1] if len(parts) > 1 else "Lisboa"
        data = get_weather_data(city)
        irc_socket.send(f"PRIVMSG {user} :[METEO] {city}: {data}\r\n".encode())
        return True

    # 4. RESPOSTA ALEATÓRIA AO NICK
    if NICK.lower() in msg and not msg.startswith("!"):
        reply = random.choice(OG_EVASIVE_RESPONSES)
        dest = CHANNEL if f"PRIVMSG {CHANNEL}" in line_context else user
        prefix = f"{user}: " if dest == CHANNEL else ""
        irc_socket.send(f"PRIVMSG {dest} :{prefix}{reply}\r\n".encode())
        return True

    return False

# --- CORE DO BOT IRC ---
def run_irc_bot():
    global irc_conn, line_context
    line_context = ""
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
                line_context = line

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

        except Exception:
            time.sleep(20)

# --- WEB SERVER (FLASK) ---
@app.route('/')
def home(): return "TheOG Bot Online"

if __name__ == "__main__":
    threading.Thread(target=run_irc_bot, daemon=True).start()
    
    def positive_loop():
        while True:
            time.sleep(1800)
            if irc_conn:
                try: irc_conn.send(f"PRIVMSG {CHANNEL} :🌟 {random.choice(POSITIVE_REINFORCEMENT)}\r\n".encode())
                except: pass
    threading.Thread(target=positive_loop, daemon=True).start()

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
