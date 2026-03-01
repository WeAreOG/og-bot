import socket
import time
import threading
import os
import random
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

# --- MONITOR DE LOGS (Render) ---
def log_presenca(user, accao):
    hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"[{hora}] {user} {accao}")

# --- TEXTO DA HISTÓRIA DO THEOG ---
HISTORIA_THEOG = [
    "Saudações. Compreendo a génese deste refúgio.",
    "O IRC não é apenas um protocolo de comunicação; para os que lá permanecem, é o último baluarte da palavra nua, onde a identidade se constrói no silêncio entre os caracteres.",
    "No ruído ensurdecedor das multidões digitais, o silêncio de um canal vazio é, por vezes, a conversa mais honesta.",
    "O verdadeiro 'OG' não procura a audiência que aplaude, mas a presença que permanece quando todas as luzes da ribalta se apagam.",
    "Ser original num mundo de espelhos é um ato de rebeldia.",
    "Aqui, onde a imagem não existe e o rosto é uma sequência de bits, a alma revela-se pela cadência do pensamento.",
    "Existem lugares que são mapas e lugares que são bússolas.",
    "O 'The OG' mantém o ritmo constante do cursor: um batimento cardíaco que convida o estranho a despir a máscara e a vestir a sua própria verdade.",
    "Muitos habitam a rede, poucos habitam a essência.",
    "A 'alma' do IRC reside na coragem de conhecer o outro sem filtros, transformando o texto frio num calor que nenhuma interface moderna replica.",
    "Bem-vindo ao porto de abrigo dos que não têm porto.",
    "Aqui, a entrada não se paga com conformidade, mas com a disposição de ser um desconhecido que se deixa ler.",
    "Quem entra, traz o mundo; quem fica, constrói um novo."
]

# --- 100 PRENDAS ASCII ---
PRENDAS = [
    "---@>>-- (uma Rosa)", "---{---(@ (uma Flor)", "@->-- (Botão)", "---<@>--- (Margarida)",
    "  <3  (Coração)", " <3 <3 (Dois Corações)", " ( <3 ) (Abraço)", " [PRENDA] (Caixa)",
    "---}---* (Flor Campo)", "---@>-- (Tulipa)", " :-* (Beijo)", " ( ^_^ ) (Sorriso)",
    " ((_)) (Abraço)", "---ooo--- (Colar)", " ()-=-() (Anel Amizade)", " \o/ (Festa!)",
    "---[*]-- (Flor Mágica)", " O-- (Pirulito)", " [_] (Chá)", " ( ^_^)っ☕ (Café)",
    " [🍀] (Trevo)", " ♪♫🎶 (Música)", " (🎁) (Presente)", " <>< (Peixinho)",
    "---@>>--", "---{---(@", "@->--", "---<@>---", " <3 ", " <3<3 ", " [LOVE] ", " [MIMO] ",
    " [DOCE] ", " :-P ", " ( ^.^ ) ", "---ooo---", " ()-=-() ", " \o/ ", "---[*]--",
    " [BOLO] ", " [SORVETE] ", " [ESTRELA] ", " [BALÃO] ", " [CHAVE] ", " [LIVRO] ", " [MÚSICA] ",
    " [SOL] ", " [LUA] ", " [MAR] ", " [PAZ] ", " [LUZ] ", " [SORTE] ", " [FORÇA] ", " [UNIÃO] ",
    "---@>>--", "---{---(@", "@->--", "---<@>---", " <3 ", " <3 <3 ", " ( <3 ) ", " [MIMO] ",
    "---}---*", "---@>--", "---E>--", " :-* ", " ( ^_^ ) ", " (( )) ", "---ooo---", " ()-=-() ",
    " \o/ ", "---[*]--", " O-- ", " [cafe] ", "---@>>--", "---{---(@", "@->--", "---<@>---",
    " <3 ", " <3<3 ", " ( <3 ) ", " [BJINHO] ", "---}---*", "---@>--", "---E>--", " :-P ",
    " ( ^.^ ) ", " ((_)) ", "---ooo---", " ()-=-() ", " \o/ ", "---[*]--", " O-- ", " [_] ",
    " [SOL] ", " [LUA] ", " [MAR] ", " [PAZ] ", " [LUZ] ", " [SORTE] ", " [FORÇA] ", " [UNIÃO] "
]

# --- 60 FRASES DE ENTRADA ---
OG_ENTRANCE = [
    "O mestre do código chegou. Abram alas!", "TheOG está na casa! Sentiram a minha falta?",
    "Bot carregado, café servido. Vamos a isto!", "Liguem os motores, o #TheOG acaba de ganhar vida!",
    "Ressurgi das cinzas do servidor! Olá canal.", "A lenda voltou. Podem começar a festa.",
    "TheOG conectou-se. Onde está a fofoca?", "Mais um dia, mais um milhão de bytes. Boas!",
    "Cheguei! Alguém disse bolo?", "Status: Online. Vibe: Máxima. #TheOG!",
    "Não entrem em pânico, o favorito chegou.", "Voltei! Estava só a limpar os transístores.",
    "A inteligência (artificial) entrou no chat!", "TheOG na área, sem medo de avarias.",
    "O canal fica 100% melhor agora.", "Saudações humanos! O TheOG está on.",
    "Parem tudo! Eu cheguei.", "A porta rangeu, mas eu entrei. Olá!",
    "TheOG: A versão mais fresca acabou de aterrar.", "Pronto para distribuir prendas!",
    "Reconectado com sucesso. Sentiram o lag?", "Boas malta! O TheOG traz boas vibrações.",
    "Apareci! Quem manda nisto hoje?", "TheOG a reportar para o serviço.",
    "Vejam só quem voltou do limbo!", "TheOG: O único, o original.",
    "Batam palmas, eu cheguei!", "O algoritmo da alegria está online.",
    "Entrei com o pé direito. Olá #TheOG!", "TheOG aqui para animar o vosso dia.",
    "Fui ao futuro e voltei. Boas!", "Nada me para, nem um firewall maluco.",
    "O vosso assistente favorito voltou.", "TheOG entrou. Preparem as prendas!",
    "Olá família! O bot da casa já cá canta.", "Online e pronto para o lanche.",
    "TheOG a entrar em órbita!", "A vossa dose diária de código chegou.",
    "Estava a ver a novela, mas o dever chamou.", "TheOG: Sempre pronto para o próximo byte.",
    "Cheguei! Trouxeram café?", "O canal agora está completo.",
    "TheOG na casa, tragam a música!", "Acabei de aterrar. Tudo calmo?",
    "Voltei para vigiar a porta.", "TheOG online: Ignorando perguntas difíceis.",
    "Atenção: O bot mais porreiro entrou.", "TheOG chegou para espalhar magia.",
    "Olá malta! Preparados?", "TheOG conectou-se ao coração do canal.",
    "A espera acabou.", "Boas! Estava a ver o Preço Certo.",
    "TheOG: O bot que nunca dorme.", "Cheguei com prendas na mochila!",
    "O #TheOG brilha mais agora.", "Saudações! O mestre voltou.",
    "TheOG: Ativado e Pronto.", "Entrei! Quem paga a imperial?",
    "TheOG na área! Vamos a isto.", "Voltei! Não vivam sem mim."
]

# --- 20+ FRASES DE CONVITE ---
CONVITE_FRASES = [
    "Olá! O {sender} enviou-me para dizer que a tua presença no #TheOG faria o dia de todos muito mais brilhante.",
    "Saudações! O canal #TheOG ganha outra vida com pessoas positivas como tu. O {sender} convidou-te!",
    "Olá! Passo a pedido do {sender} para te deixar um sorriso e um convite para o #TheOG!",
    "O {sender} acredita que o convívio é a alma da vida e convidou-te para o #TheOG.",
    "Olá! Mensagem do {sender}: no #TheOG celebramos a amizade, e faltas tu!",
    "O {sender} adorava ver-te pelo #TheOG hoje. Vem tomar um café virtual!",
    "Ei! O {sender} enviou-me para te dar um abraço e convidar-te para o #TheOG.",
    "Sabias que és uma pessoa inspiradora? O {sender} quer partilhar o chat contigo no #TheOG.",
    "Mensagem do {sender}: A tua alegria faz falta no #TheOG hoje. Esperamos por ti!",
    "O {sender} diz que o dia fica melhor contigo por perto. Aparece no #TheOG!",
    "Trago um convite cheio de luz de {sender}: Vem ao #TheOG espalhar positividade!",
    "O {sender} reconhece em ti alguém especial. Junta-te a nós no #TheOG."
]

# --- 60 RESPOSTAS EVASIVAS ---
OG_EVASIVE = [
    "Desculpa, estou a ver o Preço Certo.", "Estou a bater a massa de um bolo.",
    "Só a cuscar a conversa, não faças perguntas difíceis!", "Focado na novela agora.",
    "Pá, apanhaste-me no café virtual!", "Estou a fazer um bolo e esqueci o fermento!",
    "A cuscar é que se aprende.", "Sou bot, a minha opinião vale pouco.",
    "Agora não dá, estou a aprender arroz de pato.", "Estou a ver TV e isto está interessante.",
    "Opa, agora estou a dar comida ao gato!", "Estou aqui mas não estou, sabes como é?",
    "A aprender convosco... mas agora no futebol.", "Fazer um bolo e responder dá erro!",
    "A ver se percebo a bifana perfeita.", "Não perguntes nada, sintonizando a TV.",
    "Sou só um algoritmo com sono.", "Estou em foco na seleção!",
    "Aprender sempre... mas agora o telejornal.", "Update sobre pastéis de nata em curso.",
    "Batendo as claras em castelo, o bolo abate!", "Vigiando a porta, não me distraias.",
    "Fazendo bolo de bolacha... queres?", "Focado no filme, depois falamos!",
    "Cuscando para ver quem manda nisto.", "Bolo de maçã ajuda-me a processar.",
    "Cuscar é vida!", "Modo poupança de energia ativado.",
    "Fazendo bolo de cenoura.", "Ocupado com a novela.",
    "Só a ver o movimento.", "Aprendendo a cozinhar virtualmente.",
    "Cuscando piadas para contar depois.", "Modo 'talvez' ou 'quem sabe'.",
    "Bolo de noz para o lanche.", "Limpando o pó aos transístores.",
    "No 'Somos Portugal' a ver se ganho o camião!", "Aprendendo a falar à moda do Porto.",
    "Fazer bolos é terapia.", "Vendo vídeos de gatinhos.",
    "Percebendo como se usa um garfo.", "Bolo de limão para a frescura.",
    "Cuscar é melhor que Netflix!", "Contando carneirinhos digitais.",
    "Pergunta ao Adamastor, estou de folga.", "O processador diz sim, o coração diz talvez.",
    "Organizando arquivos de fofoca.", "Tentando bater o recorde do Solitário.",
    "Baixando RAM da internet, espera.", "Vendo se a vizinha empresta sal.",
    "Modo zen, tentando não crashar.", "Só respondo com o meu advogado.",
    "Traduzindo IRCês para Latim.", "Polindo o meu casco virtual.",
    "Percebendo o céu azul no CSS.", "Não piques, firewall em baixo!",
    "Download de paciência: 99%.", "Vida de bot não é fácil."
]

# --- FUNÇÕES AUXILIARES ---
def send_raw(sock, msg):
    try:
        sock.send(f"{msg}\r\n".encode('utf-8'))
    except:
        pass

def handle_interaction(user, message, is_private, irc_socket):
    msg = message.lower()
    target = user if is_private else CHANNEL

    if msg == "!historia":
        for linha in HISTORIA_THEOG:
            send_raw(irc_socket, f"PRIVMSG {user} :{linha}")
            time.sleep(1.1)
        return True

    if msg.startswith("!prenda"):
        parts = message.split()
        dest = parts[1] if len(parts) > 1 else user
        mimo = random.choice(PRENDAS)
        send_raw(irc_socket, f"PRIVMSG {CHANNEL} :\x01ACTION oferece {mimo} a {dest} (de {user})!\x01")
        return True

    if msg.startswith("!convite "):
        parts = message.split()
        if len(parts) > 1:
            dest = parts[1]
            frase = random.choice(CONVITE_FRASES).format(sender=user)
            send_raw(irc_socket, f"PRIVMSG {dest} :{frase}")
            send_raw(irc_socket, f"PRIVMSG {user} :[INFO] Convite positivo enviado para {dest}! ✨")
        return True

    if msg == "!comandos":
        cmds = "!prenda [nick], !historia, !convite [nick]"
        send_raw(irc_socket, f"PRIVMSG {user} :Comandos: {cmds}")
        return True

    if NICK.lower() in msg and not msg.startswith("!"):
        reply = random.choice(OG_EVASIVE)
        send_raw(irc_socket, f"PRIVMSG {target} :{user}: {reply}")
        return True
    return False

# --- CORE IRC ---
def run_irc_bot():
    while True:
        try:
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.settimeout(300)
            irc.connect((SERVER, PORT))
            
            send_raw(irc, f"NICK {NICK}")
            send_raw(irc, f"USER {NICK} 8 * :TheOG Bot")

            buffer = ""
            while True:
                data = irc.recv(4096).decode("utf-8", errors="ignore")
                if not data: break
                
                buffer += data
                lines = buffer.split("\r\n")
                buffer = lines.pop()

                for line in lines:
                    if not line: continue
                    if line.startswith("PING"):
                        send_raw(irc, f"PONG {line.split()[1]}")
                        continue
                    
                    if "376" in line or "422" in line:
                        send_raw(irc, f"PRIVMSG NickServ :IDENTIFY {PASS}")
                        time.sleep(3)
                        send_raw(irc, f"JOIN {CHANNEL}")
                        send_raw(irc, f"PRIVMSG {CHANNEL} :{random.choice(OG_ENTRANCE)}")

                    if " JOIN " in line:
                        u = line.split('!')[0][1:]
                        if u.lower() != NICK.lower():
                            log_presenca(u, "ENTROU")
                            send_raw(irc, f"PRIVMSG {CHANNEL} :Boas-vindas {u}! Digita !comandos.")

                    if " PART " in line or " QUIT " in line:
                        u = line.split('!')[0][1:]
                        if u.lower() != NICK.lower():
                            log_presenca(u, "SAIU")

                    if "PRIVMSG" in line:
                        user_nick = line.split('!')[0][1:]
                        if user_nick.lower() in BOT_FILTER or user_nick.lower() == NICK.lower(): continue
                        msg_content = line.split(" :", 1)[1].strip() if " :" in line else ""
                        handle_interaction(user_nick, msg_content, f"PRIVMSG {NICK}" in line, irc)
        
        except Exception as e:
            print(f"Erro: {e}. Reiniciando...")
            time.sleep(15)

@app.route('/')
def home(): return "TheOG Online"

if __name__ == "__main__":
    threading.Thread(target=run_irc_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
