from iqoptionapi.stable_api import IQ_Option
from datetime import datetime
from dateutil import tz
from colorama import Fore
from bs4 import BeautifulSoup
import threading, json, sys, requests, configparser, csv, time, os, colorama
import pandas as pd

vitorias = 0
derrotas = 0
timerzoner60_300 = ''
timerzoner5_15 = ''

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

colorama.init(autoreset=True)


def horaAtual():
    data = datetime.now()
    tm = tz.gettz('America/Bogota')
    tempoAtual = data.astimezone(tm)
    horaAgora = tempoAtual.strftime('%H:%M:%S')
    return horaAgora


def timerzone(timeframe):
    if traderTimerZone == 'S':
        if timeframe < 5:
            soup = BeautifulSoup(timerzoner60_300.text, 'html.parser')
        else:
            soup = BeautifulSoup(timerzoner5_15.text, 'html.parser')

        table = soup.find('table', attrs={'id': 'map-responsive'})
        rows = table.findAll('th', {"class": "th-map"})
        horariosECores = {}
        for x in rows:
            bg = x.attrs['style'].replace(";background:", "")
            if bg == "#ED3237":
                cor = "Vermelho"
            else:
                cor = ""
            hora = x.text
            hora = hora.replace("\n                                ", "").replace(
                "              ", "")
            hc = {hora: cor}
            horariosECores.update(hc)

        for x in horariosECores:
            if horaAtual()[0:5] == x and horariosECores[x] == 'Vermelho':
                return True
        return False
    else:
        return False


def Total_Operacoes(lucro):
	global total_operacoes, vitorias, derrotas, total_porcentagem
	if lucro > 0:
		vitorias += 1
	else:
		derrotas += 1
	total_operacoes = vitorias + derrotas
	total_porcentagem = int(vitorias / total_operacoes * 100)
	if trailing_stop == 'S':
		Trailing_Stop(lucro)


def banca():
	global account_type, account_balance, valor_da_banca
	account_type = config['conta']
	valor_da_banca = API.get_balance()
	account_balance = '${:,.2f}'.format(valor_da_banca) if API.get_currency(
	) == 'USD' else 'USD${:,.2f}'.format(valor_da_banca)


def configuracao():
	global vitorias, derrotas, total_operacoes, total_porcentagem
	arquivo = configparser.RawConfigParser()
	arquivo.read('config.txt')
	vitorias = 0
	derrotas = 0
	total_operacoes = 0
	total_porcentagem = 0

	return {'entrada': arquivo.get('GERAL', 'entrada'), 'entrada_percentual': arquivo.get('GERAL', 'entrada_percentual'), 'conta': arquivo.get('GERAL', 'conta'), 'stop_win': arquivo.get('GERAL', 'stop_win'), 'stop_loss': arquivo.get('GERAL', 'stop_loss'), 'payout': 0, 'banca_inicial': 0, 'martingale': arquivo.get('GERAL', 'martingale'), 'mgProxSinal': arquivo.get('GERAL', 'mgProxSinal'), 'valorGale': arquivo.get('GERAL', 'valorGale'), 'niveis': arquivo.get('GERAL', 'niveis'), 'analisarTendencia': arquivo.get('GERAL', 'analisarTendencia'), 'noticias': arquivo.get('GERAL', 'noticias'), 'timerzone': arquivo.get('GERAL', 'timerzone'), 'hitVela': arquivo.get('GERAL', 'hitVela'), 'telegram_token': arquivo.get('telegram', 'telegram_token'), 'telegram_id': arquivo.get('telegram', 'telegram_id'), 'usar_bot': arquivo.get('telegram', 'usar_bot'), 'email': arquivo.get('CONTA', 'email'), 'senha': arquivo.get('CONTA', 'senha'), 'trailing_stop': arquivo.get('GERAL', 'trailing_stop'), 'trailing_stop_valor': arquivo.get('GERAL', 'trailing_stop_valor'), 'payout_minimo': arquivo.get('GERAL', 'payout'), 'usar_ciclos': arquivo.get('CICLOS', 'usar_ciclos'), 'ciclos_nivel': arquivo.get('CICLOS', 'nivel_ciclos')}


def Clear_Screen():
	sistema = os.name
	if sistema == 'nt':
		os.system('cls')
	else:
		os.system('clear')


config = configuracao()
email = config['email']
senha = config['senha']

global galeRepete, lucroTotal, parAntigo, direcaoAntigo, timeframeAntigo, valor_entrada, galeSinalRepete, proxSinal
galeRepete = False
parAntigo = ''
direcaoAntigo = ''
timeframeAntigo = ''
lucroTotal = 0
novo_stop_loss = 0
trailing_ativo = False
valorGaleProxSinal = float(config['entrada'])
valor_entrada = float(config['entrada'])
analisarTendencia = config['analisarTendencia']
galeVela = config['mgProxSinal']
galeSinal = config['martingale']
noticias = config['noticias']
traderTimerZone = config['timerzone']
hitdeVela = config['hitVela']
trailing_stop = config['trailing_stop']
trailing_stop_valor = float(config['trailing_stop_valor'])
payout_minimo = int(config['payout_minimo'])
ciclos_ativos = 0
valor_entrada_ciclo = float(config['entrada'])
entrada_percentual = config['entrada_percentual']
periodo = 20

global VERIFICA_BOT, TELEGRAM_ID
VERIFICA_BOT = config['usar_bot']
TELEGRAM_ID = config['telegram_id']
Clear_Screen()
print(f'''{Fore.BLUE}
██████╗░░█████╗░████████╗░░░░░░███████╗██████╗░███████╗███████╗  ██████╗░░░░░█████╗░
██╔══██╗██╔══██╗╚══██╔══╝░░░░░░██╔════╝██╔══██╗██╔════╝██╔════╝  ╚════██╗░░░██╔══██╗
██████╦╝██║░░██║░░░██║░░░█████╗█████╗░░██████╔╝█████╗░░█████╗░░  ░░███╔═╝░░░██║░░██║
██╔══██╗██║░░██║░░░██║░░░╚════╝██╔══╝░░██╔══██╗██╔══╝░░██╔══╝░░  ██╔══╝░░░░░██║░░██║
██████╦╝╚█████╔╝░░░██║░░░░░░░░░██║░░░░░██║░░██ ███████╗███████╗  ███████╗██╗╚█████╔╝
╚═════╝░░╚════╝░░░░╚═╝░░░░░░░░░╚═╝░░░░░╚═╝░░╚═╝╚══════╝╚══════╝  ╚══════╝╚═╝░╚════╝░''')
print(f'\n{Fore.RED}                      ＞＞＞ ＣＯＮＥＣＴＡＮＤＯ ＜＜＜\n')
if noticias == 'S':
	try:
		response = requests.get("http://botpro.com.br/calendario-economico/")
		texto = response.content
	except:
		print('Error al cargar json de noticias!!')
		noticias = 'N'
if traderTimerZone == 'S':
	try:
		timerzoner60_300 = requests.get('https://tradertimerzone.com/web/index.php?r=operation/maps&model=60-300', headers=headers)
		timerzoner5_15 = requests.get('https://tradertimerzone.com/web/index.php?r=operation%2Fmaps&model=5-15', headers=headers)
	except:
		print('Error al cargar json de Trader Timer Zone!!')
		traderTimerZone = 'N'
API = IQ_Option(email, senha)


def Mensagem(mensagem):
	if VERIFICA_BOT == 'S':
		token = config['telegram_token']
		url = f'https://api.telegram.org/bot{token}/'
		try:
			return requests.post(url + 'sendMessage', {'chat_id': TELEGRAM_ID, 'text': str(mensagem)})
		except:
			print(f'{Fore.RED}ERROR AL ENVIAR MENSAGE AL TELEGRAM!!')


def timestamp_converter():
	hora = datetime.now()
	tm = tz.gettz('America/Bogota')
	hora_atual = hora.astimezone(tm)
	return hora_atual.strftime('%H:%M:%S')


def timeFrame(timeframe):

	if timeframe == 'M1':
		return 1

	elif timeframe == 'M5':
		return 5

	elif timeframe == 'M15':
		return 15

	elif timeframe == 'M30':
		return 30

	elif timeframe == 'H1':
		return 60
	else:
		return 'erro'


def verificarStop():
	if lucroTotal >= stop_win:
		deustop = 'WIN'
	elif lucroTotal <= stop_loss:
		deustop = 'LOSS'
	else:
		deustop = False
	if deustop:
		while True:
			thread_ativas = threading.active_count()
			if thread_ativas == 2:
				banca()
				mensagem = f'STOP {deustop} BATIDO!!! - RESULTADO: {float(round(lucroTotal, 2))}\n'
				mensagem += f'Operaciones: {total_operacoes} | Ganadoras: {vitorias} | Perdedoras: {derrotas}\nAcierto: {total_porcentagem}%\n'
				mensagem += f"Saldo de cuenta {'demo' if account_type == 'PRACTICE' else 'real'}: {account_balance}"
				print(f'{Fore.BLUE}{mensagem}')
				Mensagem(mensagem)
				sys.exit()
			else:
				print(
				    f'{Fore.RED}ESPERANDO LA FINALIZACION DE {Fore.GREEN}{thread_ativas - 2} THREADS', end='\x1b[K\r')
				time.sleep(5)


def Trailing_Stop(lucro):
	global stop_loss, novo_stop_loss
	if lucroTotal >= trailing_stop_valor and lucro > 0:
		novo_stop_loss += int(lucro)
		stop_loss = novo_stop_loss
		print(f'{Fore.GREEN}Trailing STOP ajustado! Nuevo STOP LOSS: {stop_loss}')
		Mensagem(f'Trailing STOP ajustado! Nuevo STOP LOSS: {stop_loss}')


def buscarMenor():
	global em_espera, get_profit
	get_profit = True
	arquivo = open('./lista.csv')
	leitor = csv.reader(arquivo, delimiter=';')
	timeNow = timestamp_converter()
	f = '%H:%M:%S'
	em_espera = []
	for row in leitor:
		if len(row[2]) == 5:
			horario = row[2] + ":00"
		else:
			horario = row[2]
		dif = int((datetime.strptime(timeNow, f) - datetime.strptime(horario, f)).total_seconds())
		# Filtro para excluir os sinais que ja se passaram os horarios
		if dif < -40:
			# Adiciona a diferença de tempo em segundos para posterior sorteio de menor valor
			row.append(dif)
			# Coloca os dados da paridade juntamente com o tempo restante para entrada em uma lista
			em_espera.append(row)

	# Verifica se a lista tem sinais pendentes para operar, caso contrario verifica se ainda tem posicoes abertas e aguarda o encerramento pra finalizar o bot
	if len(em_espera) == 0:
		while True:
			thread_ativas = threading.active_count()
			if thread_ativas == 2:
				em_espera = False
				banca()
				mensagem = f'Lista de señales finalizada..\nBeneficio: USD${str(round(lucroTotal, 2))}\n'
				mensagem += f'Operaciones: {total_operacoes} | Ganadas: {vitorias} | Perdidas: {derrotas}\n Efectividad: {total_porcentagem}%\n'
				mensagem += f"Saldo de cuenta {'demo' if account_type == 'PRACTICE' else 'real'}: {account_balance}"
				print(f'{Fore.GREEN}{mensagem}')
				Mensagem(mensagem)
				sys.exit()
			else:
				print(
				    f'{Fore.RED}ESPERANDO FINALIZACION DE {Fore.GREEN}{thread_ativas - 2} THREADS', end='\x1b[K\r')
				time.sleep(60)
	else:
		# Ordena a lista pela entrada mais proxima
		em_espera.sort(key=lambda x: x[4], reverse=True)
		# Informa quantos sinais restam para serem executados
		print(f'SEÑALES PENDIENTES {len(em_espera)}')
		# Informa o próximo sinal a ser executado
		print(f'{Fore.BLUE}SIGUIENTE OPERACION: {em_espera[0][1]} | TIEMPO: {em_espera[0][0]} | HORA: {em_espera[0][2]} | POSICION: {em_espera[0][3]}')
		Mensagem(f'SEÑALES PENDIENTES: {len(em_espera)}\nPROXIMO: {em_espera[0][1]} | TIEMPO: {em_espera[0][0]} | HORA: {em_espera[0][2]} | POSICION: {em_espera[0][3]}')


def noticas(paridade):
	global noticas

	if noticias == 'S':
		try:
			objeto = json.loads(texto)

			# Verifica se o status code é 200 de sucesso
			if response.status_code != 200 or objeto['success'] != True:
				print('Error al encontrar noticias')

			# Pega a data atual
			data = datetime.now()
			tm = tz.gettz('America/Bogota')
			data_atual = data.astimezone(tm)
			data_atual = data_atual.strftime('%Y-%m-%d')
			tempoAtual = data.astimezone(tm)
			minutos_lista = tempoAtual.strftime('%H:%M:%S')

			# Varre todos o result do JSON
			for noticia in objeto['result']:
				# Separa a paridade em duas Ex: AUDUSD separa AUD e USD para comparar os dois
				paridade1 = paridade[0:3]
				paridade2 = paridade[3:6]

				# Pega a paridade, impacto e separa a data da hora da API
				moeda = noticia['economy']
				impacto = noticia['impact']
				atual = noticia['data']
				data = atual.split(' ')[0]
				hora = atual.split(' ')[1]

				# Verifica se a paridade existe da noticia e se está na data atual
				if moeda == paridade1 or moeda == paridade2 and data == data_atual:
					formato = '%H:%M:%S'
					d1 = datetime.strptime(hora, formato)
					d2 = datetime.strptime(minutos_lista, formato)
					dif = (d1 - d2).total_seconds()
					# Verifica a diferença entre a hora da noticia e a hora da operação
					minutesDiff = dif / 60

					# Verifica se a noticia irá acontencer 30 min antes ou depois da operação
					if minutesDiff >= -30 and minutesDiff <= 0 or minutesDiff <= 30 and minutesDiff >= 0:
						if impacto >= 1:
							return impacto, moeda, hora, True
					else:
						pass
				else:
					pass
			return 0, 0, 0, False
		except:
			print('Error al verificar noticias!! Filtro no funcionará')
			return 0, 0, 0, False
	else:
		return 0, 0, 0, False


def Get_All_Profit():
	global all_asset, profit
	try:
		all_asset = API.get_all_open_time()
		profit = API.get_all_profit()
	except:
		print(f'{Fore.RED}Error al obtener profit!!')


def checkProfit(par, timeframe):
	digital = False
	binaria = False
	turbo = False

	try:
		if timeframe > 15:
			binaria = int(profit[par]["turbo"] * 100)
			return "binaria", binaria

		if all_asset['digital'][par]['open']:
			digital = int(API.get_digital_payout(par))

		if all_asset['turbo'][par]['open']:
			turbo = int(profit[par]["turbo"] * 100)

		if all_asset['binary'][par]['open']:
			binaria = int(profit[par]["binary"] * 100)

		if binaria > digital and timeframe > 5:
			return "binaria", binaria

		if digital >= binaria and timeframe > 5:
			return "digital", digital

		if digital >= turbo and timeframe <= 5:
			return "digital", digital

		if turbo > digital and timeframe <= 5:
			return "binaria", turbo
	except:
            return False, 0


def Calcula_Valor_Ciclo(lucro):
	global valor_entrada_ciclo, ciclos_ativos
	ciclos_ativos += 1
	if lucro < 0 and ciclos_ativos <= int(config['ciclos_nivel']):
		valor_entrada_ciclo = round(float(config['entrada']) * (float(config['valorGale']) ** int(ciclos_ativos)))
	else:
		valor_entrada_ciclo = float(config['entrada'])
		ciclos_ativos = 0


def entradas(status, id, par, dir, timeframe, opcao, n, valorGaleSinal):
	global galeRepete, lucroTotal, parAntigo, direcaoAntigo, timeframeAntigo, valor_entrada, proxSinal, valorGaleProxSinal

	if opcao == 'digital':
		while True:
			resultado, lucro = API.check_win_digital_v2(id)

			if resultado:
				entrou_gale = False
				lucroTotal += lucro

				if lucro > 0:
					n = 1
					valorGaleSinal = config['entrada']
					valor_entrada = float(config['entrada'])
					print(f' | {id} | {par} -> win | USD${str(round(lucro, 2))}\n Beneficio: USD${str(round(lucroTotal, 2))}\n')
					Mensagem(f'{id} | {par} -> win | USD${str(round(lucro, 2))}\n Beneficio: USD${str(round(lucroTotal, 2))}')
				elif lucro == 0.0:
					n = 1
					valorGaleSinal = config['entrada']
					valor_entrada = float(config['entrada'])
					print(f' | {id} | {par} -> dogi | USD$0\n Beneficio: USD${str(round(lucroTotal, 2))}\n')
					Mensagem(f'{id} | {par} -> dogi | USD$0\n Beneficio: USD${str(round(lucroTotal, 2))}')
				else:
					print(f' | {id} | {par} -> loss | USD${str(round(lucro, 2))}\n Beneficio: USD${str(round(lucroTotal, 2))}\n')
					Mensagem(f'{id} | {par} -> loss | USD${str(round(lucro, 2))}\n Beneficio: USD${str(round(lucroTotal, 2))}')
					if galeVela == 'S':
						parAntigo = par
						direcaoAntigo = dir
						timeframeAntigo = timeframe
						valorGaleSinal = round(float(valorGaleSinal) * float(config['valorGale']), 2)
						if valorGaleSinal < (round(float(config['entrada']) * int(config['niveis']) * float(config['valorGale']), 2) + 0.01):
							galeRepete = True
							valorGaleProxSinal = valorGaleSinal

						else:
							valorGaleProxSinal = config['entrada']
							galeRepete = False

					elif galeSinal == 'S':
						valorGaleSinal = round(float(valorGaleSinal) * float(config['valorGale']), 2)
						if n <= int(config['niveis']):
							entrou_gale = True
							print(f' MARTINGALE NIVEL {n} EN EL PAR {par}..')
							Mensagem(f'MARTINGALE NIVEL {n} EN EL PAR {par}..')
							status, id = API.buy_digital_spot_v2(par, valorGaleSinal, dir, timeframe)
							n += 1
							threading.Thread(target=entradas, args=(
							    status, id, par, dir, timeframe, opcao, n, valorGaleSinal), daemon=True).start()

						else:
							n = 1
							valorGaleSinal = config['entrada']
				if not entrou_gale:
					Total_Operacoes(lucro)
					if config['usar_ciclos'] == 'S':
						Calcula_Valor_Ciclo(lucro)
				break

			time.sleep(0.5)

	elif opcao == 'binaria':
		if status:
			resultado, lucro = API.check_win_v4(id)

			if resultado:
				lucroTotal += lucro
				entrou_gale = False

				if resultado == 'win':
					n = 1
					valorGaleSinal = config['entrada']
					valor_entrada = float(config['entrada'])
					print(f' | {id} | {par} -> win | USD${str(round(lucro, 2))}\n Lucro: USD${str(round(lucroTotal, 2))}\n')
					Mensagem(f'{id} | {par} -> win | USD${str(round(lucro, 2))}\n Lucro: USD${str(round(lucroTotal, 2))}')
				elif resultado == 'equal':
					n = 1
					valorGaleSinal = config['entrada']
					valor_entrada = float(config['entrada'])
					print(f' | {id} | {par} -> doji | USD$0\n Lucro: USD${str(round(lucroTotal, 2))}\n')
					Mensagem(f'{id} | {par} -> doji | USD$0\n Lucro: USD${str(round(lucroTotal, 2))}')
				elif resultado == 'loose':
					print(f' | {id} | {par} -> loss | USD${str(round(lucro, 2))}\n Lucro: USD${str(round(lucroTotal, 2))}\n')
					Mensagem(f'{id} | {par} -> loss | USD${str(round(lucro, 2))}\n Lucro: USD${str(round(lucroTotal, 2))}')
					if galeVela == 'S':
						parAntigo = par
						direcaoAntigo = dir
						timeframeAntigo = timeframe
						valorGaleSinal = round(float(valorGaleSinal) * float(config['valorGale']), 2)
						if valorGaleSinal < (round(float(config['entrada']) * int(config['niveis']) * float(config['valorGale']), 2) + 0.01):
							galeRepete = True

						else:
							valorGaleSinal = float(config['entrada'])
							galeRepete = False

					elif galeSinal == 'S':
						valorGaleSinal = round(float(valorGaleSinal) * float(config['valorGale']), 2)
						if n <= int(config['niveis']):
							entrou_gale = True
							print(f' MARTINGALE NIVEL {n} EN EL PAR {par}..')
							Mensagem(f'MARTINGALE NIVEL {n} EN EL PAR {par}..')
							status, id = API.buy(valorGaleSinal, par, dir, timeframe)
							n += 1
							threading.Thread(target=entradas, args=(
							    status, id, par, dir, timeframe, opcao, n, valorGaleSinal), daemon=True).start()

						else:
							n = 1
							valorGaleSinal = config['entrada']
				if not entrou_gale:
					Total_Operacoes(lucro)
					if config['usar_ciclos'] == 'S':
						Calcula_Valor_Ciclo(lucro)

		else:
			print(f'{Fore.RED}ERROR AL REALIZAR OPERACION!!\n')
			Mensagem(f'Error al realizar operacion')


def Verificar_Tendencia(par, timeframe):
	velas = API.get_candles(par, (timeframe * 60), periodo, time.time())
	fechamento = round(velas[-1]['close'], 4)
	df = pd.DataFrame(velas)
	EMA = df['close'].ewm(span=periodo, adjust=False).mean()
	for data in EMA:
		EMA10 = data

	if EMA10 > fechamento:
		dir = 'put'
	elif fechamento > EMA10:
		dir = 'call'
	else:
		dir = False

	return dir


def Filtro_Hit_Vela(par, timeframe):
	velas = API.get_candles(par, (60 * timeframe), 5, time.time())
	velas[0] = 'r' if velas[0]['open'] > velas[0]['close'] else 'g'
	velas[1] = 'r' if velas[1]['open'] > velas[1]['close'] else 'g'
	velas[2] = 'r' if velas[2]['open'] > velas[2]['close'] else 'g'
	velas[3] = 'r' if velas[3]['open'] > velas[3]['close'] else 'g'
	hit = velas[0] + velas[1] + velas[2] + velas[3]
	if hit == 'rrrr' or hit == 'gggg':
		return True
	else:
		return False


def operar(valor_entrada, par, direcao, timeframe, horario, opcao, payout):
	status = False
	try:
		if opcao == 'digital':
			status, id = API.buy_digital_spot_v2(par, valor_entrada, direcao, timeframe)
			threading.Thread(target=entradas, args=(status, id, par, direcao, timeframe, opcao, 1, valor_entrada), daemon=True).start()
		elif opcao == 'binaria':
			status, id = API.buy(valor_entrada, par, direcao, timeframe)
			threading.Thread(target=entradas, args=(status, id, par, direcao, timeframe, opcao, 1, valor_entrada), daemon=True).start()
		else:
			print('ERROR AL REALIZAR ENTRADA!!')
			time.sleep(1)
	except:
		print('ERROR AL REALIZAR ENTRADA!!')
		time.sleep(1)

	if status:
		print(f'\n INICIANDO OPERACION {str(id)}..\n {str(horario)} | {par} | OPCION: {opcao.upper()} | DIRECION: {direcao.upper()} | M{timeframe} | PAGO: {payout}%\n\n')
		Mensagem(f'INICIANDO OPERACION {str(id)}..\n {str(horario)} | {par} | OPCION: {opcao.upper()} | DIRECION: {direcao.upper()} | M{timeframe} | PAGO: {payout}%')


API.connect()
API.change_balance(config['conta'])
while True:
	if API.check_connect() == False:
		print('>> Error al conectar!\n')
		input('   Presione enter para salir')
		sys.exit()
	else:
		print(f'>> Conectado con exito!\n {Fore.RED}Daniel Villada!!!\n')
		Mensagem(f'----------------------------------------------------------')
		Mensagem(f'Conectado con exito')
		banca()
		config['banca_inicial'] = valor_da_banca
		print(f"{Fore.LIGHTBLUE_EX}Saldo de la cuenta {'demo' if account_type == 'PRACTICE' else 'real'}: {account_balance}")
		break
try:
	buscarMenor()
	while True:
		timeNow = timestamp_converter()
		data_hora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
		print(data_hora, end='\x1b[K\r')
		for row in em_espera:
			horario = row[2]
			if galeRepete:
				par = parAntigo
				direcao = direcaoAntigo
				timeframe = timeframeAntigo
				valor_entrada = valorGaleProxSinal
			else:
				par = row[1].upper()
				direcao = row[3].lower()
				timeframe_retorno = timeFrame(row[0])
				timeframe = 0 if (timeframe_retorno == 'error') else timeframe_retorno
				if config['usar_ciclos'] == 'S':
					valor_entrada = valor_entrada_ciclo
					stop_win = abs(float(config['stop_win']))
					stop_loss = float(config['stop_loss']) * -1.0
				elif entrada_percentual == 'S':
					valor_entrada = int((float(config['entrada']) / 100) * (valor_da_banca + lucroTotal))
					percentual_loss = float(config['stop_loss'])
					percentual_gain = float(config['stop_win'])
					stop_loss = int((percentual_loss / 100) * valor_da_banca) * -1
					stop_win = int((percentual_gain / 100) * valor_da_banca)
				else:
					valor_entrada = float(config['entrada'])
					stop_win = abs(float(config['stop_win']))
					stop_loss = float(config['stop_loss']) * -1.0
			if len(horario) == 5:
				s = horario + ":00"
			else:
				s = horario
			f = '%H:%M:%S'
			dif = (datetime.strptime(timeNow, f) - datetime.strptime(s, f)).total_seconds()

			if (dif == -40) and get_profit == True:
				get_profit = False
				Get_All_Profit()
				paridades_fechadas = []

			if dif == -20:
				opcao, payout = checkProfit(par, timeframe)
				if not opcao:
					paridades_fechadas.append(par)

			if dif == -2:
				impacto, moeda, hora, stts = noticas(par)
				if stts:
					print(f' NOTICIA CON IMPACTO DE {impacto} TOROS EN LA MONEDA {moeda} COMO {hora}!\n')
					time.sleep(1)
				else:
					if timerzone(int(timeframe)):
						print('HORARIO NO RECOMENDADO POR TIMERZONE!')
						time.sleep(1)
					else:
						if analisarTendencia == 'S':
							tend = Verificar_Tendencia(par, timeframe)
						else:
							tend = direcao

						if hitdeVela == 'S':
							hit = Filtro_Hit_Vela(par, timeframe)
						else:
							hit = False

						if tend != direcao:
							print(f' PAR {par} EN CONTRA DE LA TENDENCIA!\n')
							Mensagem(f'PAR en contra de la tendencia')
							time.sleep(1)

						else:
							if hit:
								print(f' GOLPE DE VELAS EN PAR {par}!\n')
								Mensagem(f'Golpe de velas en par')
								time.sleep(1)

							elif par not in paridades_fechadas and payout >= payout_minimo:
								thread_ativas = threading.active_count()
								if config['usar_ciclos'] == 'S' and thread_ativas > 2:
									print(' OPERACION EN CURSO. ABORTANDO ENTRADA!')
									Mensagem(f'Operaciones en curso, abortando entrada')
									time.sleep(5)
									break
								else:
									operar(valor_entrada, par, direcao, timeframe, horario, opcao, payout)
								if config['usar_ciclos'] == 'S':
									break
							else:
								if par in paridades_fechadas:
									print(f' PAR {par} CERRADAS!\n')
								else:
									print(' PAGO ABAJO DEL MINIMO ESTABLECIDO!\n')
									Mensagem(f'Pago abajo del minimo establecido')
									time.sleep(1)

			if dif > 0:
				buscarMenor()
				break
		verificarStop()

		time.sleep(0.5)
except KeyboardInterrupt:
	banca()
	mensagem = f'Operaciones: {total_operacoes} | Ganadas: {vitorias} | Perdidas: {derrotas}\nEfectividad: {total_porcentagem}%\n'
	mensagem += f"Saldo de cuenta {'demo' if account_type == 'PRACTICE' else 'real'}: {account_balance}"
	print(f'{Fore.BLUE}{mensagem}')
	Mensagem(mensagem)
	exit()
