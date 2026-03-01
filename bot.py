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
    print(f"[{hora}] {user} {accao}")

# --- TEXTO DA HISTÓRIA ---
HISTORIA_THEOG = [
    "Saudações. Compreendo a génese deste refúgio.",
    "O IRC não é apenas um protocolo de comunicação para os que lá permanecem, é o último baluarte da palavra nua, onde a identidade se constrói no silêncio entre os caracteres.",
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

# --- LISTA EXPANDIDA DE PRENDAS (100+ OPÇÕES) ---
PRENDAS = [
    "---@>>-- (uma Rosa Vermelha)", "---{---(@ (uma Flor Silvestre)", "@->-- (um Botão de Rosa)", "---<@>--- (uma Margarida)",
    "  <3  (um Coração)", " <3 <3 (Dois Corações)", " ( <3 ) (um Abraço Apertado)", " [PRENDA] (uma Caixa Surpresa)",
    "---}---* (uma Flor do Campo)", "---@>-- (uma Tulipa)", "---E>-- (um Ramo)", " :-* (um Beijo)",
    " ( ^_^ ) (um Sorriso)", " ((_)) (um Abraço)", "---ooo--- (um Colar de Pérolas)", " ()-=-() (um Anel de Amizade)",
    " \o/ (um Grito de Alegria!)", "---[*]-- (uma Flor Mágica)", " O-- (um Pirulito)", " [_] (uma Chávena de Chá)",
    " ( ^^) _旦~~ (um Chá Verde)", " ( ^_^)っ☕ (um Café Quente)", " ( 🎁 ) (um Presente Especial)", " ♪♫🎶 (uma Serenata)",
    " [̲̅$̲̅(̲̅5̲̅)̲̅$̲̅] (uma Nota de Sorte)", " (╯°□°）╯🍪 (uma Bolacha)", " (づ｡◕‿‿◕｡)づ (um Mimo)", " <>< (um Peixinho da Sorte)",
    " ٩(◕‿◕)۶ (Energia Positiva)", " [🍀] (um Trevo de 4 Folhas)", " ☼ (um Raio de Sol)", " ☾ (um Luar)",
    "---@>>--", "---{---(@", "@->--", "---<@>---", " <3 ", " <3<3 ", " [LOVE] ", "---}---*",
    " [DOCE] ", " :-P ", " ( ^.^ ) ", " (( )) ", "---ooo---", " ()-=-() ", " \o/ ", "---[*]--",
    " [BOLO] ", " [SORVETE] ", " [ESTRELA] ", " [BALÃO] ", " [CHAVE] ", " [LIVRO] ", " [MÚSICA] ",
    "---@>>--", "---{---(@", "@->--", "---<@>---", " <3 ", " <3 <3 ", " ( <3 ) ", " [MIMO] ",
    "---}---*", "---@>--", "---E>--", " :-* ", " ( ^_^ ) ", " (( )) ", "---ooo---", " ()-=-() ",
    " \o/ ", "---[*]--", " O-- ", " [cafe] ", "---@>>--", "---{---(@", "@->--", "---<@>---",
    " <3 ", " <3<3 ", " ( <3 ) ", " [BJINHO] ", "---}---*", "---@>--", "---E>--", " :-P ",
    " ( ^.^ ) ", " ((_)) ", "---ooo---", " ()-=-() ", " \o/ ", "---[*]--", " O-- ", " [_] ",
    " [SOL] ", " [LUA] ", " [MAR] ", " [PAZ] ", " [LUZ] ", " [SORTE] ", " [FORÇA] ", " [UNIÃO] "
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
    "TheOG: Ativado, Carregado e Pronto.", "Entrei! Quem é que me paga uma imperial virtual?",
    "TheOG na área! Vamos fazer deste dia um grande dia.", "Voltei! Não vivam sem mim, eu sei."
]

# --- 20+ FRASES PARA O COMANDO !CONVITE (POSITIVO) ---
CONVITE_FRASES = [
    "Olá! O meu amigo {sender} enviou-me para te dizer que a tua presença no #TheOG faria o dia de todos muito mais brilhante. Aparece!",
    "Saudações! Sabias que o canal #TheOG ganha outra vida com pessoas positivas como tu? O {sender} convidou-te pessoalmente.",
    "Olá! Passo por aqui a pedido do {sender} para te deixar um sorriso e um convite: vem partilhar a tua boa vibe connosco no #TheOG!",
    "O {sender} acredita que o convívio é a alma da vida e convidou-te para o nosso cantinho no #TheOG. Serás bem-recebido!",
    "Olá! Trago uma mensagem especial do {sender}: no canal #TheOG celebramos a amizade e a alegria, e faltas tu para completar o grupo!",
    "Passo para te desejar um dia fantástico e dizer que o {sender} adorava ver-te pelo #TheOG hoje. Vem tomar um café virtual!",
    "Ei! O {sender} enviou-me para te dar um abraço digital e convidar-te para uma conversa relaxada no #TheOG. O teu brilho faz falta!",
    "Olá! Sabias que és uma pessoa inspiradora? O {sender} quer partilhar bons momentos contigo no #TheOG. Aparece!",
    "Mensagem prioritária do {sender}: A tua alegria é contagiante e o canal #TheOG precisa desse teu carisma hoje. Esperamos por ti!",
    "Olá! O {sender} diz que o dia fica 100% melhor quando estás por perto. Que tal uma visita ao canal #TheOG para animar a malta?"
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

# --- PROCESSADOR DE INTERAÇÃO ---
def handle_interaction(user, message, is_private, irc_socket):
    msg = message.lower()
    target = user if is_private else CHANNEL

    if msg == "!historia":
        for linha in HISTORIA_THEOG:
            irc_socket.send(f"PRIVMSG {user} :{linha}\r\n".encode())
            time.sleep(0.7)
        return True

    if msg.startswith("!prenda"):
        parts = message.split()
        destinatario = parts[1] if len(parts) > 1 else user
        desenho = random.choice(PRENDAS)
        irc_socket.send(f"PRIVMSG {CHANNEL} :\x01ACTION oferece {desenho} a {destinatario} (mimo de {user})!\x01\r\n".encode())
        return True

    if msg.startswith("!convite "):
        parts = message.split()
        if len(parts) > 1:
            dest = parts[1]
            frase = random.choice(CONVITE_FRASES).format(sender=user)
            irc_socket.send(f"PRIVMSG {dest} :{frase}\r\n".encode())
            irc_socket.send(f"PRIVMSG {user} :[INFO] Convite positivo enviado para {dest}! ✨\r\n".encode())
        return True

    if msg == "!comandos":
        cmds = [
            "--- 📜 MANUAL THEOG ---",
            "!prenda [nick]   -> Oferece um mimo ASCII no canal!",
            "!historia        -> A génese do TheOG (em PVT).",
            "!convite [nick]  -> Envia um convite especial e positivo.",
            " ",
            "💡 Menciona 'TheOG' para uma resposta evasiva!",
            "-----------------------"
        ]
        for c in cmds: 
            irc_socket.send(f"PRIVMSG {user} :{c}\r\n".encode())
            time.sleep(0.4)
        return True

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
                    irc_conn.send(f"PRIVMSG NickServ :IDENTIFY {PASS}\r\n".encode())
                    time.sleep(2)
                    irc.send(f"JOIN {CHANNEL}\r\n".encode())
                    time.sleep(1)
                    irc.send(f"PRIVMSG {CHANNEL} :{random.choice(OG_ENTRANCE)}\r\n".encode())

                if " JOIN " in line:
                    u = line.split('!')[0][1:]
                    if u.lower() != NICK.lower():
                        log_presenca(u, "ENTROU")
                        irc.send(f"PRIVMSG {CHANNEL} :Boas-vindas {u}! Digita !comandos para me conheceres.\r\n".encode())

                if " PART " in line or " QUIT " in line:
                    u = line.split('!')[0][1:]
                    if u.lower() != NICK.lower():
                        log_presenca(u, "SAIU")

                if "PRIVMSG" in line:
                    user_nick = line.split('!')[0][1:]
                    if user_nick.lower() in BOT_FILTER or user_nick.lower() == NICK.lower(): continue
                    content = line.split(" :", 1)[1].strip() if " :" in line else ""
                    handle_interaction(user_nick, content, f"PRIVMSG {NICK}" in line, irc)
        except: time.sleep(20)

@app.route('/')
def home(): return "TheOG Online"

if __name__ == "__main__":
    threading.Thread(target=run_irc_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
