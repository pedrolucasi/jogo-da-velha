import socket
import threading
import sys

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
            
            print(dados)
            
            if "Tabuleiro:" in dados:
                tabuleiro = dados.split("Tabuleiro: ")[1].split("\n")[0]
                imprimir_tabuleiro(eval(tabuleiro))
            
            if "final" in dados:
                break
        except Exception as e:
            print(f"Erro ao receber mensagem: {e}")
            break

def enviar_mensagens(s):
    while True:
        try:
            jogada = input("Digite sua jogada (0-8): ")
            s.sendall(jogada.encode())
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")
            break

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORTA))
        print("Conectado ao servidor. Aguardando mensagens...")
        
        thread_receber = threading.Thread(target=receber_mensagens, args=(s,))
        thread_receber.start()
        
        thread_enviar = threading.Thread(target=enviar_mensagens, args=(s,))
        thread_enviar.start()
        
        thread_receber.join()
        thread_enviar.join()

if __name__ == "__main__":
    main()