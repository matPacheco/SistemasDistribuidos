import socket
import sys


try:
    # socket.AF_INET indica que o socket usará endereços IPv4
    # socket.SOCK_STREAM indica que o socket usará TCP, para UDP seria socket.SOCK_DGRAM
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket criado com sucesso.")
except socket.error as error:
    print(f"A criação do socket falhou com o erro {error}")

# Porta padrão para socket
port = 80

try:
    host_ip = socket.gethostbyname("www.google.com")
except socket.gaierror:
    print("Houve um erro ao determinar o host")
    sys.exit()

# Conectar ao servidor
s.connect((host_ip, port))

print("O socket se conectou ao Google com sucesso")
