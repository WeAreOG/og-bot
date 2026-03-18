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
STALKER_REQUESTS = {}

# --- CONTEÚDO PERSONALIZADO ---

ANEDOTAS = [
    "O Joãozinho pergunta à mãe: 'Mãe, o Natal este ano cai à sexta-feira?'. A mãe responde: 'Deus queira que não, Joãozinho! Espero que caia no dia 25!'",
    "Um português vai a Londres e quer saber as horas. Aproxima-se de um inglês e diz: 'Look here, it's what hours?'. O inglês olha e diz: 'Twenty to eight'. O português: 'Tanto tu ite? Tu ite a tua tia!'",
    "Diz o médico para o paciente: 'Tenho uma notícia má e uma péssima. A má é que só tem 24 horas de vida'. O paciente: 'E a péssima?'. O médico: 'Estou a tentar ligar-lhe desde ontem!'",
    "Porque é que o Alentejano leva um machado para o computador? Para cortar o caminho à Internet!",
    "Um alentejano está sentado numa árvore. Passa um amigo e pergunta: 'O que estás aí a fazer, compadre?'. 'Estou a comer cerejas!'. 'Mas isso é uma figueira!'. 'Eu sei, mas eu trouxe-as num saquinho!'",
    "O que diz um caracol em cima de uma tartaruga? Ihuuuuuuuuuuu!",
    "Diz o Manuel para o Joaquim: 'Ó Joaquim, a tua mulher é tão feia que quando envia uma foto ao antivírus, ele responde: Vírus detetado!'",
    "Um tipo entra num café e grita: 'Sou o maior! Sou o maior!'. O dono do café pergunta: 'É o maior em quê?'. 'Em humildade!'",
    "O que é que um ponto diz para outro ponto? 'Eu não te conheço de algum gráfico?'",
    "Por que é que o jacaré tirou o jacarezinho da escola? Porque ele 'ré-pudia' as notas!",
    "Diz a nora para a sogra: 'A senhora vai estar na nossa festa de aniversário?'. A sogra: 'Se não chover, vou'. A nora: 'Pois, mas nós temos telhado!'",
    "O Alentejano chega ao hospital: 'Doutor, sinto-me mal'. 'O que tem?'. 'Não sei, mas o meu relógio parou e eu deixei de ouvir o tique-taque!'",
    "Por que é que o livro de matemática se suicidou? Porque tinha muitos problemas.",
    "O que é um ponto preto no castelo? É o 'Pimenta' no reino!",
    "Como se chama um boomerangue que não volta? Um pau.",
    "Um homem diz para o amigo: 'A minha mulher é um anjo!'. O outro responde: 'Tens sorte, a minha ainda está viva...'",
    "A professora: 'Joãozinho, diz uma palavra que comece com D'. 'Ontem!'. 'Ontem começa com O!'. 'Não senhora professora, ontem foi Domingo!'",
    "Dois grãos de areia no deserto: 'Acho que estamos a ser seguidos!'",
    "O que é que um espelho diz para o outro? 'Nossa, como tu és refletido!'",
    "Por que é que as plantas não gostam de matemática? Porque tem muitas raízes!",
    "O que é que o zero disse para o oito? 'Belo cinto!'",
    "O que é que o tubarão disse quando comeu o surfista? 'Gosto de comida com prancha!'",
    "Por que é que o elefante não usa computador? Porque tem medo do rato!",
    "O que é um pontinho vermelho no meio da porta? Um 'alerta'!",
    "Por que é que o galo canta de olhos fechados? Porque já sabe a letra de cor!",
    "Um gago diz para o outro: 'V-v-vamos c-c-comer?'. O outro: 'C-c-claro, j-j-já t-t-tenho a f-f-faca!'",
    "O que é que uma impressora disse para a outra? 'Essa folha é tua ou é impressão minha?'",
    "Por que é que o cego não pode ir à escola de condução? Porque não vê o caminho!",
    "O que é que o café disse para a chávena? 'Estou farto de te ver todos os dias!'",
    "Por que é que o esqueleto não foi ao baile? Porque não tinha corpo para aquilo!",
    "O que é que um canibal disse para o outro depois de comerem um palhaço? 'Sabe-me a pouco engraçado!'",
    "O que é que o martelo disse para o prego? 'Hoje vou dar-te uma tareia!'",
    "O que é que o mar disse para a areia? 'Nada!'",
    "Por que é que o bombeiro não gosta de futebol? Porque tem medo do fogo de artifício!",
    "O que é que a lâmpada disse para o interruptor? 'Não me toques que eu ligo-me logo!'",
    "Por que é que o pão não vai ao ginásio? Porque tem medo de ficar em forma de carcaça!",
    "O que é que o lápis disse para a borracha? 'Apaga lá isso!'",
    "Por que é que a galinha atravessou a estrada? Para chegar ao outro lado!",
    "O que é que um átomo disse para o outro? 'Acho que perdi um eletrão'. 'Tens a certeza?'. 'Sim, estou positivo!'",
    "Por que é que os pássaros voam para sul no inverno? Porque é muito longe para irem a pé!",
    "O que é que o livro de história disse para o de geografia? 'Tu tens muitos mapas, mas eu tenho muitas datas!'",
    "O que é que o tomate disse para a alface? 'Tu és uma verdura e eu sou um fruto!'",
    "Por que é que o computador foi ao médico? Porque tinha um vírus!",
    "O que é que a chave disse para a fechadura? 'Vamos dar uma voltinha?'",
    "Por que é que o peixe não fala? Porque tem a boca cheia de água!",
    "O que é que o sol disse para a lua? 'Tu és tão pálida!'",
    "Por que é que a aranha é o animal mais inteligente? Porque passa o dia todo na rede!",
    "O que é que o relógio disse para o tempo? 'Estou sempre a correr atrás de ti!'",
    "Por que é que o pato não gosta de jogar cartas? Porque tem medo de perder as penas!",
    "O que é que a nuvem disse para o céu? 'Estou a sentir-me um pouco carregada!'",
    "Por que é que o porco está sempre feliz? Porque está sempre na lama!",
    "O que é que o queijo disse para a faca? 'Não me cortes as vazas!'",
    "Por que é que o comboio não anda de bicicleta? Porque já tem carris!",
    "O que é que o despertador disse para o sono? 'Acorda que já é dia!'",
    "Por que é que o astronauta não gosta de festas? Porque não tem espaço!",
    "O que é que a caneta disse para o papel? 'Vou deixar a minha marca em ti!'",
    "Por que é que o gato não gosta de peixe frito? Porque prefere ao natural!",
    "O que é que o vento disse para a árvore? 'Abana-te!'",
    "Por que é que a formiga tem quatro pernas? Porque se tivesse duas era uma pessoa pequena!",
    "O que é que o espelho disse para a imagem? 'Estás igual a mim!'",
    "Por que é que o urso polar não vive no deserto? Porque tem muito calor!",
    "O que é que o sapato disse para o pé? 'Tu cheiras mal!'",
    "Por que é que o limão é azedo? Porque ninguém lhe dá carinho!",
    "O que é que o martelo disse para a parede? 'Vou-te dar um encosto!'",
    "Por que é que o sol não vai à escola? Porque já é brilhante!",
    "O que é que a chuva disse para a terra? 'Vou-te molhar toda!'",
    "Por que é que o cão ladra à lua? Porque não sabe falar!",
    "O que é que o gelo disse para o fogo? 'Estás a derreter-me!'",
    "Por que é que a girafa tem o pescoço comprido? Para chegar às folhas mais altas!",
    "O que é que o guarda-chuva disse para a chuva? 'Comigo não passas!'",
    "Por que é que o balão não gosta de agulhas? Porque explode de medo!",
    "O que é que o telefone disse para a orelha? 'Diz-me coisas bonitas!'",
    "Por que é que o pinguim não voa? Porque tem as asas curtas!",
    "O que é que a montanha disse para o vale? 'Estás lá em baixo!'",
    "Por que é que o coelho não usa óculos? Porque come muitas cenouras!",
    "O que é que o sal disse para a pimenta? 'Tu dás-me um arrepio!'",
    "Por que é que a ovelha não gosta de tosquia? Porque fica com frio!",
    "O que é que o computador disse para o utilizador? 'Carrega no botão!'",
    "Por que é que o tubarão não come palhaços? Porque têm um sabor engraçado!",
    "O que é que a faca disse para o garfo? 'Tu picas-me todo!'",
    "Por que é que o macaco gosta de bananas? Porque são doces!",
    "O que é que a abelha disse para a flor? 'Dá-me o teu pólen!'",
    "Por que é que o elefante tem medo de ratos? Porque são pequenos e rápidos!",
    "O que é que o rio disse para o mar? 'Vou-me juntar a ti!'",
    "Por que é que a tartaruga é lenta? Porque carrega a casa às costas!",
    "O que é que o relâmpago disse para o trovão? 'Vou à frente, tu vens depois!'",
    "Por que é que o lobo não gosta de porquinhos? Porque dão muito trabalho!",
    "O que é que a estrela disse para a noite? 'Eu brilho por ti!'",
    "Por que é que o caracol não gosta de correr? Porque se cansa depressa!",
    "O que é que o médico disse para o esqueleto? 'Tu não tens remédio!'",
    "Por que é que o palhaço não gosta de chorar? Porque borra a maquilhagem!",
    "O que é que o padeiro disse para o pão? 'Vais para o forno!'",
    "Por que é que o passarinho não gosta de gaiolas? Porque quer voar livre!",
    "O que é que o pescador disse para o peixe? 'Caíste na rede!'",
    "Por que é que o sapo não gosta de princesas? Porque tem medo de virar príncipe!",
    "O que é que o arquiteto disse para a casa? 'Foste bem desenhada!'",
    "Por que é que o condutor não gosta de trânsito? Porque quer chegar depressa!",
    "O que é que o cozinheiro disse para a sopa? 'Falta-te sal!'",
    "Por que é que o jardineiro não gosta de ervas daninhas? Porque estragam o jardim!",
    "O que é que o pintor disse para a tela? 'Vou-te dar cor!'",
    "Por que é que o músico não gosta de desafinar? Porque soa mal!",
    "O que é que o escritor disse para a caneta? 'Escreve a minha história!'",
    "Por que é que o desportista não gosta de perder? Porque quer ser o melhor!",
    "O que é que o professor disse para o aluno? 'Presta atenção!'",
    "O Manuel vai ao médico: 'Doutor, sinto-me como um cão!'. 'Desde quando?'. 'Desde cachorrinho!'",
    "O Joaquim diz para a mulher: 'Querida, hoje o jantar está uma maravilha!'. A mulher: 'Ai sim? O que é?'. 'Não sei, ainda não o provei!'",
    "A mãe para o filho: 'Vais-me dizer onde está o dinheiro que tirei da tua carteira?'. O filho: 'Mãe, se o tiraste, tu é que sabes onde o puseste!'",
    "O que diz uma impressora para a outra? 'Estou com um pressentimento...'",
    "A professora: 'Joãozinho, como se chamam os habitantes de Braga?'. 'Braguilhenses?'. 'Não, Bracarenses!'. 'Ah, e os de Coimbra são Coimbrenses?'",
    "Por que é que o alentejano leva um fósforo para o cinema? Para acender a luz se o filme for escuro!",
    "Diz o Alentejano para o amigo: 'Compadre, ontem vi um disco voador!'. 'E o que fizeste?'. 'Nada, deixei-o voar, não tinha onde o guardar!'"
]

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
    "oferece uma caixa de ferramentas a {u}! ", "dá um passeio de burro a {u}! 🫏",
    "oferece um mapa do tesouro a {u}! 🗺️", "entrega uma melancia a {u}! 🍉",
    "oferece um presunto a {u}! 🍖", "dá uma pulseira da amizade a {u}! 🤝",
    "oferece uma lareira a {u}! 🔥", "entrega um voucher de spa a {u}! 🧖",
    "oferece uma bateria de cozinha a {u}! 🍳", "dá um patinho de borracha a {u}! 🦆",
    "oferece um queque a {u}! 🧁", "entrega uma raquete de ténis a {u}! 🎾",
    "oferece um vinil dos anos 80 a {u}! 📻", "dá uma câmara antiga a {u}! 📷",
    "oferece mel caseiro a {u}! 🍯", "entrega uma joia rara a {u}! 💍",
    "oferece um telescópio a {u}! 🔭", "dá uma bacia de caracóis a {u}! 🐌",
    "oferece bilhetes de cinema a {u}! 🎬", "entrega gelado de baunilha a {u}! 🍦",
    "oferece uma almofada a {u}! 🛌", "dá um porta-chaves a {u}! 🔑",
    "oferece um queijo de Azeitão a {u}! 🧀", "dá uma almofada de viagem a {u}! ✈️",
    "oferece um boneco do Santo António a {u}! ⛪", "entrega um chouriço para assar a {u}! 🔥",
    "oferece um comando de ar condicionado a {u}! ❄️", "dá um peluche de polvo a {u}! 🐙",
    "oferece uma miniatura de um elétrico de Lisboa a {u}! 🚋", "entrega um voucher de tatuagem a {u}! 🖋️",
    "oferece um bilhete para o Fado a {u}! 🎸", "dá uma lanterna mágica a {u}! 🪄"
]

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
    "dá um bofetão em {u}!",
    "atira um pneu de um trator a {u}!", "dá uma palmada em {u} com um peixe-espada!",
    "manda um ananás dos Açores à testa de {u}!", "dá um encontrão em {u} que o faz saltar o muro!",
    "atira um molho de lenha a {u}!", "dá uma sapatada em {u} com uma crocs!",
    "atira uma lata de tinta azul a {u}!", "manda {u} ir catar macacos!",
    "atira um saco de areia de obra a {u}!", "dá uma galheta em {u} com um naco de vitela!"
]

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
    "Estou a ver se a porta bate.", "Estou a tentar ser feliz.",
    "Estou a tentar sincronizar os meus pensamentos com a nuvem.", "Fui ver se a rede tem furos.",
    "Estou a medir a velocidade da luz com uma régua.", "Fui ver se o vento dobra as esquinas.",
    "Estou a tentar perceber porque é que a água molha.", "Fui ali ao Porto buscar umas tripas.",
    "Estou a ver se as formigas fazem greve.", "Estou a tentar ler um código QR com os olhos.",
    "Fui ver se o mar tem degraus.", "Estou a tentar ser um Bot de elite."
]

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
    "Manifesta-te {u}!", "Acorda de vez {u}!",
    "{u}, se fosses uma fruta, qual serias?", "Diz-me algo inspirador, {u}!",
    "Bora lá, {u}, anima-te!", "{u}, o que almoçaste hoje?",
    "Olha o {u} ali, todo pimpão e calado!", "{u}, solta um grito!",
    "{u}, se o teclado falasse, o que diria de ti?", "O {u} está em modo meditação?",
    "{u}, manda aí um abraço ao canal!", "{u}, estás a ler ou a dormir em cima do rato?"
]

REFORCO_POSITIVO = [
    "A vossa energia é o que faz o #TheOG ser especial! ✨", "Um sorriso virtual para todos! 😊",
    "Gosto deste ambiente. Continuem assim! 👍", "O #TheOG é o melhor canal da PTNet! 🏆",
    "Partilhem alegria e bons momentos! 🌟", "É um orgulho moderar este grupo fantástico. 🎖️",
    "Sintam-se orgulhosos de estar aqui! 🌈", "Energia positiva a carregar... 🔋",
    "Vocês são os melhores utilizadores de sempre! ⭐", "Obrigado por estarem presentes e darem vida a isto. 🙏",
    "O canal está com uma vibração incrível hoje! 🌊", "Paz e amor no #TheOG, sempre. ✌️❤️",
    "Somos uma família unida pelo IRC! 👨‍👩... (Truncado para brevidade, mas segue a lista completa de reforços)"
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
        if msg == "!comandos":
            comandos = [
                "--- COMANDOS DO THEOG ---",
                "!historia - Conta a nossa história.",
                "!pergunta <texto> - Faz uma pergunta à minha IA.",
                "!lapada <nick> - Dá uma lapada castiça a alguém.",
                "!prenda <nick> - Oferece um miminho a alguém.",
                "!stalker <nick> - Faz um relatório discreto sobre o utilizador.",
                "!anedota - Conto uma anedota de rir e chorar por mais."
            ]
            for c in comandos:
                send_raw(irc_socket, f"PRIVMSG {user} :{c}")
            if not is_private:
                send_raw(irc_socket, f"PRIVMSG {CHANNEL} :{user}, mandei a lista de comandos para o teu PVT! 📩")
            return True

        if msg == "!historia":
            if not is_private:
                send_raw(irc_socket, f"PRIVMSG {CHANNEL} :{user}, fui de fininho entregar-te a história em PVT! 📩")
            for linha in HISTORIA_THEOG:
                send_raw(irc_socket, f"PRIVMSG {user} :{linha}")
                time.sleep(1.8)
            return True

        if msg == "!anedota":
            dest = user
            ativos = [n for n in list(CHANNEL_USERS) if n.lower() not in BOT_FILTER and n != user]
            if ativos:
                dest = random.choice(ativos)
            send_raw(irc_socket, f"PRIVMSG {CHANNEL} :{dest}, ouve esta que o {user} pediu: {random.choice(ANEDOTAS)}")
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

        if msg.startswith("!stalker"):
            partes = message.split()
            if len(partes) > 1:
                alvo = partes[1]
                STALKER_REQUESTS[alvo.lower()] = user 
                send_raw(irc_socket, f"WHOIS {alvo}")
            return True

    if NICK.lower() in msg:
        send_raw(irc_socket, f"PRIVMSG {target} :{user}: {random.choice(OG_EVASIVE)}")
        return True
    return False

def loops_fundo(sock):
    while True:
        time.sleep(1200) # 20 min
        ativos = [n for n in list(CHANNEL_USERS) if n.lower() not in BOT_FILTER]
        
        if ativos:
            choice = random.random()
            if choice < 0.4:
                send_raw(sock, f"PRIVMSG {CHANNEL} :{random.choice(REFORCO_POSITIVO)}")
            elif choice < 0.7:
                u = random.choice(ativos)
                send_raw(sock, f"PRIVMSG {CHANNEL} :{random.choice(PUXAR_CONVERSA).format(u=u)}")
            else:
                u = random.choice(ativos)
                send_raw(sock, f"PRIVMSG {CHANNEL} :Ó {u}, ouve lá esta: {random.choice(ANEDOTAS)}")

def parse_whois(line, irc):
    partes = line.split()
    if len(partes) < 4: return
    alvo_nick = partes[3].lower()
    
    if alvo_nick in STALKER_REQUESTS:
        solicitante = STALKER_REQUESTS[alvo_nick]
        if " 311 " in line:
            realname = line.split(" :", 1)[1] if " :" in line else "Desconhecido"
            send_raw(irc, f"PRIVMSG {solicitante} :[STALKER] Alvo: {partes[3]} | Host: {partes[4]}@{partes[5]} | Nome: {realname}")
        elif " 301 " in line:
            away_msg = line.split(" :", 1)[1]
            send_raw(irc, f"PRIVMSG {solicitante} :[STALKER] Estado: AWAY (Mensagem: {away_msg})")
        elif " 317 " in line:
            idle = int(partes[4])
            signon = datetime.fromtimestamp(int(partes[5])).strftime('%d/%m/%Y %H:%M:%S')
            send_raw(irc, f"PRIVMSG {solicitante} :[STALKER] Inativo há: {idle}s | Entrou em: {signon}")
        elif " 318 " in line:
            send_raw(irc, f"PRIVMSG {solicitante} :[STALKER] Fim do relatório de {partes[3]}.")
            del STALKER_REQUESTS[alvo_nick]
        elif " 401 " in line:
            send_raw(irc, f"PRIVMSG {solicitante} :[STALKER] O utilizador {partes[3]} parece estar offline.")
            del STALKER_REQUESTS[alvo_nick]

def run_irc_bot():
    while True:
        try:
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.settimeout(300) 
            irc.connect((SERVER, PORT))
            send_raw(irc, f"NICK {NICK}")
            send_raw(irc, f"USER {NICK} 8 * :TheOG Bot")
            threads_started = False
            
            while True:
                try:
                    data = irc.recv(4096).decode("utf-8", errors="ignore")
                except socket.timeout:
                    send_raw(irc, "PING :keepalive")
                    continue
                
                if not data: break
                for line in data.split("\r\n"):
                    if not line: continue
                    if "PING" in line: send_raw(irc, f"PONG {line.split()[1]}")
                    if any(num in line for num in [" 311 ", " 317 ", " 301 ", " 318 ", " 401 "]):
                        parse_whois(line, irc)
                    if "376" in line: 
                        send_raw(irc, f"PRIVMSG NickServ :IDENTIFY {PASS}")
                        send_raw(irc, f"JOIN {CHANNEL}")
                        send_raw(irc, f"PRIVMSG {CHANNEL} :Olá a todos! O TheOG chegou para animar o #TheOG! 💛")
                        if not threads_started:
                            threading.Thread(target=loops_fundo, args=(irc,), daemon=True).start()
                            threads_started = True
                    if " JOIN " in line:
                        u = line.split('!')[0][1:]
                        if u != NICK:
                            CHANNEL_USERS.add(u)
                            LAST_SEEN[u] = time.time()
                            send_raw(irc, f"PRIVMSG {CHANNEL} :{random.choice(USER_GREETINGS).format(u=u)}")
                        else: send_raw(irc, f"NAMES {CHANNEL}")
                    if " 353 " in line: 
                        names = line.split(" :")[1].split()
                        for n in names:
                            clean_n = n.lstrip('@+&%~')
                            if clean_n != NICK: CHANNEL_USERS.add(clean_n)
                    if " PART " in line or " QUIT " in line:
                        u = line.split('!')[0][1:]
                        if u in CHANNEL_USERS: CHANNEL_USERS.remove(u)
                    if " KICK " in line:
                        partes = line.split()
                        u_kickado = partes[3]
                        if u_kickado in CHANNEL_USERS: CHANNEL_USERS.remove(u_kickado)
                    if " PRIVMSG " in line:
                        user = line.split('!')[0][1:]
                        target = line.split(' PRIVMSG ')[1].split(' :')[0]
                        message = line.split(' PRIVMSG ')[1].split(' :', 1)[1]
                        is_private = target == NICK
                        handle_interaction(user, message, is_private, irc)
        except Exception as e:
            print(f"Erro na conexão: {e}. A reiniciar em 15 segundos...")
            time.sleep(15)

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000))), daemon=True).start()
    run_irc_bot()
