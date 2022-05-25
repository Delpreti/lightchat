import socket

class AppHeader:
    """ Header utilized by the server, containing generic info about the application """

    def __init__(self, port, name, path):
        self.port = port
        self.app_socket = socket.socket()
        self.name = name
        self.path = path

        self.obj = None

        self.status = "ready"
        self.start_method = None # function

    def configure_socket(self, hostname, max_listen=5, blocking=False):
        """ When the application is initialized, the internal socket must be configured """
        self.app_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.app_socket.bind((hostname, self.port))
        self.app_socket.listen(5)
        self.app_socket.setblocking(False)
        
    def setup(self, app_cls):
        """ Keep an application object initialized """
        self.obj = app_cls()

    def close_connection(self):
        """ Close the internal socket """
        self.app_socket.close()

    def start(self):
        self.status = "running"
        self.obj.main()

    def is_running(self):
        return self.status == "running"
