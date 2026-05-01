from flask import Flask, redirect, url_for, request
import json
import os
from urllib.parse import quote, unquote

app = Flask(__name__)

ARQUIVO = "cardapio.json"
pedido = []

cardapio_padrao = {
    "Cardápio": [
        {"nome": "Cachorro Quente", "preco": 12.00},
        {"nome": "X Salada", "preco": 15.00},
        {"nome": "X Bacon", "preco": 17.00}
    ],
    "Bebidas": [
        {"nome": "Brahma", "preco": 8.00},
        {"nome": "Skol", "preco": 8.00}
    ],
    "Doces": [
        {"nome": "Trufa", "preco": 5.00},
        {"nome": "Brownie", "preco": 7.00}
    ],
    "Combos": [],
    "Promoções": [],
    "Fidelidade": []
}

def salvar_cardapio():
    with open(ARQUIVO, "w", encoding="utf-8") as arquivo:
        json.dump(cardapio, arquivo, ensure_ascii=False, indent=4)

def carregar_cardapio():
    if not os.path.exists(ARQUIVO):
        with open(ARQUIVO, "w", encoding="utf-8") as arquivo:
            json.dump(cardapio_padrao, arquivo, ensure_ascii=False, indent=4)

    with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)

cardapio = carregar_cardapio()

def link(texto):
    return quote(texto, safe="")

def abrir_link(texto):
    return unquote(texto)

def total_pedido():
    return sum(item["preco"] for item in pedido)

def resumo_pedido():
    resumo = {}
    for item in pedido:
        nome = item["nome"]
        if nome not in resumo:
            resumo[nome] = {"nome": nome, "preco": item["preco"], "qtd": 0}
        resumo[nome]["qtd"] += 1
    return list(resumo.values())

def buscar_item(nome):
    for itens in cardapio.values():
        for item in itens:
            if item["nome"] == nome:
                return item
    return None

def topo(titulo):
    return f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{titulo}</title>
    </head>
    <body>
        <h1>{titulo}</h1>
    """

def fim():
    return """
    </body>
    </html>
    """

@app.route("/")
def inicio():
    html = topo("PODRÃO DO BARRIGA")
    for categoria in cardapio.keys():
        html += f'<a href="/categoria/{link(categoria)}"><button>{categoria}</button></a><br>'
    html += '<a href="/pedido"><button>MEU PEDIDO</button></a>'
    html += fim()
    return html

@app.route("/categoria/<categoria_url>")
def ver_categoria(categoria_url):
    categoria = abrir_link(categoria_url)
    html = topo(categoria)

    itens = cardapio.get(categoria, [])

    for i, item in enumerate(itens):
        html += f'''
        <div>
            {item['nome']} - R$ {item['preco']}
            <a href="/adicionar/{link(categoria)}/{i}"><button>+</button></a>
        </div>
        '''

    html += '<br><a href="/">Voltar</a>'
    html += fim()
    return html

@app.route("/adicionar/<categoria_url>/<int:indice>")
def adicionar(categoria_url, indice):
    categoria = abrir_link(categoria_url)
    pedido.append(cardapio[categoria][indice])
    return redirect(url_for("inicio"))

@app.route("/pedido")
def ver_pedido():
    html = topo("PEDIDO")

    for item in pedido:
        html += f"<div>{item['nome']} - R$ {item['preco']}</div>"

    html += '<br><a href="/">Voltar</a>'
    html += fim()
    return html

if __name__ == "__main__":
    app.run()
