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

    def send_command(self, content, timeout=None):
        result = None
        self.command_response_lock.acquire()
        self.command = content
        self.command_event.set()
        waited = True
        if timeout is None:
            self.response_event.wait()
        else:
            waited = self.response_event.wait(timeout)
        if not waited:
            self.command_event.clear()
        else:
            self.response_event.clear()
            result = self.response
        self.command_response_lock.release()
        return result

    def process(self, text_string, connection_info):
        
        print(text_string)
        text_string = re.sub(r"^.*{", "{\"ip\":\"" + connection_info[0] + "\",", text_string) # corrigir

        print(text_string)
        content = json.loads(text_string)
        
        result = self.send_command(content, 1)
        if result is None:
            result = { "status": 404, "mensagem": "Indisponivel, tente novamente mais tarde" }
        return build_json(result)

    def read_buffer(self):
        return self.max_read_buffer

    def terminate(self):
        if self.send_command({ "terminate": True }) is None:
            raise RuntimeError("The application is unable to terminate.")

    def main(self):
        manager = UserManager()
        while True:
            self.command_event.wait()
            self.command_event.clear()

            if "terminate" in self.command:
                self.response = self.command
                self.response_event.set()
                return

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
