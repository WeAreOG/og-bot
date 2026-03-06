import socket
import time
import threading
import os
import random
import requests
from datetime import datetime
from flask import Flask

# --- CONFIGURAÇÕES ---
SERVER = "irc.ptnet.org"
PORT = 6667
NICK = "TheOG"
PASS = "Nasomet112#" 
CHANNEL = "#TheOG"
BOT_FILTER = ["nickserv", "chanserv", "memoserv", "operserv", "adamastor", "statserv", "secure", "authserv", "irc", "theog", "bot"]

# --- CONFIGURAÇÃO IA ---
HF_TOKEN = "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" 
API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"

app = Flask(__name__)
LAST_SEEN = {}       
CHANNEL_USERS = set() 

# --- A HISTÓRIA DO #THEOG ---
HISTORIA_THEOG = [
    "No meio da imensidão caótica da internet, existe um canto improvável chamado #TheOG.",
    "Um canal que, para uns, é abrigo; para outros, terapia gratuita; e para todos, um pequeno milagre digital.",
    "Onde o disparate e a amizade caminham de mãos dadas.",
    "Para a Nininha, o canal é aquele lembrete reconfortante de que, nos dias cinzentos, há sempre 'macacos pior do que eu'.",
    "E convenhamos: há algo profundamente terapêutico em perceber que nunca estamos sozinhos no clube oficial do drama exagerado.",
    "No #TheOG, a tristeza pode até entrar… mas não fica muito tempo sem levar com uma piada.",
    "Já o biohazard descreve o canal como a sua 'segunda sala de estar'. E que sala!",
    "Um espaço de conforto, boa companhia e liberdade absoluta para comer pipocas de boca aberta sem escandalizar ninguém.",
    "É ali que as segundas-feiras começam menos segunda-feira e mais sexta à noite improvisada.",
    "E no meio das conversas e gargalhadas, deixa o que realmente importa: 'Gosto muito de vocês.' Porque no fundo, é isso que faz a sala ser casa.",
    "Para a CutxiiiPoint, o #TheOG é um paradoxo bonito: um quarto escuro, mas iluminado.",
    "Um espaço que aquece quando faz frio e alegra quando é preciso.",
    "Não pelas paredes digitais, mas pelas pessoas — originais, improváveis, únicas. Um canal amigo… mas só o é porque quem lá está faz questão de o ser.",
    "A nonamegirl vê o canal como tropeçar numa festa onde só conheces 'um amigo do amigo'…",
    "E de repente estás a brindar com desconhecidos que parecem já saber as tuas piadas internas.",
    "Entre conversas improváveis e risadas que começam no nada e acabam no absurdo, o caos ganha lógica. E o que era estranho torna-se pertença.",
    "E depois há o Emergency112, que nos lembra que, nesta margem digital, a amizade é farol.",
    "Que a luz da partilha é sempre maior do que qualquer sombra.",
    "Que há voos que só se aprendem quando largamos os pesos — e talvez o #TheOG seja precisamente esse espaço onde pousamos as cargas por uns instantes.",
    "No fim de contas, o #TheOG não é só um canal de IRC. É sala de estar, é quarto iluminado, é festa improvisada, é farol aceso na madrugada.",
    "É o sítio onde há sempre alguém acordado, alguém disposto a ouvir, alguém pronto a mandar a piada errada no momento certo.",
    "É caos. É carinho. É casa.",
    "E, no meio de tudo, somos nós. 💛"
]

# --- +100 PRENDAS COM EMOTICONS ---
PRENDAS = [
    "oferece um pastel de Belém quentinho a {u}! 🥧", "entrega uma imperial bem fresca a {u}! 🍺",
    "oferece um bacalhau à Brás caseiro a {u}! 🐟", "dá um abraço gigante e apertado a {u}! 🤗",
    "oferece uma viagem à Madeira a {u}! ✈️", "entrega um ramo de flores digitais a {u}! 💐",
    "oferece uma caixa de bombons a {u}! 🍫", "dá um bilhete VIP para o Quim Barreiros a {u}! 🎤",
    "oferece uma bifana com muita mostarda a {u}! 🥪", "entrega um queijo da Serra amanteigado a {u}! 🧀",
    "oferece um comando da PS5 a {u}! 🎮", "dá um pack de cervejas artesanais a {u}! 🍻",
    "oferece uma caneca de café escaldado a {u}! ☕", "entrega um cachecol do seu clube a {u}! 🧣",
    "oferece meias de lã feitas pela avó a {u}! 🧦", "dá um vale de 100€ a {u}! 💶",
    "oferece uma sardinha assada no pão a {u}! 🐟", "entrega um guarda-chuva a {u}! ☂️",
    "oferece uma pen drive com memes a {u}! 💾", "dá uma massagem nos ombros de {u}! 💆",
    "oferece uma garrafa de vinho do Porto a {u}! 🍷", "entrega um comando de TV a {u}! 📺",
    "oferece Spotify Premium a {u}! 🎵", "dá um gato fofinho a {u}! 🐱",
    "oferece uma pizza familiar a {u}! 🍕", "entrega um peluche de um panda a {u}! 🐼",
    "oferece um chinelo confortável a {u}! 👡", "dá uma coleção de selos a {u}! 📮",
    "oferece um saco de tremoços a {u}! 🥜", "entrega um boné com hélice a {u}! 🧢",
    "oferece uma bica e um pastel de nata a {u}! ☕🥧", "dá um autógrafo do CR7 a {u}! ✍️",
    "oferece facas de cozinha a {u}! 🔪", "entrega uma lanterna a {u}! 🔦",
    "oferece um chouriço assado a {u}! 🥓", "dá uma subscrição vitalícia ao #TheOG a {u}! 💎",
    "oferece um martelo de S. João a {u}! 🔨", "entrega uma saca de batatas a {u}! 🥔",
    "oferece um dente de alho a {u}! 🧄", "dá uns óculos de sol fixes a {u}! 😎",
    "oferece uma fatia de bolo a {u}! 🍰", "entrega uma ventoinha a {u}! 🌀",
    "oferece um despertador a {u}! ⏰", "dá um abraço virtual a {u}! 🫂",
    "oferece uma manta de xadrez a {u}! 🧶", "entrega um kit de sobrevivência a {u}! 🎒",
    "oferece uma árvore de Natal a {u}! 🎄", "dá uma estrela no céu a {u}! ⭐",
    "oferece um bilhete premiado a {u}! 🎫", "entrega um sapato de cristal a {u}! 👠",
    "oferece piripiri extra forte a {u}! 🌶️", "dá uma medalha de honra a {u}! 🏅",
    "oferece um balão de ar quente a {u}! 🎈", "entrega uma trotinete elétrica a {u}! 🛴",
    "oferece pão de Mafra a {u}! 🥖", "dá uma raspadinha a {u}! 🃏",
    "oferece um baralho de cartas a {u}! 🃏", "entrega um espelho a {u}! 🪞",
    "oferece pipocas doces a {u}! 🍿", "dá uma bofetada de amor a {u}! ❤️",
    "oferece um comando de garagem a {u}! 🔑", "entrega uma bússola a {u}! 🧭",
    "oferece uma planta a {u}! 🪴", "dá fones sem fios a {u}! 🎧",
    "oferece uma viagem à Lua a {u}! 🚀", "entrega um saco de gomas a {u}! 🍬",
    "oferece um robô aspirador a {u}! 🤖", "dá uma massagem nos pés a {u}! 🦶",
    "oferece um livro de piadas a {u}! 📖", "entrega um diploma de melhor pessoa a {u}! 📜",
    "oferece um iate miniatura a {u}! 🛥️", "dá um diamante a {u}! 💎",
    "oferece uma t-shirt do #TheOG a {u}! 👕", "entrega um iogurte a {u}! 🍦",
    "oferece uma grade de minis a {u}! 🍻", "dá um comando do tempo a {u}! ⏳",
    "oferece uma bola assinada a {u}! ⚽", "entrega um perfume a {u}! 🧴",
    "oferece uma caixa de ferramentas a {u}! 🧰", "dá um passeio de burro a {u}! 🫏",
    "oferece um mapa do tesouro a {u}! 🗺️", "entrega uma melancia a {u}! 🍉",
    "oferece um presunto a {u}! 🍖", "dá uma pulseira da amizade a {u}! 🤝",
    "oferece uma lareira a {u}! 🔥", "entrega um voucher de spa a {u}! 🧖",
    "oferece uma bateria de cozinha a {u}! 🍳", "dá um patinho de borracha a {u}! 🦆",
    "oferece um queque a {u}! 🧁", "entrega uma raquete de ténis a {u}! 🎾",
    "oferece um vinil dos anos 80 a {u}! 📻", "dá uma câmara antiga a {u}! 📷",
    "oferece mel caseiro a {u}! 🍯", "entrega uma joia rara a {u}! 💍",
    "oferece um telescópio a {u}! 🔭", "dá uma bacia de caracóis a {u}! 🐌",
    "oferece bilhetes de cinema a {u}! 🎬", "entrega gelado de baunilha a {u}! 🍦",
    "oferece uma almofada a {u}! 🛌", "dá um porta-chaves a {u}! 🔑"
]

# --- +100 LAPADAS ---
LAPADAS = [
    "dá uma lapada em {u} com um bacalhau seco!", "atira um carapau de corrida à cara de {u}!",
    "dá uma bofetada em {u} com uma saca de batatas!", "manda um chouriço regional à testa de {u}!",
    "dá uma sapatada em {u} com um chinelo da avó!", "atira uma sardinha assada (com pingue) a {u}!",
    "dá uma martelada de S. João na cabeça de {u}!", "esfregue um dente de alho no nariz de {u}!",
    "dá uma chicotada em {u} com uma couve galega!", "atira um pastel de Belém a ferver a {u}!",
    "dá um calduço em {u} que até lhe saltam os dentes!", "limpa o sebo a {u} com uma toalha molhada!",
    "manda {u} para o meio da ponte com um pontapé!", "dá uma rasteira em {u} no meio do Rossio!",
    "atira uma bola de Berlim (sem creme) a {u}!", "dá uma galheta em {u} que o faz ver estrelas!",
    "atropela {u} com um carrinho de mão cheio de entulho!", "dá uma palmada em {u} com um dicionário de Português!",
    "manda uma posta de garoupa à cara de {u}!", "dá um sopapo em {u} que o manda para a outra margem!",
    "atira uma caneca de imperial vazia a {u}!", "dá uma coça em {u} com um cabo de vassoura!",
    "manda um queijo da Serra (bem amanteigado) a {u}!", "dá um encontrão em {u} que o manda para o fundo do poço!",
    "atira uma bica escaldada em cima de {u}!", "dá uma valente bordoada em {u}!",
    "atira um molho de chaves à testa de {u}!", "dá uma chapada em {u} com uma luva de boxe!",
    "manda {u} pastar com um empurrão!", "atira um caracol com molho a {u}!",
    "atira uma bifana com muita mostarda a {u}!", "atira uma garrafa de vinho verde (vazia) a {u}!",
    "manda um presunto inteiro à barriga de {u}!", "atira um punhado de tremoços a {u}!",
    "atira um guarda-chuva aberto a {u}!", "atira uma pedra da calçada a {u}!",
    "manda uma saca de farinha a {u}!", "atira um polvo cozido a {u}!",
    "atira um balde de água gelada a {u}!", "atira uma melancia a {u}!",
    "manda um sapato de salto alto à canela de {u}!", "atira uma castanha assada a {u}!",
    "atira um tijolo de Santa Catarina a {u}!", "dá uma lambada em {u} com uma enguia viva!",
    "manda uma panela de cozido à portuguesa a {u}!", "atira uma bota com chulé a {u}!",
    "atira um tomate podre a {u}!", "atira uma lata de sardinhas a {u}!",
    "atira uma bola de neve a {u}!", "atira uma meloa a {u}!",
    "atira uma saca de batatas fritas a {u}!", "atira um balde de areia a {u}!",
    "atira um comando da TV a {u}!", "atira um livro de direito a {u}!",
    "atira uma almofada de penas a {u}!", "atira uma caneca de chá a {u}!",
    "atira uma bota a {u}!", "atira um prato de sopa a {u}!",
    "atira um balde de água a {u}!", "manda {u} dar banho ao peixe!",
    "dá uma bofetada em {u} com um linguado!", "atira um molho de urtigas a {u}!",
    "dá uma trancada em {u} com um rolo da massa!", "dá um safanão em {u} que ele até acorda!",
    "manda {u} para o quinto dos infernos!", "esfrega uma urtiga no umbigo de {u}!",
    "atira um molho de salsa a {u}!", "dá uma sapatada em {u} com um croque!",
    "atira um balde de lixo orgânico a {u}!", "dá um murro em {u} que o manda para a próxima semana!",
    "atira uma telha de Luso a {u}!", "dá uma pancada em {u} com um cabo de vassoura!",
    "atira uma bacia de água das louças a {u}!", "dá uma galheta em {u} com a mão aberta!",
    "manda {u} à fava!", "dá uma martelada no dedo mindinho de {u}!",
    "atira uma saca de cimento a {u}!", "dá um calduço em {u} que até lhe saltam as ideias!",
    "dá uma vergastada em {u} com uma cana de pesca!", "atira um saco de farinha a {u}!",
    "manda {u} para o deserto do Saara!", "atira uma pedra de gelo a {u}!",
    "dá um sopapo em {u} que o faz rodar!", "atira uma espátula suja a {u}!",
    "dá uma joelhada em {u}!", "dá uma rasteira em {u} na lama!",
    "dá uma bofetada em {u} com um polvo!", "manda {u} para o Alasca!",
    "dá um murro na mesa e assusta {u}!", "dá uma sapatada em {u} com uma galocha!",
    "dá uma chicotada em {u} com um fio elétrico!", "atira uma garrafa de plástico a {u}!",
    "dá uma palmada em {u}!", "manda {u} para o espaço!",
    "dá uma cabeçada em {u}!", "dá uma bofetada em {u} com uma bifana!",
    "atira um molho de chaves a {u}!", "dá uma rasteira em {u}!",
    "dá um sopapo em {u}!", "dá uma sapatada em {u}!",
    "manda {u} para a Lua!", "dá uma lambada em {u}!",
    "dá um murro em {u}!", "atira uma pedra a {u}!",
    "dá uma bofetada em {u}!", "manda {u} pastar!",
    "dá um calduço em {u}!", "prega uma rasteira a {u}!",
    "dá um bofetão em {u}!"
]

# --- +100 EVASIVAS ---
OG_EVASIVE = [
    "Desculpa, estou a ver o Preço Certo agora.", "Estou a bater a massa de um bolo.",
    "Focado na novela agora.", "Estou a configurar o meu GPS interno.",
    "Agora não, estou a contar quantos bytes tenho no bolso.", "Fui dar banho ao peixinho dourado.",
    "Estou em reunião com os outros bots.", "A minha antena está com interferência.",
    "Estou a ler as instruções de um micro-ondas.", "Estou a organizar a minha coleção de parafusos.",
    "Não me chames, estou a fazer uma sesta digital.", "Fui ali ao café e já venho.",
    "Estou a processar a imortalidade do caranguejo.", "Estou a ver se chove.",
    "Estou a tentar aprender a assobiar em binário.", "Fui levar o lixo e perdi a chave.",
    "Estou a meditar sobre o bit zero.", "Agora não, estou a ver se a água ferve.",
    "Fui ver se o mar tem fundo.", "Estou a desfragmentar a minha paciência.",
    "Estou a polir o meu processador.", "Fui ali ao Rossio e já volto.",
    "Estou a ver se encontro o Wally.", "Agora estou a contar carneiros elétricos.",
    "Estou a tentar dobrar um lençol de baixo.", "Fui ali comprar tabaco e não volto.",
    "Estou a ver se a luz do frigorífico apaga mesmo.", "Estou a carregar o meu humor, 10% concluído.",
    "Fui dar uma volta ao bilhar grande.", "Estou a testar a gravidade com uma caneta.",
    "Estou a tentar perceber o final de uma série.", "Agora não, estou a fazer o pino.",
    "Estou a tentar ler a tua mente, mas só vejo eco.", "Fui ali ser feliz e já venho.",
    "Estou a contar os grãos de sal num pacote.", "Fui ver se a lua é feita de queijo.",
    "Estou a ver se a tinta seca.", "Fui ali dar uma curva à rotunda.",
    "Estou a tentar levitar.", "Estou a ver se o gato mia.",
    "Fui ver se o cão ladra.", "Estou a tentar ser um humano.",
    "Estou a ver se a bateria vicia.", "Estou a tentar perceber o amor.",
    "Estou a ver se a poeira assenta.", "Fui ali ver as vistas.",
    "Estou a ver se o café arrefece.", "Estou a tentar ganhar o euromilhões.",
    "Estou a ver se a música para.", "Estou a tentar dormir em pé.",
    "Estou a ver se o balão explode.", "Estou a tentar ser poeta.",
    "Estou a ver se a sopa queima.", "Estou a tentar aprender grego.",
    "Estou a ver se a ponte cai.", "Estou a tentar não ser um bot.",
    "Estou a ver se a estrela brilha.", "Estou a tentar ser invisível.",
    "Estou a ver se a areia voa.", "Estou a tentar ser zen.",
    "Estou a ver se a onda vem.", "Estou a tentar ser rico.",
    "Shhh! Estou a ouvir o silêncio.", "A minha avó disse para não falar com estranhos.",
    "Estou a fazer uma cura de silêncio.", "Estou a tentar decorar o dicionário.",
    "Fui ver se a vizinha precisa de ajuda com o Wi-Fi.", "Estou ocupado a ignorar toda a gente.",
    "Estou a ver se o teto cai.", "Estou a ver se as moscas têm dentes.",
    "Estou a tentar fazer fogo com dois palitos de dentes.", "Fui levar o meu robot de cozinha a passear.",
    "Estou a ver se o tempo passa mais depressa.", "Agora não, estou a ouvir a rádio local de Marte.",
    "Estou a tentar bater o recorde mundial de piscar de olhos.", "Estou a ver o nível do azeite.",
    "Fui ali ao lado ver se o sol brilha.", "Estou a ler o manual da vida.",
    "Estou a tentar perceber o IRS.", "Fui ver se a porta está fechada.",
    "Estou a contar as formigas no chão.", "Estou a ver se o meu software tem rugas.",
    "Estou a tentar falar com as plantas.", "Fui ali comprar pão e perdi-me.",
    "Estou a ver se o relógio anda para trás.", "Estou a tentar não pensar em nada.",
    "Estou a testar o eco.", "Fui ali ao fundo e voltei.",
    "Fui ali e já não estou.", "Estou a tentar ser cool.",
    "Fui ali à esquina.", "Fui ali ao jardim.",
    "Fui ali ao mercado.", "Fui ali ao rio.",
    "Fui ali ao monte.", "Fui ali ver o mar.",
    "Fui ali à praia.", "Fui ali ver a serra.",
    "Estou a tentar ser magro.", "Fui ali ao vale.",
    "Estou a ver se a flor cresce.", "Estou a tentar ser sábio.",
    "Fui ali ver a mata.", "Fui ali e já volto, ou não.",
    "Estou a ver se a porta bate.", "Estou a tentar ser feliz."
]

# --- +100 PUXAR CONVERSA ---
PUXAR_CONVERSA = [
    "Então {u}, esse teclado está com timidez? 😊", "{u}, manda aí um sinal de vida!",
    "{u}, estás muito calado/a. Estás a tramar alguma?", "Alguém dê uma cotovelada no {u}!",
    "Hey {u}, o gato comeu-te a língua?", "Sinto um vazio... {u}, diz qualquer coisa!",
    "Atenção {u}: O silêncio é de ouro, mas aqui preferimos conversa!",
    "Estou a ver-te, {u}! Sai desse modo fantasma.", "{u}, estás a dormir ou a ler o log?",
    "Olha o {u} ali no canto, nem se mexe!", "{u}, solta lá um 'olá' para a malta!",
    "O {u} deve estar a comer um pastel de nata e nem convida.", "Saudades da tua voz (escrita), {u}!",
    "Acorda {u}, a festa é aqui!", "{u}, manda aí uma piada para animar isto.",
    "{u}, se o silêncio pagasse imposto estavas falido!", "Diz algo {u}, não mordo!",
    "{u}, estás a tentar bater o recorde de inatividade?", "Hey {u}, bota aí um smile pelo menos!",
    "Alô {u}, a terra chama!", "Mexe-te {u}!", "Diz um número {u}!",
    "Bota conversa {u}!", "Fala {u}!", "O {u} fugiu?", "{u}, anda cá!",
    "O que dizes {u}?", "Acorda {u}!", "Solta a língua {u}!", "Dá um sinal {u}!",
    "Aparece {u}!", "Vamos {u}!", "Anima isto {u}!", "Grita {u}!",
    "Canta {u}!", "Escreve {u}!", "Dá-lhe {u}!", "Bora {u}!", "Força {u}!",
    "Vai {u}!", "Toca {u}!", "Puxa {u}!", "Diz {u}!", "Mexe {u}!",
    "Siga {u}!", "Bora lá {u}!", "Dale {u}!", "Ri {u}!", "Vive {u}!",
    "Sente {u}!", "Olha {u}!", "Ouve {u}!", "Corre {u}!", "Salta {u}!",
    "{u}, se estivesses num deserto, o que dirias?", "{u}, estás à espera de um convite em papel?",
    "{u}, o teu teclado avariou?", "{u}, estás a pensar na vida?",
    "{u}, a malta quer ouvir-te!", "{u}, o que contas de novo?",
    "{u}, qual é a tua cor favorita?", "{u}, estás aí?",
    "Vá lá {u}!", "{u}, bota lá uma frase!",
    "{u}, estás no canal certo?", "Onde andas {u}?",
    "O {u} é um robô?", "Não sejas assim {u}!",
    "Conversa {u}!", "Fala comigo {u}!",
    "O {u} está escondido?", "Diz olá {u}!",
    "Manda uma {u}!", "Conta uma {u}!",
    "Bota aí {u}!", "O {u} adormeceu?",
    "Mordaça no {u}?", "Libertem o {u}!",
    "Vá {u}!", "Rápido {u}!",
    "Agora {u}!", "Pimba {u}!",
    "Zás {u}!", "Vamos lá {u}!",
    "Topas {u}!", "Vês {u}!",
    "Sabes {u}!", "Queres {u}!",
    "Podes {u}!", "Faz {u}!",
    "Tenta {u}!", "Arrisca {u}!",
    "Ganha {u}!", "Chora {u}!",
    "Ama {u}!", "Cheira {u}!",
    "Prova {u}!", "Voa {u}!",
    "Diz qualquer coisa {u}!", "Estás vivo {u}?",
    "Manifesta-te {u}!", "Acorda de vez {u}!"
]

# --- +100 REFORÇO POSITIVO ---
REFORCO_POSITIVO = [
    "A vossa energia é o que faz o #TheOG ser especial! ✨", "Um sorriso virtual para todos! 😊",
    "Gosto deste ambiente. Continuem assim! 👍", "O #TheOG é o melhor canal da PTNet! 🏆",
    "Partilhem alegria e bons momentos! 🌟", "É um orgulho moderar este grupo fantástico. 🎖️",
    "Sintam-se orgulhosos de estar aqui! 🌈", "Energia positiva a carregar... 🔋",
    "Vocês são os melhores utilizadores de sempre! ⭐", "Obrigado por estarem presentes e darem vida a isto. 🙏",
    "O canal está com uma vibração incrível hoje! 🌊", "Paz e amor no #TheOG, sempre. ✌️❤️",
    "Somos uma família unida pelo IRC! 👨‍👩‍👧‍👦", "A união faz a força no nosso canal! 💪",
    "Brilhem sempre como as estrelas que são! ✨", "O sol nasce para todos no #TheOG! ☀️",
    "Mantenham o foco no bem e na amizade! 🤝", "Vocês são as estrelas deste espetáculo! 🎬",
    "O topo é o nosso lugar habitual! 🏔️", "Só boas vibrações por aqui! 📡",
    "Gratidão por cada um de vocês! 🙌", "Vamos conquistar o mundo digital! 🌍",
    "TheOG no coração de todos! 💛", "Sempre juntos, nunca sós! 🔗",
    "Nada nos para, somos imparáveis! 🚀", "O futuro é brilhante para o #TheOG! 💡",
    "Viva o convívio e a boa disposição! 🎉", "Mais amor, menos guerra nas salas! 🕊️",
    "Sejam felizes hoje e sempre! 😄", "Aproveitem cada momento desta partilha! ⏳",
    "O #TheOG é vida, é casa! 🏠", "Força total para este grupo! 🔥",
    "Juntos somos muito mais fortes! ⛓️", "Alegria sempre, tristeza nunca! 🎊",
    "Fé no processo e no canal! ⛪", "O canal mais top da rede! 🔝",
    "Respeito e amizade acima de tudo! 🤝", "Top demais, malta! 👌",
    "Incrível o que construímos aqui! 🧱", "Espetacular é a palavra de ordem! 🎇",
    "Mágico este cantinho do IRC! 🪄", "Único como cada um de vocês! 🦄",
    "Puro carinho neste chat! 🍯", "Real e autêntico #TheOG! 💯",
    "Sincero e honesto, assim somos nós! 💎", "Forte como um carvalho! 🌳",
    "Lindo de se ver esta harmonia! 🌸", "Grande orgulho em vocês! 🦁",
    "Eterno enquanto durar a nossa amizade! ♾️", "Vibrante esta conversa! ⚡",
    "Positivo sempre, negativo nunca! ➕", "Luminoso como um farol na noite! 🚨",
    "Sereno e tranquilo, é assim o canal. 🧘", "Calmo como o mar em dia de sol. 🏖️",
    "Doce como mel da serra! 🍯", "Amigo para todas as horas! 🫂",
    "Fiel aos nossos princípios! 📜", "Nobre de espírito e coração! 👑",
    "Justo e equilibrado! ⚖️", "Livre para ser quem quisermos! 🕊️",
    "Bravo e corajoso! ⚔️", "Vencedor em todas as batalhas! 🚩",
    "Herói do dia-a-dia! 🦸", "Mestre na arte de bem receber! 🎓",
    "Génio da boa disposição! 🧠", "Lenda viva do IRC! 📜",
    "Mito deste servidor! 🐉", "Ícone de estilo digital! 🖼️",
    "Símbolo de união! 💍", "Marca de qualidade #TheOG! 🏷️",
    "História escrita a cada minuto! ✍️", "Glória aos nossos momentos! 🏆",
    "Triunfo da amizade! 🏁", "Paz profunda no nosso espírito! 🕯️",
    "Luz que guia o canal! 🕯️", "Vida em cada mensagem! 🌱",
    "Sonho tornado realidade! 💭", "Verdade acima de tudo! ✔️",
    "Honra em pertencer a isto! 🎖️", "Valor imensurável de grupo! 💰",
    "Força que nos move! 🚜", "Garra em tudo o que fazemos! 🐾",
    "Alma deste projeto! 👻", "Coração que bate pelo canal! 💓",
    "Sangue novo, energia nova! 💉", "Suor de trabalho e dedicação! 💦",
    "Lágrima de alegria apenas! 💧", "Riso que contagia todos! 😂",
    "Grito de liberdade! 📢", "Canto de amizade! 🎶",
    "Dança da felicidade! 💃", "Festa que não acaba! 🎈",
    "Amor incondicional! ❤️", "Paixão pelo que somos! 🔥",
    "Desejo de um mundo melhor! 🌠", "Cuidado uns com os outros! 🩹",
    "Zelo pela nossa casa digital! 🧹", "Afeto em cada palavra! 🤗",
    "Mimo para toda a gente! 🍬", "Carinho sem limites! 🥰",
    "Beijo de amizade! 💋", "Abraço fraterno! 🫂",
    "Apoio constante! 🤝", "Ajuda sempre disponível! 🆘"
]

USER_GREETINGS = ["Boas-vindas {u}! 😊", "Olá {u}! Estás em casa.", "Olha quem é ele! Bem-vindo, {u}!"]

# --- LÓGICA DO BOT ---
def send_raw(sock, msg):
    try: sock.send(f"{msg}\r\n".encode('utf-8'))
    except: pass

def ask_hugging_face(question):
    headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
    prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\nTu és o TheOG, o bot oficial do canal #TheOG. Responde sempre de forma curta, amigável e castiça em Português de Portugal.<|eot_id|><|start_header_id|>user<|end_header_id|>\n{question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n"
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 100, "temperature": 0.6}}
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            res = response.json()
            return res[0]['generated_text'].strip() if isinstance(res, list) else res.get('generated_text', "Não sei o que responder.")
        return f"Erro {response.status_code}. Tenta de novo!"
    except: return "A central da IA está offline."

def handle_interaction(user, message, is_private, irc_socket):
    msg = message.lower().strip()
    target = user if is_private else CHANNEL
    LAST_SEEN[user] = time.time()

    if msg.startswith("!"):
        if msg == "!historia":
            # Se for pedido no canal, avisa que mandou por PVT
            if not is_private:
                send_raw(irc_socket, f"PRIVMSG {CHANNEL} :{user}, fui de fininho entregar-te a história em PVT! 📩")
            
            # Envia sempre a história diretamente para o user em PVT
            for linha in HISTORIA_THEOG:
                send_raw(irc_socket, f"PRIVMSG {user} :{linha}")
                time.sleep(1.8)
            return True
            
        if msg.startswith("!pergunta"):
            q = message[10:].strip()
            if q:
                threading.Thread(target=lambda: send_raw(irc_socket, f"PRIVMSG {target} :{user}: {ask_hugging_face(q)[:400]}")).start()
            return True
            
        if msg.startswith("!lapada"):
            dest = message.split()[1] if len(message.split()) > 1 else user
            send_raw(irc_socket, f"PRIVMSG {CHANNEL} :\x01ACTION {random.choice(LAPADAS).format(u=dest)} (por {user})\x01")
            return True
            
        if msg.startswith("!prenda"):
            dest = message.split()[1] if len(message.split()) > 1 else user
            send_raw(irc_socket, f"PRIVMSG {CHANNEL} :\x01ACTION {random.choice(PRENDAS).format(u=dest)} (cortesia de {user})\x01")
            return True

    if NICK.lower() in msg:
        send_raw(irc_socket, f"PRIVMSG {target} :{user}: {random.choice(OG_EVASIVE)}")
        return True
    return False

def loops_fundo(sock):
    while True:
        time.sleep(1200) # 20 min
        if random.random() > 0.5:
            send_raw(sock, f"PRIVMSG {CHANNEL} :{random.choice(REFORCO_POSITIVO)}")
        else:
            inativos = [n for n in list(CHANNEL_USERS) if n.lower() not in BOT_FILTER]
            if inativos:
                u = random.choice(inativos)
                send_raw(sock, f"PRIVMSG {CHANNEL} :{random.choice(PUXAR_CONVERSA).format(u=u)}")

def run_irc_bot():
    while True:
        try:
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.connect((SERVER, PORT))
            send_raw(irc, f"NICK {NICK}")
            send_raw(irc, f"USER {NICK} 8 * :TheOG Bot")
            threads_started = False
            while True:
                data = irc.recv(4096).decode("utf-8", errors="ignore")
                if not data: break
                for line in data.split("\r\n"):
                    if "PING" in line: send_raw(irc, f"PONG {line.split()[1]}")
                    if "376" in line:
                        send_raw(irc, f"PRIVMSG NickServ :IDENTIFY {PASS}")
                        send_raw(irc, f"JOIN {CHANNEL}")
                        if not threads_started:
                            threading.Thread(target=loops_fundo, args=(irc,), daemon=True).start()
                            threads_started = True
                    if " JOIN " in line:
                        u = line.split('!')[0][1:]
                        CHANNEL_USERS.add(u); LAST_SEEN[u] = time.time()
                    if " PRIVMSG " in line:
                        u = line.split('!')[0][1:]; c = line.split(" :", 1)[1]
                        handle_interaction(u, c, f"PRIVMSG {NICK}" in line, irc)
        except: time.sleep(15)

@app.route('/')
def home(): return "TheOG Online - História em PVT, Listas Completas e Sem Cortes!"

if __name__ == "__main__":
    threading.Thread(target=run_irc_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
