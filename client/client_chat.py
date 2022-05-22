#!/usr/bin/env python3

import socket, argparse, json

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
        s.connect(self.socket)
        while True:
            size = ord(recvall(socket, 1))
            response = recvall(socket, size).decode("utf-8")
            response = json.loads(response)


if __name__ == "__main__":
    main()
