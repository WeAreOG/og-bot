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

# Nicks que o bot deve ignorar completamente (não cumprimentar)
BOT_FILTER = ["nickserv", "chanserv", "memoserv", "operserv", "adamastor", "statserv"]

HF_API_URL = "https://api-inference.huggingface.co/models/deepseek-ai/DeepSeek-V3"
HF_TOKEN = "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"

app = Flask(__name__)

# --- 30 FRASES DE REENTRADA ---
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
    "O {user} é the best! Bem-vindo.", "Saudações {user}, a malta saúda-te.",
    "Viva {user}, que bom ter-te connosco!", "O {user} chegou para pôr ordem nisto!",
    "Bem-vindo {user}, o canal estava morto sem ti.", "Viva {user}, brilha aí!",
    "O {user} é o nosso herói hoje!", "Saudações {user}, que bom ver-te.",
    "Boas {user}, entra e desfruta!", "Aí está o {user}, que maravilha.",
    "Bem-vindo {user}, o melhor de sempre!", "O {user} entrou, o céu é o limite!",
    "Viva {user}, estamos contigo!", "Boas {user}, sê muito feliz aqui!",
    "Grande {user}, que força a tua!", "Bem-vindo {user}, o canal sorri!",
    "O {user} chegou, tudo a postos!", "Viva {user}, o mestre da palavra!",
    "Boas {user}, o canal estava à tua espera!", "Saudações {user}, entra em grande!"
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
    "Mantenham-se fantásticos como são!", "O #TheOG é o vosso legado.",
    "Obrigado pela vossa luz aqui.", "Um viva à nossa união!",
    "O #TheOG é o topo da rede!", "Obrigado pela vossa alegria infinita.",
    "Sempre juntos no #TheOG!", "Este é o nosso espaço sagrado.",
    "Vocês dão sentido ao chat.", "Obrigado pela vossa bondade.",
    "O #TheOG é onde tudo brilha!", "Sempre em frente, equipa!",
    "Vocês são a essência do IRC.", "Obrigado por serem tão especiais."
]

# --- FUNÇÕES ---

def get_wiki(subject):
    try:
        url = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{subject.replace(' ', '_')}"
        res = requests.get(url, timeout=5).json()
        if "extract" not in res: return "Não encontrei nada sobre isso na Wikipedia."
        return res["extract"][:450] + "..."
    except: return "Erro ao consultar a Wikipedia."

def get_ai_response(prompt, context="canal"):
    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
        system_p = "Tu és o TheOG, bot de IRC tuga, informal. Responde curto em PT-PT."
        payload = {
            "inputs": f"{system_p} Utilizador: {prompt}\nTheOG:",
            "parameters": {"max_new_tokens": 60, "temperature": 0.6}
        }
        res = requests.post(HF_API_URL, headers=headers, json=payload, timeout=10)
        if res.status_code == 200:
            text = res.json()[0]['generated_text']
            return text.split("TheOG:")[-1].strip()
    except: pass
    return "Tudo tranquilo!"

# --- MOTOR IRC ---
irc_conn = None

def run_irc_bot():
    global irc_conn
    while True:
        try:
            irc_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
                    time.sleep(6)
                    irc_conn.send(f"JOIN {CHANNEL}\r\n".encode())
                    time.sleep(1)
                    irc_conn.send(f"PRIVMSG {CHANNEL} :{random.choice(REENTRY_PHRASES)}\r\n".encode())

                # --- Lógica de JOIN com Filtro ---
                if " JOIN " in line:
                    u = line.split('!')[0][1:]
                    # IGNORA bots e o próprio nick
                    if u.lower() not in BOT_FILTER and u.lower() != NICK.lower():
                        msg = random.choice(WELCOME_BASES).format(user=u)
                        irc_conn.send(f"PRIVMSG {CHANNEL} :{msg}\r\n".encode())

                if "PRIVMSG" in line:
                    user_nick = line.split('!')[0][1:]
                    if user_nick.lower() == NICK.lower(): continue

                    # QUERY (PRIVADO)
                    if f"PRIVMSG {NICK} :" in line:
                        pvt_c = line.split(f"PRIVMSG {NICK} :", 1)[1].strip()
                        # Se não for o NickServ a mandar instruções, responde com IA
                        if user_nick.lower() not in ["nickserv", "chanserv"]:
                            resp = get_ai_response(pvt_c, context="pvt")
                            irc_conn.send(f"PRIVMSG {user_nick} :{resp} (Fala no canal!)\r\n".encode())
                        continue

                    # CANAL
                    msg_match = re.search(f"PRIVMSG {CHANNEL} :(.+)", line)
                    if msg_match:
                        cmd = msg_match.group(1).strip()
                        if cmd.lower() == "!comandos":
                            irc_conn.send(f"NOTICE {user_nick} :Comandos: !wiki [tema], !comandos.\r\n".encode())
                        elif cmd.lower().startswith("!wiki "):
                            irc_conn.send(f"NOTICE {user_nick} :Wikipedia: {get_wiki(cmd[6:])}\r\n".encode())
                        elif NICK.lower() in cmd.lower():
                            p = re.sub(rf'{NICK}', '', cmd, flags=re.IGNORECASE).strip()
                            irc_conn.send(f"PRIVMSG {CHANNEL} :{user_nick}: {get_ai_response(p)}\r\n".encode())

        except Exception: time.sleep(10)

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
