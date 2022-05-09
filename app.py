# Logica da aplicacao a ser rodada no servidor

import re

def read_file(filename):
    """ Metodo para retornar todo o conteudo do arquivo (como string de texto) """
    with open(filename, "r") as f:
        return f.read()

def word_count(string):
    """ Metodo para contar as ocorrencias de cada palavra em um determinado texto """
    result = {}
    unique_words = set(re.split(r"\W+", string))
    for word in unique_words:
        result[word] = len(re.findall(r"^" + word + r"$|\W" + word + r"$|^" + word + r"\W|\W" + word + r"\W", string))
    del result[""]
    return result

def high_words(counted, amount=1):
    """ Metodo para pegar uma quantia de palavras com as maiores frequencias """
    if amount >= len(counted.keys()):
        return counted.keys()
    ordered = sorted(counted.items(), key=lambda item: item[1]) # lista de tuplas no formato [(chave, valor), ... ]
    if ordered[0][1] > ordered[-1][1]:
        return dict(ordered[:amount]).keys()
    return dict(ordered[-amount:]).keys()

def all_counts(filename):
    """ Metodo que retorna a frequencia de todas as palavras unicas que ocorrem no texto """
    try:
        contents = read_file(str(filename, encoding='utf-8'));
        result = ""
        counted = word_count(contents)
        test = dict(sorted(counted.items(), key=lambda item: item[1]))
        for key, value in test.items():
            result += f"[{key}:{value}]"
        return result
    except FileNotFoundError:
        return "Arquivo não encontrado."

def high_five(filename):
    """ Metodo que retorna as 5 palavras que mais ocorrem dentro de um determinado texto """
    try:
        contents = read_file(str(filename, encoding='utf-8'));
        return ", ".join(high_words(word_count(contents), 5))
    except FileNotFoundError:
        return "Arquivo não encontrado."

# ------------------------
# ---- Metodo process ----

def process(text_string):
    """ Nome de metodo reservado, a aplicacao precisa estar definida aqui """
    return high_five(text_string)

# ------------------------