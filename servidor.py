import socket
import threading

HOST = '127.0.0.1'  # Endereço IP do servidor
PORTA = 5000        # Porta do servidor

jogos_ativos = []   # Lista para armazenar os jogos ativos
lock = threading.Lock()  # Lock para garantir sincronização entre threads

# Função para verificar se há um vencedo
def check_vencedor(tabuleiro):
    jogadas = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Linhas
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Colunas
        [0, 4, 8], [2, 4, 6]  # Diagonais
    ]
    
    # Verifica todas as combinações possíveis de vitória
    for combo in jogadas:
        if tabuleiro[combo[0]] == tabuleiro[combo[1]] == tabuleiro[combo[2]] != ' ':
            return tabuleiro[combo[0]]  # Retorna o símbolo do vencedor ('X' ou 'O')
    
    # Verifica se houve empate (não há mais espaços vazios)
    if " " not in tabuleiro:
        return "Empate"
    
    return None  # Retorna None se o jogo ainda não terminou

# Função que envia o estado do tabuleiro para os jogadores
def send_tab_to_jogadores(jogo):
    for jogador in jogo['jogadores']:
        jogador.send(str(jogo['tabuleiro']).encode())  # Envia o tabuleiro para cada jogador

# Função para tratar cada cliente
def tratar_client(conn):
    global jogos_ativos
    with lock:
        # Verifica se há uma partida disponível com um jogador esperando
        jogo_disponivel = None
        for jogo in jogos_ativos:
            if len(jogo['jogadores']) == 1:
                jogo_disponivel = jogo
                break

        if jogo_disponivel:
            # Adiciona o segundo jogador ao jogo existente
            jogo_disponivel['jogadores'].append(conn)
            jogador_symbol = 'O'  # O segundo jogador será 'O'
        else:
            # Cria um novo jogo se não houver partidas disponíveis
            novo_jogo = {
                'tabuleiro': [' ' for _ in range(9)],  # Tabuleiro vazio
                'jogadores': [conn],  # Lista de jogadores (inicia com o primeiro)
                'jogador_atual': 'X'  # O primeiro jogador será 'X'
            }
            jogos_ativos.append(novo_jogo)
            jogador_symbol = 'X'  # O primeiro jogador será 'X'
            jogo_disponivel = novo_jogo

    # Informa ao jogador qual símbolo ele está usando
    conn.send(f'Você é o jogador {jogador_symbol}'.encode())
    # Envia o estado atual do tabuleiro para os jogadores
    send_tab_to_jogadores(jogo_disponivel)

    while True:
        try:
            # Recebe a jogada do cliente
            data = conn.recv(1024).decode()
            if not data:
                break

            move = int(data)  # Converte a jogada para inteiro
            # Verifica se a jogada é válida
            if jogo_disponivel['tabuleiro'][move] == ' ' and jogo_disponivel['jogador_atual'] == jogador_symbol:
                # Atualiza o tabuleiro com a jogada do jogador
                jogo_disponivel['tabuleiro'][move] = jogador_symbol
                # Verifica se há um vencedor
                vencedor = check_vencedor(jogo_disponivel['tabuleiro'])
                if vencedor:
                    # Envia o tabuleiro final para os jogadores
                    send_tab_to_jogadores(jogo_disponivel)
                    for p in jogo_disponivel['jogadores']:
                        if vencedor == 'Empate':
                            p.send('Empate! O jogo terminou'.encode())
                        else:
                            p.send(f'Jogador {vencedor} venceu!'.encode())
                    break  # Encerra o loop do jogo
                
                # Alterna o jogador atual
                jogo_disponivel['jogador_atual'] = 'O' if jogo_disponivel['jogador_atual'] == 'X' else 'X'
                # Envia o tabuleiro atualizado para os jogadores
                send_tab_to_jogadores(jogo_disponivel)
            else:
                # Informa ao jogador que a jogada é inválida
                conn.send('Jogada inválida! Tente novamente.'.encode())
        except:
            break  # Encerra o loop em caso de erro

    # Fecha a conexão com o cliente
    conn.close()
    with lock:
        # Remove o jogador da lista de jogadores do jogo
        jogo_disponivel['jogadores'].remove(conn)
        # Remove o jogo da lista de jogos ativos se não houver mais jogadores
        if len(jogo_disponivel['jogadores']) == 0:
            jogos_ativos.remove(jogo_disponivel)
        else:
            # Notifica o outro jogador que o oponente desconectou
            for jogador in jogo_disponivel['jogadores']:
                jogador.send('Seu oponente desconectou. O jogo foi encerrado.'.encode())
            jogos_ativos.remove(jogo_disponivel)

# Função principal do servidor
def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.bind((HOST, PORTA))  # Associa o socket ao endereço e porta
        servidor.listen()  # Coloca o socket em modo de escuta
        print(f"Servidor iniciado em {HOST}:{PORTA}. Aguardando conexões...")
        
        while True:
            conn, addr = servidor.accept()  # Aceita uma nova conexão
            print(f"Conexão estabelecida com {addr}")
            threading.Thread(target=tratar_client, args=(conn,)).start()  # Inicia uma nova thread para o cliente

if __name__ == "__main__":
    main()