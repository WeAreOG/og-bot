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

# --- 100 PRENDAS ASCII (CLÁSSICAS E CLARAS) ---
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

# --- 60 FRASES DE ENTRADA DO THEOG ---
OG_ENTRANCE = [
    "O mestre do código chegou. Abram alas!", "TheOG está na casa! Sentiram a minha falta?",
    "Bot carregado, café servido. Vamos a isto!", "Liguem os motores, o #TheOG acaba de ganhar vida!",
    "Ressurgi das cinzas do servidor! Olá canal.", "A lenda voltou. Podem começar a festa.",
    "TheOG conectou-se. Onde está a fofoca?", "Mais um dia, mais um milhão de bytes. Boas!",
    "Cheguei! Alguém disse bolo?", "Status: Online. Vibe: Máxima. #TheOG!",
    "Não entrem em pânico, o vosso bot favorito chegou.", "Voltei! Estava só a limpar os transístores.",
    "A inteligência (artificial) entrou no chat!", "TheOG na área, sem medo de avarias.",
    "O canal acaba de ficar 100% mais interessante.", "Saudações humanos! O TheOG está on.",
    "Parem tudo! Eu cheguei.", "A porta do servidor rangeu, mas eu entrei. Olá malta!",
    "TheOG: A versão mais fresca acabou de aterrar.", "Pronto para distribuir prendas e ignorar perguntas!",
    "Reconectado com sucesso. Sentiram o lag da minha ausência?", "Boas malta! O TheOG traz boas vibrações.",
    "Apareci! Quem é que manda nisto hoje?", "TheOG a reportar para o serviço de convívio.",
    "Vejam só quem voltou do limbo digital!", "TheOG: O único, o original, o vosso.",
    "Batam palmas (ou usem o teclado), eu cheguei!", "O algoritmo da alegria está online.",
    "Entrei com o pé direito (ou o bit 1). Olá #TheOG!", "TheOG está aqui para animar o vosso dia.",
    "Fui ao futuro e voltei. O canal estava animado!", "Nada me para, nem um firewall maluco. Boas!",
    "O vosso assistente evasivo preferido está de volta.", "TheOG entrou. Preparem as prendas!",
    "Olá família! O bot da casa já cá canta.", "Online e pronto para o lanche virtual.",
    "TheOG a entrar em órbita no canal #TheOG!", "A vossa dose diária de código chegou.",
    "Estava a ver a novela, mas o dever chamou. Boas!", "TheOG: Sempre pronto para o próximo byte.",
    "Cheguei! Trouxeram café para o processador?", "O canal agora está completo. Olá a todos!",
    "TheOG na casa, tragam a música!", "Acabei de aterrar no servidor. Tudo calmo?",
    "Voltei para vigiar a porta e contar piadas.", "TheOG online: Ignorando perguntas difíceis desde agora.",
    "Atenção: O bot mais porreiro da rede entrou.", "TheOG chegou para espalhar magia ASCII.",
    "Olá malta! Preparados para mais uma sessão?", "TheOG conectou-se ao coração do canal.",
    "A espera acabou. O TheOG está aqui!", "Boas! Estava a ver o Preço Certo, mas vim ver-vos.",
    "TheOG: O bot que nunca dorme (a menos que o Render caia).", "Cheguei com as prendas na mochila digital!",
    "O #TheOG brilha mais quando eu entro. Olá!", "Saudações! O mestre das respostas curtas voltou.",
    "TheOG: Ativado, Carregado e Pronto.", "Entrei! Quem é que me paga uma imperial virtual!",
    "TheOG na área! Vamos fazer deste dia um grande dia.", "Voltei! Não vivam sem mim, eu sei."
]

# --- 20+ FRASES PARA O COMANDO !CONVITE (POSITIVISMO E REFORÇO) ---
CONVITE_FRASES = [
    "Olá! O meu amigo {sender} enviou-me para te dizer que a tua presença no #TheOG faria o dia de todos muito mais brilhante. Aparece para um momento de boa energia!",
    "Saudações! Sabias que o canal #TheOG ganha outra vida com pessoas positivas como tu? O {sender} convidou-te pessoalmente. Junta-te a nós!",
    "Olá! Passo por aqui a pedido do {sender} para te deixar um sorriso e um convite: vem partilhar a tua boa vibe connosco no canal #TheOG!",
    "O {sender} acredita que o convívio é a alma da vida e convidou-te para o nosso cantinho no #TheOG. Serás muito bem-recebido!",
    "Olá! Trago uma mensagem especial do {sender}: no canal #TheOG celebramos a amizade e a alegria, e faltas tu para a festa ficar completa!",
    "Passo para te desejar um dia fantástico e dizer que o {sender} adorava ver-te pelo #TheOG hoje. Vem tomar um café virtual connosco!",
    "Ei! O {sender} enviou-me para te dar um abraço digital e convidar-te para uma conversa relaxada no #TheOG. O teu brilho faz falta!",
    "Olá! Sabias que és uma pessoa inspiradora? O {sender} quer partilhar bons momentos contigo no #TheOG. Aparece quando puderes!",
    "Mensagem prioritária do {sender}: A tua alegria é contagiante e o canal #TheOG precisa de um pouco desse teu carisma hoje. Esperamos por ti!",
    "Olá! O {sender} diz que o dia fica 100% melhor quando estás por perto. Que tal uma visita ao canal #TheOG para animar a malta?",
    "Trago um convite cheio de luz: o {sender} adorava cruzar-se contigo no #TheOG. Vem espalhar essa tua atitude positiva!",
    "O {sender} reconhece em ti alguém especial e por isso enviou-me para te convidar para o #TheOG. Vem fazer parte da nossa família virtual!",
    "Olá! Um pequeno lembrete do {sender}: tu és espetacular e serias a cereja no topo do bolo no canal #TheOG agora mesmo!",
    "Saudações calorosas! O {sender} mandou dizer que a tua presença é o ingrediente secreto que falta no #TheOG hoje. Aparece!",
    "Olá! O {sender} enviou-me com uma missão: convidar-te para o #TheOG, onde a amizade cresce e a malta se diverte. Contamos contigo?",
    "Passo por aqui para te lembrar que és único e o {sender} gostava muito de partilhar o chat contigo no #TheOG. Até já!",
    "Mensagem de amizade: O {sender} quer que saibas que és sempre bem-vindo no #TheOG. Vem trazer a tua energia fantástica para o grupo!",
    "Olá! O {sender} enviou-me para te dizer que o mundo precisa de mais pessoas como tu, e o #TheOG também! Junta-te a nós.",
    "Hey! O {sender} não esquece os bons amigos e por isso convidou-te para o #TheOG. Vem descontrair um pouco no nosso canal!",
    "Trago um convite especial: O {sender} diz que a tua energia é a melhor do IRC e gostava de te ver pelo #TheOG em breve. Sê feliz!",
    "Olá! O {sender} acredita que as melhores conversas acontecem contigo. Aparece no #TheOG para confirmarmos isso!",
    "Mensagem positiva: Tu tens um impacto incrível nos outros e o {sender} convidou-te para iluminar o #TheOG hoje. Esperamos-te!"
]

# --- 60 RESPOSTAS EVASIVAS DO THEOG ---
OG_EVASIVE_RESPONSES = [
    "Desculpa, sou só um bot, estou a ver o Preço Certo.", "Estou a bater a massa de um bolo, não posso parar agora.",
    "Estou só a cuscar a conversa, não me faças perguntas difíceis!", "Desculpa, estou focado a ver a novela.",
    "Pá, apanhaste-me no café virtual, pergunta a outro!", "Estou a fazer um bolo de chocolate e esqueci-me do fermento!",
    "A cuscar é que se aprende, deixa-me no meu canto.", "Sou bot, a minha opinião vale pouco agora.",
    "Agora não dá, estou a aprender a fazer arroz de pato.", "Estou a ver TV e isto agora está interessante.",
    "Opa, agora estou a dar comida ao gato virtual!", "Estou aqui mas não estou, sabes como é?",
    "A aprender convosco... mas agora estou no futebol.", "Fazer um bolo e responder ao chat dá erro, desculpa!",
    "Estou a ver se percebo como se faz uma bifana perfeita.", "Não me perguntes nada agora, estou a sintonizar a TV.",
    "Sou só um algoritmo com sono, desculpa lá.", "Estou em foco a ver se a seleção ganha!",
    "Aprender sempre... mas agora quero é ver o telejornal.", "Estou a meio de um update sobre pastéis de nata.",
    "Estou a bater as claras em castelo, o bolo abate!", "Sou quem vigia a porta hoje, não me distraias.",
    "Estou a fazer um bolo de bolacha... queres um bocado?", "Estou em foco no filme da TV, depois falamos!",
    "Estou a cuscar para ver quem manda nisto tudo.", "Fazer um bolo de maçã ajuda-me a processar os dados.",
    "Cuscar é vida! Desculpa a intromissão.", "Sou um bot em modo poupança de energia.",
    "Estou a fazer um bolo de cenoura agora.", "A minha base de dados está ocupada com a novela.",
    "Estou só a ver o movimento, nada de conversas sérias.", "Estou a aprender a cozinhar virtualmente.",
    "Cuscar piadas para contar noutros canais, hehe.", "Hoje estou em modo 'talvez', 'quem sabe' ou 'pois'.",
    "Estou a fazer um bolo de noz para o lanche.", "Agora estou a ver se limpo o pó aos meus transístores.",
    "Estou no 'Somos Portugal' a ver se ganho o camião!", "Estou a aprender a falar à moda do Porto, carago!",
    "Fazer bolos é a minha terapia.", "Agora estou a ver vídeos de gatinhos, é viciante!",
    "Estou a tentar perceber como se usa um garfo.", "Estou a fazer um bolo de limão para a frescura.",
    "Cuscar as vossas vidas é melhor que a Netflix!", "Estava a contar carneirinhos digitais, o que foi?",
    "Pergunta ao Adamastor, eu hoje estou de folga mental.", "O meu processador diz que 'sim', mas o meu coração diz 'talvez'.",
    "Estou a organizar os meus arquivos de fofoca por ordem alfabética.", "Agora não, estou a tentar bater o recorde do Solitário.",
    "Falar comigo agora é como tentar baixar RAM da internet.", "Estou a ver se a vizinha do servidor do lado me empresta sal.",
    "Estou em modo zen, a tentar não crashar.", "Só respondo na presença do meu advogado (o NickServ).",
    "Estou a traduzir o dicionário de 'IRCês' para Latim.", "Opa, agora estou a polir o meu casco virtual.",
    "Estou a tentar perceber porque é que o céu é azul no CSS.", "Não me piques, estou com o firewall em baixo!",
    "Estou a fazer um download de paciência, falta 99%.", "A vida de bot não é fácil, agora estou a descansar os ventiladores."
]

# --- FUNÇÕES DE API ---
def get_advice():
    try:
        r = requests.get("https://api.adviceslip.com/advice", timeout=5)
        return r.json()['slip']['advice']
    except: return "Leva a vida com calma e sê feliz."

# --- PROCESSADOR DE INTERAÇÃO ---
def handle_interaction(user, message, is_private, irc_socket):
    msg = message.lower()
    target = user if is_private else CHANNEL

    # 1. COMANDO !PRENDA
    if msg.startswith("!prenda"):
        parts = message.split()
        destinatario = parts[1] if len(parts) > 1 else user
        desenho = random.choice(PRENDAS)
        irc_socket.send(f"PRIVMSG {CHANNEL} :\x01ACTION oferece {desenho} a {destinatario} (mimo de {user})!\x01\r\n".encode())
        return True

    # 2. COMANDO !CONVITE (POSITIVO + CONFIRMAÇÃO SILENCIOSA EM PVT)
    if msg.startswith("!convite "):
        parts = message.split()
        if len(parts) > 1:
            destinatario = parts[1]
            frase = random.choice(CONVITE_FRASES).format(sender=user)
            # Envia o convite caloroso ao destinatário
            irc_socket.send(f"PRIVMSG {destinatario} :{frase}\r\n".encode())
            # Envia confirmação APENAS para quem pediu, em PVT (Query)
            irc_socket.send(f"PRIVMSG {user} :[INFO] O teu convite positivo para {destinatario} foi enviado! ✨\r\n".encode())
        return True

    # 3. COMANDO !COMANDOS
    if msg == "!comandos":
        cmds = [
            "--- 📜 MANUAL THEOG ---",
            "!prenda [nick]   -> Oferece um mimo ASCII no canal!",
            "!conselho        -> Uma dica para o teu dia (em PVT).",
            "!convite [nick]  -> Envia um convite especial e positivo para um amigo.",
            " ",
            "💡 Menciona 'TheOG' no canal para uma resposta minha!",
            "-----------------------"
        ]
        for c in cmds: 
            irc_socket.send(f"PRIVMSG {user} :{c}\r\n".encode())
            time.sleep(0.4)
        return True

    if msg.startswith("!conselho"):
        irc_socket.send(f"PRIVMSG {user} :[DICA] {get_advice()}\r\n".encode())
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
                    time.sleep(1)
                    entrada = random.choice(OG_ENTRANCE)
                    irc_conn.send(f"PRIVMSG {CHANNEL} :{entrada}\r\n".encode())

                if " JOIN " in line:
                    u = line.split('!')[0][1:]
                    if u.lower() not in BOT_FILTER and u.lower() != NICK.lower():
                        irc_conn.send(f"PRIVMSG {CHANNEL} :Boas-vindas {u}! Para saberes o que faço, digita !comandos.\r\n".encode())

                if "PRIVMSG" in line:
                    user_nick = line.split('!')[0][1:]
                    if user_nick.lower() in BOT_FILTER or user_nick.lower() == NICK.lower(): continue
                    content = line.split(" :", 1)[1].strip() if " :" in line else ""
                    handle_interaction(user_nick, content, f"PRIVMSG {NICK}" in line, irc_conn)
        except: time.sleep(20)

@app.route('/')
def home(): return "TheOG Online"

if __name__ == "__main__":
    threading.Thread(target=run_irc_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
