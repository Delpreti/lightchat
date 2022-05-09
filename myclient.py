import socket

class MyClient:
    """ Class to encapsulate the client functions """
    def __init__(self, hostname='', send_port=5000, recv_port=5001):
        self.hostname = hostname
        self.send_port = send_port
        self.recv_port = recv_port
        self._sender_socket = socket.socket()
        self._reciever_socket = socket.socket()

    def __enter__(self):
        """ When the server is initialized, the internal socket must be configured """
        self._sender_socket.connect((self.hostname, self.send_port))
        self._reciever_socket.connect((self.hostname, self.recv_port))
        print(f"Connection succeeded with {self.hostname}:{self.port}")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ When the server is finishing, the internal socket must be closed """
        self._sender_socket.close()
        self._reciever_socket.close()

    def chat(self):
        msg = input("Write a message ('exit' to end):")
        self._sender_socket.sendall(bytes(msg, 'utf-8')) # envia a mensagem
        result = str(self._sender_socket.recv(1024),  encoding='utf-8') # recebe a mensagem de "ok"
        if result != "ok":
            print(f"Ocorreu um Erro: {result}")

