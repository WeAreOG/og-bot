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

# Usamos um modelo da Hugging Face que é gratuito e estável
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
HF_TOKEN = "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" # O teu token

app = Flask(__name__)

# --- 60 FRASES DE BOAS-VINDAS (Fallback Garantido) ---
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
    "Ora aí está o homem! Grande {user}.", "{user}, vieste para o barulho ou para a calma?",
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
    return "TheOG Online", 200

# --- FUNÇÃO DE IA (Hugging Face com Fallback) ---

def get_ai_response(prompt, context="conversa"):
    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        if context == "welcome":
            input_text = f"<s>[INST] Tu és o TheOG. Dá as boas-vindas curtas e engraçadas em Português de Portugal ao utilizador: {prompt} [/INST]</s>"
        else:
            input_text = f"<s>[INST] Responde muito curto em PT-PT como o TheOG: {prompt} [/INST]</s>"
        
        payload = {"inputs": input_text, "parameters": {"max_new_tokens": 50, "temperature": 0.8}}
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=7)
        
        if response.status_code == 200:
            res_json = response.json()
            # Extrair apenas a resposta da IA, removendo o prompt original
            full_text = res_json[0].get('generated_text', '')
            clean_res = full_text.split("[/INST]</s>")[-1].strip()
            return re.sub(r'[\r\n\t]+', ' ', clean_res)
    except Exception as e:
        print(f"Erro IA: {e}")
    
    # Se a IA falhar, usamos a lista de 60 frases (O SEGURO)
    if context == "welcome":
        return random.choice(WELCOME_BASES).format(user=prompt)
    return "Estou sem bateria nos neurónios, pergunta outra vez!"

# --- CORE DO BOT ---

def run_irc_bot():
    while True:
        try:
            print(f"[{time.strftime('%H:%M:%S')}] A ligar a {SERVER}...")
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            irc.settimeout(300)
            irc.connect((SERVER, PORT))
            
            irc.send(f"NICK {NICK}\r\n".encode())
            irc.send(f"USER {NICK} 8 * :TheOG Bot\r\n".encode())

            while True:
                try:
                    line = irc.recv(4096).decode("utf-8", errors="ignore")
                except: break # Se der erro na receção, sai do loop e reconecta
                
                if not line: break

                if line.startswith("PING"):
                    irc.send(f"PONG {line.split()[1]}\r\n".encode())
                    continue

                # Quando o servidor envia o MOTD (fim do login)
                if "376" in line or "422" in line:
                    irc.send(f"PRIVMSG NickServ :IDENTIFY {PASS}\r\n".encode())
                    time.sleep(2)
                    irc.send(f"JOIN {CHANNEL}\r\n".encode())
                    print("No canal!")

                # --- DETETAR ENTRADA (JOIN) ---
                if " JOIN " in line:
                    user_nick = line.split('!')[0][1:]
                    if user_nick.lower() != NICK.lower():
                        welcome_msg = get_ai_response(user_nick, context="welcome")
                        irc.send(f"PRIVMSG {CHANNEL} :{welcome_msg}\r\n".encode())

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
            print(f"Erro Geral: {e}. Reconectar em 10s...")
            time.sleep(10)

if __name__ == "__main__":
    # Inicia o bot
    threading.Thread(target=run_irc_bot, daemon=True).start()
    # Inicia o servidor Web (Flask)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
