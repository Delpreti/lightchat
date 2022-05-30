#!/usr/bin/env python3

HOST = ""
PORT = 1234

import socket

with socket.socket() as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()

    while True:
        conn, addr = s.accept()
        with conn:
            req = conn.recv(1024)
            print(req)
            if b"get_lista" in req:
                conn.sendall(b'\x62{"operacao":"get_lista","status":200,"clientes":{"luanzinho32":{"ip":"127.0.0.1","porta":"4321"}}}')
            elif b"login" in req:
                conn.sendall(b'\x21{"operacao":"login","status":200}')
            elif b"logoff" in req:
                conn.sendall(b'\x26{"operacao":"logoff","status":200}')
