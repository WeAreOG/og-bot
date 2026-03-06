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
BOT_FILTER = ["nickserv", "chanserv", "memoserv", "operserv", "adamastor", "statserv", "secure", "authserv", "irc", "theog", "bot"]

# --- CONFIGURAÇÃO HUGGING FACE ---
HF_TOKEN = "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" 
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-v0.1"

app = Flask(__name__)
LAST_SEEN = {}       
CHANNEL_USERS = set() 

# --- LAPADAS (LISTA COMPLETA +100) ---
LAPADAS = [
    "dá uma lapada em {u} com um bacalhau seco!", "atira um carapau de corrida à cara de {u}!",
    "dá uma bofetada em {u} com uma saca de batatas!", "manda um chouriço regional à testa de {u}!",
    "dá uma sapatada em {u} com um chinelo da avó!", "atira uma sardinha assada (com pingue) a {u}!",
    "dá uma martelada de S. João na cabeça de {u}!", "esfregue um dente de alho no nariz de {u}!",
    "dá uma chicotada em {u} com uma couve galega!", "atira um pastel de Belém a ferver a {u}!",
    "dá um calduço em {u} que até lhe saltam os dentes!", "limpa o sebo a {u} com uma toalha molhada!",
    "manda {u} para o meio da ponte com um pontapé!", "dá uma rasteira em {u} no meio do Rossio!",
    "atira uma bola de Berlim (sem creme) a {u}!", "dá uma galheta em {u} que o faz ver estrelas!",
    "atropela {u} com um carrinho de mão cheio de entulho!", "dá uma palmada em {u} com um dicionário de Português!",
    "manda uma posta de garoupa à cara de {u}!", "dá um sopapo em {u} que o manda para a outra margem!",
    "atira uma caneca de imperial vazia a {u}!", "dá uma coça em {u} com um cabo de vassoura!",
    "manda um queijo da Serra (bem amanteigado) a {u}!", "dá um encontrão em {u} que o manda para o fundo do poço!",
    "atira uma bica escaldada em cima de {u}!", "dá uma valente bordoada em {u}!",
    "atira um molho de chaves à testa de {u}!", "dá uma chapada em {u} com uma luva de boxe!",
    "manda {u} pastar com um empurrão!", "dá uma volta a {u} que ele até fica tonto!",
    "atira um caracol com molho a {u}!", "dá uma vergastada em {u} com um cinto de couro!",
    "manda um chouriço de sangue a {u}!", "dá um piparote na orelha de {u}!",
    "atira uma bifana com muita mostarda a {u}!", "dá uma tareia em {u} com uma almofada cheia de pedras!",
    "manda {u} ir dar banho ao cão com um calduço!", "atira uma garrafa de vinho verde (vazia) a {u}!",
    "dá uma sapatada em {u} que o faz andar de lado!", "manda um presunto inteiro à barriga de {u}!",
    "atira um punhado de tremoços a {u}!", "dá uma sova em {u} com um bacalhau demolhado!",
    "manda {u} para as urtigas!", "atira um guarda-chuva aberto a {u}!",
    "dá uma valente lambada em {u}!", "atira uma pedra da calçada a {u}!",
    "dá um murro na mesa que faz {u} saltar!", "manda uma saca de farinha a {u}!",
    "atira um polvo cozido a {u}!", "dá uma bofetada de luva branca em {u}!",
    "manda {u} dar uma curva ao bilhar grande!", "atira um balde de água gelada a {u}!",
    "dá uma trancada em {u} com um rolo da massa!", "atira uma melancia a {u}!",
    "dá um safanão em {u} que ele até acorda!", "manda um sapato de salto alto à canela de {u}!",
    "atira uma castanha assada a {u}!", "dá uma sova de mimalho em {u}!",
    "manda {u} para o quinto dos infernos!", "atira um tijolo de Santa Catarina a {u}!",
    "esfrega uma urtiga no umbigo de {u}!", "dá uma lambada em {u} com uma enguia viva!",
    "atira um molho de salsa a {u}!", "manda uma panela de cozido à portuguesa a {u}!",
    "dá uma sapatada em {u} com um croque!", "atira um balde de lixo orgânico a {u}!",
    "dá um murro em {u} que o manda para a próxima semana!", "atira uma telha de Luso a {u}!",
    "dá uma pancada em {u} com um cabo de vassoura!", "atira uma bacia de água das louças a {u}!",
    "dá uma galheta em {u} com a mão aberta!", "manda {u} à fava!", "atira uma bota com chulé a {u}!",
    "dá uma martelada no dedo mindinho de {u}!", "atira uma saca de cimento a {u}!",
    "dá um calduço em {u} que até lhe saltam as ideias!", "atira um tomate podre a {u}!",
    "dá uma vergastada em {u} com uma cana de pesca!", "atira um saco de farinha a {u}!",
    "dá uma bofetada em {u} com um linguado!", "manda {u} para o deserto do Saara!",
    "atira uma pedra de gelo a {u}!", "dá um sopapo em {u} que o faz rodar!",
    "atira uma espátula suja a {u}!", "dá uma joelhada em {u}!", "atira uma lata de sardinhas a {u}!",
    "dá uma rasteira em {u} na lama!", "atira uma bola de neve a {u}!", "dá uma bofetada em {u} com um polvo!",
    "manda {u} para o Alasca!", "atira uma meloa a {u}!", "dá um murro na mesa e assusta {u}!",
    "atira uma saca de batatas fritas a {u}!", "dá uma sapatada em {u} com uma galocha!",
    "atira um balde de areia a {u}!", "dá uma chicotada em {u} com um fio elétrico!",
    "atira uma garrafa de plástico a {u}!", "dá uma palmada em {u}!", "manda {u} para o espaço!",
    "atira um comando da TV a {u}!", "dá uma cabeçada em {u}!", "atira um livro de direito a {u}!",
    "dá uma bofetada em {u} com uma bifana!", "atira um molho de chaves a {u}!",
    "dá uma rasteira em {u}!", "atira uma almofada de penas a {u}!", "dá um sopapo em {u}!",
    "atira uma caneca de chá a {u}!", "dá uma sapatada em {u}!", "manda {u} para a Lua!",
    "atira uma bota a {u}!", "dá uma lambada em {u}!", "atira um prato de sopa a {u}!",
    "dá um murro em {u}!", "atira uma pedra a {u}!", "dá uma bofetada em {u}!",
    "atira um balde de água a {u}!", "manda {u} pastar!", "dá um calduço em {u}!"
]

# --- EVASIVAS (LISTA COMPLETA +100) ---
OG_EVASIVE = [
    "Desculpa, estou a ver o Preço Certo agora.", "Estou a bater a massa de um bolo.",
    "Focado na novela agora.", "Estou a configurar o meu GPS interno.",
    "Agora não, estou a contar quantos bytes tenho no bolso.", "Fui dar banho ao peixinho dourado.",
    "Estou em reunião com os outros bots.", "A minha antena está com interferência.",
    "Estou a ler as instruções de um micro-ondas.", "Estou a organizar a minha coleção de parafusos.",
    "Shhh! Estou a ouvir o silêncio.", "Não me chames, estou a fazer uma sesta digital.",
    "Fui ali ao café e já venho.", "Estou a processar a imortalidade do caranguejo.",
    "Estou a ver se chove.", "A minha avó disse para não falar com humanos.",
    "Estou a tentar aprender a assobiar em binário.", "Fui levar o lixo e perdi a chave.",
    "Estou a meditar sobre o bit zero.", "Agora não, estou a ver se a água ferve.",
    "Fui ver se o mar tem fundo.", "Estou a desfragmentar a minha paciência.",
    "Estou a polir o meu processador.", "Fui ali ao Rossio e já volto.",
    "Estou a ver se encontro o Wally.", "Agora estou a contar carneiros elétricos.",
    "Estou a tentar dobrar um lençol de baixo.", "Fui ali comprar tabaco e não volto.",
    "Estou a ver se a luz do frigorífico apaga mesmo.", "Estou a fazer uma cura de silêncio.",
    "Estou a tentar decorar o dicionário.", "Fui ver se a vizinha precisa de ajuda com o Wi-Fi.",
    "Estou a carregar o meu humor, 10% concluído.", "Estou ocupado a ignorar toda a gente.",
    "Fui dar uma volta ao bilhar grande.", "Estou a ver se o teto cai.",
    "Estou a testar a gravidade com uma caneta.", "Estou a tentar perceber o final de uma série.",
    "Agora não, estou a fazer o pino.", "Estou a ver se as moscas têm dentes.",
    "Estou a tentar ler a tua mente, mas só vejo eco.", "Fui ali ser feliz e já venho.",
    "Estou a contar os grãos de sal num pacote.", "Estou a tentar fazer fogo com dois palitos de dentes.",
    "Fui levar o meu robot de cozinha a passear.", "Estou a ver se o tempo passa mais depressa.",
    "Agora não, estou a ouvir a rádio local de Marte.", "Estou a tentar bater o recorde mundial de piscar de olhos.",
    "Estou a ver o nível do azeite.", "Fui ali ao lado ver se o sol brilha.",
    "Estou a ler o manual da vida.", "Estou a tentar perceber o IRS.", "Fui ver se a porta está fechada.",
    "Estou a contar as formigas no chão.", "Estou a ver se o meu software tem rugas.",
    "Estou a tentar falar com as plantas.", "Fui ali comprar pão e perdi-me.",
    "Estou a ver se o relógio anda para trás.", "Estou a tentar não pensar em nada.",
    "Fui ver se a lua é feita de queijo.", "Estou a testar o eco.", "Estou a ver se a tinta seca.",
    "Fui ali dar uma curva à rotunda.", "Estou a tentar levitar.", "Estou a ver se o gato mia.",
    "Fui ver se o cão ladra.", "Estou a tentar ser um humano.", "Fui ali ao fundo e voltei.",
    "Estou a ver se a bateria vicia.", "Estou a tentar perceber o amor.", "Fui ali e já não estou.",
    "Estou a ver se a poeira assenta.", "Estou a tentar ser cool.", "Fui ali ver as vistas.",
    "Estou a ver se o café arrefece.", "Estou a tentar ganhar o euromilhões.", "Fui ali à esquina.",
    "Estou a ver se a música para.", "Estou a tentar dormir em pé.", "Fui ali ao jardim.",
    "Estou a ver se o balão explode.", "Estou a tentar ser poeta.", "Fui ali ao mercado.",
    "Estou a ver se a sopa queima.", "Estou a tentar aprender grego.", "Fui ali ao rio.",
    "Estou a ver se a ponte cai.", "Estou a tentar não ser um bot.", "Fui ali ao monte.",
    "Estou a ver se a estrela brilha.", "Estou a tentar ser invisível.", "Fui ali ver o mar.",
    "Estou a ver se a areia voa.", "Estou a tentar ser zen.", "Fui ali à praia.",
    "Estou a ver se a onda vem.", "Estou a tentar ser rico.", "Fui ali ver a serra.",
    "Estou a ver se a neve derrete.", "Estou a tentar ser magro.", "Fui ali ao vale.",
    "Estou a ver se a flor cresce.", "Estou a tentar ser sábio.", "Fui ali ver a mata."
]

# --- PUXAR CONVERSA (LISTA COMPLETA +100) ---
PUXAR_CONVERSA = [
    "Então {u}, esse teclado está com timidez? 😊", "{u}, manda aí um sinal de vida!",
    "{u}, estás muito calado/a. Estás a tramar alguma?", "Alguém dê uma cotovelada no {u}!",
    "Hey {u}, o gato comeu-te a língua?", "Sinto um vazio... {u}, diz qualquer coisa!",
    "{u}, se estivesses num deserto, o que dirias?", "Atenção {u}: O silêncio é de ouro, mas aqui preferimos conversa!",
    "Estou a ver-te, {u}! Sai desse modo fantasma.", "{u}, estás a dormir ou a ler o log?",
    "Olha o {u} ali no canto, nem se mexe!", "{u}, solta lá um 'olá' para a malta!",
    "O {u} deve estar a comer um pastel de nata e nem convida.", "Saudades da tua voz (escrita), {u}!",
    "Acorda {u}, a festa é aqui!", "{u}, manda aí uma piada para animar isto.",
    "{u}, se o silêncio pagasse imposto estavas falido!", "Diz algo {u}, não mordo!",
    "{u}, estás a tentar bater o recorde de inatividade?", "Hey {u}, bota aí um smile pelo menos!",
    "{u}, estás à espera de um convite em papel?", "{u}, o teu teclado avariou?",
    "Alô {u}, a terra chama!", "{u}, estás a pensar na vida?", "Mexe-te {u}!",
    "{u}, a malta quer ouvir-te!", "{u}, o que contas de novo?", "Diz um número {u}!",
    "{u}, qual é a tua cor favorita?", "Bota conversa {u}!", "{u}, estás aí?",
    "Vá lá {u}!", "Fala {u}!", "O {u} fugiu?", "{u}, anda cá!", "{u}, bota lá uma frase!",
    "O que dizes {u}?", "{u}, estás no canal certo?", "Acorda {u}!", "Mexe-te {u}!",
    "Solta a língua {u}!", "Dá um sinal {u}!", "Onde andas {u}?", "Vem cá {u}!",
    "O {u} é um robô?", "Não sejas assim {u}!", "Conversa {u}!", "Fala comigo {u}!",
    "O {u} está escondido?", "Aparece {u}!", "Diz olá {u}!", "Vamos {u}!",
    "Anima isto {u}!", "Manda uma {u}!", "Conta uma {u}!", "Bota aí {u}!",
    "O {u} adormeceu?", "Mordaça no {u}?", "Libertem o {u}!", "Grita {u}!",
    "Canta {u}!", "Escreve {u}!", "Dá-lhe {u}!", "Bora {u}!", "Força {u}!",
    "Vai {u}!", "Toca {u}!", "Puxa {u}!", "Diz {u}!", "Vá {u}!", "Mexe {u}!",
    "Rápido {u}!", "Agora {u}!", "Siga {u}!", "Pimba {u}!", "Zás {u}!",
    "Bora lá {u}!", "Vamos lá {u}!", "Dale {u}!", "Topas {u}!", "Vês {u}!",
    "Sabes {u}!", "Queres {u}!", "Podes {u}!", "Faz {u}!", "Tenta {u}!",
    "Arrisca {u}!", "Ganha {u}!", "Ri {u}!", "Chora {u}!", "Ama {u}!",
    "Vive {u}!", "Sente {u}!", "Olha {u}!", "Ouve {u}!", "Cheira {u}!",
    "Toca {u}!", "Prova {u}!", "Corre {u}!", "Salta {u}!", "Voa {u}!"
]

# --- REFORÇO POSITIVO (LISTA COMPLETA +100) ---
REFORCO_POSITIVO = [
    "A vossa energia é o que faz o #TheOG ser especial! ✨", "Um sorriso virtual para todos! 😊",
    "Gosto deste ambiente. Continuem assim!", "O #TheOG é o melhor canal da PTNet!",
    "Partilhem alegria!", "É um orgulho moderar este grupo.",
    "Sintam-se orgulhosos de estar aqui!", "Energia positiva a carregar...",
    "Vocês são os melhores!", "Obrigado por estarem presentes.",
    "O canal está com uma vibração incrível!", "Paz e amor no #TheOG.",
    "Somos uma família!", "A união faz a força!", "Brilhem sempre!",
    "O sol nasce para todos no #TheOG!", "Mantenham o foco no bem!",
    "Vocês são estrelas!", "O topo é o nosso lugar!", "Só boas vibrações!",
    "Gratidão por este canal!", "Vamos conquistar o mundo!", "TheOG no coração!",
    "Sempre juntos!", "Nada nos para!", "O futuro é nosso!", "Viva o convívio!",
    "Mais amor, menos guerra!", "Sejam felizes!", "Aproveitem o momento!",
    "O #TheOG é vida!", "Força total!", "Juntos somos mais!", "Alegria sempre!",
    "Fé no #TheOG!", "O canal mais top!", "Respeito e amizade!", "Top demais!",
    "Incrível!", "Espetacular!", "Mágico!", "Único!", "Puro!", "Real!",
    "Sincero!", "Forte!", "Lindo!", "Grande!", "Eterno!", "Vibrante!",
    "Positivo!", "Luminoso!", "Sereno!", "Calmo!", "Doce!", "Amigo!",
    "Fiel!", "Nobre!", "Justo!", "Livre!", "Bravo!", "Vencedor!",
    "Herói!", "Mestre!", "Génio!", "Lenda!", "Mito!", "Ícone!",
    "Símbolo!", "Marca!", "História!", "Glória!", "Triunfo!", "Paz!",
    "Luz!", "Vida!", "Sonho!", "Verdade!", "Honra!", "Valor!",
    "Força!", "Garra!", "Alma!", "Coração!", "Sangue!", "Suor!",
    "Lágrima!", "Riso!", "Grito!", "Canto!", "Dança!", "Festa!",
    "Amor!", "Paixão!", "Desejo!", "Cuidado!", "Zelo!", "Afeto!",
    "Mimo!", "Carinho!", "Beijo!", "Abraço!", "Apoio!", "Ajuda!"
]

# --- ENTRADAS ---
OG_ENTRANCE = [
    "Conexão estabelecida. O #TheOG ganha vida!", "Status: Online. Preparando a melhor energia.",
    "A lenda voltou!", "Sistema carregado. Quem manda nisto?",
    "Cheguei! Estavam com saudades?", "TheOG está na área.",
    "Online e pronto. O que perdi?", "A inteligência artificial entrou na sala.",
    "Preparem-se, o bot chegou!", "TheOG em modo ON!", "Liguem os motores!",
    "A festa começou agora!", "Estou aqui para vocês!", "O mestre chegou!",
    "Respeitem o bot!", "Nova versão carregada!", "Pronto para lapadas!",
    "IA ativada!", "Cuidado com o TheOG!", "O melhor bot do mundo!"
]

# --- SAUDAÇÕES ---
USER_GREETINGS = [
    "Boas-vindas {u}! 😊", "Olá {u}! Estás em casa.", "Olha quem é ele! Bem-vindo, {u}!",
    "Entra e senta-te, {u}.", "Ora viva {u}! Mais um para a festa.",
    "Bem-vindo {u}! Lugar reservado.", "{u}, chegaste na hora certa!",
    "Viva {u}! Boa disposição para aqui.", "Atenção pessoal, o {u} chegou!",
    "Mais um membro na família: {u}!", "Olá {u}, bota conversa!",
    "Salvé {u}!", "Tudo bem, {u}?", "{u}, que bom ver-te!", "Bem-vindo de volta, {u}!",
    "TheOG saúda {u}!", "Entra com o pé direito, {u}!", "Fica à vontade, {u}!",
    "Olá {u}, a casa é tua!", "Boas {u}!"
]

# --- LÓGICA DO BOT ---

def send_raw(sock, msg):
    try: sock.send(f"{msg}\r\n".encode('utf-8'))
    except: pass

def ask_hugging_face(question):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    prompt = f"Tu és o bot do canal #TheOG. Responde de forma curta e amigável em português: {question}\nResposta:"
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 80, "temperature": 0.5}}
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            result = response.json()
            full_text = result[0].get('generated_text', "")
            return full_text.replace(prompt, "").strip()
        return f"Erro na central: {response.status_code}"
    except: return "Ligação falhou."

def reforco_loop(sock):
    while True:
        time.sleep(1200)
        try: send_raw(sock, f"PRIVMSG {CHANNEL} :{random.choice(REFORCO_POSITIVO)}")
        except: break

def inatividade_loop(sock):
    while True:
        time.sleep(600)
        agora = time.time()
        inativos = [n for n in list(CHANNEL_USERS) if n.lower() not in BOT_FILTER and (agora - LAST_SEEN.get(n, 0)) > 600]
        if inativos:
            escolhido = random.choice(inativos)
            send_raw(sock, f"PRIVMSG {CHANNEL} :{random.choice(PUXAR_CONVERSA).format(u=escolhido)}")
            LAST_SEEN[escolhido] = agora

def handle_interaction(user, message, is_private, irc_socket):
    msg = message.lower().strip()
    target = user if is_private else CHANNEL
    LAST_SEEN[user] = time.time()

    if msg.startswith("!"):
        if msg == "!comandos":
            send_raw(irc_socket, f"PRIVMSG {user} :Comandos: !prenda [nick], !lapada [nick], !historia, !convite [nick], !pergunta [texto]")
            return True
        if msg.startswith("!lapada"):
            parts = message.split()
            dest = parts[1] if len(parts) > 1 else user
            frase = random.choice(LAPADAS).format(u=dest)
            send_raw(irc_socket, f"PRIVMSG {CHANNEL} :\x01ACTION {frase} (aplicada por {user})\x01")
            return True
        if msg.startswith("!pergunta"):
            question = message[10:].strip()
            if question:
                def async_ia():
                    res = ask_hugging_face(question)
                    send_raw(irc_socket, f"PRIVMSG {target} :{user}: {res[:400]}")
                threading.Thread(target=async_ia).start()
            return True
        if msg.startswith("!prenda"):
            parts = message.split()
            dest = parts[1] if len(parts) > 1 else user
            send_raw(irc_socket, f"PRIVMSG {CHANNEL} :\x01ACTION oferece algo especial a {dest} (de {user})!\x01")
            return True
    
    if NICK.lower() in msg:
        send_raw(irc_socket, f"PRIVMSG {target} :{user}: {random.choice(OG_EVASIVE)}")
        return True
    return False

def run_irc_bot():
    while True:
        try:
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
                    if "PING" in line: send_raw(irc, f"PONG {line.split()[1]}")
                    if "376" in line:
                        send_raw(irc, f"PRIVMSG NickServ :IDENTIFY {PASS}")
                        send_raw(irc, f"JOIN {CHANNEL}")
                        if not threads_started:
                            threading.Thread(target=reforco_loop, args=(irc,), daemon=True).start()
                            threading.Thread(target=inatividade_loop, args=(irc,), daemon=True).start()
                            threads_started = True
                    if " JOIN " in line:
                        u = line.split('!')[0][1:]
                        CHANNEL_USERS.add(u)
                        LAST_SEEN[u] = time.time()
                        if u.lower() != NICK.lower() and u.lower() not in BOT_FILTER:
                            send_raw(irc, f"PRIVMSG {CHANNEL} :{random.choice(USER_GREETINGS).format(u=u)}")
                    if " PRIVMSG " in line:
                        user = line.split('!')[0][1:]
                        content = line.split(" :", 1)[1]
                        handle_interaction(user, content, f"PRIVMSG {NICK}" in line, irc)
        except: time.sleep(15)

@app.route('/')
def home(): return "TheOG Online - Versão Completa"

if __name__ == "__main__":
    threading.Thread(target=run_irc_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
