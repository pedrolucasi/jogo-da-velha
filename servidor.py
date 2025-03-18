import socket
import threading

HOST = '127.0.0.1'
PORT = 5555

jogos_ativos = []
lock = threading.Lock()

#verificando se existe um vencedor 
def check_vencedor(tabuleiro): 
    jogada = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6],  #combinações possíveis para vencer a jogada
               [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]  
    
    for combo in jogada:
        if tabuleiro[jogada[0]] == tabuleiro[jogada[1]] == tabuleiro[jogada[2]] != ' ':
            return tabuleiro[jogada[0]]
        if " " not in tabuleiro:
            return "Empate"
        return None 
    
# Função que envia o estado do tabuleiro para os jogadores 
def send_tab_to_jogadores(jogo):
    for jogador in jogo['jogadores']:
        jogador.send(str(jogo['tabuleiro']).encode())

#Função para tratar cada cliente
def tratar_client(conn):
    global jogos_ativos
    with lock:
        #verificando se há uma partida disponível com um jogador esperando
        jogo_disponivel = None
        for jogo in jogos_ativos:
            if len(jogo['jogadores']) == 1:
                jogo_disponivel = jogo
                break

        if jogo_disponivel:
            jogo_disponivel['jogadores'].append(conn)
            jogador_symbol = 'O'
        else:

            #Cria um novo jogo
            novo_jogo = {
                'tabuleiro':[' ' for _ in range(9)],
                'jogadores':[conn],
                'jogador_atual': 'X'  
            }

            jogos_ativos.append(novo_jogo)
            jogador_symbol = 'X'
            jogo_disponivel = novo_jogo

    conn.send(f'Você é o jogador {jogador_symbol}'.encode())
    send_tab_to_jogadores(jogo_disponivel)

    while True: 
        try: 
            data = conn.recv(1024).decode()
            if not data:
                break

            move = int(data)
            if jogo_disponivel['tabuleiro'][move] == ' ' and  jogo_disponivel['jogador_atual'] == jogador_symbol:
               
               jogo_disponivel['tabuleiro'][move] = jogador_symbol
               vencedor = check_vencedor(jogo_disponivel['tabuleiro'])
               if vencedor:
                   send_tab_to_jogadores(jogo_disponivel) 
                   for p in jogo_disponivel['jogadores']:
                       if vencedor == 'Empate':
                           p.send('Empate! O jogo terminou'.encode())
                       else:
                           p.send(f'Jogador {vencedor} venceu!'.encode())
                   break 
            jogo_disponivel['jogador_atual'] = 'O' 
            if jogo_disponivel['jogador_atual'] == 'X' else 'X'  #erro pra corrigir
                send_tab_to_jogadores(jogo_disponivel)
            else:
               conn.send('Jogada inválida! Tente novamente.'.encode())

        except:
            break

    conn.close()
    with lock:
        jogo_disponivel['jogadores'].remove(conn)
        if len(jogo_disponivel['jogadores']) == 0:
            jogos_ativos.remove(jogo_disponivel)



