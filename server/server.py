# Lado passivo/server

from myserver import MyServer

def main():
    # passar hostname e porta aqui para conectar a alguem diferente
    with MyServer() as server:
        # inicia o servidor
        server.run()

main()
