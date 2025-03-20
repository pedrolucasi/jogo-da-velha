class Game:
    def __init__(self):
        self.board = [" " for _ in range(9)]  # Tabuleiro 3x3
        self.current_player = "X"  # Jogador atual
        self.players = []  # Lista de jogadores (nome, socket, símbolo)
        self.spectators = []  # Lista de espectadores (socket)

    def add_player(self, nome, client_socket):
        """
        Adiciona um jogador ao jogo.
        :param nome: Nome do jogador.
        :param client_socket: Socket do jogador.
        :return: Símbolo do jogador ("X" ou "O") ou None se não houver vagas.
        """
        if len(self.players) < 2:
            simbolo = "X" if len(self.players) == 0 else "O"
            self.players.append((nome, client_socket, simbolo))
            return simbolo
        return None

    def make_move(self, position, player):
        """
        Faz uma jogada no tabuleiro.
        :param position: Posição no tabuleiro (0-8).
        :param player: Símbolo do jogador ("X" ou "O").
        :return: True se a jogada for válida, False caso contrário.
        """
        if 0 <= position <= 8 and self.board[position] == " ":
            self.board[position] = player
            return True
        return False

    def check_winner(self):
        """
        Verifica se há um vencedor ou empate.
        :return: "X" ou "O" se houver um vencedor, "Empate" se o jogo terminar em empate, None caso contrário.
        """
        winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Linhas
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Colunas
            [0, 4, 8], [2, 4, 6]              # Diagonais
        ]
        for combo in winning_combinations:
            if self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]] != " ":
                return self.board[combo[0]]
        if " " not in self.board:
            return "Empate"
        return None

    def reset(self):
        """
        Reinicia o jogo, limpando o tabuleiro e redefinindo o jogador atual.
        """
        self.board = [" " for _ in range(9)]
        self.current_player = "X"