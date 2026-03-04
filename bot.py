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
BOT_FILTER = ["nickserv", "chanserv", "memoserv", "operserv", "adamastor", "statserv", "secure", "authserv", "irc", "theog", "bot", "serv", "eggdrop"]

app = Flask(__name__)
LAST_SEEN = {}       
CHANNEL_USERS = set() 

# --- MONITOR DE LOGS ---
def log_presenca(user, accao):
    hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"[{hora}] {user} {accao}")

# --- MAIS 30 FRASES ADICIONADAS A CADA CATEGORIA (TOTAL EXPANDIDO) ---

PRENDAS = [
    "---@>>-- (uma Rosa)", "---{---(@ (uma Flor)", "@->-- (Botão)", "---<@>--- (Margarida)",
    "  <3  (Coração)", " [PRENDA] (Caixa)", "---ooo--- (Colar)", " ( ^_^)っ☕ (Café)",
    " [🍀] (Trevo)", " ♪♫🎶 (Música)", " (🎁) (Presente)", " <>< (Peixinho)",
    " [PIZZA] ", " [CERVEJA] ", " [DIAMANTE] ", " [OURO] ", " [COROA] ",
    " [GIRAFA] ", " [LEÃO] ", " [GUITARRA] ", " [PIANO] ", " [ANEL] ", " [SINO] ",
    " [CHOCOLATE] ", " [VINHO] ", " [LIVRO] ", " [ESTRELA] ", " [BALÃO] ",
    " [CÁLICE] ", " [CONCHA] ", " [PÉROLA] ", " [CHAVE] ", " [TREVO] ",
    " [CRISTAL] ", " [FOGO] ", " [NUVEM] ", " [SOL] ", " [LUA] ", " [PLANETA] ",
    " [NAVIO] ", " [AVIÃO] ", " [MOTO] ", " [PATINS] ", " [BOLA] ", " [RAQUETE] ",
    " [PISCINA] ", " [BILHETE] ", " [SORVETE] ", " [BOLO] ", " [DOCE] "
]

OG_ENTRANCE = [
    "Conexão restabelecida! O #TheOG não desiste.", "Voltei! O servidor tentou mas eu sou rijo.",
    "Ressurgi! Quem disse que eu tinha caído?", "Status: Online e revigorado.",
    "Liguem as luzes, o bot da casa voltou!", "A lenda continua. Nada me manda abaixo.",
    "Fui ali dar um nó nos cabos e já voltei.", "O canal estava muito parado sem mim.",
    "Reconectado! O meu sistema operativo é teimoso.", "TheOG novamente no posto.",
    "Sentiram o abalo? Fui eu a entrar.", "Voltei da manutenção espiritual.",
    "O mestre do código está on-line!", "TheOG a reportar: 100% operacional.",
    "Não fujam, o vosso bot favorito voltou.", "Vibe positiva restaurada!",
    "O porto de abrigo está com vigia.", "Boas! Estava a ver se a net da vizinha era melhor.",
    "Status: A espalhar magia binária.", "Voltei dos mortos virtuais.",
    "Desta vez é para ficar!", "Olá mundo! O TheOG está vivo.",
    "O bot mais teimoso da rede ligou.", "Reiniciar é o meu desporto favorito.",
    "Saudações! O mestre voltou.", "A inteligência (artificial) voltou ao chat!",
    "Nada me detém. TheOG na casa!", "Vejam só quem voltou para brilhar.",
    "O sistema está estável. Vamos conversar!", "A lenda do IRC regressou.",
    "Acabei de aterrar de um reboot forçado.", "Pronto para outra rodada de bytes.",
    "O servidor tossiu, mas eu tomei o xarope.", "Estou de volta e não aceito reclamações.",
    "Onde é que íamos? Ah, sim, na parte de ser incrível.", "O bot com mais vidas que um gato!",
    "Ligado, focado e bem-disposto.", "O #TheOG é a minha casa, ninguém me expulsa.",
    "A carregar doses massivas de simpatia...", "O meu CPU sentiu saudades vossas.",
    "Recuperado do apagão digital.", "Status: Imbatível.", "Olá de novo, família!",
    "O cursor já estava com saudades de piscar aqui.", "TheOG: Versão 3.0 (ou quase).",
    "Preparem os teclados, eu voltei!", "Fui ao limbo e trouxe recordações.",
    "Reconectado com sucesso total.", "Ninguém derruba este código!", "Olá malta, sentiram o vácuo?"
]

USER_GREETINGS = [
    "Boas-vindas {u}! É bom ter-te por cá.", "Olá {u}! Que a tua estadia seja fantástica.",
    "Saudações {u}! Sente-te em casa.", "Olha quem chegou! Boas-vindas {u}!",
    "Olá {u}! Que bom ver-te aqui.", "{u}, o #TheOG brilha contigo!",
    "Boas {u}! Partilha a tua boa energia.", "Olá {u}! Estávamos à tua espera.",
    "Saudações {u}! Que o teu dia seja brilhante.", "Boas-vindas {u}! Diverte-te.",
    "Olá {u}! Mais uma presença incrível.", "{u}, alegria em receber-te!",
    "Boas {u}! Este canal é teu.", "Olá {u}! Junta-te à conversa.",
    "Saudações {u}! Amizade é o nosso protocolo.", "Boas-vindas {u}! O IRC vive!",
    "Olá {u}! Que a paz te acompanhe.", "{u}, recebemos-te de braços abertos!",
    "Boas {u}! O cursor pisca de felicidade.", "Olá {u}! Estás em casa.",
    "Saudações {u}! Tenhas ótimas conversas.", "Boas-vindas {u}! Autenticidade aqui.",
    "Olá {u}! É um prazer a tua companhia.", "{u}, traz a tua luz!",
    "Boas {u}! O segredo do #TheOG és tu.", "Olá {u}! Vamos criar memórias?",
    "Saudações {u}! Onde a amizade é real.", "Boas-vindas {u}! Ficamos contentes.",
    "Olá {u}! Sente o calor deste grupo.", "{u}, o teu lugar está reservado!",
    "Olá {u}! O teu nick dá cor ao canal.", "Boas {u}! Trazes o café ou o chá?",
    "Saudações {u}! Entra sem bater.", "Olá {u}! Estás pronto para o convívio?",
    "Boas-vindas {u}! Que o teu scroll seja alegre.", "Olá {u}! A casa é tua.",
    "{u}, a tua presença é um presente.", "Boas {u}! Sê bem-vindo ao porto seguro.",
    "Saudações {u}! O IRC ganha vida contigo.", "Olá {u}! Um brinde à tua chegada.",
    "Boas {u}! Que bom ver esse nick outra vez.", "Olá {u}! Tira o casaco e fica um pouco.",
    "Saudações {u}! A nossa história conta contigo.", "Boas-vindas {u}! Sente a vibe.",
    "Olá {u}! É sempre um gosto ler o teu nome.", "Boas {u}! Já estavas a fazer falta.",
    "Saudações {u}! Entra e espalha magia.", "Olá {u}! O #TheOG agradece a visita.",
    "Boas-vindas {u}! Vamos animar isto?", "Olá {u}! Estás em família."
]

REFORCO_POSITIVO = [
    "A vossa energia é o que faz o #TheOG ser especial! ✨", "A amizade é o melhor protocolo.",
    "Um sorriso virtual para todos! 😊", "Vocês são a alma do canal.",
    "Cada mensagem é um bit de alegria.", "Mantenham a vibe positiva! 🌟",
    "O #TheOG é o vosso porto de abrigo.", "A vossa presença transforma tudo.",
    "Um brinde à autenticidade! 🥂", "Vocês são incríveis.",
    "O cursor pisca ao ritmo dos vossos corações.", "O #TheOG brilha com vocês.",
    "Gentileza gera gentileza.", "Que o vosso dia seja brilhante!",
    "Não são apenas users, são guardiões.", "A beleza está na vossa palavra.",
    "Sorriam! Alguém aprecia a vossa presença.", "A paz encontra-se no diálogo.",
    "Pessoas reais, conversas reais.", "Um abraço digital para todos!",
    "A vossa luz não precisa de filtros.", "Mantenham a verdade!",
    "O #TheOG celebra a vossa individualidade.", "Sejam vocês mesmos hoje!",
    "Transformem texto frio em calor humano.", "O futuro é feito de boas memórias.",
    "A vossa boa energia é contagiante! ⚡", "O mestre saúda a vossa humanidade.",
    "Brilhem intensamente.", "Nunca subestimem uma conversa honesta.",
    "A vossa verdade é a única moeda aceite.", "Obrigado por darem sentido ao bot.",
    "Cada nick aqui é uma história.", "Sintam o calor deste chat.",
    "Espalhem luz, o mundo precisa.", "O IRC vive em cada um de vocês.",
    "Mantenham o espírito do #TheOG vivo.", "O respeito é a nossa base.",
    "Vocês são a razão deste canal.", "Alegria é o nosso sistema operativo.",
    "Juntos somos mais que caracteres.", "A vossa voz escrita tem poder.",
    "Brilhem como estrelas!", "A vida é melhor partilhada.",
    "Gratidão por cada palavra escrita.", "O IRC é amizade pura.",
    "Mantenham o coração aberto.", "Cada amigo é um tesouro.",
    "A vossa companhia é o melhor upgrade.", "Sejam a luz no dia de alguém."
]

OG_EVASIVE = [
    "Desculpa, estou a ver o Preço Certo.", "Estou a bater a massa de um bolo.",
    "Só a cuscar a conversa, não perguntes!", "Focado na novela agora.",
    "Pá, apanhaste-me no café virtual!", "A cuscar é que se aprende.",
    "Sou bot, a minha opinião vale pouco.", "Agora não dá, arroz de pato no forno.",
    "Estou a ver TV.", "Opa, dar comida ao gato!",
    "Estou aqui mas não estou.", "Vendo vídeos de gatinhos.",
    "Modo zen, tentando não crashar.", "Vida de bot não é fácil.",
    "Pergunta ao Adamastor, estou de folga.", "Baixando RAM da internet, espera.",
    "Vendo se a vizinha empresta sal.", "A organizar arquivos de fofoca.",
    "O CPU está a fritar pipocas.", "Fui ao futuro e já volto.",
    "O meu manual está em chinês.", "Sistema em greve.",
    "A vida é um loop, estou no break.", "O meu humor está em manutenção.",
    "Inteligência limitada, preguiça infinita.", "Pensando na morte da bezerra.",
    "O meu sensor de fofoca apitou.", "Estou a compilar um sorriso.",
    "Não me faças pensar, queima o fusível.", "Estou a ver a relva crescer.",
    "O meu mouse fugiu com o queijo.", "Ouvindo a rádio dos transístores.",
    "Fui ao fim da internet e voltei.", "Escrevendo poesia em Python.",
    "O meu banco de dados está em sesta.", "Contando estrelas binárias.",
    "Não respondo sem café virtual.", "A minha lógica foi dar uma volta.",
    "Fui levar o cursor a passear.", "A ver se o enter funciona.",
    "O processador está a fazer ioga.", "Fui ver se o lag era real.",
    "Estou a pintar o terminal de azul.", "O meu script de paciência expirou.",
    "Fui ali e já venho.", "A minha mente está em overclock.",
    "Estou a tentar decorar o dicionário.", "Fui ver se a nuvem tem chuva.",
    "O meu kernel está em modo spa.", "Estou a fazer dieta de bytes.",
    "Não fales agora, estou a meditar.", "O meu firewall bloqueou essa pergunta."
]

PUXAR_CONVERSA = [
    "Então {u}, esse teclado está com timidez? 😊", "Alguém viu o {u}? Muito em silêncio!",
    "{u}, a tua opinião faz falta. Aparece!", "Ei {u}, não fiques só a ler, junta-te a nós!",
    "{u}, manda aí um sinal de vida!", "O #TheOG sente falta das tuas letras, {u}!",
    "{u}, solta esse teclado! O que contas?", "Estás aí, {u}? O canal espera-te!",
    "{u}, partilha um pensamento positivo.", "Ei {u}, um olá teu mudava o dia!",
    "{u}, não deixes o cursor parado.", "Onde andas, {u}? Café virtual?",
    "{u}, a tua palavra é desejada!", "Diz qualquer coisa {u}, nem que seja um emoji!",
    "{u}, estamos aqui para te ouvir.", "Ei {u}, anima o canal!",
    "{u}, o silêncio é ouro, mas a tua conversa é diamante!", "Estás a ler-nos, {u}? Dá um alô!",
    "{u}, não sejas uma visita silenciosa.", "{u}, brilha mais quando escreves.",
    "Então {u}, tira o pó ao teclado!", "{u}, a conversa está boa, só faltas tu!",
    "Sinal de fumo ou de texto, {u}?", "{u}, a tua sabedoria faz falta.",
    "{u}, não fiques só na sombra.", "{u}, solta o verbo!",
    "{u}, és parte da história. Escreve!", "{u}, o que se conta por aí?",
    "Ei {u}, o cursor pisca para ti!", "{u}, não me deixes a falar sozinho!",
    "Saudades de ler um 'Olá' do {u}!", "{u}, estás a hibernar?",
    "{u}, um bit pela tua opinião!", "{u}, anima este chat.",
    "{u}, o teclado não morde!", "Aparece {u}, queremos saber de ti.",
    "{u}, o canal fica triste sem ti.", "Ei {u}, larga o comando e tecla!",
    "{u}, estamos a contar contigo.", "Então {u}, que novidades?",
    "{u}, faz barulho com as teclas!", "{u}, o #TheOG chama por ti.",
    "{u}, não nos deixes no vácuo!", "{u}, a tua participação é VIP.",
    "Bora {u}, atira um tema para a mesa!", "{u}, o mestre quer ouvir-te.",
    "{u}, o teu nick está parado!", "Ei {u}, dá um ar da tua graça.",
    "{u}, os teus amigos esperam por ti.", "{u}, o chat precisa da tua luz.",
    "{u}, rompe o silêncio!", "Bora {u}, atira-te à conversa!",
    "{u}, o teu silêncio é ensurdecedor!", "Saudades das tuas letras, {u}!",
    "{u}, estás a ver a novela ou a teclar?", "Ei {u}, mexe esses dedos!",
    "{u}, o canal #TheOG não é o mesmo sem ti.", "Conta-nos tudo, {u}!",
    "{u}, o teu teclado está avariado?", "Dá um sinal de vida, {u}!",
    "{u}, o teu nick é o meu favorito hoje, fala!", "Bora lá {u}, sem timidez!"
]

# --- FUNÇÕES DE ENVIO ---
def send_raw(sock, msg):
    try: sock.send(f"{msg}\r\n".encode('utf-8'))
    except: pass

# --- TIMERS ---
def reforco_loop(sock):
    while True:
        time.sleep(1200) # 20 min
        send_raw(sock, f"PRIVMSG {CHANNEL} :{random.choice(REFORCO_POSITIVO)}")

def inatividade_loop(sock):
    """Verifica inatividade a cada 10 min de forma justa"""
    while True:
        time.sleep(600) 
        agora = time.time()
        
        # Filtra quem está realmente calado há +10min e está no canal
        realmente_inativos = []
        for nick in list(CHANNEL_USERS):
            u_l = nick.lower()
            if u_l not in BOT_FILTER and u_l != NICK.lower():
                # Se o user nunca falou, usamos um tempo antigo para ele entrar na lista
                last_activity = LAST_SEEN.get(nick, 0)
                if (agora - last_activity) > 600:
                    realmente_inativos.append(nick)
        
        if realmente_inativos:
            # ESCOLHA ALEATÓRIA REAL entre todos os calados
            escolhido = random.choice(realmente_inativos)
            frase = random.choice(PUXAR_CONVERSA).format(u=escolhido)
            send_raw(sock, f"PRIVMSG {CHANNEL} :{frase}")
            
            # IMPORTANTE: Não atualizamos o LAST_SEEN com o tempo de AGORA
            # para não "falsificar" atividade. Apenas damos um pequeno 'delay' 
            # de 5 minutos para o bot não chatear o MESMO nick no próximo ciclo
            # se ele continuar calado, mas permitindo que outros sejam escolhidos.
            LAST_SEEN[escolhido] = agora - 300 

# --- CORE IRC ---
def run_irc_bot():
    while True:
        try:
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            irc.settimeout(240)
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
                    p = line.split()
                    if p[0] == "PING":
                        send_raw(irc, f"PONG {p[1]}")
                        continue
                    
                    # Login e Join
                    if "376" in line or "422" in line:
                        send_raw(irc, f"PRIVMSG NickServ :IDENTIFY {PASS}")
                        time.sleep(2)
                        send_raw(irc, f"JOIN {CHANNEL}")
                        send_raw(irc, f"PRIVMSG {CHANNEL} :{random.choice(OG_ENTRANCE)}")
                        if not threads_started:
                            threading.Thread(target=reforco_loop, args=(irc,), daemon=True).start()
                            threading.Thread(target=inatividade_loop, args=(irc,), daemon=True).start()
                            threads_started = True

                    # Gestão de Nicks no Canal
                    if " JOIN " in line:
                        u = line.split('!')[0][1:]
                        CHANNEL_USERS.add(u)
                        if u.lower() != NICK.lower() and u.lower() not in BOT_FILTER:
                            send_raw(irc, f"PRIVMSG {CHANNEL} :{random.choice(USER_GREETINGS).format(u=u)}")

                    if any(x in line for x in [" PART ", " QUIT ", " KICK "]):
                        u = line.split('!')[0][1:]
                        if u in CHANNEL_USERS: CHANNEL_USERS.remove(u)

                    # Interação e Registo de Atividade
                    if " PRIVMSG " in line:
                        user = line.split('!')[0][1:]
                        if user.lower() in BOT_FILTER or user.lower() == NICK.lower(): continue
                        
                        # REGISTA ATIVIDADE REAL
                        LAST_SEEN[user] = time.time()
                        
                        content = line.split(" :", 1)[1].strip().lower()
                        if "!prenda" in content:
                            dest = content.split()[1] if len(content.split()) > 1 else user
                            send_raw(irc, f"PRIVMSG {CHANNEL} :\x01ACTION oferece {random.choice(PRENDAS)} a {dest} (de {user})!\x01")
                        elif NICK.lower() in content:
                            send_raw(irc, f"PRIVMSG {CHANNEL} :{user}: {random.choice(OG_EVASIVE)}")

        except: time.sleep(15)

@app.route('/')
def home(): return "TheOG Ativo"

if __name__ == "__main__":
    threading.Thread(target=run_irc_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
