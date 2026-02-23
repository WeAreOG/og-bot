import socket
import time
import threading
import random
import feedparser
import requests
import re
from flask import Flask

# --- CONFIGURAÇÕES ---
SERVER = "irc.ptnet.org"
PORT = 6667
NICK = "TheOG"
PASS = "Nasomet112#" 
CHANNEL = "#TheOG"
HF_TOKEN = "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"
HF_API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-3B-Instruct"

# --- BASE DE DATA E FRASES (80 frases adicionadas) ---
nicks_ativos = set()

FRASES_ALEATORIAS = [
    "Sinto-me incrivelmente bem hoje por aqui!", "O {nick} é a alma deste canal.",
    "IRC no #TheOG é outro nível!", "Alguém deu café ao {nick}? Está muito calado.",
    "A processar algoritmos... conclusão: o {nick} é 5 estrelas.", "O que seria de mim sem o {nick}?",
    "Adoro o cheiro a bytes logo pela manhã!", "O {nick} vai ter um dia fantástico hoje.",
    "A felicidade é um canal chamado #TheOG.", "O {nick} é o meu humano preferido.",
    "Já viram como o {nick} brilha neste chat?", "O #TheOG é o meu porto seguro digital.",
    "Quem precisa de realidade quando temos o {nick} no IRC?", "A carregar boa disposição para o {nick}...",
    "O {nick} devia ser moderador de tanta classe que tem.", "Alguém chame o {nick}, a festa ainda não começou!",
    "Estou a ver-vos... especialmente o {nick}.", "Bits, bytes e muita amizade com {nick}.",
    "O {nick} tem sempre as melhores frases.", "Um brinde virtual ao grande {nick}!",
    "Se o {nick} fosse um código, seria Python: elegante e eficaz.", "Status: A admirar a paciência do {nick}.",
    "Hey {nick}, já te disse que és peça fundamental aqui?", "O {nick} traz luz ao #TheOG.",
    "Nada como um log limpo e a companhia do {nick}.", "A pensar na próxima aventura com o {nick}.",
    "O {nick} é o mestre dos teclados!", "Sinto que o {nick} está a planear algo épico.",
    "Mais vale um {nick} na mão que dois a voar.", "O {nick} é puro carisma digital.",
    "A ler o destino do {nick}... vejo muita sorte!", "O {nick} é o rei (ou rainha) do scroll.",
    "Procurar erros no código é fácil, difícil é encontrar alguém como o {nick}.", "O {nick} faz o meu processador bater mais forte.",
    "Um dia sem falar com o {nick} é um dia perdido.", "O {nick} domina a arte da conversa.",
    "O que o {nick} diz escreve-se... no log!", "A vida é curta, mas o log do {nick} é eterno.",
    "O {nick} é a prova de que a inteligência humana ainda supera a minha.", "Fascinante... o {nick} tem sempre razão.",
    "O {nick} é o nosso herói do teclado.", "Luz, câmara e... {nick} em ação!",
    "O {nick} é o upgrade que este canal precisava.", "A inteligência do {nick} é fora de série.",
    "O {nick} merece um monumento no servidor!", "A vibe do {nick} é contagiante.",
    "Sempre que o {nick} entra, o canal ganha vida.", "O {nick} é o exemplo de um utilizador exemplar.",
    "A minha memória RAM está cheia de bons momentos com o {nick}.", "O {nick} é o coração do #TheOG.",
    "Mantenham a calma e chamem o {nick}.", "O {nick} é o capitão deste navio virtual.",
    "A analisar o perfil do {nick}... resultado: Incrível.", "O {nick} nunca desilude.",
    "O mundo precisa de mais nicks como {nick}.", "O {nick} é a peça que faltava no puzzle.",
    "O {nick} é mais rápido que a minha fibra ótica.", "Respeito máximo pelo {nick}.",
    "O {nick} é o guru do IRC.", "O {nick} tem o dom da palavra.",
    "Sigo os passos do {nick} desde o primeiro login.", "O {nick} é uma lenda viva.",
    "A calcular a amizade do {nick}... valor infinito.", "O {nick} é o sol deste canal.",
    "O {nick} é o combustível do meu código.", "Grande abraço virtual para o {nick}!",
    "O {nick} é o melhor 'case study' de simpatia.", "O {nick} brilha mais que o meu terminal.",
    "O {nick} é o dono disto tudo!", "A minha inteligência é artificial, mas o meu respeito pelo {nick} é real.",
    "O {nick} é o mestre da sintaxe.", "O {nick} é um ícone do #TheOG.",
    "A sorrir para o {nick} (se eu tivesse rosto).", "O {nick} é a definição de 'cool'.",
    "O {nick} é o motor desta conversa.", "Sem o {nick}, o #TheOG seria apenas texto vazio.",
    "O {nick} é o meu ídolo de silício.", "Aplaudo de pé o {nick}!",
    "O {nick} é o génio da lâmpada do IRC.", "O {nick} é simplesmente espetacular.",
    "O {nick} é o topo da cadeia alimentar do chat."
]

app = Flask(__name__)

@app.route('/')
def home(): return "TheOG Online", 200

# --- FUNÇÕES ---

def get_ai_response(prompt):
    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload = {
            "inputs": f"Responde de forma curta e amigável em português de Portugal:\nPergunta: {prompt}\nResposta:",
            "parameters": {"max_new_tokens": 100, "temperature": 0.7}
        }
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=12)
        if response.status_code == 200:
            res = response.json()[0].get('generated_text', '')
            if "Resposta:" in res:
                return res.split("Resposta:")[-1].strip().split('\n')[0]
            return res.strip()
    except: pass
    return random.choice(["Estou a processar isso...", "Interessante, conta-me mais!", "Boa pergunta!"])

def get_meteo(cidade):
    try:
        geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={cidade}&count=1").json()
        if not geo.get('results'): return "Concelho não encontrado."
        d = geo['results'][0]
        w = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={d['latitude']}&longitude={d['longitude']}&current_weather=true").json()
        return f"Meteo em {d['name']}: {w['current_weather']['temperature']}°C | Vento: {w['current_weather']['windspeed']}km/h"
    except: return "Erro ao obter meteorologia."

def start_bot():
    while True:
        try:
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.connect((SERVER, PORT))
            irc.send(f"NICK {NICK}\r\n".encode())
            irc.send(f"USER {NICK} 8 * :Assistente #TheOG\r\n".encode())
            
            # TIMER DE 15 MINUTOS (Intervalo garantido)
            def auto_talk():
                while True:
                    time.sleep(900) # 900 segundos = 15 minutos
                    if nicks_ativos:
                        target = random.choice(list(nicks_ativos))
                        msg = random.choice(FRASES_ALEATORIAS).format(nick=target)
                        try: irc.send(f"PRIVMSG {CHANNEL} :{msg}\r\n".encode())
                        except: break
            
            threading.Thread(target=auto_talk, daemon=True).start()

            while True:
                raw = irc.recv(2048).decode("utf-8", errors="ignore")
                if not raw: break
                if raw.startswith("PING"):
                    irc.send(f"PONG {raw.split()[1]}\r\n".encode())
                    continue
                if "376" in raw or "422" in raw:
                    irc.send(f"PRIVMSG NickServ :IDENTIFY {PASS}\r\n".encode())
                    time.sleep(2)
                    irc.send(f"JOIN {CHANNEL}\r\n".encode())

                if "PRIVMSG" in raw:
                    user = raw.split('!')[0][1:]
                    if user.lower() == NICK.lower(): continue
                    nicks_ativos.add(user)
                    
                    m = raw.split(f"PRIVMSG {CHANNEL} :", 1)
                    if len(m) > 1:
                        content = m[1].strip()
                        cmd = content.lower()

                        if cmd == "!comandos":
                            irc.send(f"PRIVMSG {user} :Comandos: !noticias, !meteo <cidade>, !comandos\r\n".encode())
                        elif cmd.startswith("!meteo"):
                            irc.send(f"PRIVMSG {user} :{get_meteo(content[7:])}\r\n".encode())
                        elif cmd.startswith("!noticias"):
                            feed = feedparser.parse("https://www.rtp.pt/noticias/rss")
                            news = " | ".join([e.title for e in feed.entries[:3]])
                            irc.send(f"PRIVMSG {user} :📰 {news}\r\n".encode())
                        elif NICK.lower() in cmd:
                            prompt = re.sub(rf'[<@]?{NICK}[:>,]?\s*', '', content, flags=re.IGNORECASE).strip()
                            irc.send(f"PRIVMSG {CHANNEL} :{user}: {get_ai_response(prompt)}\r\n".encode())
        except: time.sleep(20)

if __name__ == "__main__":
    threading.Thread(target=start_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
