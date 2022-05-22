# Lado ativo/client

from myclient import MyClient

def main():

    # passar hostname e porta aqui para conectar a alguem diferente
    with MyClient() as client:
        # inicia o servidor
        client.start_chat(1)

main()
