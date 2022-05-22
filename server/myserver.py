import socket
import select
import sys
import threading
from importlib import util

class MyServer:
    """ Class to encapsulate the server functions """
    def __init__(self, hostname='', port=5000):
        self.hostname = hostname
        self.port = port
        self._internal_socket = socket.socket()
        
        self.entradas = [sys.stdin]
        self.connections = {}
        self.connections_lock = threading.Lock()

        self.method = None
        self.app_name = None
        self.app_path = None

        self.quit_flag = False

    def __enter__(self):
        """ When the server is initialized, the internal socket must be configured """
        self._internal_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._internal_socket.bind((self.hostname, self.port))
        self._internal_socket.listen(5)
        self._internal_socket.setblocking(False)
        self.entradas.append(self._internal_socket)
        print(f"Server started, listening on port {self.port}")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ When the server is finishing, the internal socket must be closed """
        self._internal_socket.close()

    def run(self, app_name="app", app_path=""):
        """ method to start the server """
        self.set_application(app_name, app_path)
        print(self.app_path)
        self.update(False)
        while not self.quit_flag:
            reciever_list, _, _ = select.select(self.entradas, [], [])
            for reciever in reciever_list:
                if reciever == self._internal_socket:
                    self._spawn_client_thread()
                elif reciever == sys.stdin:
                    self._answer_commands()

    def set_external_method(self, function):
        """ receives a function that takes a string as an argument (request), and returns a string (response) """
        self.method = function

    def set_application(self, app_name, app_path):
        """ receives strings containing the name and path to the file where the app() method is defined """
        self.app_name = app_name
        self.app_path = app_path

    def update(self, verbose=True):
        """
        in case the app() method has been redefined, the server can update itself to run the new app
        without having to close the socket that it currently reserves
        """
        if (self.app_name is None) or (self.app_path is None):
            print("The application must be set first.")
            return
        self.set_external_method(MyServer.load_module(self.app_name, f"{self.app_path}{self.app_name}.py", piece="process"))
        if verbose:
            print("The server has been successfully updated.")

    def _spawn_client_thread(self):
        cliente = threading.Thread(target=self._method_caller, args=self._internal_socket.accept())
        cliente.start()

    def _answer_commands(self):
        cmd = input()
        if cmd == "exit":
            if self.connections:
                print("Failed to exit the server: there are open connections")
            else: 
                self.quit_flag = True
        elif cmd == "forceexit":
            for connection in self.connections:
                connection.close()
                self._unregister_connection(connection)
            self.quit_flag = True
        elif cmd == "hist":
            print(str(self.connections.values()))
        elif cmd == "update":
            self.update()

    def _register_connection(self, conn, addr):
        self.connections_lock.acquire()
        self.connections[conn] = addr
        self.connections_lock.release()
        print("Accepted connection from: ", addr)

    def _unregister_connection(self, conn):
        self.connections_lock.acquire()
        del self.connections[conn]
        self.connections_lock.release()

    def _method_caller(self, conn, addr):
        self._register_connection(conn, addr)
        while True:
            data = conn.recv(1024)
            if not data:
                print(str(addr) + " has requested to end his session.")
                self._unregister_connection(conn)
                conn.close()
                return
            conn.sendall(bytes(self.method(data), 'utf-8'))

    @staticmethod
    def load_module(module_name, module_path, piece=None):
        """ Method used for dinamic module importing """
        # print(f"Loading module {module_name}")
        spec = util.spec_from_file_location(module_name, module_path)
        module = util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        if piece:
            return getattr(module, piece)
