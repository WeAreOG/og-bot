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
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"

app = Flask(__name__)
LAST_SEEN = {}       
CHANNEL_USERS = set() 

# --- MONITOR DE LOGS ---
def log_presenca(user, accao):
    hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"[{hora}] {user} {accao}")

# --- TEXTO DA HISTÓRIA ---
HISTORIA_THEOG = ["Estamos a construir a história com base em cada um dos utilizadores."]

# --- PRENDAS ---
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

# --- LAPADAS (PT-PT) ---
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
    "manda {u} para o quinto dos infernos!", "atira um tijolo de Santa Catarina a {u}!"
]

# --- ENTRADAS E MENSAGENS ---
OG_ENTRANCE = ["Conexão estabelecida. O #TheOG ganha vida!", "Status: Online. Preparando a melhor energia."]
USER_GREETINGS = ["Boas-vindas {u}! É bom ter alguém como tu por cá.", "Olá {u}! Estás em casa, no #TheOG."]
REFORCO_POSITIVO = ["A vossa energia é o que faz o #TheOG ser especial! ✨", "Um sorriso virtual para todos! 😊"]
OG_EVASIVE = ["Desculpa, estou a ver o Preço Certo.", "Estou a bater a massa de um bolo agora."]
PUXAR_CONVERSA = ["Então {u}, esse teclado está com timidez? Diz algo! 😊", "{u}, manda aí um sinal de vida!"]

def send_raw(sock, msg):
    try:
        sock.send(f"{msg}\r\n".encode('utf-8'))
    except: pass

# --- FUNÇÃO IA HUGGING FACE ---
def ask_hugging_face(question):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    # Contexto para a IA saber quem é
    prompt = f"<s>[INST] Tu és o bot do canal #TheOG no IRC. Responde de forma curta, castiça e em português de Portugal à seguinte questão: {question} [/INST]</s>"
    
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 150, "temperature": 0.7, "top_p": 0.9}
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            result = response.json()
            res = result[0]['generated_text']
            if "[/INST]" in res:
                res = res.split("[/INST]")[-1].strip()
            return res
        elif response.status_code == 503:
            return "Estou a carregar as baterias (modelo a iniciar)... tenta de novo em 20 segundos!"
        return f"Tive um precalço técnico (Erro {response.status_code})."
    except:
        return "A ligação à central falhou. Tenta outra vez!"

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
        
        if msg == "!historia":
            for linha in HISTORIA_THEOG:
                send_raw(irc_socket, f"PRIVMSG {user} :{linha}")
                time.sleep(1.0)
            return True

        if msg.startswith("!prenda"):
            parts = message.split()
            dest = parts[1] if len(parts) > 1 else user
            send_raw(irc_socket, f"PRIVMSG {CHANNEL} :\x01ACTION oferece {random.choice(PRENDAS)} a {dest} (de {user})!\x01")
            return True

        if msg.startswith("!lapada"):
            parts = message.split()
            dest = parts[1] if len(parts) > 1 else user
            frase = random.choice(LAPADAS).format(u=dest)
            send_raw(irc_socket, f"PRIVMSG {CHANNEL} :\x01ACTION {frase} (aplicada por {user})\x01")
            return True

        if msg.startswith("!pergunta"):
            question = message[10:].strip()
            if not question:
                send_raw(irc_socket, f"PRIVMSG {target} :{user}, o que queres saber?")
            else:
                def async_ia():
                    resposta = ask_hugging_face(question)
                    # Envia a resposta dividida se for muito longa (limite IRC)
                    send_raw(irc_socket, f"PRIVMSG {target} :{user}: {resposta[:400]}")
                threading.Thread(target=async_ia).start()
            return True

        if msg.startswith("!convite"):
            parts = message.split()
            if len(parts) > 1:
                dest = parts[1]
                send_raw(irc_socket, f"PRIVMSG {dest} :Olá! {user} convidou-te para o #TheOG. Aparece!")
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
                try:
                    data = irc.recv(4096).decode("utf-8", errors="ignore")
                except socket.timeout:
                    send_raw(irc, "PING :keepalive")
                    continue
                
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
                        time.sleep(2)
                        send_raw(irc, f"JOIN {CHANNEL}")
                        send_raw(irc, f"PRIVMSG {CHANNEL} :{random.choice(OG_ENTRANCE)}")
                        if not threads_started:
                            threading.Thread(target=reforco_loop, args=(irc,), daemon=True).start()
                            threading.Thread(target=inatividade_loop, args=(irc,), daemon=True).start()
                            threads_started = True

                    if " JOIN " in line:
                        u = line.split('!')[0][1:]
                        CHANNEL_USERS.add(u)
                        LAST_SEEN[u] = time.time()
                        if u.lower() != NICK.lower() and u.lower() not in BOT_FILTER:
                            log_presenca(u, "ENTROU")
                            send_raw(irc, f"PRIVMSG {CHANNEL} :{random.choice(USER_GREETINGS).format(u=u)}")

                    if any(x in line for x in [" PART ", " QUIT ", " KICK "]):
                        u = line.split('!')[0][1:]
                        if u in CHANNEL_USERS: CHANNEL_USERS.remove(u)

                    if " PRIVMSG " in line:
                        user = line.split('!')[0][1:]
                        if user.lower() == NICK.lower() or user.lower() in BOT_FILTER: continue
                        content = line.split(" :", 1)[1].strip() if " :" in line else ""
                        handle_interaction(user, content, f"PRIVMSG {NICK}" in line, irc)
        except Exception as e:
            print(f"Erro: {e}. Reiniciando em 15s...")
            time.sleep(15)

@app.route('/')
def home(): return "TheOG Online com IA"

if __name__ == "__main__":
    threading.Thread(target=run_irc_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
