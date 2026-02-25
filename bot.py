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

HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
HF_TOKEN = "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"

app = Flask(__name__)

# --- 60 FRASES DE BOAS-VINDAS ---
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

# --- 60 FRASES DE REFORÇO POSITIVO (A cada 40 min) ---
POSITIVE_REINFORCEMENT = [
    "Este canal é o melhor spot da PTNet, sem dúvida!", "É um orgulho ter malta tão porreira aqui no #TheOG.",
    "A energia deste canal é outra coisa. Continuem assim!", "Um brinde a todos os que fazem do #TheOG a sua casa.",
    "Sinto que o #TheOG é mais que um canal, é uma família.", "Obrigado por estarem por aqui, vocês são top!",
    "Não há canal com melhor conversa que este.", "A malta do #TheOG é a elite do IRC!",
    "É bom ver que o espírito do IRC continua vivo aqui.", "Mantenham o ambiente positivo, vocês são incríveis!",
    "Obrigado a todos os que mantêm o #TheOG ativo e vibrante.", "Cada um de vocês traz algo único ao canal. Obrigado!",
    "Este canal brilha graças a quem o frequenta.", "O #TheOG é o sítio onde a amizade acontece.",
    "Que bom é partilhar este espaço com pessoas como vocês.", "Respeito e boa onda: a marca do #TheOG!",
    "Vocês são a razão deste bot existir. Grande abraço à malta!", "O #TheOG não seria o mesmo sem a vossa presença.",
    "Continuem a espalhar magia por aqui!", "Este canal é um exemplo de camaradagem.",
    "Aqui no #TheOG ninguém fica de fora.", "A melhor comunidade está aqui!",
    "Obrigado pelas conversas e pelos bons momentos.", "Vocês são o motor deste canal!",
    "Mantenham essa vibe positiva!", "O #TheOG é o nosso refúgio digital.",
    "Não há tédio quando vocês estão por aqui.", "Orgulho nesta malta!",
    "O #TheOG é sinónimo de qualidade.", "É um privilégio ser o vosso bot.",
    "Espalhem sorrisos, o canal agradece!", "A vossa companhia é o melhor deste dia.",
    "O #TheOG é o lugar onde todos têm voz.", "Obrigado pela vossa lealdade ao canal.",
    "Vocês fazem do IRC um lugar melhor.", "Energia positiva atrai coisas boas!",
    "O #TheOG é a prova de que o IRC ainda recomenda-se.", "Um viva a todos os frequentadores habituais!",
    "Obrigado por fazerem parte desta história.", "O ambiente aqui é simplesmente fenomenal.",
    "Dêem valor aos amigos que fazem aqui no canal.", "O #TheOG é o ponto de encontro perfeito.",
    "Vocês são brutais, nunca mudem!", "Partilhar o canal convosco é uma honra.",
    "O #TheOG é o coração da rede!", "Obrigado pela paciência e pela alegria.",
    "Fazer parte desta comunidade é especial.", "Vocês tornam o meu código mais feliz!",
    "A vossa presença é o que dá vida ao #TheOG.", "O canal está em boas mãos convosco.",
    "Respeitem-se e divirtam-se, esse é o lema!", "O #TheOG é feito de gente boa.",
    "Obrigado por tornarem este canal tão acolhedor.", "A elite da conversa está aqui reunida.",
    "Mantenham o foco no que é bom!", "O #TheOG é a nossa segunda casa.",
    "Vocês são a alma deste projeto.", "Obrigado por darem cor ao #TheOG.",
    "Um abraço virtual para todos os presentes!", "O #TheOG é onde a conversa nunca morre."
]

irc_conn = None # Variável global para o socket

def send_positive_msg():
    global irc_conn
    while True:
        time.sleep(2400) # 40 minutos (40 * 60 segundos)
        if irc_conn:
            try:
                msg = random.choice(POSITIVE_REINFORCEMENT)
                irc_conn.send(f"PRIVMSG {CHANNEL} :🌟 {msg}\r\n".encode())
                print(f"[{time.strftime('%H:%M:%S')}] Reforço positivo enviado.")
            except:
                pass

def get_ai_response(prompt, context="conversa"):
    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        if context == "welcome":
            input_text = f"<s>[INST] Dá as boas-vindas a {prompt} em Português de Portugal. Curto e informal. [/INST]</s>"
        else:
            input_text = f"<s>[INST] Responde em Português de Portugal, muito curto: {prompt} [/INST]</s>"
        
        payload = {"inputs": input_text, "parameters": {"max_new_tokens": 40, "temperature": 0.7}}
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=5)
        
        if response.status_code == 200:
            full_text = response.json()[0].get('generated_text', '')
            clean_res = full_text.split("[/INST]</s>")[-1].strip()
            if clean_res:
                return re.sub(r'[\r\n\t]+', ' ', clean_res)
    except:
        pass
    
    if context == "welcome":
        return random.choice(WELCOME_BASES).format(user=prompt)
    return "Tudo tranquilo por aqui!"

def run_irc_bot():
    global irc_conn
    while True:
        try:
            print(f"[{time.strftime('%H:%M:%S')}] A ligar...")
            irc_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc_conn.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            irc_conn.connect((SERVER, PORT))
            
            irc_conn.send(f"NICK {NICK}\r\n".encode())
            irc_conn.send(f"USER {NICK} 8 * :TheOG Bot\r\n".encode())

            while True:
                line = irc_conn.recv(4096).decode("utf-8", errors="ignore")
                if not line: break

                if line.startswith("PING"):
                    irc_conn.send(f"PONG {line.split()[1]}\r\n".encode())
                    continue

                if "376" in line or "422" in line:
                    irc_conn.send(f"PRIVMSG NickServ :IDENTIFY {PASS}\r\n".encode())
                    time.sleep(2)
                    irc_conn.send(f"JOIN {CHANNEL}\r\n".encode())

                if " JOIN " in line:
                    user_nick = line.split('!')[0][1:]
                    if user_nick.lower() != NICK.lower():
                        msg = get_ai_response(user_nick, context="welcome")
                        irc_conn.send(f"PRIVMSG {CHANNEL} :{msg}\r\n".encode())

                if "PRIVMSG" in line:
                    user = line.split('!')[0][1:]
                    if user.lower() == NICK.lower(): continue
                    
                    msg_match = re.search(f"PRIVMSG {CHANNEL} :(.+)", line)
                    if msg_match:
                        msg_content = msg_match.group(1).strip()
                        if NICK.lower() in msg_content.lower():
                            p_clean = re.sub(rf'{NICK}', '', msg_content, flags=re.IGNORECASE).strip()
                            resp = get_ai_response(p_clean)
                            irc_conn.send(f"PRIVMSG {CHANNEL} :{user}: {resp}\r\n".encode())

        except Exception as e:
            print(f"Erro: {e}. Reconectar em 10s...")
            time.sleep(10)

if __name__ == "__main__":
    # Thread para o Bot IRC
    threading.Thread(target=run_irc_bot, daemon=True).start()
    # Thread para as Mensagens de Reforço (40 min)
    threading.Thread(target=send_positive_msg, daemon=True).start()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
