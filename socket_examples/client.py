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

# Conectar ao servidor no computador local
# 127.0.0.1 significa o computador local
s.connect(('127.0.0.1', port))

# Recebe dados do servidor e decodifica
print(s.recv(1024).decode())

# Fechar a conexão
s.close()
