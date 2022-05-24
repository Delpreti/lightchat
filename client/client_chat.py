#!/usr/bin/env python3

import sys, socket, argparse, json
from select import select

username = None

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", dest="username")
    parser.add_argument("-H", "--host", dest="host")
    parser.add_argument("-p", "--port", type=int, dest="port")
    args = parser.parse_args()

    with socket.socket() as s:
        s.connect((args.host, args.port))

        while True:
            read, _, _ = select([sys.stdin, s], [], [])

            for ready in read:
                if ready is s:
                    size = ord(recvall(socket, 1))
                    r = recvall(socket, size).decode("utf-8")
                    r = json.loads(r)
                    print(f'{r["username]}> {r["mensagem"]}')
                elif ready is sys.stdin:
                    msg = input()
                    s.sendall(msg.encode("utf-8"))

    import time
    time.sleep(10)

if __name__ == "__main__":
    main()
