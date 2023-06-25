import socket
import json


class Server:
    def __init__(self, port=1099):
        # TODO retirar prints
        # Inicializar variável do socket e da peer_list
        self.socket = None
        self.peer_list = {}

        # Criar o socket
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("Socket criado com sucesso.")
        except socket.error as error:
            print(f"A criação do socket falhou com o erro {error}")

        # Vincular a porta
        # Sem nenhum IP porque estamos conectando ao localhost
        self.socket.bind(('', port))
        print(f"Socket vinculado a porta={str(port)}")

        # Colocar o socket em "listening mode"
        self.socket.listen(5)
        print("Socket is listening")

        # Um loop infinito até que o interrompemos ou um erro ocorra
        while True:
            # TODO verificar quando finalizar
            # Estabelecer conexão com o cliente
            c, address = self.socket.accept()

            # Endereço de IP e Porta do peer
            ip_peer = address[0]
            port_peer = address[1]

            # Vamos receber uma requisição em formato de json com as informações
            # Decodificamos e em "tipo" teremos qual é o tipo da requisição e chamaremos o método correspondente
            response = json.loads(c.recv(4096).decode())
            if response["tipo"] == "JOIN":
                self.join(c, ip_peer, port_peer, response["files_list"])
            elif response["tipo"] == "SEARCH":
                self.search(c, ip_peer, port_peer, response["file_name"])
            elif response["tipo"] == "UPDATE":
                self.update(c, ip_peer, port_peer, response["file_name"])

            # Encerrar a conexão com o client
            c.close()

    def join(self, client, ip_address, port, data):
        # Adicionamos a lista de arquivos ao dicionário com a lista dos peers
        # Usamos [IP_ADDRESS]:[PORT] como chave
        self.peer_list[f"{ip_address}:{port}"] = data
        print(f"Peer {ip_address}:{port} adicionado com arquivos {str(data)}.")

        # Enviamos de volta uma mensagem avisando que o join foi concluído com sucesso
        client.send("JOIN_OK".encode())

    def search(self, client, ip_address, port, file_name):
        print(f"Peer {ip_address}:{port} solicitou arquivo {file_name}")

        peers_result = []
        for peer in self.peer_list:  # TODO refazer esse for, agora é um dicionário
            if file_name in peer["files"]:
                peers_result.append('peer["ip_address"]:peer["port"]')

        # Enviar a lista com os peers encodada com json
        client.send(json.dumps(peers_result).encode())

    def update(self, client, ip_address, port, file_name):
        # Adiciona esse arquivo na lista desse peer
        self.peer_list[f"{ip_address}:{port}"].append(file_name)

        # Enviamos de volta uma mensagem avisando que o update foi concluído com sucesso
        client.send("UPDATE_OK".encode())
        return


class Peer:
    def __init__(self, port=1099):
        # Inicializar variável do socket e da peer_list
        self.socket = None
        self.port = port

        # Criar o socket
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("Socket criado com sucesso.")
        except socket.error as error:
            print(f"A criação do socket falhou com o erro {error}")

    def menu(self):
        print("Escolha a opção desejada, escrevendo o número correspondente")
        print("1- JOIN")
        print("2- SEARCH")
        print("3- DOWNLOAD")

        option = int(input())
        if option == 1:
            ip = input("Qual o IP desse peer?")
            port = input("Qual a porta desse peer?")
            files_path = input("Em qual pasta estão os arquivos?")
            self.join(ip, port, files_path)
        elif option == 2:
            self.search("TODO")
        elif option == 3:
            self.download()

    def join(self, ip_peer, port_peer, path):
        # TODO criar pasta para cada peer
        self.socket.connect(('127.0.0.1', self.port))  # TODO tirar isso daqui e colocar em outro lugar

        # Vamos enviar os dados como um dicionário
        to_send_dict = {
            "tipo": "JOIN",
            "ip_peer": ip_peer,
            "port_peer": port_peer,
            "files_list": files_list
        }

        # Usamos em formato json para carregarmos várias informações
        self.socket.send(json.dumps(to_send_dict).encode())

        # Recebemos a resposta se tudo ok
        response = self.socket.recv(2048).decode()

        # Se a requisição foi concluída com sucesso, vai receber um JOIN_OK
        if "JOIN_OK" in response:
            print(f"Sou peer [IP]:[porta] com arquivos {str(files_list)}")  # TODO ip:porta

    def search(self, file_name):
        # TODO conectar o socket ao servidor
        to_send_dict = {
            "tipo": "SEARCH",
            "file_name": file_name
        }

        # Usamos em formato json para carregarmos várias informações
        self.socket.send(json.dumps(to_send_dict).encode())

        # Recebemos a resposta em json por se tratar de uma lista
        response = json.dumps(self.socket.recv(2048).decode())

        print(f"peers com arquivo solicitado: {str(response)}")

    def download(self):
        return  # TODO

    def update(self, file_name):
        to_send_dict = {
            "tipo": "UPDATE",
            "file_name": file_name
        }

        # Usamos o JSON para transformar os dados em bytes e os enviamos
        self.socket.send(json.dumps(to_send_dict).encode())

        # Resposta para verificar se o update deu certo
        response = self.socket.recv(2048).decode()
        is_response_ok = False

        if "UPDATE_OK" in response:
            is_response_ok = True
