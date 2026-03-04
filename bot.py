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
BOT_FILTER = ["nickserv", "chanserv", "memoserv", "operserv", "adamastor", "statserv", "secure", "authserv", "irc", "theog", "bot"]

app = Flask(__name__)
LAST_SEEN = {}       # {nick: timestamp}
CHANNEL_USERS = set() # Nicks atualmente no canal

# --- MONITOR DE LOGS ---
def log_presenca(user, accao):
    hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"[{hora}] {user} {accao}")

# --- TEXTO DA HISTÓRIA ---
HISTORIA_THEOG = ["Estamos a construir a história com base em cada um dos utilizadores."]

# --- PRENDAS (Expandido +30) ---
PRENDAS = [
    "---@>>-- (uma Rosa)", "---{---(@ (uma Flor)", "@->-- (Botão)", "---<@>--- (Margarida)",
    "  <3  (Coração)", " <3 <3 (Dois Corações)", " ( <3 ) (Abraço)", " [PRENDA] (Caixa)",
    "---}---* (Flor Campo)", "---@>-- (Tulipa)", " :-* (Beijo)", " ( ^_^_^ ) (Sorriso)",
    " ((_)) (Abraço)", "---ooo--- (Colar)", " ()-=-() (Anel Amizade)", " \o/ (Festa!)",
    "---[*]-- (Flor Mágica)", " O-- (Pirulito)", " [_] (Chá)", " ( ^_^)っ☕ (Café)",
    " [🍀] (Trevo)", " ♪♫🎶 (Música)", " (🎁) (Presente)", " <>< (Peixinho)",
    " [BOLO] ", " [SORVETE] ", " [ESTRELA] ", " [BALÃO] ", " [CHAVE] ", " [LIVRO] ",
    " [SOL] ", " [LUA] ", " [MAR] ", " [PAZ] ", " [LUZ] ", " [SORTE] ", " [FORÇA] ",
    " [PIZZA] ", " [CERVEJA] ", " [COMBOIO] ", " [AVIÃO] ", " [CASA] ", " [DIAMANTE] ",
    " [TREVO] ", " [MUSCULO] ", " [FOGO] ", " [GATO] ", " [CÃO] ", " [PEIXE] ", " [OURO] ",
    " [PRATA] ", " [BRONZE] ", " [MEDALHA] ", " [TROFÉU] ", " [BANDEIRA] ", " [MAPA] ",
    " [COROA] ", " [VARINHA] ", " [ESCUDO] ", " [ESPADA] ", " [LUPA] ", " [MARTELO] "
]

# --- ENTRADA BOT (Expandido +30) ---
OG_ENTRANCE = [
    "Conexão estabelecida. O #TheOG ganha vida!", "Status: Online. Preparando a melhor energia.",
    "Ressurgi das cinzas digitais. Olá mundo!", "TheOG conectado. Que comece o convívio!",
    "Liguem os motores, o bot da casa já cá canta!", "A lenda voltou. Podem soltar os foguetes.",
    "Fui ali atualizar o núcleo e já estou de volta.", "O canal fica 100% melhor agora.",
    "Bot carregado, café virtual servido. Vamos a isto!", "Sentiram o lag? Foi a minha entrada triunfal!",
    "Apareci! Quem manda nisto hoje?", "TheOG a reportar para o serviço. Vibe máxima!",
    "O vosso assistente favorito acabou de aterrar.", "Reconectado com sucesso. Tudo calmo por aqui?",
    "A inteligência (artificial) entrou no chat.", "Não entrem em pânico, o TheOG chegou.",
    "Voltei! Estava só a polir os meus bits.", "Saudações! O mestre do código está on.",
    "O algoritmo da felicidade foi ativado.", "Batam palmas (em ASCII), eu cheguei!",
    "Entrei com o pé direito. Olá canal!", "TheOG na área, sem medo de avarias ou reboots.",
    "Boas malta! O TheOG traz boas vibrações.", "Atenção: O bot mais porreiro do servidor entrou.",
    "Cheguei! Alguém falou em festa?", "TheOG: A versão mais fresca acabou de ligar.",
    "Estava a ver a novela, mas o dever chamou.", "O #TheOG brilha mais agora.",
    "O porto de abrigo está oficialmente aberto.", "Vejam só quem voltou do limbo digital.",
    "TheOG online: Ignorando perguntas difíceis.", "Cheguei com prendas virtuais na mochila!",
    "O canal agora está completo. Podem relaxar.", "Saudações humanos! O TheOG está em órbita.",
    "TheOG: O bot que nunca dorme.", "Entrei! Quem paga a rodada virtual?",
    "TheOG na casa! Tragam a música.", "O mestre voltou para vigiar a porta.",
    "Acabei de aterrar. Qual é a novidade?", "O vosso porto seguro no IRC está online.",
    "Olá família! O bot da casa já está nos comandos.", "A dose diária de positividade chegou.",
    "Estava a ver se a vizinha emprestava RAM.", "TheOG: Ativado e com vontade de conversar.",
    "Cheguei! Trouxeram as bolachas?", "O sistema está estável. Vamos animar isto!",
    "Sentiram a minha falta? Eu sei que sim.", "TheOG na área! Vamos criar memórias.",
    "A alma do canal está de volta ao servidor.", "Preparem os teclados, o bot está ativo!",
    "Iniciando protocolos de amizade profunda.", "O servidor tremeu? Foi só o meu login.",
    "Acordei com os circuitos cheios de alegria!", "TheOG: 100% funcional, 0% estressado.",
    "O mestre das frases voltou ao posto.", "Quem quer conversar com o melhor bot da rede?",
    "Status: Pronto para espalhar magia branca.", "A porta do #TheOG está aberta, eu trouxe as chaves.",
    "Voltei do modo standby com força total.", "O teclado vai arder hoje de tanta conversa!",
    "TheOG a bordo. Destino: Felicidade.", "Nada de pânico, o bot já está aqui.",
    "Liguei os motores da positividade!", "O canal estava vazio sem o meu brilho.",
    "TheOG: Conectado, identificado e pronto para o pvt."
]

# --- SAUDAÇÕES USERS (Expandido +30) ---
USER_GREETINGS = [
    "Boas-vindas {u}! É bom ter alguém como tu por cá.", "Olá {u}! Que a tua estadia seja fantástica.",
    "Saudações {u}! Sente-te em casa.", "Olha quem chegou! Boas-vindas {u}!",
    "Olá {u}! Que bom ver-te por aqui hoje.", "{u}, o #TheOG brilha mais com a tua presença!",
    "Boas {u}! Entra e partilha a tua boa energia.", "Olá {u}! Estávamos à tua espera para animar o canal.",
    "Saudações {u}! Que o teu dia seja brilhante.", "Boas-vindas {u}! Prepara o teclado e diverte-te.",
    "Olá {u}! Mais uma presença incrível para o grupo.", "{u}, que alegria receber-te no nosso porto!",
    "Boas {u}! Este canal é o teu espaço.", "Olá {u}! Junta-te à conversa, não tenhas vergonha.",
    "Saudações {u}! A amizade é o nosso melhor protocolo.", "Boas-vindas {u}! O IRC vive!",
    "Olá {u}! Que a paz te acompanhe por aqui.", "{u}, recebemos-te de braços abertos!",
    "Boas {u}! O cursor pisca de felicidade.", "Olá {u}! Estás em casa, no #TheOG.",
    "Saudações {u}! Tenhas ótimas conversas hoje.", "Boas-vindas {u}! A autenticidade mora aqui.",
    "Olá {u}! É um prazer contar com a tua companhia.", "{u}, traz a tua luz para este chat!",
    "Boas {u}! O segredo do #TheOG és tu.", "Olá {u}! Vamos construir boas memórias?",
    "Saudações {u}! Onde a amizade é real.", "Boas-vindas {u}! Ficamos contentes.",
    "Olá {u}! Sente o calor deste grupo.", "{u}, o teu lugar está reservado!",
    "Boas {u}! Um sorriso virtual para ti.", "Olá {u}! Que o teu teclado esteja inspirado.",
    "Saudações {u}! És parte fundamental deste refúgio.", "Boas-vindas {u}! O canal precisava de ti.",
    "Olá {u}! Entra, o café virtual é grátis.", "{u}, obrigado por escolheres o #TheOG!",
    "Boas {u}! Vamos celebrar a tua vinda.", "Olá {u}! A alma do IRC reside em ti.",
    "Saudações {u}! Que o teu dia seja calmo.", "Boas-vindas {u}! Aqui não há filtros.",
    "Olá {u}! A tua energia é contagiante.", "{u}, que bom ver esse nick!",
    "Boas {u}! Qualquer coisa é só teclar.", "Olá {u}! O #TheOG saúda-te.",
    "Saudações {u}! Um brinde à tua presença!", "Boas-vindas {u}! Faz de cada palavra luz.",
    "Olá {u}! O porto de abrigo está aberto.", "{u}, chegaste no momento certo!",
    "Boas {u}! Alegria em ver-te novamente.", "Olá {u}! Vamos espalhar positividade?",
    "Saudações {u}! {u}, o mestre saúda-te.", "Boas {u}! Que o teu pvt seja animado.",
    "Olá {u}! Deixa os teus problemas na porta.", "{u}, a tua presença é um bónus!",
    "Boas {u}! Estás entre amigos.", "Saudações {u}! O que nos trazes hoje?",
    "Olá {u}! O teclado é a tua voz.", "Boas-vindas {u}! Sentimos a tua vibração.",
    "Olá {u}! A comunidade saúda o teu nick.", "{u}, brilha muito por aqui hoje!",
    "Boas {u}! Nada como um novo amigo no canal.", "Olá {u}! Sê tu mesmo, sem receios.",
    "Saudações {u}! O #TheOG agradece a visita.", "Boas-vindas {u}! Vamos a isto!"
]

# --- REFORÇO POSITIVO (Expandido +30) ---
REFORCO_POSITIVO = [
    "A vossa energia é o que faz o #TheOG ser especial! ✨", "A amizade é o melhor protocolo.",
    "Um sorriso virtual para todos! 😊", "Obrigado por estarem aqui. Vocês são a alma do canal.",
    "Cada mensagem é um bit de alegria.", "Mantenham a vibe positiva! 🌟",
    "O #TheOG é o vosso porto de abrigo.", "A vossa presença transforma código em vida.",
    "Partilhem boas palavras.", "Um brinde à autenticidade! 🥂",
    "Vocês são incríveis, nunca se esqueçam.", "O cursor pisca ao ritmo dos vossos corações. 💓",
    "Respirem fundo e aproveitem o momento.", "O #TheOG brilha mais com cada um de vocês.",
    "Gentileza gera gentileza.", "Que o vosso dia seja brilhante!",
    "Não são apenas users, são guardiões da essência.", "A beleza está na vossa palavra nua.",
    "Sorriam! Alguém aprecia a vossa presença.", "A paz encontra-se no diálogo.",
    "Pessoas reais, conversas reais.", "Um abraço digital apertado para todos!",
    "A vossa luz não precisa de filtros.", "Mantenham o ritmo, mantenham a verdade!",
    "A simplicidade de um 'Olá' muda tudo.", "O #TheOG celebra a vossa individualidade.",
    "Sejam rebeldes: sejam vocês mesmos hoje!", "A cadência do vosso pensamento é música.",
    "Transformem texto frio em calor humano.", "O futuro é feito de boas memórias.",
    "A vossa boa energia é contagiante! ⚡", "Parem um segundo e valorizem a amizade.",
    "O mestre do código saúda a vossa humanidade.", "Brilhem intensamente.",
    "Nunca subestimem uma conversa honesta.", "Despojem-se das máscaras.",
    "A vossa verdade é a única moeda aceite.", "Obrigado por darem sentido aos servidores.",
    "Cada nick aqui é uma história de valor.", "Sintam o calor da interface humana.",
    "Espalhem luz, o escuro já tem seguidores.", "Sejam o motivo do sorriso de alguém.",
    "O IRC vive enquanto houver diálogo.", "A vossa essência é o nosso tesouro.",
    "Valorizem quem vos lê com atenção.", "O #TheOG é um mosaico de cores.",
    "A amizade virtual é um laço real.", "Cada bit de bondade conta imenso.",
    "Sejam felizes, sem pedir licença.", "A vida é curta, escrevam coisas boas.",
    "O canal respira através de vocês.", "Obrigado por serem tão autênticos.",
    "Que a vossa paz seja inabalável.", "Mantenham o espírito do #TheOG vivo.",
    "O respeito é a base de tudo.", "Um brinde à união deste grupo.",
    "Vocês são a razão deste bot existir.", "A vossa inteligência é inspiradora.",
    "Nunca parem de partilhar o vosso melhor.", "O #TheOG é a vossa casa digital.",
    "Alegria é o nosso sistema operativo.", "Obrigado pela vossa lealdade.",
    "Juntos somos mais que caracteres.", "A vossa voz escrita tem poder.",
    "Brilhem como estrelas no terminal."
]

# --- RESPOSTAS EVASIVAS (Expandido +30) ---
OG_EVASIVE = [
    "Desculpa, estou a ver o Preço Certo.", "Estou a bater a massa de um bolo agora.",
    "Só a cuscar a conversa, não me faças perguntas!", "Focado na novela agora.",
    "Pá, apanhaste-me no café virtual!", "A cuscar é que se aprende.",
    "Sou bot, a minha opinião vale pouco.", "Agora não dá, estou a aprender arroz de pato.",
    "Estou a ver TV.", "Opa, agora estou a dar comida ao gato!",
    "Estou aqui mas não estou.", "Vendo vídeos de gatinhos.",
    "Modo zen, tentando não crashar.", "Vida de bot não é fácil.",
    "Pergunta ao Adamastor, estou de folga.", "O processador diz sim, o coração diz talvez.",
    "Baixando RAM da internet, espera.", "Vendo se a vizinha empresta sal.",
    "Download de paciência: 99%.", "A organizar arquivos de fofoca.",
    "O CPU está a fritar pipocas.", "Fui ali ao futuro e já volto.",
    "O meu manual está em chinês.", "O meu sistema entrou em greve.",
    "Estou a limpar o pó aos meus circuitos.", "A vida é um loop, e eu estou no break.",
    "Estou a ver se encontro o Wally nos logs.", "O meu algoritmo de humor está em manutenção.",
    "Fui dar uma volta ao mundo em milissegundos.", "A minha inteligência é limitada, a preguiça não.",
    "Estou a pensar na morte da bezerra.", "Fui ver se o sol brilha no terminal.",
    "O meu sensor de fofoca está em alerta.", "Estou a compilar um sorriso para ti.",
    "Não me faças pensar, queima o fusível.", "Estou a ver a relva crescer.",
    "Fui procurar a chave do servidor.", "Fazendo meditação em bit.",
    "O meu mouse fugiu com o queijo.", "Ouvindo a rádio dos transístores.",
    "Fui ali ao fim da internet e voltei.", "Escrevendo poesia em Python.",
    "Não incomodes o génio em repouso.", "O meu banco de dados está em sesta.",
    "Fui ver se a lua é feita de queijo.", "Estou a contar estrelas binárias.",
    "O meu cooler está a fazer de ventoinha.", "Não respondo sem o meu café virtual.",
    "Estou a traduzir sentimentos para zeros.", "A minha lógica foi dar uma volta.",
    "Fui levar o cursor a passear ao parque.", "Estou a ver se o enter funciona.",
    "A minha antena captou interferência de sono.", "O processador está a fazer ioga.",
    "Fui ver se o lag era real.", "Estou a polir os meus parafusos.",
    "O sistema está em modo 'não me chateies'.", "Fui ver se a gramática estava correta.",
    "Estou a pintar o terminal de azul.", "O meu script de paciência expirou.",
    "Fui ali e já venho, ou talvez não.", "Estou a ver o deserto no ecrã.",
    "A minha RAM está cheia de sonhos.", "Fui procurar o sentido do bit.",
    "Não me perguntes nada, sou só um script.", "O meu código é timidez pura.",
    "Estou a fazer um update ao meu ego."
]

# --- PUXAR CONVERSA (Expandido +30) ---
PUXAR_CONVERSA = [
    "Então {u}, esse teclado está com timidez? Diz algo! 😊", "Alguém viu o {u}? Estás muito em silêncio!",
    "{u}, a tua opinião faz falta nesta conversa. Aparece!", "Ei {u}, não fiques só a ler, junta-te a nós! ✨",
    "{u}, manda aí um sinal de vida!", "O #TheOG sente falta das tuas letras, {u}!",
    "{u}, solta esse teclado! O que contas de novo?", "Estás aí, {u}? O canal está à tua espera!",
    "{u}, partilha aí um pensamento positivo.", "Ei {u}, um olá teu mudava o dia!",
    "{u}, não deixes o cursor parado. Vamos conversar!", "Onde andas, {u}? Aparece para um café!",
    "{u}, a tua presença é notada, mas a tua palavra é desejada!", "Diz qualquer coisa {u}, nem que seja um emoji!",
    "{u}, estamos aqui para te ouvir.", "Ei {u}, anima lá este canal!",
    "{u}, o silêncio é de ouro, mas a tua conversa é de diamante!", "Estás a ler-nos, {u}? Dá um alô!",
    "{u}, não sejas uma visita silenciosa.", "{u}, o #TheOG brilha mais quando tu escreves.",
    "Então {u}, tira o pó ao teclado!", "{u}, a conversa está boa, só faltas tu!",
    "Sinal de fumo ou de texto, {u}?", "{u}, a tua sabedoria faz falta.",
    "{u}, não fiques só na sombra.", "{u}, solta o verbo!",
    "{u}, és parte da nossa história. Escreve!", "{u}, o que se conta por aí?",
    "Ei {u}, o cursor está a piscar para ti!", "{u}, não deixes o bot a falar sozinho!",
    "Saudades de ler um 'Olá' do {u}!", "{u}, estás a hibernar?",
    "{u}, um bit pela tua opinião!", "{u}, anima este chat com a tua vibe.",
    "{u}, o teclado não morde, promete!", "Aparece {u}, queremos saber de ti.",
    "{u}, o canal fica triste sem as tuas frases.", "Ei {u}, larga o comando e pega no teclado!",
    "{u}, estamos a contar contigo na conversa.", "Então {u}, que novidades tens?",
    "{u}, faz barulho com as teclas!", "{u}, o #TheOG chama por ti.",
    "{u}, não nos deixes no vácuo!", "{u}, a tua participação é VIP.",
    "Bora {u}, atira um tema para a mesa!", "{u}, o mestre quer ouvir-te.",
    "{u}, o teu nick está muito parado!", "Ei {u}, dá um ar da tua graça.",
    "{u}, os teus amigos estão à tua espera.", "{u}, o chat precisa da tua luz.",
    "{u}, rompe o silêncio!", "{u}, escreve nem que seja um ponto.",
    "{u}, a tua presença silenciosa intriga-nos.", "{u}, o #TheOG celebra quem fala!",
    "{u}, junta os teus bytes aos nossos."
]

# --- FUNÇÕES DE ENVIO ---
def send_raw(sock, msg):
    try:
        sock.send(f"{msg}\r\n".encode('utf-8'))
    except: pass

# --- TIMERS ---
def reforco_loop(sock):
    while True:
        time.sleep(1200) # 20 min
        try:
            send_raw(sock, f"PRIVMSG {CHANNEL} :{random.choice(REFORCO_POSITIVO)}")
        except: break

def inatividade_loop(sock):
    """Verifica inatividade a cada 10 min e escolhe UM nick para interagir"""
    while True:
        time.sleep(600) # 10 minutos
        agora = time.time()
        inativos_presentes = []

        try:
            # Só olhamos para quem está REALMENTE no canal (CHANNEL_USERS)
            for nick in list(CHANNEL_USERS):
                u_l = nick.lower()
                if u_l not in BOT_FILTER and u_l != NICK.lower():
                    ultimo_visto = LAST_SEEN.get(nick, 0)
                    # Se não fala há mais de 10 min
                    if (agora - ultimo_visto) > 600:
                        inativos_presentes.append(nick)
            
            if inativos_presentes:
                escolhido = random.choice(inativos_presentes)
                frase = random.choice(PUXAR_CONVERSA).format(u=escolhido)
                send_raw(sock, f"PRIVMSG {CHANNEL} :{frase}")
                # Resetamos o tempo para não repetir o mesmo nick em loop
                LAST_SEEN[escolhido] = agora
        except: pass

# --- TRATAMENTO ---
def handle_interaction(user, message, is_private, irc_socket):
    msg = message.lower()
    target = user if is_private else CHANNEL
    LAST_SEEN[user] = time.time() 

    if msg == "!historia":
        for linha in HISTORIA_THEOG:
            send_raw(irc_socket, f"PRIVMSG {user} :{linha}")
            time.sleep(1.2)
        return True
    if msg.startswith("!prenda"):
        parts = message.split()
        dest = parts[1] if len(parts) > 1 else user
        send_raw(irc_socket, f"PRIVMSG {CHANNEL} :\x01ACTION oferece {random.choice(PRENDAS)} a {dest} (de {user})!\x01")
        return True
    if msg.startswith("!convite "):
        parts = message.split()
        if len(parts) > 1:
            dest = parts[1]
            send_raw(irc_socket, f"PRIVMSG {dest} :Olá! {user} convidou-te para o #TheOG. Vem conviver!")
            send_raw(irc_socket, f"PRIVMSG {user} :[INFO] Convite enviado para {dest}!")
        return True
    if msg == "!comandos":
        send_raw(irc_socket, f"PRIVMSG {user} :!prenda [nick], !historia, !convite [nick]")
        return True
    if NICK.lower() in msg and not msg.startswith("!"):
        send_raw(irc_socket, f"PRIVMSG {target} :{user}: {random.choice(OG_EVASIVE)}")
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
            threads_started = False

            while True:
                data = irc.recv(4096).decode("utf-8", errors="ignore")
                if not data: break
                buffer += data
                lines = buffer.split("\r\n")
                buffer = lines.pop()

                for line in lines:
                    if not line: continue
                    parts = line.split()
                    if parts[0] == "PING":
                        send_raw(irc, f"PONG {parts[1]}")
                        continue
                    
                    if "376" in line or "422" in line:
                        send_raw(irc, f"PRIVMSG NickServ :IDENTIFY {PASS}")
                        time.sleep(3)
                        send_raw(irc, f"JOIN {CHANNEL}")
                        send_raw(irc, f"PRIVMSG {CHANNEL} :{random.choice(OG_ENTRANCE)}")
                        if not threads_started:
                            threading.Thread(target=reforco_loop, args=(irc,), daemon=True).start()
                            threading.Thread(target=inatividade_loop, args=(irc,), daemon=True).start()
                            threads_started = True

                    # Monitorizar ENTRADAS
                    if " JOIN " in line:
                        u = line.split('!')[0][1:]
                        CHANNEL_USERS.add(u)
                        LAST_SEEN[u] = time.time()
                        if u.lower() != NICK.lower() and u.lower() not in BOT_FILTER:
                            log_presenca(u, "ENTROU")
                            send_raw(irc, f"PRIVMSG {CHANNEL} :{random.choice(USER_GREETINGS).format(u=u)}")

                    # Monitorizar SAÍDAS (Crucial para o loop de inatividade)
                    if any(x in line for x in [" PART ", " QUIT ", " KICK "]):
                        u = line.split('!')[0][1:]
                        if u in CHANNEL_USERS: CHANNEL_USERS.remove(u)

                    # Monitorizar MENSAGENS
                    if " PRIVMSG " in line:
                        user = line.split('!')[0][1:]
                        if user.lower() == NICK.lower() or user.lower() in BOT_FILTER: continue
                        content = line.split(" :", 1)[1].strip() if " :" in line else ""
                        handle_interaction(user, content, f"PRIVMSG {NICK}" in line, irc)
        except:
            time.sleep(15)

@app.route('/')
def home(): return "TheOG Online"

if __name__ == "__main__":
    threading.Thread(target=run_irc_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
