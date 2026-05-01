from flask import Flask, redirect, url_for, request
import json
import os
from urllib.parse import quote, unquote

app = Flask(__name__)

ARQUIVO = "cardapio.json"
pedido = []

def carregar_cardapio():
    if not os.path.exists(ARQUIVO):
        return {
            "Cardápio": [],
            "Bebidas": [],
            "Doces": [],
            "Combos": [],
            "Promoções": [],
            "Fidelidade": []
        }
    with open(ARQUIVO, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_cardapio():
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(cardapio, f, ensure_ascii=False, indent=4)

cardapio = carregar_cardapio()

def link(txt):
    return quote(txt, safe="")

def abrir_link(txt):
    return unquote(txt)

def topo(t):
    return f"<h1>{t}</h1>"

@app.route("/")
def inicio():
    html = topo("PODRÃO DO BARRIGA")
    for cat in cardapio:
        html += f'<br><a href="/cat/{link(cat)}">{cat}</a>'
    html += '<br><br><a href="/pedido">VER PEDIDO</a>'
    html += '<br><br><a href="/admin">ADMIN</a>'
    return html

@app.route("/cat/<c>")
def categoria(c):
    c = abrir_link(c)
    html = topo(c)
    for i, item in enumerate(cardapio[c]):
        html += f'<br>{item["nome"]} - {item["preco"]} <a href="/add/{link(c)}/{i}">[+]</a>'
    html += '<br><br><a href="/">Voltar</a>'
    return html

@app.route("/add/<c>/<int:i>")
def add(c, i):
    c = abrir_link(c)
    pedido.append(cardapio[c][i])
    return redirect("/")

@app.route("/pedido")
def ver_pedido():
    html = topo("PEDIDO")
    total = 0
    for item in pedido:
        html += f'<br>{item["nome"]} - {item["preco"]}'
        total += item["preco"]
    html += f"<br><br>TOTAL: {total}"
    html += '<br><a href="/">Voltar</a>'
    return html

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        nome = request.form["nome"]
        preco = float(request.form["preco"])
        cat = request.form["categoria"]
        cardapio[cat].append({"nome": nome, "preco": preco})
        salvar_cardapio()
        return redirect("/admin")

    html = topo("ADMIN")
    html += '''
    <form method="post">
    Nome: <input name="nome"><br>
    Preço: <input name="preco"><br>
    Categoria:
    <select name="categoria">
        <option>Cardápio</option>
        <option>Bebidas</option>
        <option>Doces</option>
    </select><br>
    <button>Salvar</button>
    </form>
    '''
    html += '<br><a href="/">Voltar</a>'
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
