import socket


# Inicializar variável do socket
s = None
try:
    # Por padrão, se usa IPV4 e TCP
    s = socket.socket()
    print("Socket criado com sucesso.")
except socket.error as error:
    print(f"A criação do socket falhou com o erro {error}")


# Reservar uma porta no computador
port = 12345

# Vincular a porta
# Sem nenhum IP porque estamos conectando ao localhost
s.bind(('', port))
print(f"Socket vinculado a {str(port)}")

# Colocar o socket em "listening mode"
s.listen(5)
print("Socket is listening")

# Um loop infinito até que o interrompemos ou um erro ocorra
while True:
    # Estabelecer conexão com o cliente
    c, addr = s.accept()
    print(f"C={c}")
    print(f"addr[0]={addr[0]} e addr[1]={addr[1]}")
    print(f"Conectado de {addr}")

    # Enviar uma mensagem ao client
    # Encoding para transformar em byte
    c.send("Obrigado por se conectar".encode())

    # Encerrar a conexão com o client
    c.close()

    # Interromper o while após fechar conexão
    break
