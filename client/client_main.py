#!/usr/bin/env python3

import os, socket, argparse, json, subprocess

peers = {}
server = None
username = None

class ServerConnection:
    def __init__(self, host, port):
        self.socket = (host, port)

    def _send_request(self, args):
        with socket.socket() as s:
            s.connect(self.socket)
            return send_request(s, args)

    def login(self, username, port):
        return self._send_request({"operacao": "login", "username": username, "porta": port})

    def logoff(self, username):
        return self._send_request({"operacao": "logoff", "username": username})

    def get_lista(self):
        return self._send_request({"operacao": "get_lista"})

def build_request(args):
    content = json.dumps(args, separators=(",", ":")).encode("utf-8")
    if len(content) > 0xff:
        return None

    length = len(content).to_bytes(1, byteorder="big")
    return length + content

def send_request(socket, args):
    req = build_request(args)
    socket.sendall(req)

    size = ord(recvall(socket, 1))
    response = recvall(socket, size).decode("utf-8")
    return json.loads(response)

def recvall(socket, length):
    buff = bytearray(length)
    pos = 0
    while pos < length:
        read = socket.recv_into(memoryview(buff)[pos:])
        if read == 0:
            raise EOFError
        pos += read
    return buff

def update_peers():
    global peers

    r = server.get_lista()
    if r["status"] == 200:
        peers = r["clientes"]

def handle_command(cmd):
    if cmd == "list":
        update_peers()
        print("Lista de usuários online:")
        for peer in peers.keys():
            print(peer)

    elif cmd == "exit":
        server.logoff(username)
        exit(0)

    elif cmd.startswith("msg"):
        peer = cmd[4:]
        peer = peers.get(peer)
        if not peer:
            print("Esse usuário não existe ou está offline.")
            return

        terminal_args = [os.environ.get("TERMINAL", "gnome-terminal"), "-e"]
        chat_args = ["./client_chat.py", "-H", peer["ip"], "-p", peer["port"], "-u", username]
        process = subprocess.Popen(terminal_args + chat_args)

def main():
    global server, username

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", dest="username")
    parser.add_argument("-H", "--host", dest="host")
    parser.add_argument("-p", "--port", type=int, dest="port")
    args = parser.parse_args()

    server = ServerConnection(args.host, args.port)
    username = args.username

    r = server.login(args.username, 4321)
    if r["status"] != 200:
        exit(1)
    update_peers()

    while True:
        cmd = input("> ")
        handle_command(cmd)

if __name__ == "__main__":
    main()
