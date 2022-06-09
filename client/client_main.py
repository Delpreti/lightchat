#!/usr/bin/env python3

import sys, os, socket, argparse, json, subprocess, platform, fcntl, random, signal
from select import select

RECV_HOST = ""
RECV_PORT = random.randrange(1024, 65536)

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
        return self._send_request({"operacao": "login", "username": username, "Porta": port})

    def logoff(self, username):
        return self._send_request({"operacao": "logoff", "username": username})

    def get_lista(self):
        return self._send_request({"operacao": "get_lista"})

def build_request(args):
    content = json.dumps(args, separators=(",", ":")).encode("utf-8")
    if len(content) > 0xffff:
        return None

    length = len(content).to_bytes(2, byteorder="big")
    return length + content

def send_request(socket, args):
    req = build_request(args)
    socket.sendall(req)

    size = int.from_bytes(recvall(socket, 2), "big")
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

def open_process(args):
    return subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=False)

def create_chat(peer):
    # MacOS
    if platform.system() == "Darwin":
        script = f'cd {os.getcwd()}; ./client_chat.py -H {peer["Endereco"]} -p {peer["Porta"]} -u {username}'
        terminal_args = ["osascript", "-e", f'tell app "Terminal" to do script "{script}"']
        open_process(terminal_args)

    # Linux
    elif platform.system() == "Linux":
        chat_args = ["./client_chat.py", "-H", peer["Endereco"], "-p", peer["Porta"], "-u", username]
        if os.environ.get("TERMINAL"):
            terminal_args = [os.environ.get("TERMINAL"), "-e"] + chat_args
            open_process(terminal_args)
        else:
            terminal_args = ["gnome-terminal", "--"] + chat_args
            open_process(terminal_args)

def receive_chat(fd):
    fd = str(fd)

    # MacOS
    if platform.system() == "Darwin":
        script = f'cd {os.getcwd()}; ./client_chat.py -f {fd} -u {username}'
        terminal_args = ["osascript", "-e", f'tell app "Terminal" to do script "{script}"']
        open_process(terminal_args)

    # Linux
    elif platform.system() == "Linux":
        chat_args = ["./client_chat.py", "-f", fd, "-u", username]
        if os.environ.get("TERMINAL"):
            terminal_args = [os.environ.get("TERMINAL"), "-e"] + chat_args
            open_process(terminal_args)
        else:
            terminal_args = ["gnome-terminal", "--fd", fd, "--"] + chat_args
            open_process(terminal_args)

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
        update_peers()
        peer = cmd[4:]
        peer = peers.get(peer)
        if not peer:
            print("Esse usuário não existe ou está offline.")
            return

        create_chat(peer)

def main():
    global server, username, RECV_PORT

    def sigint_handler(sig, frame):
        server.logoff(username)
        exit(0)

    signal.signal(signal.SIGINT, sigint_handler)

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", dest="username", required=True)
    parser.add_argument("-H", "--host", dest="host", required=True)
    parser.add_argument("-p", "--port", type=int, dest="port", required=True)
    parser.add_argument("-l", "--listen", type=int, dest="listen")
    args = parser.parse_args()

    server = ServerConnection(args.host, args.port)
    username = args.username

    if args.listen:
        RECV_PORT = args.listen

    r = server.login(args.username, RECV_PORT)
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
                    conn, addr = s.accept()
                    print(f"\r{addr} abriu um chat com você")
                    print("> ", end="", flush=True)

                    flags = fcntl.fcntl(conn, fcntl.F_GETFD, 0)
                    fcntl.fcntl(conn, fcntl.F_SETFD, flags & ~fcntl.FD_CLOEXEC)
                    receive_chat(conn.fileno())
                    conn.close()
                elif ready is sys.stdin:
                    cmd = input()
                    handle_command(cmd)
                    print("> ", end="", flush=True)

if __name__ == "__main__":
    main()
