#!/usr/bin/env python3

import sys, os, socket, argparse, json, subprocess
from select import select

RECV_HOST = ""
RECV_PORT = 54322

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

        chat_args = f'cd ~/lightchat/client; ./client_chat.py -H {peer["ip"]} -p {peer["porta"]} -u {username}'
        terminal_args = ["osascript", "-e", f'tell app "Terminal" to do script "{chat_args}"']
        # terminal_args = [os.environ.get("TERMINAL", "gnome-terminal"), "-e"]
        # chat_args = [f'./client_chat.py -H {peer["ip"]} -p {peer["porta"]} -u {username}']
        process = subprocess.Popen(terminal_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    global server, username

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", dest="username", required=True)
    parser.add_argument("-H", "--host", dest="host", required=True)
    parser.add_argument("-p", "--port", type=int, dest="port", required=True)
    args = parser.parse_args()

    server = ServerConnection(args.host, args.port)
    username = args.username

    r = server.login(args.username, 4321)
    if r["status"] != 200:
        print(r["status"])
        print("Erro ao fazer login")
        exit(1)
    update_peers()

    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((RECV_HOST, RECV_PORT))
        s.listen()

        print("> ", end="", flush=True)

        while True:
            read, _, _ = select([sys.stdin, s], [], [])
            for ready in read:
                if ready is s:
                    print("received something lol")
                elif ready is sys.stdin:
                    cmd = input()
                    handle_command(cmd)
                    print("> ", end="", flush=True)

if __name__ == "__main__":
    main()
