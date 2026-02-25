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

# Filtro de bots e serviços para não cumprimentar
BOT_FILTER = ["nickserv", "chanserv", "memoserv", "operserv", "adamastor", "statserv", "secure"]

# Motor DeepSeek (Estável)
HF_API_URL = "https://api-inference.huggingface.co/models/deepseek-ai/DeepSeek-V3"
HF_TOKEN = "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"

app = Flask(__name__)

# --- FRASES ---
REENTRY_PHRASES = ["Voltei! Quem desligou o cabo?", "Reboot concluído!", "TheOG na área!"]
WELCOME_BASES = ["Bem-vindo ao antro, {user}!", "Olha quem é ele! Boas {user}."]
POSITIVE_REINFORCEMENT = ["Este canal é o melhor spot!", "Orgulho nesta malta!"]

# --- FUNÇÕES ---

def get_wiki(subject):
    try:
        # Limpar o tema para a URL
        topic = subject.strip().replace(" ", "_")
        url = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{topic}"
        res = requests.get(url, timeout=7)
        
        if res.status_code == 200:
            data = res.json()
            extract = data.get("extract", "Não encontrei um resumo para isso.")
            return extract[:450] + "..."
        else:
            return f"Não encontrei nada sobre '{subject}' na Wikipedia Portuguesa."
    except Exception as e:
        return "Erro ao ligar à Wikipedia. Tenta de novo mais tarde."

def get_ai_response(prompt):
    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
        payload = {
            "inputs": f"Tu és o TheOG, um bot tuga informal. Responde curto: {prompt}",
            "parameters": {"max_new_tokens": 60, "temperature": 0.7}
        }
        res = requests.post(HF_API_URL, headers=headers, json=payload, timeout=10)
        if res.status_code == 200:
            text = res.json()[0]['generated_text']
            # Limpeza básica da resposta
            return text.split("bot tuga informal.")[-1].replace("Responde curto:", "").strip()
    except: pass
    return "Tudo tranquilo por aqui!"

# --- CORE DO BOT ---
irc_conn = None

def run_irc_bot():
    global irc_conn
    while True:
        try:
            irc_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc_conn.connect((SERVER, PORT))
            irc_conn.send(f"NICK {NICK}\r\n".encode())
            irc_conn.send(f"USER {NICK} 8 * :TheOG DeepSeek Bot\r\n".encode())

            while True:
                line = irc_conn.recv(4096).decode("utf-8", errors="ignore")
                if not line: break
                
                if line.startswith("PING"):
                    irc_conn.send(f"PONG {line.split()[1]}\r\n".encode())
                    continue

                # Login e Identificação
                if "376" in line or "422" in line:
                    irc_conn.send(f"PRIVMSG NickServ :IDENTIFY {PASS}\r\n".encode())
                    time.sleep(6)
                    irc_conn.send(f"JOIN {CHANNEL}\r\n".encode())
                    time.sleep(1)
                    irc_conn.send(f"PRIVMSG {CHANNEL} :{random.choice(REENTRY_PHRASES)}\r\n".encode())

                # JOIN (Boas-vindas com filtro)
                if " JOIN " in line:
                    u = line.split('!')[0][1:]
                    if u.lower() not in BOT_FILTER and u.lower() != NICK.lower():
                        msg = random.choice(WELCOME_BASES).format(user=u)
                        irc_conn.send(f"PRIVMSG {CHANNEL} :{msg}\r\n".encode())

                # MENSAGENS (PRIVMSG)
                if "PRIVMSG" in line:
                    user_nick = line.split('!')[0][1:]
                    if user_nick.lower() == NICK.lower(): continue

                    # 1. MENSAGEM EM PRIVADO (PVT)
                    if f"PRIVMSG {NICK} :" in line:
                        pvt_content = line.split(f"PRIVMSG {NICK} :", 1)[1].strip()
                        if user_nick.lower() not in BOT_FILTER:
                            resp = get_ai_response(pvt_content)
                            irc_conn.send(f"PRIVMSG {user_nick} :{resp}\r\n".encode())
                        continue

                    # 2. MENSAGEM NO CANAL
                    msg_match = re.search(f"PRIVMSG {CHANNEL} :(.+)", line)
                    if msg_match:
                        msg_text = msg_match.group(1).strip()
                        
                        # COMANDOS - AGORA ENVIADOS SEMPRE PARA O PVT DO USER
                        if msg_text.lower() == "!comandos":
                            irc_conn.send(f"PRIVMSG {user_nick} :--- Comandos do TheOG ---\r\n".encode())
                            irc_conn.send(f"PRIVMSG {user_nick} :!wiki [tema] - Pesquisa Wikipedia.\r\n".encode())
                            irc_conn.send(f"PRIVMSG {user_nick} :Diz o meu nome para falar com a IA.\r\n".encode())
                        
                        elif msg_text.lower().startswith("!wiki "):
                            tema = msg_text[6:]
                            resultado = get_wiki(tema)
                            # Envia para o PRIVADO do utilizador e não para o canal
                            irc_conn.send(f"PRIVMSG {user_nick} :[Wikipedia] {resultado}\r\n".encode())

                        # RESPOSTA IA NO CANAL
                        elif NICK.lower() in msg_text.lower():
                            p_clean = re.sub(rf'{NICK}', '', msg_text, flags=re.IGNORECASE).strip()
                            resp = get_ai_response(p_clean)
                            irc_conn.send(f"PRIVMSG {CHANNEL} :{user_nick}: {resp}\r\n".encode())

        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(10)

if __name__ == "__main__":
    threading.Thread(target=run_irc_bot, daemon=True).start()
    
    # Loop de Reforço Positivo
    def pos_loop():
        while True:
            time.sleep(1800)
            if irc_conn:
                try: irc_conn.send(f"PRIVMSG {CHANNEL} :🌟 {random.choice(POSITIVE_REINFORCEMENT)}\r\n".encode())
                except: pass
    threading.Thread(target=pos_loop, daemon=True).start()

    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
