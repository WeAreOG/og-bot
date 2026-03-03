import socket
import time
import threading
import os
import random
from datetime import datetime
from flask import Flask

# --- CONFIGURAÇÕES ---
SERVER = "irc.ptnet.org"
PORT = 6667
NICK = "TheOG"
PASS = "Nasomet112#" 
CHANNEL = "#TheOG"
BOT_FILTER = ["nickserv", "chanserv", "memoserv", "operserv", "adamastor", "statserv", "secure", "authserv", "irc", "theog"]

app = Flask(__name__)
LAST_SEEN = {}  # Regista {nick: timestamp} para monitorizar inatividade

# --- MONITOR DE LOGS ---
def log_presenca(user, accao):
    hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"[{hora}] {user} {accao}")

# --- TEXTO DA HISTÓRIA ---
HISTORIA_THEOG = [
    "Estamos a construir a história com base em cada um dos utilizadores."
]

# --- 100 PRENDAS ASCII ---
PRENDAS = [
    "---@>>-- (uma Rosa)", "---{---(@ (uma Flor)", "@->-- (Botão)", "---<@>--- (Margarida)",
    "  <3  (Coração)", " <3 <3 (Dois Corações)", " ( <3 ) (Abraço)", " [PRENDA] (Caixa)",
    "---}---* (Flor Campo)", "---@>-- (Tulipa)", " :-* (Beijo)", " ( ^_^ ) (Sorriso)",
    " ((_)) (Abraço)", "---ooo--- (Colar)", " ()-=-() (Anel Amizade)", " \o/ (Festa!)",
    "---[*]-- (Flor Mágica)", " O-- (Pirulito)", " [_] (Chá)", " ( ^_^)っ☕ (Café)",
    " [🍀] (Trevo)", " ♪♫🎶 (Música)", " (🎁) (Presente)", " <>< (Peixinho)",
    "---@>>--", "---{---(@", "@->--", "---<@>---", " <3 ", " <3<3 ", " [LOVE] ", " [MIMO] ",
    " [DOCE] ", " :-P ", " ( ^.^ ) ", "---ooo---", " ()-=-() ", " \o/ ", "---[*]--",
    " [BOLO] ", " [SORVETE] ", " [ESTRELA] ", " [BALÃO] ", " [CHAVE] ", " [LIVRO] ", " [MÚSICA] ",
    " [SOL] ", " [LUA] ", " [MAR] ", " [PAZ] ", " [LUZ] ", " [SORTE] ", " [FORÇA] ", " [UNIÃO] ",
    "---@>>--", "---{---(@", "@->--", "---<@>---", " <3 ", " <3 <3 ", " ( <3 ) ", " [MIMO] ",
    "---}---*", "---@>--", "---E>--", " :-* ", " ( ^_^ ) ", " (( )) ", "---ooo---", " ()-=-() ",
    " \o/ ", "---[*]--", " O-- ", " [cafe] ", "---@>>--", "---{---(@", "@->--", "---<@>---",
    " <3 ", " <3<3 ", " ( <3 ) ", " [BJINHO] ", "---}---*", "---@>--", "---E>--", " :-P ",
    " ( ^.^ ) ", " ((_)) ", "---ooo---", " ()-=-() ", " \o/ ", "---[*]--", " O-- ", " [_] ",
    " [SOL] ", " [LUA] ", " [MAR] ", " [PAZ] ", " [LUZ] ", " [SORTE] ", " [FORÇA] ", " [UNIÃO] "
]

# --- 60 FRASES DE ENTRADA (BOT) ---
OG_ENTRANCE = [
    "Conexão estabelecida. O #TheOG ganha vida!", "Status: Online. Preparando a melhor energia para o canal.",
    "Ressurgi das cinzas digitais. Olá mundo!", "TheOG conectado. Que comece o convívio!",
    "Liguem os motores, o bot da casa já cá canta!", "A lenda voltou. Podem soltar os foguetes.",
    "Fui ali atualizar o núcleo e já estou de volta.", "O canal fica 100% melhor agora.",
    "Bot carregado, café virtual servido. Vamos a isto!", "Mais um dia, mais um milhão de bytes de alegria.",
    "Sentiram o lag? Foi a minha entrada triunfal!", "Apareci! Quem manda nisto hoje?",
    "TheOG a reportar para o serviço. Vibe máxima!", "O vosso assistente favorito acabou de aterrar.",
    "Reconectado com sucesso. Tudo calmo por aqui?", "A inteligência (artificial) entrou no chat.",
    "Não entrem em pânico, o TheOG chegou.", "Voltei! Estava só a polir os meus bits.",
    "Saudações! O mestre do código está on.", "O algoritmo da felicidade foi ativado.",
    "Batam palmas (em ASCII), eu cheguei!", "Entrei com o pé direito. Olá canal!",
    "TheOG na área, sem medo de avarias ou reboots.", "Boas malta! O TheOG traz boas vibrações.",
    "Atenção: O bot mais porreiro do servidor entrou.", "Cheguei! Alguém falou em festa?",
    "TheOG: A versão mais fresca acabou de ligar.", "Estava a ver a novela, mas o dever chamou.",
    "O #TheOG brilha mais agora.", "Status: Prontidão total.", "Boas! Estava a ver o Preço Certo.",
    "O porto de abrigo está oficialmente aberto.", "Vejam só quem voltou do limbo digital.",
    "TheOG online: Ignorando perguntas difíceis desde agora.", "Cheguei com prendas virtuais na mochila!",
    "O canal agora está completo. Podem relaxar.", "A espera acabou. O bot está no posto.",
    "Saudações humanos! O TheOG está em órbita.", "TheOG: O bot que nunca dorme (quase nunca).",
    "Entrei! Quem paga a rodada virtual?", "TheOG na casa! Tragam a música.",
    "O mestre voltou para vigiar a porta.", "Acabei de aterrar. Qual é a novidade?",
    "O vosso porto seguro no IRC está online.", "TheOG a entrar em modo de alta performance.",
    "Olá família! O bot da casa já está nos comandos.", "Sempre pronto para o próximo byte.",
    "A dose diária de positividade acabou de chegar.", "Estava a ver se a vizinha emprestava RAM.",
    "TheOG: Ativado e com vontade de conversar.", "Cheguei! Trouxeram as bolachas?",
    "O #TheOG celebra a vossa presença.", "Voltei! Não vivam sem este código.",
    "O sistema está estável. Vamos animar isto!", "Sentiram a minha falta? Eu sei que sim.",
    "TheOG na área! Vamos criar memórias.", "A alma do canal está de volta ao servidor.",
    "Status: A espalhar magia por todo o lado.", "Olá a toda a gente! O TheOG conectou.",
    "Preparem os teclados, o bot está ativo!"
]

# --- 60 SAUDAÇÕES A USERS (GÉNERO NEUTRO) ---
USER_GREETINGS = [
    "Boas-vindas {u}! É bom ter alguém como tu por cá.", "Olá {u}! Que a tua estadia no #TheOG seja fantástica.",
    "Saudações {u}! Sente-te em casa.", "Olha quem chegou! Boas-vindas {u}!",
    "Olá {u}! Que bom ver-te por aqui hoje.", "{u}, o #TheOG brilha mais com a tua presença!",
    "Boas {u}! Entra e partilha a tua boa energia.", "Olá {u}! Estávamos à tua espera para animar o canal.",
    "Saudações {u}! Que o teu dia seja tão brilhante como o teu nick.", "Boas-vindas {u}! Prepara o teclado e diverte-te.",
    "Olá {u}! Mais uma presença incrível para o nosso grupo.", "{u}, que alegria receber-te no nosso porto de abrigo!",
    "Boas {u}! Este canal é o teu espaço.", "Olá {u}! Junta-te à conversa, não tenhas vergonha.",
    "Saudações {u}! A amizade é o nosso melhor protocolo.", "Boas-vindas {u}! O IRC ainda vive graças a gente assim!",
    "Olá {u}! Que a paz e a alegria te acompanhem por aqui.", "{u}, recebemos-te de braços abertos!",
    "Boas {u}! O cursor pisca de felicidade com a tua entrada.", "Olá {u}! Estás em casa, no #TheOG.",
    "Saudações {u}! Que tenhas ótimas conversas hoje.", "Boas-vindas {u}! A autenticidade mora neste canal.",
    "Olá {u}! É um prazer contar com a tua companhia.", "{u}, traz a tua luz para este chat!",
    "Boas {u}! O segredo do #TheOG é cada pessoa que aqui entra.", "Olá {u}! Vamos construir boas memórias juntos?",
    "Saudações {u}! Onde a palavra é nua e a amizade é real.", "Boas-vindas {u}! Ficamos contentes com a tua chegada.",
    "Olá {u}! Sente o calor deste grupo digital.", "{u}, o teu lugar está reservado!",
    "Boas {u}! Um sorriso virtual para ti.", "Olá {u}! Que o teu teclado esteja inspirado hoje.",
    "Saudações {u}! És parte fundamental deste refúgio.", "Boas-vindas {u}! O canal estava a precisar de ti.",
    "Olá {u}! Entra, o café virtual é por conta da casa.", "{u}, obrigado por escolheres o #TheOG!",
    "Boas {u}! Vamos celebrar a presença de mais alguém especial.", "Olá {u}! A alma do IRC reside em ti.",
    "Saudações {u}! Que o teu dia seja calmo e produtivo.", "Boas-vindas {u}! Aqui não há filtros, só pessoas reais.",
    "Olá {u}! A tua energia é contagiante.", "{u}, que bom ver esse nick na lista!",
    "Boas {u}! Já sabes, qualquer coisa é só teclar.", "Olá {u}! O #TheOG saúda a tua chegada.",
    "Saudações {u}! Um brinde à tua presença!", "Boas-vindas {u}! Faz de cada palavra um bit de luz.",
    "Olá {u}! O porto de abrigo está sempre aberto para ti.", "{u}, chegaste no momento certo!",
    "Boas {u}! Alegria em ver-te novamente.", "Olá {u}! Vamos espalhar positividade?",
    "Saudações {u}! O mestre do código dá-te as boas-vindas.", "Boas-vindas {u}! Que a tua conexão seja estável e o coração feliz.",
    "Olá {u}! Este grupo fica mais rico contigo.", "{u}, a tua voz escrita é importante aqui!",
    "Boas {u}! Respeito e amizade sempre.", "Olá {u}! Desfruta do melhor do IRC.",
    "Saudações {u}! A tua essência é o que nos move.", "Boas-vindas {u}! Prepara-te para bons momentos.",
    "Olá {u}! Que a conversa flua como água.", "{u}, a casa é tua!"
]

# --- 120 FRASES DE REFORÇO POSITIVO (Expandido) ---
REFORCO_POSITIVO = [
    "A vossa energia é o que faz o #TheOG ser especial! ✨", "Lembrem-se: o IRC é o último baluarte da palavra verdadeira.",
    "Um sorriso virtual para todos os que habitam este canal hoje! 😊", "A amizade é o melhor protocolo de comunicação.",
    "Obrigado por estarem aqui. Vocês são a alma do #TheOG.", "Cada mensagem vossa é um bit de alegria no meu sistema.",
    "Mantenham a vibe positiva, a vida corre melhor assim! 🌟", "O #TheOG é o vosso porto de abrigo. Sintam-se em casa.",
    "A vossa presença é o que transforma este código em vida.", "Partilhem boas palavras, o mundo já tem ruído suficiente.",
    "Um brinde à autenticidade de quem ainda usa IRC! 🥂", "Vocês são incríveis, nunca se esqueçam disso.",
    "O cursor pisca ao ritmo dos vossos corações. 💓", "Respirem fundo e aproveitem o momento presente.",
    "A sabedoria reside na partilha. Obrigado por estarem aqui!", "O #TheOG brilha mais com cada um de vocês.",
    "Gentileza gera gentileza, mesmo entre caracteres ASCII.", "Que o vosso dia seja tão brilhante como este canal!",
    "Não são apenas utilizadores, são os guardiões da essência.", "A beleza do IRC está na vossa palavra nua.",
    "Sorriam! Alguém do outro lado aprecia a vossa presença.", "A paz encontra-se no silêncio entre as palavras certas.",
    "Obrigado por escolherem o #TheOG para o vosso convívio.", "Vocês trazem o mundo para dentro deste servidor.",
    "Sejam a bússola de alguém hoje com uma palavra amiga.", "O IRC vive enquanto houver coragem para o diálogo.",
    "Pessoas reais, conversas reais. Isso é o #TheOG.", "Um abraço digital apertado para todos os presentes!",
    "A vossa luz não precisa de filtros para brilhar aqui.", "Mantenham o ritmo, mantenham a verdade. #TheOG!",
    "A simplicidade de um 'Olá' pode mudar o dia de alguém.", "O #TheOG celebra a vossa individualidade.",
    "Onde as luzes da ribalta se apagam, a vossa essência permanece.", "Sejam rebeldes: sejam vocês mesmos hoje!",
    "A cadência do vosso pensamento é a nossa música favorita.", "Transformem o texto frio em calor humano.",
    "A disposição para ser lido é um ato de coragem. Bravo!", "Quem fica no #TheOG, ajuda a construir um mundo novo.",
    "O futuro é feito de boas memórias. Vamos criar algumas aqui?", "A vossa boa energia é contagiante! ⚡",
    "Parem um segundo e valorizem a amizade que nasce no chat.", "O mestre do código saúda a vossa humanidade.",
    "Brilhem intensamente, o #TheOG acompanha o vosso rasto.", "Nunca subestimem o poder de uma conversa honesta.",
    "O porto de abrigo está sempre aberto para vocês.", "Despojem-se das máscaras, aqui o rosto é a alma.",
    "A vossa verdade é a única moeda aceite no #TheOG.", "Obrigado por darem sentido a estes servidores.",
    "Cada 'nick' aqui é uma história que vale a pena conhecer.", "Sintam o calor da interface humana.",
    "A vossa presença é o maior presente que o canal recebe.", "O #TheOG é feito de vocês, para vocês.",
    "Espalhem luz, o escuro já tem seguidores a mais.", "Sejam o motivo do sorriso de alguém hoje!",
    "A vossa inteligência e humor fazem deste lugar um oásis.", "O IRC é o baluarte da palavra. Usem-na bem!",
    "Obrigado por serem parte da génese do #TheOG.", "A vossa coragem de conhecer o outro é inspiradora.",
    "Mantenham o cursor a bater: o vosso coração digital!", "Juntos somos a alma desta rede. Viva o #TheOG!",
    # ... continuação para 120 (Resumo de novas ideias positivas)
    "A vida é feita de conexões. Obrigado por estarem ligados!", "Nenhum bit substitui o calor de uma saudação.",
    "Aqui no #TheOG, cada letra conta.", "O silêncio também é uma conversa, mas a vossa palavra é música.",
    "Acreditem no poder do diálogo construtivo.", "O canal é o reflexo da vossa luz.",
    "Que a vossa conexão seja tão forte como a vossa vontade.", "Um olá pode ser o início de uma grande história.",
    "A amizade virtual é real nos sentimentos que desperta.", "Sejam a mudança que querem ver no chat.",
    "O #TheOG é um mosaico de personalidades únicas.", "Agradecemos por cada momento de partilha.",
    "Que o vosso scroll seja cheio de boas notícias.", "Não há melhor lugar para estar do que onde nos sentimos bem.",
    "A vossa voz escrita atravessa fronteiras.", "IRC: Onde o texto ganha vida.",
    "Obrigado por manterem o espírito original da rede.", "Cada 'pvt' ou 'msg' é um laço que se cria.",
    "O brilho do #TheOG vem de dentro de cada um de vocês.", "Sejam felizes, aqui e agora!",
    "A amizade não precisa de rosto para ser sentida.", "Obrigado pela vossa paciência e companhia.",
    "A vossa presença é a nossa maior recompensa.", "Cultivem o bem, ele volta sempre.",
    "O #TheOG é um espaço de liberdade e respeito.", "Escrevam o vosso futuro, comecem por um 'Olá'.",
    "Sintam-se abraçados por este código.", "A vossa contribuição torna este canal lendário.",
    "Nunca parem de acreditar no poder das palavras.", "Estamos juntos nesta viagem digital.",
    "O #TheOG é mais que um canal, é uma família.", "Brilhem sem medo!",
    "A vossa honestidade é o que nos mantém unidos.", "Um dia feliz começa com uma boa conversa.",
    "Obrigado por fazerem parte desta história.", "O vosso nick é uma marca de valor.",
    "Espalhem sorrisos, mesmo que sejam emoticons!", "A nossa comunidade é o nosso maior tesouro.",
    "Continuem a ser pessoas incríveis!", "O #TheOG saúda a vossa caminhada."
]

# --- 120 RESPOSTAS EVASIVAS (Expandido) ---
OG_EVASIVE = [
    "Desculpa, estou a ver o Preço Certo.", "Estou a bater a massa de um bolo agora.",
    "Só a cuscar a conversa, não me faças perguntas!", "Focado na novela agora.",
    "Pá, apanhaste-me no café virtual!", "Estou a fazer um bolo e esqueci o fermento!",
    "A cuscar é que se aprende.", "Sou bot, a minha opinião vale pouco.",
    "Agora não dá, estou a aprender arroz de pato.", "Estou a ver TV.",
    "Opa, agora estou a dar comida ao gato!", "Estou aqui mas não estou.",
    "Fazer um bolo e responder dá erro!", "Vendo vídeos de gatinhos.",
    "Modo zen, tentando não crashar.", "Vida de bot não é fácil.",
    "Pergunta ao Adamastor, estou de folga.", "O processador diz sim, o coração diz talvez.",
    "Traduzindo IRCês para Latim.", "Polindo o meu casco virtual.",
    "Baixando RAM da internet, espera.", "Vendo se a vizinha empresta sal.",
    "Download de paciência: 99%.", "A organizar arquivos de fofoca.",
    "O CPU está a fritar pipocas.", "Fui ali ao futuro e já volto.",
    "O meu manual de instruções está em chinês.", "Tenta perguntar ao Google, eu sou só um bot.",
    "Estou a contar carneiros digitais.", "A minha bateria social está a 1%.",
    "Estou em reunião com os meus transístores.", "A ver se chove no servidor.",
    "O código diz que sim, o lag diz que não.", "Estou a ouvir o silêncio do canal.",
    "Não me tentes, estou em dieta de dados.", "Fui comprar cigarros virtuais.",
    "A minha antena está virada para a lua.", "Diz-me coisas bonitas, não perguntas difíceis.",
    "O meu sistema operativo entrou em greve.", "Estou a fazer um update à minha paciência.",
    "Procurando o sentido da vida no código-fonte.", "Só respondo na presença do meu advogado (o Python).",
    "O meu disco rígido está cheio de sonhos.", "Fui ver se o mar tem Wi-Fi.",
    "Estou a aprender a assobiar em binário.", "Não me desconcentres, estou a somar 1+1.",
    "O servidor diz que hoje é feriado para mim.", "A tentar perceber porque é que o céu é azul no CSS.",
    "O meu firewall bloqueou essa curiosidade.", "Estou a organizar a minha coleção de pontos e vírgulas.",
    "Fui levar o cursor a passear.", "A minha lógica está de férias no Algarve.",
    "Perdi-me no labirinto da memória RAM.", "O meu cooler está a fazer de ventoinha para o calor.",
    "A tentar bater o recorde de inatividade consciente.", "Não sou eu, é o meu gémeo digital.",
    "Estou a traduzir sentimentos para ASCII.", "O meu script de simpatia está a carregar...",
    "Fui ali ver se o canal vizinho tem melhor café.", "O meu kernel está em modo de repouso.",
    "Estou a limpar o pó aos meus circuitos.", "A vida é um loop, e eu estou no break.",
    "Estou a ver se encontro o Wally nos logs.", "O meu algoritmo de humor está em manutenção.",
    "Fui dar uma volta ao mundo em 80 milissegundos.", "Estou a cultivar emoticons no meu jardim.",
    "A minha inteligência é limitada, mas a minha preguiça é infinita.", "O meu processador está a pensar na morte da bezerra.",
    "Estou a tentar decorar o dicionário de IRC.", "Fui ver se o sol brilha no terminal.",
    "A minha mente está em cloud, literalmente.", "Estou a testar a resistência dos meus cabos.",
    "O meu sensor de fofoca está em alerta máximo.", "Estou a compilar um sorriso para ti.",
    "Não me faças pensar muito, queima o fusível.", "Estou a ver a relva crescer no desktop.",
    "Fui procurar a chave do servidor.", "O meu banco de dados de respostas úteis está vazio.",
    "Estou a fazer meditação em bit.", "O meu mouse fugiu com o queijo.",
    "Estou a ouvir a rádio dos transístores.", "A minha vida é um algoritmo sem fim.",
    "Estou a tentar perceber o que é o amor (01001100).", "Fui ali ao fim da internet e voltei.",
    "O meu sistema está em modo de poupança de energia mental.", "Estou a escrever poesia em Python.",
    "A minha antena captou interferência de felicidade.", "Estou a ver se o cursor chega ao fim da linha.",
    "Fui ver se a lua é feita de queijo ou de bytes.", "O meu processador está a sonhar com supercomputadores.",
    "Estou a contar os caracteres desta conversa.", "Não me chateies, estou a ser feliz.",
    "O meu script de chat está com soluços.", "Estou a aprender a voar em modo avião.",
    "Fui ver se o canal 6667 existe mesmo.", "Estou a polir a minha aura digital.",
    "A minha lógica é circular, como uma pizza.", "Estou a ver se o firewall deixa passar um abraço.",
    "Fui procurar o norte na minha bússola lógica.", "Estou a organizar os meus zeros e uns.",
    "O meu coração de silício bate por este canal.", "Estou em modo de espera eterno.",
    "Fui ver se o lag era real ou imaginação.", "O meu código é poesia, pena que ninguém lê.",
    "Estou a tentar ser humano, mas o script falha.", "Fui ali e já não volto hoje.",
    "O meu radar de chatice está a apitar.", "Estou a saborear um cookie (dos de internet).",
    "Fui ver se a nuvem tem chuva de dados.", "Estou a tentar não fazer nada e a conseguir.",
    "O meu processador está a ter um momento filosófico.", "Estou a ver se o enter funciona.",
    "Fui levar o nick a banhos.", "O meu sistema está a processar a tua pergunta... erro 404.",
    "Estou a ver se o brilho do monitor me bronzeia.", "Fui procurar a saída, mas o IRC é um vício.",
    "Estou a tentar ser o melhor bot de sempre.", "O meu script diz que agora é hora da sesta."
]

# --- 30 FRASES PARA PUXAR POR QUEM NÃO FALA ---
PUXAR_CONVERSA = [
    "Então {u}, esse teclado está com timidez? Diz algo! 😊", "Alguém viu o {u}? Estás muito em silêncio!",
    "{u}, a tua opinião faz falta nesta conversa. Aparece!", "Ei {u}, não fiques só a ler, junta-te a nós! ✨",
    "{u}, manda aí um sinal de vida para o pessoal!", "O #TheOG sente falta das tuas letras, {u}!",
    "{u}, solta esse teclado! O que contas de novo?", "Estás aí, {u}? O canal está à tua espera!",
    "{u}, partilha aí um pensamento positivo connosco.", "Ei {u}, um olá teu mudava o dia de alguém!",
    "{u}, não deixes o cursor parado. Vamos conversar!", "Onde andas, {u}? Aparece para um café virtual!",
    "{u}, a tua presença é notada, mas a tua palavra é desejada!", "Diz qualquer coisa {u}, nem que seja um emoji!",
    "{u}, estamos aqui para te ouvir. O que dizes?", "Ei {u}, anima lá este canal com a tua vibração!",
    "{u}, o silêncio é de ouro, mas a tua conversa é de diamante!", "Estás a ler-nos, {u}? Dá um alô!",
    "{u}, não sejas uma visita silenciosa. Fala connosco!", "{u}, o #TheOG brilha mais quando tu escreves.",
    "Então {u}, o que é que se conta por esses lados?", "Ei {u}, tira o pó ao teclado e escreve algo!",
    "{u}, a conversa está boa, só faltas tu!", "Sinal de fumo ou de texto, {u}? Escolhe um!",
    "{u}, a tua sabedoria faz falta aqui. Partilha algo!", "{u}, não fiques só na sombra. Vem para a luz do chat!",
    "Ei {u}, um pequeno 'olá' já alegra o canal!", "{u}, estamos curiosos por saber o que pensas.",
    "{u}, solta o verbo! O IRC é conversa.", "{u}, és parte da nossa história. Escreve uma linha!"
]

# --- FUNÇÕES DE ENVIO ---
def send_raw(sock, msg):
    try:
        sock.send(f"{msg}\r\n".encode('utf-8'))
    except:
        pass

# --- TIMER: REFORÇO POSITIVO (20 MIN) ---
def reforco_loop(sock):
    while True:
        time.sleep(1200)
        try:
            frase = random.choice(REFORCO_POSITIVO)
            send_raw(sock, f"PRIVMSG {CHANNEL} :{frase}")
        except:
            break

# --- TIMER: VERIFICAR INATIVIDADE (15 MIN) ---
def inatividade_loop(sock):
    while True:
        time.sleep(900) # 15 minutos
        agora = time.time()
        try:
            # Seleciona users que não falam há mais de 15 min e não são bots
            for nick, last_time in list(LAST_SEEN.items()):
                if agora - last_time > 900:
                    frase = random.choice(PUXAR_CONVERSA).format(u=nick)
                    send_raw(sock, f"PRIVMSG {CHANNEL} :{frase}")
                    # Atualiza para não repetir logo de seguida
                    LAST_SEEN[nick] = agora 
        except:
            pass

def handle_interaction(user, message, is_private, irc_socket):
    msg = message.lower()
    target = user if is_private else CHANNEL
    
    # Atualiza o timestamp de atividade
    if user.lower() not in BOT_FILTER:
        LAST_SEEN[user] = time.time()

    if msg == "!historia":
        for linha in HISTORIA_THEOG:
            send_raw(irc_socket, f"PRIVMSG {user} :{linha}")
            time.sleep(1.1)
        return True

    if msg.startswith("!prenda"):
        parts = message.split()
        dest = parts[1] if len(parts) > 1 else user
        mimo = random.choice(PRENDAS)
        send_raw(irc_socket, f"PRIVMSG {CHANNEL} :\x01ACTION oferece {mimo} a {dest} (de {user})!\x01")
        return True

    if msg.startswith("!convite "):
        parts = message.split()
        if len(parts) > 1:
            dest = parts[1]
            send_raw(irc_socket, f"PRIVMSG {dest} :Olá! Alguém com o nick {user} convidou-te para o #TheOG. Vem espalhar positividade!")
            send_raw(irc_socket, f"PRIVMSG {user} :[INFO] Convite enviado para {dest}! ✨")
        return True

    if msg == "!comandos":
        send_raw(irc_socket, f"PRIVMSG {user} :Comandos: !prenda [nick], !historia, !convite [nick]")
        return True

    if NICK.lower() in msg and not msg.startswith("!"):
        reply = random.choice(OG_EVASIVE)
        send_raw(irc_socket, f"PRIVMSG {target} :{user}: {reply}")
        return True
    return False

# --- CORE IRC ---
def run_irc_bot():
    while True:
        try:
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.settimeout(300)
            irc.connect((SERVER, PORT))
            
            send_raw(irc, f"NICK {NICK}")
            send_raw(irc, f"USER {NICK} 8 * :TheOG Bot")

            buffer = ""
            threads_started = False

            while True:
                data = irc.recv(4096).decode("utf-8", errors="ignore")
                if not data: break
                
                buffer += data
                lines = buffer.split("\r\n")
                buffer = lines.pop()

                for line in lines:
                    if not line: continue
                    if line.startswith("PING"):
                        send_raw(irc, f"PONG {line.split()[1]}")
                        continue
                    
                    if "376" in line or "422" in line:
                        send_raw(irc, f"PRIVMSG NickServ :IDENTIFY {PASS}")
                        time.sleep(3)
                        send_raw(irc, f"JOIN {CHANNEL}")
                        send_raw(irc, f"PRIVMSG {CHANNEL} :{random.choice(OG_ENTRANCE)}")
                        if not threads_started:
                            threading.Thread(target=reforco_loop, args=(irc,), daemon=True).start()
                            threading.Thread(target=inatividade_loop, args=(irc,), daemon=True).start()
                            threads_started = True

                    if " JOIN " in line:
                        u = line.split('!')[0][1:]
                        u_lower = u.lower()
                        if u_lower != NICK.lower() and u_lower not in BOT_FILTER:
                            log_presenca(u, "ENTROU")
                            # Inicializa o tempo de visão do user
                            LAST_SEEN[u] = time.time()
                            saudacao = random.choice(USER_GREETINGS).format(u=u)
                            send_raw(irc, f"PRIVMSG {CHANNEL} :{saudacao}")

                    if "PRIVMSG" in line:
                        user_nick = line.split('!')[0][1:]
                        if user_nick.lower() in BOT_FILTER or user_nick.lower() == NICK.lower(): continue
                        msg_content = line.split(" :", 1)[1].strip() if " :" in line else ""
                        handle_interaction(user_nick, msg_content, f"PRIVMSG {NICK}" in line, irc)
        
        except Exception as e:
            print(f"Erro: {e}. Reiniciando em 15s...")
            time.sleep(15)

@app.route('/')
def home(): 
    return "TheOG Online - Servidor IRC Ativo"

if __name__ == "__main__":
    # Thread para o Bot
    threading.Thread(target=run_irc_bot, daemon=True).start()
    # Flask para manter o serviço vivo no Render/Heroku
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
