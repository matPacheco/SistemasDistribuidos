import socket


class Server:
    def __init__(self, port=1099):
        # Inicializar variável do socket e da peer_list
        self.socket = None
        self.peer_list = []

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
            # Estabelecer conexão com o cliente
            c, addr = self.socket.accept()
            print(f"Conectado de {addr}")

            # Enviar uma mensagem ao client
            # Encoding para transformar em byte
            c.send("Obrigado por se conectar".encode())

            # Encerrar a conexão com o client
            c.close()

            # Interromper o while após fechar conexão
            break

        def join(client, address, data):
            if type(data) == list:
                self.peer_list.append({
                    "ip_address": address[0],
                    "port": address[1],
                    "files": data
                })

                client.send("JOIN_OK")
                client.close()
            else:
                client.send("Erro: Tipo de Arquivos incompatíveis.")

        def search(client, file_name):
            peers_result = []
            for peer in self.peer_list:
                if file_name in peer["files"]:
                    peers_result.append('peer["ip_address"]:peer["port"]')
            client.send(peers_result)
