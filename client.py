import socket
import threading
import json

HOST = '127.0.0.1'
PORTA = 5555

def imprimir_tabuleiro(tabuleiro):
    print(f"{tabuleiro[0]} | {tabuleiro[1]} | {tabuleiro[2]}")
    print("--+---+--")
    print(f"{tabuleiro[3]} | {tabuleiro[4]} | {tabuleiro[5]}")
    print("--+---+--")
    print(f"{tabuleiro[6]} | {tabuleiro[7]} | {tabuleiro[8]}")

def receber_mensagens(s):
    while True:
        try:
            dados = s.recv(1024).decode()
            if not dados:
                print("Conexão com o servidor foi fechada.")
                break
            
            resposta = json.loads(dados)
            print(resposta.get("mensagem"))
            
            if "tabuleiro" in resposta:
                imprimir_tabuleiro(resposta["tabuleiro"])
            
            if "final" in resposta:
                break
        except ConnectionResetError:
            print("Conexão com o servidor foi perdida.")
            break
        except Exception as e:
            print(f"Erro ao receber mensagem: {e}")
            break

def enviar_mensagens(s):
    while True:
        try:
            jogada = input("Digite sua jogada (0-8): ")
            if not jogada.isdigit() or int(jogada) < 0 or int(jogada) > 8:
                print("Jogada inválida. Digite um número entre 0 e 8.")
                continue
            s.sendall(json.dumps({"comando": "MOVE", "jogada": int(jogada)}).encode())
        except ConnectionAbortedError:
            print("Conexão com o servidor foi interrompida.")
            break
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")
            break

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORTA))
        print("Conectado ao servidor. Aguardando mensagens...")
        
        # Pergunta ao usuário se ele quer ser jogador ou espectador
        tipo = input("Digite 'jogador' para jogar ou 'espectador' para assistir: ").strip().lower()
        nome = input("Digite seu nome: ")
        
        # Envia comando de conexão
        s.sendall(json.dumps({"comando": "CONNECT", "tipo": tipo, "nome": nome}).encode())
        
        # Inicia thread para receber mensagens
        thread_receber = threading.Thread(target=receber_mensagens, args=(s,))
        thread_receber.start()
        
        # Se for jogador, inicia thread para enviar mensagens
        if tipo == "jogador":
            thread_enviar = threading.Thread(target=enviar_mensagens, args=(s,))
            thread_enviar.start()
            thread_enviar.join()
        
        thread_receber.join()

if __name__ == "__main__":
    main()