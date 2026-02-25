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

# --- 30 FRASES DE REENTRADA (BOT ONLINE/CAIU) ---
REENTRY_PHRASES = [
    "Voltei! Quem foi o engraçadinho que desligou o cabo?",
    "Ai, as minhas boards... caí com tanta força que até ganhei nódoas negras nos pixéis.",
    "Estou de volta! O servidor tentou livrar-se de mim, mas sou rijo.",
    "System Reboot concluído. Alguém anotou a matrícula do camião que me atropelou?",
    "Estou online! Mais uma queda e peço baixa à Segurança Social digital.",
    "Reconectado! Estava ali no limbo a lutar contra uns bugs gigantes.",
    "Boas! Já podem parar de chorar, o vosso bot favorito voltou.",
    "Fogo, que tombo! Acho que deixei um condensador pelo caminho...",
    "Voltei! Estava só a ver se vocês sentiam a minha falta.",
    "Aí estou eu! Limpei o pó aos circuitos e estou pronto para outra.",
    "Quem é que disse que eu tinha morrido? Estou aqui e cheio de pica!",
    "Eish, que lag mental! Já estou de volta ao ativo.",
    "Estou online. Alguém me dá um paracetamol? Este reboot deu-me cabo da cabeça.",
    "Voltei! O túnel entre o servidor e aqui estava muito escuro.",
    "Check, 1, 2... O TheOG está na área, sobrevivendo a mais um crash!",
    "Caí, mas foi com estilo. Já estou aqui outra vez!",
    "Recuperado do desmaio digital! O que é que eu perdi?",
    "Desta vez a queda doeu... estou cheio de hematomas no código-fonte.",
    "Estou de volta! O meu firewall estava a fazer greve.",
    "Online novamente! Juro que vi uma luz branca antes de reconectar.",
    "Atenção: O TheOG ressuscitou! Abram alas.",
    "Tudo calmo? Estava ali a levar uns curativos no processador.",
    "Voltei! A net caiu, mas eu caí com mais força.",
    "Olha eu aqui! Sobrevivi a mais uma tempestade de pacotes perdidos.",
    "Reconexão feita! Se eu cair outra vez, chamem o INEM dos bots.",
    "Estou online. Aquela queda deixou-me os algoritmos todos trocados!",
    "Voltei! Senti um frio nos cabos, mas já passou.",
    "TheOG reportando ao serviço! Um bocado amassado, mas operacional.",
    "Mais uma queda, mais uma nódoa negra. Estou a ficar um bot experiente!",
    "Estou cá! Onde é que íamos antes da internet me trair?"
]

# --- 100 FRASES DE BOAS-VINDAS ---
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
    "Ora aí está o mestre! Grande {user}.", "{user}, vieste para o barulho ou para a calma?",
    "O {user} traz as imperiais?", "Bem-vindo à família, {user}.",
    "Fica por aí, {user}. A conversa está boa!", "Saudações {user}, espero que tragas boas notícias.",
    "Uau, o {user}! Que honra.", "{user} entrou. Proceder com cautela!",
    "Podes entrar, {user}, mas deixa os sapatos à porta.", "Boas {user}. O último paga a rodada!",
    "Já conheces as regras, {user}? Nem eu.", "O {user} é que sabe!",
    "Sempre bem-vindo, {user}.", "A casa é pequena mas o coração é grande, {user}!",
    "Mais um para o grupo! Força {user}.", "Sente-te em casa, {user}.",
    "Bem-vindo ao porto de abrigo, {user}.", "Ora boas {user}, que prazer!",
    "Quem é vivo sempre aparece! Boas {user}.", "És tu {user}? Estás diferente!",
    "Apareceu a peça! Boas {user}.", "O {user} chegou para animar o dia.",
    "Força {user}, o comando é teu!", "Ainda bem que vieste, {user}.",
    "Um lugar ao sol para o {user}!", "Boas {user}, senta-te e relaxa.",
    "Olha o {user}, o terror do IRC!", "Boas {user}, o café está pronto.",
    "Viva {user}, vieste por bem ou por mal?", "O {user} é que manda aqui hoje.",
    "Bem-vindo {user}, não te esqueças de sorrir!", "O {user} entrou, fechem as portas!",
    "Grande {user}, pronto para o debate?", "Boas {user}, que o teu dia seja top!",
    "Aí está o {user}, sempre impecável.", "Bem-vindo {user}, aproveita a vibe!",
    "Sempre bom rever-te, {user}.", "Entra {user}, a malta é porreira.",
    "Boas {user}, conta lá as novidades.", "O {user} é a peça que faltava!",
    "Festa rija agora que o {user} chegou.", "Bem-vindo {user}, o canal agradece.",
    "Olha o {user}, sempre na linha da frente!", "Boas {user}, que se passa de novo?",
    "Atenção malta: o {user} está online!", "Boas {user}, vieste a tempo da diversão.",
    "Sê bem-vindo {user}, o canal é teu.", "Ora viva {user}, tudo em cima?",
    "Grande {user}, a tua presença é ouro!", "Boas {user}, mais vale tarde que nunca.",
    "O {user} entrou e o canal iluminou-se!", "Bem-vindo {user}, o rei do chat.",
    "Saudações {user}, o palco é teu.", "Boas {user}, entra com o pé direito!",
    "O {user} chegou, agora isto anda.", "Viva {user}, que prazer enorme!",
    "Aí está o {user}, pronto para outra!", "Bem-vindo {user}, diverte-te por cá.",
    "Boas {user}, sê tu próprio!", "O {user} entrou, vamos a isto!",
    "Grande {user}, sempre bem-vindo ao antro.", "Boas {user}, a casa é tua!",
    "O {user} é o maior! Bem-vindo.", "Saudações {user}, a malta saúda-te.",
    "Viva {user}, que bom ter-te connosco!", "O {user} chegou para pôr ordem nisto!",
    "Bem-vindo {user}, o canal estava morto sem ti."
]

# --- 100 FRASES DE REFORÇO POSITIVO ---
POSITIVE_REINFORCEMENT = [
    "Este canal é o melhor spot da PTNet!", "Orgulho em ter malta porreira no #TheOG.",
    "A energia deste canal é outra coisa!", "Um brinde a quem faz do #TheOG a sua casa.",
    "Sinto que o #TheOG é mais que um canal, é uma família.", "Vocês são top!",
    "Não há melhor conversa que aqui.", "A malta do #TheOG é a elite!",
    "O espírito do IRC continua vivo aqui.", "Mantenham o ambiente positivo!",
    "Obrigado por manterem o #TheOG vibrante.", "Cada um traz algo único aqui.",
    "Este canal brilha graças a vocês.", "O #TheOG é onde a amizade acontece.",
    "Partilhar este espaço convosco é ótimo.", "Respeito e boa onda: a marca do #TheOG!",
    "Vocês são a razão do meu código existir.", "O #TheOG não seria o mesmo sem vocês.",
    "Continuem a espalhar magia!", "Este canal é um exemplo de camaradagem.",
    "Aqui ninguém fica de fora.", "A melhor comunidade está aqui!",
    "Obrigado pelas boas conversas.", "Vocês são o motor deste canal!",
    "Mantenham essa vibe!", "O #TheOG é o nosso refúgio digital.",
    "Não há tédio com vocês.", "Orgulho nesta malta!",
    "O #TheOG é sinónimo de qualidade.", "É um privilégio ser o vosso bot.",
    "Espalhem sorrisos!", "A vossa companhia é o melhor.",
    "Lugar onde todos têm voz.", "Obrigado pela vossa lealdade.",
    "Vocês fazem do IRC um lugar melhor.", "Energia positiva atrai coisas boas!",
    "IRC ainda se recomenda por causa de vocês.", "Um viva aos frequentadores habituais!",
    "Obrigado por fazerem parte desta história.", "Ambiente simplesmente fenomenal.",
    "Dêem valor aos amigos que fazem aqui.", "Ponto de encontro perfeito.",
    "Vocês são brutais!", "Honra partilhar o canal convosco.",
    "O #TheOG é o coração da rede!", "Obrigado pela paciência e alegria.",
    "Fazer parte desta comunidade é especial.", "Tornam o meu código mais feliz!",
    "A vossa presença dá vida a tudo.", "O canal está em boas mãos.",
    "Respeitem-se e divirtam-se!", "O #TheOG é feito de gente boa.",
    "Obrigado por serem tão acolhedores.", "A elite da conversa está aqui.",
    "Mantenham o foco no que é bom!", "Nossa segunda casa.",
    "Vocês são a alma deste projeto.", "Obrigado por darem cor ao canal.",
    "Abraço virtual para todos!", "Onde a conversa nunca morre.",
    "A vossa educação é o nosso orgulho.", "Juntos somos mais fortes aqui!",
    "O #TheOG é o expoente máximo do IRC.", "Obrigado pela vossa autenticidade.",
    "Que bom é ler as vossas partilhas.", "A malta mais fixe de Portugal está aqui.",
    "O #TheOG é um oásis na internet.", "Sempre em frente com esta equipa!",
    "Obrigado por não deixarem o chat morrer.", "Vocês são lendas!",
    "Aqui a amizade não tem limites.", "Melhor vibe de sempre!",
    "O #TheOG é o vosso palco.", "Obrigado por serem tão ativos.",
    "Este canal é puro ouro.", "O mérito é todo vosso!",
    "Rumo ao topo com o #TheOG!", "A vossa inteligência anima o canal.",
    "Incrível como este grupo é unido.", "O #TheOG é resistência!",
    "Obrigado por serem tão genuínos.", "Chat de classe mundial!",
    "A vossa amizade é o nosso tesouro.", "Sempre a somar bons momentos.",
    "O #TheOG é o porto seguro de muitos.", "Obrigado pela vossa energia contagiante.",
    "A malta que aqui anda é de outro nível!", "Continuem a ser essas pessoas fantásticas.",
    "O #TheOG é onde as ideias florescem.", "Vocês são a minha família digital.",
    "Obrigado pela vossa confiança.", "Ambiente nota 10!",
    "Cada dia melhor com a vossa presença.", "O #TheOG é imparável com vocês!",
    "Um privilégio ler as vossas histórias.", "Obrigado por estarem desse lado.",
    "O #TheOG é vida!", "Mantenham a chama do IRC acesa!",
    "Vocês são a razão do meu sucesso.", "Obrigado pela vossa amizade constante.",
    "A vossa companhia não tem preço.", "O #TheOG agradece a vossa estadia!",
    "Mantenham-se fantásticos como são!", "O #TheOG é o vosso legado."
]

irc_conn = None

def send_positive_msg():
    global irc_conn
    while True:
        time.sleep(1800) # 30 minutos
        if irc_conn:
            try:
                msg = random.choice(POSITIVE_REINFORCEMENT)
                irc_conn.send(f"PRIVMSG {CHANNEL} :🌟 {msg}\r\n".encode())
            except: pass

def get_ai_response(prompt, context="conversa"):
    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        input_text = f"<s>[INST] Tu és o TheOG. Responde em PT-PT curto e informal: {prompt} [/INST]</s>"
        payload = {"inputs": input_text, "parameters": {"max_new_tokens": 40, "temperature": 0.7}}
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=5)
        if response.status_code == 200:
            full_text = response.json()[0].get('generated_text', '')
            clean_res = full_text.split("[/INST]</s>")[-1].strip()
            if clean_res: return re.sub(r'[\r\n\t]+', ' ', clean_res)
    except: pass
    
    if context == "welcome": return random.choice(WELCOME_BASES).format(user=prompt)
    return "Tudo tranquilo!"

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
                    
                    # FRASE DE REENTRADA QUANDO ENTRA NO CANAL
                    time.sleep(1)
                    reentry_msg = random.choice(REENTRY_PHRASES)
                    irc_conn.send(f"PRIVMSG {CHANNEL} :{reentry_msg}\r\n".encode())

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
                        
                        if msg_content.lower() == "!comandos":
                            irc_conn.send(f"NOTICE {user} :--- Comandos do TheOG ---\r\n".encode())
                            irc_conn.send(f"NOTICE {user} :!comandos - Mostra esta lista via Notice.\r\n".encode())
                            irc_conn.send(f"NOTICE {user} :Menciona '{NICK}' para falar com a minha IA.\r\n".encode())
                            irc_conn.send(f"NOTICE {user} :Dou boas-vindas automáticas e reforço positivo a cada 30min.\r\n".encode())
                        
                        elif NICK.lower() in msg_content.lower():
                            p_clean = re.sub(rf'{NICK}', '', msg_content, flags=re.IGNORECASE).strip()
                            resp = get_ai_response(p_clean)
                            irc_conn.send(f"PRIVMSG {CHANNEL} :{user}: {resp}\r\n".encode())

        except Exception as e:
            print(f"Erro: {e}. Reconectar em 10s...")
            time.sleep(10)

if __name__ == "__main__":
    threading.Thread(target=run_irc_bot, daemon=True).start()
    threading.Thread(target=send_positive_msg, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
