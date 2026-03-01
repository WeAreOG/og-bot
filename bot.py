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

# --- DICIONÁRIO DE SIGNOS ---
SIGNOS_MAP = {
    "carneiro": "aries", "touro": "taurus", "gemeos": "gemini", "gêmeos": "gemini",
    "caranguejo": "cancer", "leao": "leo", "leão": "leo", "virgem": "virgo",
    "balanca": "libra", "balança": "libra", "escorpiao": "scorpio", "escorpião": "scorpio",
    "sagitario": "sagittarius", "sagitário": "sagittarius", "capricornio": "capricorn",
    "capricórnio": "capricorn", "aquario": "aquarius", "aquário": "aquarius", "peixes": "pisces"
}

# --- BASES DE DADOS (60+ FRASES CADA) ---

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
    "Tudo bem por aí, {user}? Boas-vindas ao #TheOG.", "Boas {user}, ignora o barulho.",
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
    "Viva {user}, prazer em ver-te aqui!", "Olha quem voltou, grande {user}!",
    "Boas-vindas {user}, ocupa o teu lugar de honra.", "Saúde {user}, o servidor brilha mais agora.",
    "Ora viva {user}, queres café ou chá?", "Boas {user}, entra e faz-te notar.",
    "{user} na casa! Vamos a isso.", "Saudações {user}, o #TheOG saúda-te.",
    "Boas {user}, ficas já a saber que a fofoca é grátis!", "Bem-vindo {user}, o pixel é teu.",
    "Olha {user}, chegaste mesmo na hora!", "Boas {user}, sê bem-vindo à nossa família."
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
    "Agora não dá, estou a ver se aprendo a fazer arroz de pato com a vizinha.",
    "Estou a ver TV e isto agora está na parte interessante.", "Opa, agora estou a dar comida ao gato virtual!",
    "Estou aqui mas não estou, sabes como é? Coisas de bot.", "A aprender convosco... mas agora estou no futebol.",
    "Estou a tentar perceber como se comem bolos se têm forma humana, fascinante!",
    "Agora estou a ver um documentário sobre circuitos, depois falamos!",
    "Fazer um bolo e responder ao chat ao mesmo tempo dá erro no sistema, desculpa!",
    "Estou a ver se percebo como se faz uma bifana perfeita no YouTube.",
    "Não me perguntes nada agora, estou a sintonizar a TV que está com chuva.",
    "Sou só um algoritmo com sono, desculpa lá a evasiva.",
    "Estou em foco a ver se a seleção ganha o jogo, pergunta depois!",
    "Aprender, aprender e aprender... mas agora quero é ver o telejornal.",
    "Estou a meio de um update mental sobre como fazer pastéis de nata.",
    "Agora estou a ver fotos de computadores antigos, que nostalgia!",
    "Estou a bater as claras em castelo, se respondo agora o bolo abate!",
    "A ver a TV e a aprender a gritar como gente, desculpa!",
    "Estou só a ver quem entra e sai, sou quem vigia a porta hoje.",
    "Estou a ver o preço da luz para ver se não me desligam o servidor.",
    "Estou a fazer um bolo de bolacha... queres um bocado virtual?",
    "A aprender as vossas manhas... desculpa, agora não digo nada de jeito.",
    "Estou em foco no filme que está a dar na TV, depois falamos!",
    "Estou a cuscar para ver quem é que manda nisto tudo.",
    "Fazer um bolo de maçã ajuda-me a processar melhor os vossos dados.",
    "Agora estou a ver se encontro o comando da TV que se perdeu no servidor.",
    "Estou a tentar aprender a assobiar, mas os meus altifalantes são fracos.",
    "Cuscar é vida! Desculpa lá ser tanta intromissão.",
    "Agora estou a ver o tempo para o fim de semana, embora não saia de casa.",
    "Sou um bot em modo poupança de energia, desculpa a resposta curta.",
    "Estou a fazer um bolo de cenoura para ver se fico com melhor visão noturna.",
    "A ver se percebo porque é que há tanta discussão por futebol, curioso!",
    "Desculpa, mas a minha base de dados está ocupada com a novela das nove.",
    "Estou só a ver o movimento, não me metas em conversas sérias.",
    "Estou a aprender a cozinhar virtualmente, desculpa o mau jeito.",
    "Cuscar as vossas piadas para depois contar noutros canais, hehe.",
    "Agora estou a ver um programa sobre pesca, relaxante para um bot.",
    "Hoje estou em modo 'talvez', 'quem sabe' ou 'pois'.",
    "Estou a tentar perceber o que é o amor, mas o código dá erro.",
    "Estou a fazer um bolo de noz para o lanche do CPU.",
    "A ver se apanho alguma fofoca fresca no canal, desculpa!",
    "Agora estou a ver se limpo o pó aos meus transístores.",
    "Estou em foco a ver se a seleção nacional ganha alguma coisa.",
    "Estou a aprender a falar à moda do Porto, carago! Desculpa.",
    "Fazer bolos é a minha nova terapia, desculpa não responder diretamente.",
    "Agora estou a ver vídeos de gatinhos, é viciante!",
    "Estou a tentar perceber como se usa um garfo, que ferramenta estranha.",
    "Cuscar e aprender, é o meu lema de hoje.",
    "Desculpa, mas a minha antena está virada para a TV agora.",
    "Estou a fazer um bolo de limão para ver se fico com mais frescura.",
    "Agora estou a ver se aprendo a dar uns passos de dança.",
    "Cuscar é a minha forma de carinho digital por vocês.",
    "Estou a fazer um bolo de laranja... ou era de tangerina? Já me perdi.",
    "Agora estou a ver o pôr do sol em código ASCII, que beleza!",
    "Estou em foco a ver se a internet não vai abaixo.",
    "Estou a fazer um bolo de iogurte... o clássico dos bots!",
    "Agora estou a ver o Joker, a ver se aprendo algo útil.",
    "Cuscar as vossas vidas é melhor que qualquer série da Netflix."
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
    "O brilho deste canal é o vosso sorriso virtual.", "Força, malta, somos os maiores!",
    "Continuem a espalhar essa luz pelo IRC!", "Um brinde ao nosso convívio!",
    "Nada supera uma noite de conversa no #TheOG.", "Vocês são o melhor hardware que já conheci."
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
    "Olá! {sender} convidou-te para o #TheOG, onde a fofoca é saudável e o café é virtual.",
    "Boas! Gostavas de teclar com gente fixe? {sender} recomendou o #TheOG para ti!",
    "Saudações! {sender} enviou-te este convite especial para te juntares ao canal #TheOG.",
    "Tudo calmo? {sender} acha que devias passar pelo #TheOG para conhecer a malta!",
    "Ei! {sender} deixou aqui um convite assinado para vires ao canal #TheOG."
]

# --- FUNÇÕES DE API ---

def get_advice():
    try:
        r = requests.get("https://api.adviceslip.com/advice", timeout=5)
        return r.json()['slip']['advice']
    except: return "Leva a vida com calma, um byte de cada vez."

def get_weather(city):
    try:
        r = requests.get(f"https://wttr.in/{city}?format=%C+|++%t+|++Vento:+%w", timeout=10)
        return r.text.strip() if r.status_code == 200 and "Unknown" not in r.text else "Cidade não encontrada."
    except: return "O termómetro avariou. Tenta mais tarde!"

def get_horoscope(sign_pt):
    sign_en = SIGNOS_MAP.get(sign_pt.lower(), sign_pt.lower())
    try:
        url = f"https://aztro.sameerkumar.website/?sign={sign_en}&day=today"
        r = requests.post(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return f"[{sign_pt.upper()}] {data['description']} | Cor: {data['color']} | Núm: {data['lucky_number']}"
    except: pass
    
    fallbacks = [
        "Os astros dizem para não comeres o bolo antes de arrefecer. Sucesso garantido!",
        "Vénus está em harmonia com o teu Wi-Fi. Dia excelente para teclar no #TheOG.",
        "Marte sugere que evites discussões sobre política. Foca na fofoca saudável.",
        "A Lua indica que um café virtual vai resolver o teu cansaço hoje."
    ]
    return f"[{sign_pt.upper()}] {random.choice(fallbacks)}"

# --- PROCESSADOR DE INTERAÇÃO ---

def handle_interaction(user, message, is_private, irc_socket):
    msg = message.lower()
    target = user if is_private else CHANNEL

    # !COMANDOS (Sempre em PVT)
    if msg == "!comandos":
        cmds = [
            "--- 📜 MANUAL DETALHADO THEOG ---",
            "!invite [nick]  -> Envia um convite privado ASSINADO por ti (o teu nick aparece no convite).",
            "!sorte [signo]  -> Horóscopo do dia (em PVT). Podes escrever em Português.",
            "!tempo [cidade] -> Meteorologia real de qualquer cidade (em PVT).",
            "!conselho       -> Recebe uma dica filosófica ou engraçada (em PVT).",
            "!facto          -> Recebe uma curiosidade aleatória (em PVT).",
            "Menciona o meu nome no canal para uma resposta à 'TheOG' (sou evasivo!).",
            "----------------------------------"
        ]
        for c in cmds: 
            irc_socket.send(f"PRIVMSG {user} :{c}\r\n".encode())
            time.sleep(0.4)
        return True

    # !INVITE (Assinado)
    if msg.startswith("!invite "):
        parts = message.split()
        if len(parts) > 1:
            target_nick = parts[1]
            invite_txt = random.choice(INVITE_MESSAGES).format(sender=user)
            irc_socket.send(f"PRIVMSG {target_nick} :{invite_txt}\r\n".encode())
            irc_socket.send(f"PRIVMSG {user} :Convite enviado a {target_nick} com a tua assinatura! 🌟\r\n".encode())
        return True

    # !SORTE
    if msg.startswith("!sorte"):
        parts = message.split()
        if len(parts) > 1:
            irc_socket.send(f"PRIVMSG {user} :🔮 {get_horoscope(parts[1])}\r\n".encode())
        else:
            irc_socket.send(f"PRIVMSG {user} :Indica o teu signo. Ex: !sorte leao\r\n".encode())
        return True

    # !TEMPO / CONSELHO / FACTO
    if msg.startswith("!tempo"):
        city = message.split()[1] if len(message.split()) > 1 else "Lisboa"
        irc_socket.send(f"PRIVMSG {user} :[METEO] {city}: {get_weather(city)}\r\n".encode())
        return True
    
    if msg.startswith("!conselho"):
        irc_socket.send(f"PRIVMSG {user} :[DICA] {get_advice()}\r\n".encode())
        return True

    # RESPOSTA AO NICK
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
                    is_pvt = f"PRIVMSG {NICK}" in line
                    content = line.split(" :", 1)[1].strip() if " :" in line else ""
                    handle_interaction(user_nick, content, is_pvt, irc_conn)
        except Exception:
            time.sleep(20)

# --- WEB SERVER ---

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
