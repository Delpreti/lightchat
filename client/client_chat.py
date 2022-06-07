#!/usr/bin/env python3

import sys, socket, argparse, json
from select import select
from client_main import build_request

username = None

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

def main():
    import time
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", dest="username", required=True)
    parser.add_argument("-H", "--host", dest="host")
    parser.add_argument("-p", "--port", type=int, dest="port")
    parser.add_argument("-f", "--fd", type=int, dest="fd")
    args = parser.parse_args()

    if args.fd:
        s = socket.fromfd(args.fd, socket.AF_INET, socket.SOCK_STREAM)
    else:
        s = socket.socket()
        s.connect((args.host, args.port))

    with s:
        print(f"{args.username}> ", end="", flush=True)

        while True:
            read, _, _ = select([sys.stdin, s], [], [])

            for ready in read:
                if ready is s:
                    size = int.from_bytes(recvall(s, 2), "big")
                    r = recvall(s, size).decode("utf-8")
                    r = json.loads(r)
                    print(f'\r{r["username"]}> {r["mensagem"]}', end="")
                    print("                                           ")
                    print(f"{args.username}> ", end="", flush=True)
                elif ready is sys.stdin:
                    msg = input(f"{args.username}> ")
                    req = build_request({"username": args.username, "mensagem": msg})
                    s.sendall(req)

if __name__ == "__main__":
    main()
