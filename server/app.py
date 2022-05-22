# Logica da aplicacao a ser rodada no servidor

import re
import json

def build_json(args):
    content = json.dumps(args, separators=(",", ":")).encode("utf-8")
    if len(content) > 0xff:
        return None

    length = len(content).to_bytes(1, byteorder="big")
    return length + content

def operate(jstring):
    """ Metodo para retornar uma mensagem de boas vindas """
    print(jstring)
    jstring = re.sub(r"^.*{", "{", jstring)
    content = json.loads(jstring)
    if "operacao" not in content:
        return build_json({"status": "69"})
    operation = content.get("operacao")
    if operation == "login":
        user = content.get("username")
        return build_json({ "operacao": "login", "status": 200, "mensagem": "Login com sucesso" })
    elif operation == "logoff":
        return build_json({ "operacao": "logoff", "status": 200, "mensagem": "Logoff com sucesso" })
    elif operation == "get_lista":
        return build_json({ "operacao": "get_lista", "status": 200, "clientes": { "luanzinho32": "(10.10.10.10, 5000)", "Usuario": "(IP, Porta)" } })
    else:
        return build_json({"status": "171"})

# ------------------------
# ---- Metodo process ----

def process(text_string):
    """ Nome de metodo reservado, a aplicacao precisa estar definida aqui """
    return operate(text_string)

# ------------------------