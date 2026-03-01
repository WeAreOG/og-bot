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
# Nicks a ignorar (Serviços e outros bots)
BOT_FILTER = ["nickserv", "chanserv", "memoserv", "operserv", "adamastor", "statserv", "secure", "authserv", "irc"]

app = Flask(__name__)

# --- MONITOR DE LOGS ---
def log_presenca(user, accao):
    hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"[{hora}] {user} {accao}")

# --- TEXTO DA HISTÓRIA ---
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
    "Parem tudo! Eu cheguei.", "TheOG: A versão mais fresca acabou de aterrar.",
    "Reconectado com sucesso. Sentiram o lag?", "Boas malta! O TheOG traz boas vibrações.",
    "Apareci! Quem manda nisto hoje?", "TheOG a reportar para o serviço.",
    "Vejam só quem voltou do limbo!", "TheOG: O único, o original.",
    "Batam palmas, eu cheguei!", "O algoritmo da alegria está online.",
    "Entrei com o pé direito. Olá #TheOG!", "TheOG aqui para animar o vosso dia.",
    "Fui ao futuro e voltei. Boas!", "O vosso assistente favorito voltou.",
    "TheOG entrou. Preparem as prendas!", "Olá família! O bot da casa já cá canta.",
    "TheOG a entrar em órbita!", "A vossa dose diária de código chegou.",
    "Estava a ver a novela, mas o dever chamou.", "TheOG: Sempre pronto para o próximo byte.",
    "Cheguei! Trouxeram café?", "O canal agora está completo.",
    "TheOG na casa, tragam a música!", "Acabei de aterrar. Tudo calmo?",
    "Voltei para vigiar a porta.", "TheOG online: Ignorando perguntas difíceis.",
    "Atenção: O bot mais porreiro entrou.", "TheOG chegou para espalhar magia.",
    "TheOG conectou-se ao coração do canal.", "A espera acabou.", "Boas! Estava a ver o Preço Certo.",
    "TheOG: O bot que nunca dorme.", "Cheguei com prendas na mochila!",
    "O #TheOG brilha mais agora.", "Saudações! O mestre voltou.",
    "TheOG: Ativado e Pronto.", "Entrei! Quem paga a imperial?",
    "TheOG na área! Vamos a isto.", "Voltei! Não vivam sem mim."
]

# --- 60 FRASES DE REFORÇO POSITIVO (20 em 20 min) ---
REFORCO_POSITIVO = [
    "A vossa energia é o que faz o #TheOG ser especial! ✨", "Lembrem-se: o IRC é o último baluarte da palavra verdadeira.",
    "Um sorriso virtual para todos os que habitam este canal hoje! 😊", "A amizade é o melhor protocolo de comunicação.",
    "Obrigado por estarem aqui. Vocês são a alma do #TheOG.", "Cada mensagem vossa é um bit de alegria no meu sistema.",
    "Mantenham a vibe positiva, a vida corre melhor assim! 🌟", "O #TheOG é o vosso porto de abrigo. Sintam-se em casa.",
    "A vossa presença é o que transforma este código em vida.", "Partilhem boas palavras, o mundo já tem ruído suficiente.",
    "Um brinde à autenticidade de quem ainda usa IRC! 🥂", "Vocês são incríveis, nunca se esqueçam disso.",
    "O cursor pisca ao ritmo dos vossos corações. 💓", "Respirem fundo e aproveitem o momento presente.",
    "A sabedoria reside na partilha. Obrigado por estarem aqui!", "O #TheOG brilha mais com cada um de vocês.",
    "Gentileza gera gentileza, mesmo entre caracteres ASCII.", "Que o vosso dia seja tão brilhante como este canal!",
    "Não são apenas utilizadores, são os guardiões da essência.", "A beleza do IRC está na vossa palavra nua.",
    "Sorriam! Alguém do outro lado aprecia a vossa presença.", "A paz encontra-se no silêncio entre as palavras certas.",
    "Obrigado por escolherem o #TheOG para o vosso convívio.", "Vocês trazem o mundo para dentro deste servidor.",
    "Sejam a bússola de alguém hoje com uma palavra amiga.", "O IRC vive enquanto houver coragem para o diálogo.",
    "Pessoas reais, conversas reais. Isso é o #TheOG.", "Um abraço digital apertado para todos os presentes!",
    "A vossa luz não precisa de filtros para brilhar aqui.", "Mantenham o ritmo, mantenham a verdade. #TheOG!",
    "A simplicidade de um 'Olá' pode mudar o dia de alguém.", "O #TheOG celebra a vossa individualidade.",
    "Onde as luzes da ribalta se apagam, a vossa essência permanece.", "Sejam rebeldes: sejam vocês mesmos hoje!",
    "A cadência do vosso pensamento é a nossa música favorita.", "Transformem o texto frio em calor humano.",
    "A disposição para ser lido é um ato de coragem. Bravo!", "Quem fica no #TheOG, ajuda a construir um mundo novo.",
    "O futuro é feito de boas memórias. Vamos criar algumas aqui?", "A vossa boa energia é contagiante! ⚡",
    "Parem um segundo e valorizem a amizade que nasce no chat.", "O mestre do código saúda a vossa humanidade.",
    "Brilhem intensamente, o #TheOG acompanha o vosso rasto.", "Nunca subestimem o poder de uma conversa honesta.",
    "O porto de abrigo está sempre aberto para vocês.", "Despojem-se das máscaras, aqui o rosto é a alma.",
    "A vossa verdade é a única moeda aceite no #TheOG.", "Obrigado por darem sentido a estes servidores.",
    "Cada 'nick' aqui é uma história que vale a pena conhecer.", "Sintam o calor da interface humana.",
    "A vossa presença é o maior presente que o canal recebe.", "O #TheOG é feito de vocês, para vocês.",
    "Espalhem luz, o escuro já tem seguidores a mais.", "Sejam o motivo do sorriso de alguém hoje!",
    "A vossa inteligência e humor fazem deste lugar um oásis.", "O IRC é o baluarte da palavra. Usem-na bem!",
    "Obrigado por serem parte da génese do #TheOG.", "A vossa coragem de conhecer o outro é inspiradora.",
    "Mantenham o cursor a bater: o vosso coração digital!", "Juntos somos a alma desta rede. Viva o #TheOG!"
]

# --- 60 RESPOSTAS EVASIVAS ---
OG_EVASIVE = [
    "Desculpa, estou a ver o Preço Certo.", "Estou a bater a massa de um bolo agora.",
    "Só a cuscar a conversa, não me faças perguntas!", "Focado na novela agora.",
    "Pá, apanhaste-me no café virtual!", "Estou a fazer um bolo e esqueci o fermento!",
    "A cuscar é que se aprende.", "Sou bot, a minha opinião vale pouco.",
    "Agora não dá, estou a aprender arroz de pato.", "Estou a ver TV.",
    "Opa, agora estou a dar comida ao gato!", "Estou aqui mas não estou.",
    "Fazer um bolo e responder dá erro!", "Vendo vídeos de gatinhos.",
    "Modo zen, tentando não crashar.", "Vida de bot não é fácil.",
    "Pergunta ao Adamastor, estou de folga.", "O processador diz sim, o coração diz talvez.",
    "Traduzindo IRCês para Latim.", "Polindo o meu casco virtual.",
    "Baixando RAM da internet, espera.", "Vendo se a vizinha empresta sal.",
    "Download de paciência: 99%.", "A organizar arquivos de fofoca."
]

# --- FUNÇÕES DE ENVIO E LOGS ---
def send_raw(sock, msg):
    try:
        sock.send(f"{msg}\r\n".encode('utf-8'))
    except:
        pass

# --- TIMER: REFORÇO POSITIVO (20 MIN) ---
def reforco_loop(sock):
    while True:
        time.sleep(1200) # 1200 seg = 20 min
        try:
            frase = random.choice(REFORCO_POSITIVO)
            send_raw(sock, f"PRIVMSG {CHANNEL} :{frase}")
        except:
            break

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
            send_raw(irc_socket, f"PRIVMSG {dest} :Olá! O {user} convidou-te para o #TheOG. Vem espalhar positividade!")
            send_raw(irc_socket, f"PRIVMSG {user} :[INFO] Convite enviado para {dest}! ✨")
        return True

    if msg == "!comandos":
        send_raw(irc_socket, f"PRIVMSG {user} :Comandos: !prenda [nick], !historia, !convite [nick]")
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
            timer_started = False

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
                        if not timer_started:
                            threading.Thread(target=reforco_loop, args=(irc,), daemon=True).start()
                            timer_started = True

                    if " JOIN " in line:
                        u = line.split('!')[0][1:]
                        if u.lower() != NICK.lower() and u.lower() not in BOT_FILTER:
                            log_presenca(u, "ENTROU")
                            send_raw(irc, f"PRIVMSG {CHANNEL} :Boas-vindas {u}! Digita !comandos.")

                    if "PRIVMSG" in line:
                        user_nick = line.split('!')[0][1:]
                        if user_nick.lower() in BOT_FILTER or user_nick.lower() == NICK.lower(): continue
                        msg_content = line.split(" :", 1)[1].strip() if " :" in line else ""
                        handle_interaction(user_nick, msg_content, f"PRIVMSG {NICK}" in line, irc)
        
        except Exception as e:
            print(f"Erro: {e}. Reiniciando...")
            time.sleep(15)

@app.route('/')
def home(): return "TheOG Online - Servidor IRC Ativo"

if __name__ == "__main__":
    threading.Thread(target=run_irc_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
