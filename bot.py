import socket
import time
import threading
import re
import os
import random
from flask import Flask
from duckduckgo_search import DDGS

# --- CONFIGURAÇÕES ---
SERVER = "irc.ptnet.org"
PORT = 6667
NICK = "TheOG"
PASS = "Nasomet112#" 
CHANNEL = "#TheOG"

app = Flask(__name__)

# --- 60 FRASES DE BOAS-VINDAS (Base para a IA ou Diretas) ---
WELCOME_BASES = [
    "Bem-vindo ao antro, {user}!", "Olha quem é ele! Entra e serve-te, {user}.", 
    "Boas {user}! Estávamos mesmo a precisar de gente nova.", "Finalmente chegaste, {user}!",
    "Ora vivas {user}! Tudo calmo por aqui?", "A lenda {user} acabou de entrar!",
    "Cuidado malta, o {user} chegou!", "{user}, a casa é tua (mas não partas nada).",
    "Mais um para a festa! Bem-vindo {user}.", "Grande {user}! Como é que é?",
    "Sentia um vazio no canal, era a falta do {user}!", "Puxa uma cadeira, {user}.",
    "Boas {user}! Vieste para o sítio certo.", "Atenção a todos: {user} está na área!",
    "Viva {user}! Que se conta?", "{user}, já estávamos à tua espera!",
    "Bem-vindo {user}, o mestre disto tudo.", "Saudações, {user}! Bebes alguma coisa?",
    "Aí está ele! Boas {user}.", "Entra com calma, {user}. O ambiente está bom!",
    "Foste o escolhido, {user}! Bem-vindo.", "Apareceste, {user}! Já não era sem tempo.",
    "O canal acaba de subir de nível com o {user}!", "Boas {user}. Não repares na desarrumação.",
    "A lenda, o mito, o {user} chegou!", "{user}, que bom ver-te por aqui.",
    "Sê bem-vindo ao melhor canal da PTNet, {user}!", "Dá cá cinco, {user}!",
    "Mais um membro para a elite: bem-vindo {user}.", "Fica à vontade, {user}.",
    "Olha o {user}! Que surpresa agradável.", "A festa começa agora, o {user} chegou!",
    "Tudo a fazer vénia, o {user} entrou!", "Bem-vindo ao caos organizado, {user}.",
    "Saudações cibernéticas, {user}!", "O {user} entrou. Agora é que isto vai aquecer.",
    "É um pássaro? É um avião? Não, é o {user}!", "Boas {user}, conta coisas!",
    "Entra e não batas com a porta, {user}.", "Bem-vindo à zona VIP, {user}!",
    "Ora aí está o homem/mulher! Grande {user}.", "{user}, vieste para o barulho ou para a calma?",
    "O {user} traz as imperiais?", "Bem-vindo à família, {user}.",
    "Fica por aí, {user}. A conversa está boa!", "Saudações {user}, espero que tragas boas notícias.",
    "Uau, o {user}! Que honra.", "{user} entrou. Proceder com cautela!",
    "Podes entrar, {user}, mas deixa os sapatos à porta.", "Boas {user}. O último paga a rodada!",
    "Já conheces as regras, {user}? Nem eu.", "O {user} é que sabe!",
    "Sempre bem-vindo, {user}.", "A casa é pequena mas o coração é grande, {user}!",
    "Mais um para o grupo! Força {user}.", "Sente-te em casa, {user}.",
    "Bem-vindo ao porto de abrigo, {user}.", "Ora boas {user}, que prazer!",
    "Quem é vivo sempre aparece! Boas {user}.", "És tu {user}? Estás diferente!"
]

@app.route('/')
def health_check():
    return "TheOG Online - IA & Welcome 60 Active", 200

# --- FUNÇÕES DE IA ---

def get_ai_response(prompt, context="conversa"):
    try:
        with DDGS() as ddgs:
            if context == "welcome":
                # A IA personaliza a frase base escolhida
                instr = f"Dá as boas-vindas a {prompt} no IRC. Sê curto, muito informal, usa calão de Portugal e sê engraçado."
            else:
                instr = f"Tu és o TheOG no IRC. Responde curto, informal e em PT-PT. Pergunta: {prompt}"
            
            results = ddgs.chat(instr, model="gpt-4o-mini")
            return re.sub(r'[\r\n\t]+', ' ', results)[:400]
    except:
        # Fallback se a IA falhar
        return random.choice(WELCOME_BASES).format(user=prompt) if context == "welcome" else "Estou off, tenta logo."

# --- CORE DO BOT ---

def run_irc_bot():
    while True:
        try:
            print(f"[{time.strftime('%H:%M:%S')}] A ligar...")
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            irc.connect((SERVER, PORT))
            
            irc.send(f"NICK {NICK}\r\n".encode())
            irc.send(f"USER {NICK} 8 * :TheOG AI Bot\r\n".encode())

            while True:
                line = irc.recv(4096).decode("utf-8", errors="ignore")
                if not line: break

                if line.startswith("PING"):
                    irc.send(f"PONG {line.split()[1]}\r\n".encode())
                    continue

                # Login e Join
                if "376" in line or "422" in line:
                    irc.send(f"PRIVMSG NickServ :IDENTIFY {PASS}\r\n".encode())
                    time.sleep(2)
                    irc.send(f"JOIN {CHANNEL}\r\n".encode())

                # --- EVENTO DE ENTRADA (JOIN) ---
                if " JOIN " in line:
                    user_nick = line.split('!')[0][1:]
                    if user_nick.lower() != NICK.lower():
                        # Escolhe entre IA ou lista estática para variar ainda mais
                        if random.random() > 0.3: # 70% das vezes usa IA
                            msg = get_ai_response(user_nick, context="welcome")
                        else: # 30% das vezes usa a lista de 60 frases
                            msg = random.choice(WELCOME_BASES).format(user=user_nick)
                        
                        irc.send(f"PRIVMSG {CHANNEL} :{msg}\r\n".encode())

                # --- MENSAGENS NO CANAL ---
                if "PRIVMSG" in line:
                    user = line.split('!')[0][1:]
                    if user.lower() == NICK.lower(): continue
                    
                    if f"PRIVMSG {CHANNEL} :" in line:
                        msg_content = line.split(f"PRIVMSG {CHANNEL} :", 1)[1].strip()
                        
                        if NICK.lower() in msg_content.lower():
                            p_clean = re.sub(rf'{NICK}', '', msg_content, flags=re.IGNORECASE).strip()
                            resp = get_ai_response(p_clean)
                            irc.send(f"PRIVMSG {CHANNEL} :{user}: {resp}\r\n".encode())

        except Exception as e:
            print(f"Erro: {e}. Retry em 15s...")
            time.sleep(15)

if __name__ == "__main__":
    threading.Thread(target=run_irc_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
