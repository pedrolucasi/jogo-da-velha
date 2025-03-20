import json
from game_logic import Game

game = Game()  # Instância do jogo

def broadcast(mensagem, clientes):
    """
    Envia uma mensagem para todos os clientes conectados.
    :param mensagem: Mensagem a ser enviada.
    :param clientes: Lista de clientes conectados.
    """
    for cliente in clientes:
        try:
            cliente.sendall(mensagem.encode())
        except Exception as e:
            print(f"Erro ao enviar mensagem para um cliente: {e}")

def processar_mensagem(mensagem, client_socket, clientes):
    """
    Processa uma mensagem recebida do cliente.
    :param mensagem: Mensagem recebida (string).
    :param client_socket: Socket do cliente.
    :param clientes: Lista de clientes conectados.
    :return: Resposta a ser enviada ao cliente.
    """
    try:
        dados = json.loads(mensagem)
        comando = dados.get("comando")

        if comando == "CONNECT":
            tipo = dados.get("tipo")
            nome = dados.get("nome")
            if tipo == "jogador":
                simbolo = game.add_player(nome, client_socket)
                if simbolo:
                    resposta = {"status": "ok", "mensagem": f"Jogador {nome} conectado como {simbolo}."}
                else:
                    resposta = {"status": "erro", "mensagem": "Número máximo de jogadores atingido."}
            elif tipo == "espectador":
                game.spectators.append(client_socket)
                resposta = {"status": "ok", "mensagem": f"Espectador {nome} conectado.", "tabuleiro": game.board}
            else:
                resposta = {"status": "erro", "mensagem": "Tipo de conexão inválido."}

        elif comando == "MOVE":
            jogada = dados.get("jogada")
            jogador = next((p for p in game.players if p[1] == client_socket), None)
            if jogador and game.make_move(jogada, jogador[2]):
                vencedor = game.check_winner()
                if vencedor:
                    resposta = {"status": "ok", "tabuleiro": game.board, "mensagem": f"Jogador {vencedor} venceu!"}
                    broadcast(json.dumps(resposta), clientes)
                    game.reset()
                else:
                    resposta = {"status": "ok", "tabuleiro": game.board, "mensagem": "Jogada realizada com sucesso."}
                    broadcast(json.dumps(resposta), clientes)
            else:
                resposta = {"status": "erro", "mensagem": "Jogada inválida."}

        elif comando == "SPECTATE":
            resposta = {"status": "ok", "tabuleiro": game.board, "mensagem": "Você está assistindo ao jogo."}

        else:
            resposta = {"status": "erro", "mensagem": "Comando inválido."}

    except json.JSONDecodeError:
        resposta = {"status": "erro", "mensagem": "Formato de mensagem inválido."}
    except KeyError:
        resposta = {"status": "erro", "mensagem": "Parâmetros ausentes na mensagem."}
    except Exception as e:
        resposta = {"status": "erro", "mensagem": f"Erro interno: {e}"}

    return json.dumps(resposta)