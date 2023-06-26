import socket
import json


class Server:
    def __init__(self, port=1099):
        # Inicializar atributo do socket e da files_list
        self.socket = None
        self.files_list = {}

        # Criar o socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Vincular a porta
        # Sem nenhum IP porque estamos conectando ao localhost
        self.socket.bind(('', port))

        # Colocar o socket em "listening mode"
        self.socket.listen(5)

        # Um loop infinito até que o interrompemos ou um erro ocorra
        while True:
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

    def join(self, client, ip_address, port, files):
        # Recebe uma requisição JOIN

        # Vamos adicionar as informações desse peer para cada um de seus arquivos
        peer_info = {
            "ip_address": ip_address,
            "port": port
        }
        for file in files:
            try:  # Se esse arquivo já foi catalogado, simplesmente adicionamos esse peer na lista
                self.files_list[file].append(peer_info)
            except KeyError:  # Se esse arquivo não foi catalogado, criamos uma lista com as informações desse peer
                self.files_list[file] = [peer_info]
        print(f"Peer {ip_address}:{port} adicionado com arquivos {str(files)}.")

        # Enviamos de volta uma mensagem avisando que o join foi concluído com sucesso
        client.send("JOIN_OK".encode())

    def search(self, client, ip_address, port, file_name):
        # Recebe uma requisição SEARCH

        print(f"Peer {ip_address}:{port} solicitou arquivo {file_name}")

        peers_result = self.files_list[file_name]

        # Enviar a lista com os peers encodada com json
        client.send(json.dumps(peers_result).encode())

    def update(self, client, ip_address, port, file_name):
        # Recebe uma requisição UPDATE

        peer_info = {
            "ip_address": ip_address,
            "port": port
        }
        # Adiciona esse peer na lista desse arquivo
        self.files_list[file_name].append(peer_info)

        # Enviamos de volta uma mensagem avisando que o update foi concluído com sucesso
        client.send("UPDATE_OK".encode())
        return

