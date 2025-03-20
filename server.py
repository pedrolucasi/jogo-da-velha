import socket
import threading
import signal
import sys
from protocol import processar_mensagem, broadcast

HOST = "0.0.0.0"
PORT = 5555

servidor_ativo = True
clientes = []

def encerrar_servidor(sig, frame):
    global servidor_ativo
    print("\nEncerrando o servidor...")
    servidor_ativo = False
    for cliente in clientes:
        cliente.close()
    sys.exit(0)

def cliente_thread(client_socket, addr):
    print(f"Conexão recebida de {addr}")
    clientes.append(client_socket)
    try:
        while True:
            mensagem = client_socket.recv(4096).decode()
            if not mensagem:
                break
            resposta = processar_mensagem(mensagem, client_socket, clientes)
            client_socket.sendall(resposta.encode())
    except ConnectionResetError:
        print(f"Conexão com {addr} foi perdida.")
    except Exception as e:
        print(f"Erro ao processar mensagem de {addr}: {e}")
    finally:
        clientes.remove(client_socket)
        client_socket.close()
        print(f"Fim da conexão com {addr}")

def iniciar_servidor():
    signal.signal(signal.SIGINT, encerrar_servidor)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Servidor rodando em {HOST}:{PORT}")
        while servidor_ativo:
            try:
                client_socket, addr = server_socket.accept()
                threading.Thread(target=cliente_thread, args=(client_socket, addr)).start()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Erro no servidor: {e}")
                break
        print("Servidor encerrado.")

if __name__ == "__main__":
    iniciar_servidor()