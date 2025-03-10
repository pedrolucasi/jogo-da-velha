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
    
    for i in jogada:
        if tabuleiro[jogada[0]] == tabuleiro[jogada[1]] == tabuleiro[jogada[2]] != ' ':
            return tabuleiro[jogada[0]]