import socket
import time
import threading
import random
import requests
import os
from flask import Flask

# --- CONFIGURAÇÕES GERAIS ---
SERVER = "irc.ptnet.org"
PORT = 6667
CHANNEL = "#TheOG"
HF_TOKEN = "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"
API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"

# Lista de utilizadores fictícios para encher o canal
# Formato: (NICK, IDENT, REALNAME, PASSWORD)
USERS_TO_LOAD = [
    ("ThePretender", "pretender", "Viajante do Tempo", "SenhaPretender123"),
    ("LusoPuto", "luso", "Estudante de LX", "SenhaLuso123"),
    ("MistycGirl", "mistyc", "Nas estrelas", "SenhaMistyc123")
]

app = Flask(__name__)

def send_raw(sock, msg):
    try:
        sock.send(f"{msg}\r\n".encode('utf-8'))
    except:
        pass

def ask_ai(question, nick_name):
    headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
    prompt = (f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n"
              f"Tu és o {nick_name}, um utilizador do canal #TheOG. "
              f"Fala como um jovem de Portugal (calão leve: 'pá', 'tá-se', 'fixe'). "
              f"Respostas muito curtas e humanas. Não admitas que és um bot.<|eot_id|>"
              f"<|start_header_id|>user<|end_header_id|>\n{question}<|eot_id|>"
              f"<|start_header_id|>assistant<|end_header_id|>\n")
    
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 50, "temperature": 0.8}}
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            res = response.json()
            full_text = res[0]['generated_text'] if isinstance(res, list) else res.get('generated_text', "")
            return full_text.split("assistant")[-1].strip().replace("|", "")
    except:
        return "Agora não posso falar, pá."
    return "..."

def bot_instance(nick, ident, realname, password):
    while True:
        try:
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.connect((SERVER, PORT))
            
            send_raw(irc, f"USER {ident} 8 * :{realname}")
            send_raw(irc, f"NICK {nick}")
            
            while True:
                data = irc.recv(4096).decode("utf-8", errors="ignore")
                if not data: break
                
                for line in data.split("\r\n"):
                    if "PING" in line:
                        send_raw(irc, f"PONG {line.split()[1]}")

                    if "376" in line:
                        send_raw(irc, f"PRIVMSG NickServ :IDENTIFY {password}")
                        time.sleep(3)
                        send_raw(irc, "PRIVMSG HostServ :ON")
                        send_raw(irc, f"MODE {nick} +g")
                        send_raw(irc, f"JOIN {CHANNEL}")
                    
                    if " PRIVMSG " in line:
                        user = line.split('!')[0][1:]
                        msg_content = line.split(" :", 1)[1] if " :" in line else ""
                        
                        if nick.lower() in msg_content.lower() or f"PRIVMSG {nick}" in line:
                            if user.lower() not in ["nickserv", "chanserv", "theog", nick.lower()]:
                                resposta = ask_ai(msg_content, nick)
                                target = CHANNEL if " #" in line else user
                                send_raw(irc, f"PRIVMSG {target} :{user}: {resposta}")
        except:
            time.sleep(30)

@app.route('/')
def home():
    return "ThePretender Crew - Operacional no Koyeb!"

if __name__ == "__main__":
    for u_nick, u_ident, u_real, u_pass in USERS_TO_LOAD:
        threading.Thread(target=bot_instance, args=(u_nick, u_ident, u_real, u_pass), daemon=True).start()
        time.sleep(10)
        
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
