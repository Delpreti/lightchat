
import select
import sys
import os
import threading
from importlib import util
from apphead import AppHeader

class MyServer:
    """ Class to encapsulate the server functions """
    def __init__(self, hostname=''):
        self.hostname = hostname

        self.entradas = [sys.stdin]
        self.connections = {}
        self.connections_lock = threading.Lock()

        self.applications = {}

        self.quit_flag = False

    def __enter__(self):
        """ When the server is initialized, the internal sockets must be configured """
        for entry in os.scandir():
            if entry.is_file():
                if entry.name != "apphead.py" and entry.name.startswith("app"):
                    port_num = entry.name.split(".")[0][4:]
                    self.set_application(port_num, entry.name, entry.path)
        print(f"Server started, {len(self.applications)} applications are available.")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ When the server is finishing, the internal sockets must be closed """
        for app in self.applications.values():
            app.close_connection()
            if app.is_running():
                app.stop(5)

    def start(self, app_name="app", app_path=""):
        """ method to start the server """
        self.update(False)
        for port, app in self.applications.items():
            if app.is_executable():
                self._run_app(port, app);
        while not self.quit_flag:
            reciever_list, _, _ = select.select(self.entradas, [], [])
            for reciever in reciever_list:
                if reciever == sys.stdin:
                    self._answer_commands()
                else:
                    self._attend_client(reciever)

    def set_application(self, port_num, app_name, app_path):
        """ sets the application on a specified port """
        if isinstance(port_num, str):
            port_num = int(port_num) # posso fazer isso ?
        self.applications[port_num] = AppHeader(port_num, app_name, app_path)
        self.applications[port_num].configure_socket(self.hostname)
        self.entradas.append(self.applications[port_num].app_socket)

    def update(self, verbose=True):
        """
        in case the app() method has been redefined, the server can update itself to run the new app
        without having to close the socket that it currently reserves
        """
        for app in self.applications.values():
            app.setup(MyServer.load_module(app.name, app.path, piece="App"))
        if verbose:
            print("The server has been successfully updated.")

    def _attend_client(self, socket):
        cliente = threading.Thread(target=self._method_caller, args=socket.accept())
        cliente.setDaemon(True)
        cliente.start()

    def _run_app(self, portnum, apphead):
        apphead.thread_obj = threading.Thread(target=apphead.obj.main)
        apphead.start()
        print(f"Application on port {portnum} is now running.")

    def _answer_commands(self):
        cmd = input()
        if cmd == "exit":
            if self.connections:
                print("Failed to exit the server: there are open connections")
            else: 
                self.quit_flag = True
        elif cmd == "forceexit":
            for connection in self.connections.copy():
                connection.close()
                self._unregister_connection(connection)
            self.quit_flag = True
        elif cmd == "hist":
            print(str(self.connections.values()))
        elif cmd == "update":
            self.update()
        elif cmd == "ports":
            print(list(self.applications.keys()))
        elif cmd.startswith("run"):
            pcmd = cmd.split(" ")
            if self.applications[int(pcmd[1])].is_running():
                print(f"Requested application is already running.")
            else:
                self._run_app(pcmd[1], self.applications[int(pcmd[1])])
        elif cmd.startswith("stop"):
            pcmd = cmd.split(" ")
            if self.applications[int(pcmd[1])].is_running():
                self.applications[int(pcmd[1])].stop()
                print(f"Application on port {pcmd[1]} was stopped.")
            else:
                print(f"Requested application is not running.")
        elif cmd == "apps":
            i = 0
            for app in self.applications.values():
                if app.is_running():
                    i += 1
            print(f"There are currently {i} apps running on this server.")

    def _register_connection(self, conn, addr):
        self.connections_lock.acquire()
        self.connections[conn] = addr
        self.connections_lock.release()
        print("Accepted connection from: ", addr)

    def _unregister_connection(self, conn):
        self.connections_lock.acquire()
        del self.connections[conn]
        self.connections_lock.release()

    def _recvall(self, sock, length):
        buff = bytearray(length)
        pos = 0
        while pos < length:
            read = sock.recv_into(memoryview(buff)[pos:])
            if read == 0:
                raise EOFError
            pos += read
        return buff

    def _recv_ott(self, sock):
        size = int.from_bytes(self._recvall(sock, 2), "big")
        #size = ord(self._recvall(sock, 1))
        return self._recvall(sock, size)

    def _method_caller(self, conn, addr):
        self._register_connection(conn, addr)
        sock_id = conn.getsockname()[1]
        while True:
            data = bytearray()
            try:
                #data = conn.recv(self.applications[sock_id].obj.read_buffer())
                data = self._recv_ott(conn)
            except EOFError:
                print(str(addr) + " session has ended.")
                self._unregister_connection(conn)
                conn.close()
                sys.exit()
            response_data = self.applications[sock_id].obj.process(data.decode("utf-8"), addr)
            if isinstance(response_data, str):
                response_data = response_data.encode('utf-8')
            conn.sendall(response_data)

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
