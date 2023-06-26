import socket
import json
import os
import threading


class Peer:
    def __init__(self):
        # Inicializar atributos da classe
        self.socket = None
        self.ip = None
        self.port = None
        self.files_path = None
        self.file_last_search = None
        self.peers_last_search = []

    def menu(self):
        print("Escolha a opção desejada, escrevendo o número correspondente")
        print("1- JOIN")
        print("2- SEARCH")
        print("3- DOWNLOAD")

        option = int(input())
        if option == 1:  # JOIN
            ip = input("Qual o IP desse peer?")
            self.ip = ip    # Salva o IP como atributo

            port = input("Qual a porta desse peer?")
            self.port = port    # Salva a Porta como atributo

            files_path = input("Em qual pasta estão os arquivos?")
            self.files_path = files_path    # Salva o caminho da pasta como atributo

            self.join(ip, port, files_path)

            # Começar a thread que vai esperar conexão de outros peers
            thread = threading.Thread(target=self.wait_download())
            thread.start()
        elif option == 2:  # SEARCH
            file_name = input("Qual o nome do arquivo que deseja baixar?")
            self.file_last_search = file_name   # Salva o nome do arquivo como atributo
            self.search(file_name)
        elif option == 3:  # DOWNLOAD
            ip = input("Qual o IP desse peer?")
            port = input("Qual a porta desse peer?")

            self.download(ip, port, self.file_last_search)

    def _connect_to_server(self):
        s = socket.socket()
        s.connect(('127.0.0.1', 1099))

        return s

    def join(self, ip_peer, port_peer, path):
        # Requisição JOIN ao servidor

        s = self._connect_to_server()
        # Lista com todos os arquivos do caminho especificado
        files_list = os.listdir(path)

        # Vamos enviar os dados como um dicionário
        to_send_dict = {
            "tipo": "JOIN",
            "ip_peer": ip_peer,
            "port_peer": port_peer,
            "files_list": files_list
        }

        # Usamos em formato json para carregarmos várias informações
        s.send(json.dumps(to_send_dict).encode())

        # Recebemos a resposta se tudo ok
        response = s.recv(4096).decode()

        # Se a requisição foi concluída com sucesso, vai receber um JOIN_OK
        if "JOIN_OK" in response:
            print(f"Sou peer {ip_peer}:{port_peer} com arquivos {str(files_list)}")

        # Encerra conexão
        s.close()

    def search(self, file_name):
        # Requisição SEARCH ao servidor

        s = self._connect_to_server()
        to_send_dict = {
            "tipo": "SEARCH",
            "file_name": file_name
        }

        # Usamos em formato json para carregarmos várias informações
        s.send(json.dumps(to_send_dict).encode())

        # Recebemos a resposta em json por se tratar de uma lista
        response = json.loads(s.recv(4096).decode())
        # Salvar essa última pesquisa no atributo do objeto
        self.peers_last_search = response

        # Vamos formatar a lista para podermos imprimir em formato de IP:Port
        peer_list_formatted = []
        for peer in response:
            ip = peer["ip_address"]
            port = peer["port"]
            peer_formatted = f'{ip}:{port}'
            peer_list_formatted.append(peer_formatted)

        print(f"Peers com arquivo solicitado: {str(peer_list_formatted)}")

        # Encerra conexão
        s.close()

    def wait_download(self):
        # Espera uma requisição DOWNLOAD de outro peer

        # Cria um socket novo para comunicaçao entre peers
        socket_recv_download = socket.socket()

        # Vincula esse socket com o IP/Porta que foi capturado anteriormente
        socket_recv_download.bind((self.ip, self.port))
        socket_recv_download.listen(5)

        # Aguarda outros peers conectarem
        while True:
            client, addr = socket_recv_download.accept()

            # Recebe o nome do arquivo a ser baixado
            file_name = client.recv(4096).decode()

            # Caminho do arquivo
            file_path = os.path.join(self.files_path, file_name)

            # Abre o arquivo e o seu conteúdo como binário
            file = open(file_path, "rb")
            data = file.read()

            # Envia o conteúdo do arquivo
            client.sendall(data)

            # Ao fim, envia uma flag para o outro peer saber quando parar
            client.send("b<FIM>")

            # Fecha a conexão e o arquivo
            client.close()
            file.close()

    def download(self, ip, port, file_name):
        # Requisição DOWNLOAD a outro peer

        # Cria um socket para conexão entre peers
        socket_download = socket.socket()

        # Conecta com o peer do IP/Porta correspondente
        socket_download.connect((ip, port))

        # Envia o nome do arquivo a ser baixado
        socket_download.send(file_name.encode())

        # Caminho onde o arquivo ficará depois de baixado
        file_path = os.path.join(self.files_path, file_name)
        file = open(file_path, "wb")

        done = False  # Variável para saber quando parar de receber dados
        while not done:
            # Recebe repetidamente o conteúdo e escreve no arquivo criado
            received = socket_download.recv(4096)
            # Quando receber a flag <FIM> significa que o conteúdo chegou ao fim
            if received[-5:] == b"<FIM>":
                file.write(received[:-5])
                done = True
            else:
                file.write(received)
        # Fecha a conexão e o arquivo
        socket_download.close()
        file.close()

    def update(self, file_name):
        # Requisição UPDATE ao servidor

        s = self._connect_to_server()
        to_send_dict = {
            "tipo": "UPDATE",
            "file_name": file_name
        }

        # Usamos o JSON para transformar os dados em bytes e os enviamos
        s.send(json.dumps(to_send_dict).encode())

        # Resposta para verificar se o update deu certo
        response = s.recv(2048).decode()
        is_response_ok = False

        if "UPDATE_OK" in response:
            is_response_ok = True

        # Encerra conexão
        s.close()
