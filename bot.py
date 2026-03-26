import socket
import time
import threading
import os
import random
import logging
import sys
import json
from datetime import datetime
from flask import Flask, Response, request, render_template_string

# --- CONFIGURAÇÃO E LOGS ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
LOG_FILE = "chat_log.txt"
irc_socket = None 

SERVER = "irc.ptnet.org"
PORT = 6667
NICK = "TheOG"
PASS = "Nasomet112#"
CHANNEL = "#TheOG"

# --- ESTADO GLOBAL ---
START_TIME = datetime.now()
STALKER_DATA = {}
STALKER_REQUESTS = {}
dados = {}

def force_log(msg):
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_line = f"[{timestamp}] {msg}"
    print(f"[RENDER] {log_line}")
    sys.stdout.flush()
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")
    except: pass

def carregar_dados():
    global dados
    try:
        if os.path.exists('frases.json'):
            with open('frases.json', 'r', encoding='utf-8') as f:
                dados = json.load(f)
                force_log(f"✅ JSON Carregado: {len(dados.get('prendas',[]))} frases de prendas detetadas.")
        else:
            force_log("⚠️ frases.json não encontrado! Usando emergência.")
            dados = {"admins": ["Emergency112", "Padre", "CutxiiiPoint"], "stalker_config": {"alvos_ativos": {}}, "prendas": ["oferece um café a {u}!"], "lapadas": ["dá uma lapada em {u}!"]}
    except Exception as e:
        force_log(f"🔥 Erro no JSON: {e}")

def salvar_dados():
    try:
        with open('frases.json', 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    except: pass

carregar_dados()

def get_uptime():
    delta = datetime.now() - START_TIME
    return f"{delta.days}d {delta.seconds//3600}h {(delta.seconds//60)%60}m"

def send_raw(sock, msg):
    try:
        if sock: sock.send(f"{msg}\r\n".encode('utf-8'))
    except: pass

# --- INTERFACE HTML COM BOTÕES DE ATALHO ---
HTML_CONSOLA = """
<!DOCTYPE html>
<html>
<head>
    <title>TheOG - Consola Master</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #121212; color: #eee; padding: 15px; margin: 0; }
        .container { max-width: 800px; margin: auto; }
        #chat { background: #000; height: 350px; overflow-y: scroll; border: 1px solid #333; padding: 10px; font-family: 'Consolas', monospace; border-radius: 8px; margin-bottom: 10px; font-size: 13px; }
        .controls { display: flex; gap: 5px; margin-bottom: 10px; }
        input[type="text"] { flex-grow: 1; padding: 12px; background: #222; color: #fff; border: 1px solid #444; border-radius: 5px; }
        button { padding: 10px 15px; cursor: pointer; border: none; border-radius: 5px; font-weight: bold; transition: 0.2s; }
        .btn-send { background: #007bff; color: white; }
        .btn-action { background: #28a745; color: white; flex: 1; }
        .btn-lapada { background: #fd7e14; color: white; flex: 1; }
        .btn-clear { background: #dc3545; color: white; width: 100%; margin-top: 20px; }
        button:hover { opacity: 0.8; }
        .actions-bar { display: flex; gap: 10px; margin-bottom: 20px; }
    </style>
    <script>
        function update() {
            fetch('/logs_raw').then(r => r.text()).then(t => {
                const c = document.getElementById('chat');
                c.innerText = t; c.scrollTop = c.scrollHeight;
            });
        }
        setInterval(update, 2500);
    </script>
</head>
<body onload="update()">
    <div class="container">
        <h3>TheOG Console Master</h3>
        <div id="chat">A ler IRC...</div>
        
        <form action="/enviar" method="get" class="controls">
            <input type="hidden" name="pass" value="{{ pass_enviada }}">
            <input type="text" name="msg" placeholder="Escreve aqui..." autofocus autocomplete="off">
            <button type="submit" class="btn-send">Enviar</button>
        </form>

        <div class="actions-bar">
            <form action="/enviar" method="get" style="flex:1; display:flex;">
                <input type="hidden" name="pass" value="{{ pass_enviada }}">
                <input type="hidden" name="msg" value="!prenda">
                <button type="submit" class="btn-action">🎁 Gerar Prenda</button>
            </form>
            <form action="/enviar" method="get" style="flex:1; display:flex;">
                <input type="hidden" name="pass" value="{{ pass_enviada }}">
                <input type="hidden" name="msg" value="!lapada">
                <button type="submit" class="btn-lapada">💥 Dar Lapada</button>
            </form>
        </div>

        <form action="/limpar" method="get">
            <input type="hidden" name="pass" value="{{ pass_enviada }}">
            <button type="submit" class="btn-clear">🗑️ Limpar Histórico do Ecrã</button>
        </form>
    </div>
</body>
</html>
"""

# --- ROTAS FLASK ---
app = Flask(__name__)

@app.route('/consola')
def consola():
    senha = request.args.get('pass')
    if senha != PASS: return "Acesso negado", 403
    return render_template_string(HTML_CONSOLA, pass_enviada=senha)

@app.route('/enviar')
def enviar():
    if request.args.get('pass') == PASS and irc_socket:
        msg = request.args.get('msg')
        send_raw(irc_socket, f"PRIVMSG {CHANNEL} :{msg}")
        force_log(f"VOCÊ (Web): {msg}")
        return f"<script>window.location.href='/consola?pass={PASS}';</script>"
    return "Erro"

@app.route('/limpar')
def limpar():
    if request.args.get('pass') == PASS:
        if os.path.exists(LOG_FILE): os.remove(LOG_FILE)
        force_log("--- Consola Reiniciada ---")
        return f"<script>window.location.href='/consola?pass={PASS}';</script>"
    return "Erro"

@app.route('/logs_raw')
def logs_raw():
    if not os.path.exists(LOG_FILE): return "Vazio."
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return "".join(f.readlines()[-35:])

# --- LÓGICA IRC (STALKER + FRASES) ---
def handle_irc_msg(user, message, is_private, irc):
    global dados
    msg_low = message.lower().strip()
    partes = msg_low.split()
    if not partes: return
    cmd = partes[0]
    target = user if is_private else CHANNEL

    if cmd == "!stalkerpro":
        if user not in dados.get("admins", []): return
        if len(partes) < 2: return
        acao = partes[1]
        if acao == "list":
            vigia = dados.get("stalker_config", {}).get("alvos_ativos", {})
            for a, adm in vigia.items(): send_raw(irc, f"PRIVMSG {user} :🕵️ {a} (por {adm})")
        elif len(partes) > 2:
            alvo = partes[2].lower()
            if acao == "+":
                dados.setdefault("stalker_config", {}).setdefault("alvos_ativos", {})[alvo] = user
                send_raw(irc, f"WATCH +{alvo}")
                send_raw(irc, f"PRIVMSG {user} :🎯 {alvo} vigiado.")
            elif acao == "-":
                if alvo in dados.get("stalker_config", {}).get("alvos_ativos", {}):
                    del dados["stalker_config"]["alvos_ativos"][alvo]
                    send_raw(irc, f"WATCH -{alvo}")
            salvar_dados()

    elif cmd == "!prenda":
        alvo = partes[1] if len(partes) > 1 else user
        f = random.choice(dados.get("prendas", ["oferece um café a {u}"]))
        send_raw(irc, f"PRIVMSG {CHANNEL} :\x01ACTION {f.format(u=alvo)}\x01")

    elif cmd == "!lapada":
        alvo = partes[1] if len(partes) > 1 else user
        f = random.choice(dados.get("lapadas", ["dá uma lapada em {u}"]))
        send_raw(irc, f"PRIVMSG {CHANNEL} :\x01ACTION {f.format(u=alvo)}\x01")

    elif cmd == "!uptime":
        send_raw(irc, f"PRIVMSG {target} :🚀 Uptime: {get_uptime()}")

# --- BOT LOOP ---
def run_bot():
    global irc_socket
    while True:
        try:
            irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc_socket.settimeout(240)
            irc_socket.connect((SERVER, PORT))
            send_raw(irc_socket, f"PASS {PASS}")
            send_raw(irc_socket, f"NICK {NICK}")
            send_raw(irc_socket, f"USER {NICK} 8 * :TheOG Bot")
            
            while True:
                data = irc_socket.recv(4096).decode("utf-8", errors="ignore")
                if not data: break
                for line in data.split("\r\n"):
                    if not line: continue
                    if line.startswith("PING"): send_raw(irc_socket, f"PONG {line.split()[1]}")
                    
                    if " 353 " in line: force_log(f"👥 NO CANAL: {line.split(' :')[-1]}")
                    
                    if " PRIVMSG " in line:
                        u = line.split('!')[0][1:]
                        t = line.split(' PRIVMSG ')[1].split(' :', 1)[1]
                        d = line.split(' PRIVMSG ')[1].split(' :')[0]
                        force_log(f"<{u}> {t}")
                        handle_irc_msg(u, t, d == NICK, irc_socket)
                    
                    if " 376 " in line:
                        send_raw(irc_socket, f"JOIN {CHANNEL}")
                        for a in dados.get("stalker_config", {}).get("alvos_ativos", {}): send_raw(irc_socket, f"WATCH +{a}")
                        force_log(f"🚩 Entrou em {CHANNEL}")
        except: time.sleep(10)

if __name__ == "__main__":
    p = int(os.environ.get("PORT", 5000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=p), daemon=True).start()
    run_bot()
