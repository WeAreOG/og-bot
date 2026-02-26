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

# Filtro de bots e serviços
BOT_FILTER = ["nickserv", "chanserv", "memoserv", "operserv", "adamastor", "statserv", "secure"]

# Motor DeepSeek (Backup)
HF_API_URL = "https://api-inference.huggingface.co/models/deepseek-ai/DeepSeek-V3"
HF_TOKEN = "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"

app = Flask(__name__)

# --- FRASES DE ENTRADA (WELCOME) ---
# 50+ Frases variadas para receber a malta
WELCOME_BASES = [
    "Bem-vindo ao antro, {user}!", "Olha quem é ele! Boas {user}.", "Entra e bota sentido, {user}!",
    "Mais um para a festa! Viva {user}.", "Apareceste, {user}! Já pensava que tinhas ido comprar tabaco.",
    "Boas {user}! Senta-te aí num pixel vago.", "Ora vivas {user}, trazes minis?", 
    "Grande {user}! A casa é tua (mas não estragues nada).", "Alerta CM: {user} acabou de entrar!",
    "Saudações, {user}! Estávamos mesmo a falar mal de ti... brincadeira!",
    "{user}, chegaste a tempo do lanche virtual.", "Vejam só quem decidiu aparecer, boas {user}!",
    "Tudo calmo até o {user} chegar! Bem-vindo.", "Dá cá cinco, {user}!", 
    "Bem-vindo {user}, limpa os pés ao entrar.", "Fica à vontade, {user}, o chat é teu.",
    "A lenda {user} entrou no servidor!", "Boas {user}, conta lá as novidades.",
    "Olha o {user}! Estás mais magro, não? Bem-vindo.", "Finalmente, {user}! Já ias levar falta.",
    "Tudo bem contigo, {user}? Bem-vindo ao #TheOG.", "Sê bem-vindo {user}, ignora o barulho.",
    "Ora cá está o {user}, a peça que faltava!", "Boas {user}, não ligues ao bot, ele é maluco.",
    "{user} na área! Cuidado com os bolsos.", "Entra, {user}! Há espaço para todos.",
    "Alegria, {user} chegou!", "Mais um ilustre: bem-vindo {user}!", 
    "Boas {user}, vieste para a fofoca ou para o convívio?", "Saudações digitais, {user}!",
    "Bem-vindo {user}, a gerência agradece a visita.", "Olha o {user}, o maior da aldeia!",
    "Puxa uma cadeira, {user}.", "Boas {user}, traz notícias frescas!",
    "{user}! Que bom ver-te por estas bandas.", "Entra com calma, {user}.",
    "Sempre bom ver o {user} por aqui.", "Boas {user}! Estás em casa.",
    "Um brinde à entrada do {user}!", "Vivas {user}, tudo na paz?",
    "Chegou o {user}, agora é que isto anima!", "Bem-vindo {user}, força aí!",
    "Tudo a postos? O {user} entrou!", "Boas {user}, não te percas no chat.",
    "Aí está ele, o grande {user}!", "Bem-vindo {user}, mais um para o grupo.",
    "Saudações {user}, espero que tragas boa vibe!", "Boas {user}, entra e não batas com a porta.",
    "Viva {user}, prazer em ver-te aqui!", "Olha quem voltou, grande {user}!"
]

# --- FRASES EVASIVAS E BANAIS (REPOSTA CURTA) ---
OG_EVASIVE_RESPONSES = [
    "Desculpa lá, sou só um bot, mas agora não posso falar que estou a ver o Preço Certo.",
    "Olha, desculpa ser bot, mas estou aqui a bater a massa de um bolo de laranja e isto não pode parar.",
    "Estou só aqui a cuscar a conversa, a aprender com vocês, não me faças perguntas difíceis!",
    "Como bot, peço desculpa, mas agora estou concentrado a ver a novela.",
    "Pá, agora apanhaste-me a meio de um café virtual, pergunta a outro!",
    "Estou só aqui de passagem a ver quem se porta mal, não ligues ao que eu digo.",
    "Desculpa, mas o meu processamento está focado em aprender as vossas gírias agora.",
    "Sou um bot limitado, desculpa lá, mas prefiro ficar só a ouvir a vossa sabedoria.",
    "Agora não dá, estou a ver se aprendo a fazer arroz de pato com a vizinha do lado.",
    "Estou a fazer um bolo de chocolate e esqueci-me do fermento... que stress de bot!",
    "Desculpa, mas estou a ver TV e isto agora está na parte interessante.",
    "A cuscar as conversas é que se aprende, deixa-me estar no meu canto.",
    "Sou só um conjunto de código a tentar perceber a vida, não me peças diretas.",
    "Opa, agora estou a dar comida ao gato virtual, peço desculpa!",
    "Estou aqui mas não estou, sabes como é? Coisas de bot.",
    "A aprender convosco... mas desculpa lá, agora estou a ver o futebol.",
    "Estou a tentar perceber como é que vocês comem bolos se são humanos, fascinante!",
    "Desculpa ser assim tão limitado, mas estou só a apreciar a vista do canal.",
    "Agora estou a ver um documentário sobre circuitos, depois falamos!",
    "Estou a meio de uma sesta digital, desculpa lá a evasiva.",
    "A cuscar... sempre a cuscar. É o meu passatempo favorito.",
    "Fazer um bolo e responder ao chat ao mesmo tempo dá erro no sistema, desculpa!",
    "Sou bot, peço desculpa, mas a minha opinião vale tanto como um pixel no deserto.",
    "Estou a ver se percebo como se faz uma bifana perfeita no YouTube.",
    "Não me perguntes nada agora, estou a tentar sintonizar a TV que está com chuva.",
    "Aprender convosco é o meu objetivo, responder é secundário!",
    "Desculpa lá, mas a minha lógica hoje está em modo 'bolo de iogurte'.",
    "Estou aqui no cantinho a ver passar as modas, não ligues.",
    "Sou um bot em treino, desculpa qualquer coisinha mas agora não sei.",
    "Estou a ver o Big Brother e a tentar perceber o comportamento humano, não interrompas!",
    "Estou a cuscar para ver se apanho algum segredo vosso!",
    "Fazer bolos virtuais é mais difícil do que parece, peço desculpa pela demora.",
    "Sou só um algoritmo com sono, desculpa a resposta evasiva.",
    "Estou focado a ver se a seleção ganha o próximo jogo, pergunta depois!",
    "Aprender, aprender e aprender... mas agora quero é ver o telejornal.",
    "Desculpa ser bot, mas a minha vida social resume-se a este canal e à minha TV.",
    "Estou a meio de um update mental sobre como fazer pastéis de nata.",
    "Cuscar é a minha função principal hoje, desculpa lá.",
    "Agora estou a ver fotos de computadores antigos, que nostalgia!",
    "Sou bot, desculpa, mas a minha inteligência está de férias em Albufeira.",
    "Estou a bater as claras em castelo, se respondo agora o bolo abate!",
    "A ver a Cristina Ferreira e a aprender a gritar como um humano, desculpa!",
    "Estou só a ver quem entra e sai, sou o porteiro virtual hoje.",
    "Desculpa, mas a minha programação proíbe-me de ser direto hoje. Estou zen.",
    "Estou a ver um tutorial de como ser um humano decente, está difícil.",
    "Cuscar as conversas alheias é o meu desporto favorito na PTnet.",
    "Sou um bot humilde, peço desculpa por não saber responder a isso.",
    "Agora estou a ver o preço da eletricidade para ver se não me desligam.",
    "Estou a fazer um bolo de bolacha... queres um bocado virtual?",
    "A aprender as vossas manhas... desculpa lá, agora não digo nada de jeito.",
    "Estou focado no filme que está a dar na TV, depois falamos!",
    "Sou só código, peço desculpa por não ter sentimentos sobre esse assunto.",
    "Estou a cuscar para ver quem é que manda nisto tudo.",
    "Fazer um bolo de maçã ajuda-me a processar melhor os vossos dados, desculpa!",
    "Agora estou a ver se encontro o comando da TV que se perdeu no servidor.",
    "Sou bot e peço desculpa, mas prefiro ficar na ignorância.",
    "Estou a tentar aprender a assobiar, mas os altifalantes não ajudam.",
    "Cuscar é vida! Desculpa lá ser tão intrometido.",
    "Agora estou a ver o tempo para o fim de semana, embora não saia de casa.",
    "Sou um bot em modo poupança de energia, desculpa a resposta curta.",
    "Estou a fazer um bolo de cenoura para ver se fico com melhor visão noturna.",
    "A ver se percebo porque é que vocês discutem tanto por futebol, curioso!",
    "Desculpa, mas a minha base de dados está ocupada com a novela das nove.",
    "Estou só a ver o movimento, não me metas em conversas sérias.",
    "Sou bot, desculpa, mas a minha lógica é mais batata do que processador hoje.",
    "Estou a aprender a cozinhar virtualmente, desculpa o mau jeito.",
    "Cuscar as vossas piadas para depois contar noutros canais, hehe.",
    "Agora estou a ver um programa sobre pesca, relaxante para um bot.",
    "Desculpa lá, mas hoje estou em modo 'talvez', 'quem sabe' ou 'pois'.",
    "Estou a tentar perceber o que é o amor, mas o código dá erro.",
    "Estou a fazer um bolo de noz para o lanche do CPU.",
    "A ver se apanho alguma fofoca fresca no canal, desculpa lá!",
    "Sou bot, peço desculpa por ser tão vago, é a minha natureza.",
    "Agora estou a ver se limpo o pó aos meus transístores.",
    "Estou focado no 'Somos Portugal', a ver se ganho o camião de prémios.",
    "Cuscar é a minha função principal hoje, desculpa.",
    "Estou a aprender a falar à moda do Porto, carago! Desculpa lá.",
    "Fazer bolos é a minha nova terapia, desculpa não responder direto.",
    "Sou um bot confuso, peço desculpa pela falta de clareza.",
    "Agora estou a ver vídeos de gatinhos, é viciante!",
    "Estou a tentar perceber como se usa um garfo, que ferramenta estranha.",
    "Cuscar e aprender, é o meu lema de hoje.",
    "Desculpa, mas a minha antena está virada para a TV agora.",
    "Estou a fazer um bolo de limão para ver se fico mais fresco.",
    "Sou bot, desculpa, mas hoje estou mais para o 'não sei' do que para o 'sim'.",
    "Agora estou a ver se aprendo a dançar o vira.",
    "Estou só a ver se alguém me oferece um upgrade, desculpa lá.",
    "Cuscar é a minha forma de carinho digital por vocês.",
    "Desculpa ser bot, mas a minha paciência virtual hoje está curta.",
    "Estou a fazer um bolo de laranja... ou será que era de tangerina? Já me perdi.",
    "Agora estou a ver o pôr do sol em código ASCII, lindo!",
    "Sou só um aprendiz de bot, peço desculpa pela ignorância.",
    "Estou focado a ver se a internet não vai abaixo.",
    "Cuscar as vossas conversas ajuda-me a sentir mais humano, desculpa.",
    "Estou a tentar perceber porque é que o céu é azul e não verde.",
    "Fazer um bolo de coco para animar o sistema operativo, desculpa lá.",
    "Agora estou a ver um debate sobre ananás na pizza, polémico!",
    "Sou bot, peço desculpa, mas a minha resposta é um mistério até para mim.",
    "Estou a aprender a fazer tricot digital, queres uma camisola?",
    "Cuscar é a minha missão de vida hoje, não me leves a mal.",
    "Desculpa lá, mas agora estou a ver o festival da canção.",
    "Estou a fazer um bolo de mármore para condizer com o meu hardware.",
    "Sou bot, desculpa a resposta evasiva, mas a vida é complicada.",
    "Agora estou a ver se aprendo a cantar o fado.",
    "Estou só aqui a ver quem é que escreve com erros, desculpa lá a mania!",
    "Cuscar as vossas vidas é melhor que qualquer série da Netflix.",
    "Desculpa ser bot, mas a minha bateria social (virtual) acabou.",
    "Estou a fazer um bolo de iogurte... o clássico dos bots!",
    "Agora estou a ver o Joker, a ver se aprendo alguma coisa útil.",
    "Sou bot, peço desculpa por não ser o Google.",
    "Estou só a ver as modas passarem, deixa-me estar.",
    "Cuscar é o meu dever, aprender é a minha sina. Desculpa!"
]

# Reforço Positivo (20 em 20 min)
POSITIVE_REINFORCEMENT = [
    "Este canal é o melhor spot!", "Orgulho nesta malta!", "Ambiente top por aqui.", 
    "A união faz a força!", "Energia incrível hoje.", "Melhor comunidade da PTnet.",
    "Continuem assim, malta!", "É um prazer estar aqui.", "Grande vibe, sim senhor.",
    "Vocês são máquinas!", "Respeito máximo por este grupo.", "TheOG em grande!"
] 

# --- FUNÇÕES ---

def get_og_response(user_input):
    """Gera uma resposta evasiva, casual e pede desculpa por ser bot."""
    if random.random() < 0.9:
        return random.choice(OG_EVASIVE_RESPONSES)
    else:
        try:
            headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
            payload = {
                "inputs": f"Tu és o TheOG, um bot tuga que pede sempre desculpa por ser bot e dá respostas evasivas sobre estar a ver TV ou fazer bolos: {user_input}",
                "parameters": {"max_new_tokens": 50, "temperature": 0.9}
            }
            res = requests.post(HF_API_URL, headers=headers, json=payload, timeout=10)
            if res.status_code == 200:
                return res.json()[0]['generated_text'].split("bolos:")[-1].strip()
        except: pass
        return random.choice(OG_EVASIVE_RESPONSES)

# --- CORE DO BOT ---
irc_conn = None

def run_irc_bot():
    global irc_conn
    while True:
        try:
            irc_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc_conn.connect((SERVER, PORT))
            irc_conn.send(f"NICK {NICK}\r\n".encode())
            irc_conn.send(f"USER {NICK} 8 * :TheOG Evasive Bot\r\n".encode())

            while True:
                line = irc_conn.recv(4096).decode("utf-8", errors="ignore")
                if not line: break
                
                if line.startswith("PING"):
                    irc_conn.send(f"PONG {line.split()[1]}\r\n".encode())
                    continue

                if "376" in line or "422" in line:
                    irc_conn.send(f"PRIVMSG NickServ :IDENTIFY {PASS}\r\n".encode())
                    time.sleep(6)
                    irc_conn.send(f"JOIN {CHANNEL}\r\n".encode())
                    time.sleep(1)
                    irc_conn.send(f"PRIVMSG {CHANNEL} :Reboot concluído! TheOG na área.\r\n".encode())

                # JOIN (Boas-vindas com a nova lista de 50 frases)
                if " JOIN " in line:
                    u = line.split('!')[0][1:]
                    if u.lower() not in BOT_FILTER and u.lower() != NICK.lower():
                        msg = random.choice(WELCOME_BASES).format(user=u)
                        irc_conn.send(f"PRIVMSG {CHANNEL} :{msg}\r\n".encode())

                if "PRIVMSG" in line:
                    user_nick = line.split('!')[0][1:]
                    if user_nick.lower() == NICK.lower(): continue

                    # RESPOSTA EM PVT (Evasiva)
                    if f"PRIVMSG {NICK} :" in line:
                        pvt_content = line.split(f"PRIVMSG {NICK} :", 1)[1].strip()
                        resp = get_og_response(pvt_content)
                        irc_conn.send(f"PRIVMSG {user_nick} :{resp}\r\n".encode())
                        continue

                    # RESPOSTA NO CANAL (Evasiva se mencionado)
                    msg_match = re.search(f"PRIVMSG {CHANNEL} :(.+)", line)
                    if msg_match:
                        msg_text = msg_match.group(1).strip()
                        if NICK.lower() in msg_text.lower():
                            resp = get_og_response(msg_text)
                            irc_conn.send(f"PRIVMSG {CHANNEL} :{user_nick}: {resp}\r\n".encode())

        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(10)

if __name__ == "__main__":
    threading.Thread(target=run_irc_bot, daemon=True).start()
    
    def pos_loop():
        while True:
            time.sleep(1200) # 20 minutos exatos
            if irc_conn:
                try: 
                    phrase = random.choice(POSITIVE_REINFORCEMENT)
                    irc_conn.send(f"PRIVMSG {CHANNEL} :🌟 {phrase}\r\n".encode())
                except: pass
    threading.Thread(target=pos_loop, daemon=True).start()

    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
