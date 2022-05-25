# Logica da aplicacao a ser rodada no servidor

import re
import json
import threading
from usermanager import UserManager

def build_json(args):
    content = json.dumps(args, separators=(",", ":")).encode("utf-8")
    if len(content) > 0xff:
        return None

    length = len(content).to_bytes(1, byteorder="big")
    return length + content

class App: # separar classe abstrata

    def __init__(self):
        self.max_read_buffer = 3000

        self.command_event = threading.Event()
        self.response_event = threading.Event()
        self.command = None
        self.response = None
        self.command_response_lock = threading.Lock()

    def process(self, text_string):
        
        print(text_string)
        text_string = re.sub(r"^.*{", "{", text_string)
        content = json.loads(text_string)
        
        result = {}
        # lock to guarantee that the user commands dont get mixed up
        self.command_response_lock.acquire()
        self.command = content
        self.command_event.set()
        waited = self.response_event.wait(1)
        if not waited: # timeout
            self.command_event.clear()
            result = { "status": 404, "mensagem": "Indisponivel, tente novamente mais tarde" }
        else:
            self.response_event.clear()
            result = self.response
        self.command_response_lock.release()

        print(result)
        return build_json(result)

    def read_buffer(self):
        return self.max_read_buffer

    def main(self):
        manager = UserManager() # precisa estar inicializado
        while True:
            self.command_event.wait()
            self.command_event.clear()

            # processa aqui
            if "operacao" not in self.command:
                self.response = {"status": 171, "mensagem": "O json nao contem o campo \"operacao\""}
            else:
                operation = self.command.get("operacao")
                if operation == "login":
                    try:
                        user_name = self.command.get("username")
                        user_ip = "undefined" # corrigir
                        user_port = self.command.get("porta")
                        manager.user_login(user_name, { "ip": user_ip, "porta": user_port})
                        self.response = { "operacao": "login", "status": 200, "mensagem": "Login com sucesso" }
                    except:
                        self.response = { "operacao": "login", "status": 400, "mensagem": "Login falhou!" }
                elif operation == "logoff":
                    try:
                        user_name = self.command.get("username")
                        manager.user_logoff(user_name)
                        self.response = { "operacao": "logoff", "status": 200, "mensagem": "Logoff com sucesso" }
                    except:
                        self.response = { "operacao": "logoff", "status": 400, "mensagem": "Logoff falhou!" }
                elif operation == "get_lista":
                    try:
                        self.response = { "operacao": "get_lista", "status": 200, "clientes": manager.get_list() }
                    except:
                        self.response = { "operacao": "get_lista", "status": 400, "mensagem": "Nao foi possivel obter a lista" }
                else:
                    self.response = { "operacao": "nao_reconhecida", "status": 69 }

            self.response_event.set()
