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
        <style>
            body {{ margin:0; font-family:Arial; background:#f3f4f6; }}
            .app {{ max-width:430px; margin:auto; background:white; min-height:100vh; padding-bottom:80px; }}
            .topo {{ background:#111827; color:white; text-align:center; padding:18px; font-size:22px; font-weight:bold; }}
            .marca {{ background:#ea1d2c; color:white; text-align:center; padding:10px; font-weight:bold; }}
            .info {{ display:flex; justify-content:space-around; background:#fff0f1; padding:10px; font-weight:bold; }}
            .conteudo {{ padding:12px; }}
            .menu {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; }}
            button {{ border:none; border-radius:12px; padding:13px; font-size:15px; font-weight:bold; cursor:pointer; }}
            a {{ text-decoration:none; }}
            .btn-vermelho {{ background:#ea1d2c; color:white; width:100%; }}
            .btn-preto {{ background:#111827; color:white; width:100%; }}
            .btn-verde {{ background:#16a34a; color:white; width:100%; }}
            .btn-azul {{ background:#2563eb; color:white; width:100%; }}
            .btn-laranja {{ background:#ea580c; color:white; width:100%; }}
            .btn-cinza {{ background:#6b7280; color:white; width:100%; }}
            .item {{ border:1px solid #e5e7eb; border-radius:12px; padding:12px; margin-bottom:10px; background:white; }}
            .linha {{ display:flex; justify-content:space-between; align-items:center; gap:8px; }}
            .nome {{ font-size:16px; font-weight:bold; }}
            .preco {{ color:#16a34a; font-weight:bold; margin-top:4px; }}
            .total {{ font-size:26px; color:#16a34a; text-align:center; font-weight:bold; margin:18px 0; }}
            input, select {{ width:100%; padding:12px; margin-bottom:10px; border-radius:10px; border:1px solid #ddd; font-size:16px; box-sizing:border-box; }}
            label {{ font-weight:bold; }}
            .titulo-sec {{ font-size:20px; font-weight:bold; margin:20px 0 10px; }}
            .admin-box {{ background:#f9fafb; border:1px solid #ddd; border-radius:12px; padding:12px; margin-bottom:12px; }}
            .acoes {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:6px; margin-top:10px; }}
        </style>
    </head>
    <body>
        <div class="app">
            <div class="topo">{titulo}</div>
            <div class="marca">Lancheria universitária do Barriga</div>
            <div class="info">
                <div>Itens: {len(pedido)}</div>
                <div>Total: R$ {total_pedido():.2f}</div>
            </div>
            <div class="conteudo">
    """

def fim():
    return """
            </div>
        </div>
    </body>
    </html>
    """

@app.route("/")
def inicio():
    html = topo("PODRÃO DO BARRIGA")
    html += '<div class="menu">'

    for categoria, itens in cardapio.items():
        if categoria == "Fidelidade" or len(itens) > 0:
            html += f"""
            <a href="/categoria/{link(categoria)}">
                <button class="btn-vermelho">{categoria.upper()}</button>
            </a>
            """

    html += """
        <a href="/pedido">
            <button class="btn-preto">MEU PEDIDO</button>
        </a>
    </div>
    """

    html += fim()
    return html

@app.route("/categoria/<categoria_url>")
def ver_categoria(categoria_url):
    categoria = abrir_link(categoria_url)
    html = topo(categoria.upper())

    itens = cardapio.get(categoria, [])

    if categoria == "Fidelidade":
        html += """
        <div class="item">
            <div class="nome">Parceiros do Barriga</div>
            <div class="preco">Em breve: junte pontos e troque por brindes!</div>
        </div>
        """
    elif len(itens) == 0:
        html += '<div class="item">Nenhum item cadastrado ainda.</div>'
    else:
        for i, item in enumerate(itens):
            html += f"""
            <div class="item">
                <div class="linha">
                    <div>
                        <div class="nome">{item['nome']}</div>
                        <div class="preco">R$ {item['preco']:.2f}</div>
                    </div>
                    <a href="/adicionar/{link(categoria)}/{i}">
                        <button class="btn-vermelho">+</button>
                    </a>
                </div>
            </div>
            """

    html += '<a href="/"><button class="btn-preto">VOLTAR</button></a>'
    html += fim()
    return html

@app.route("/adicionar/<categoria_url>/<int:indice>")
def adicionar(categoria_url, indice):
    categoria = abrir_link(categoria_url)
    pedido.append(cardapio[categoria][indice])
    return redirect(url_for("ver_categoria", categoria_url=categoria_url))

@app.route("/pedido")
def ver_pedido():
    html = topo("MEU PEDIDO")
    itens = resumo_pedido()

    if not itens:
        html += '<div class="item">Pedido vazio.</div>'
    else:
        for item in itens:
            subtotal = item["qtd"] * item["preco"]
            html += f"""
            <div class="item">
                <div class="nome">{item['nome']}</div>
                <div class="preco">{item['qtd']} x R$ {item['preco']:.2f} = R$ {subtotal:.2f}</div>
                <div class="acoes">
                    <a href="/menos/{link(item['nome'])}"><button class="btn-cinza">-1</button></a>
                    <a href="/mais/{link(item['nome'])}"><button class="btn-verde">+1</button></a>
                    <a href="/excluir_pedido/{link(item['nome'])}"><button class="btn-laranja">EXCLUIR</button></a>
                </div>
            </div>
            """

        html += f'<div class="total">TOTAL: R$ {total_pedido():.2f}</div>'
        html += '<a href="/pagamento"><button class="btn-verde">PAGAR</button></a><br><br>'
        html += '<a href="/limpar_pedido"><button class="btn-laranja">LIMPAR PEDIDO</button></a><br><br>'

    html += '<a href="/"><button class="btn-preto">VOLTAR</button></a>'
    html += fim()
    return html

@app.route("/mais/<nome_url>")
def mais(nome_url):
    nome = abrir_link(nome_url)
    item = buscar_item(nome)
    if item:
        pedido.append(item)
    return redirect(url_for("ver_pedido"))

@app.route("/menos/<nome_url>")
def menos(nome_url):
    nome = abrir_link(nome_url)
    for item in pedido:
        if item["nome"] == nome:
            pedido.remove(item)
            break
    return redirect(url_for("ver_pedido"))

@app.route("/excluir_pedido/<nome_url>")
def excluir_pedido(nome_url):
    global pedido
    nome = abrir_link(nome_url)
    pedido = [item for item in pedido if item["nome"] != nome]
    return redirect(url_for("ver_pedido"))

@app.route("/limpar_pedido")
def limpar_pedido():
    pedido.clear()
    return redirect(url_for("ver_pedido"))

@app.route("/pagamento")
def pagamento():
    html = topo("PAGAMENTO")
    html += f'<div class="total">TOTAL: R$ {total_pedido():.2f}</div>'
    html += """
    <a href="/finalizar/pix"><button class="btn-verde">PIX</button></a><br><br>
    <a href="/finalizar/cartao"><button class="btn-azul">CARTÃO</button></a><br><br>
    <a href="/dinheiro"><button class="btn-laranja">DINHEIRO</button></a><br><br>
    <a href="/pedido"><button class="btn-preto">VOLTAR</button></a>
    """
    html += fim()
    return html

@app.route("/dinheiro")
def dinheiro():
    html = topo("DINHEIRO")
    html += f'<div class="total">TOTAL: R$ {total_pedido():.2f}</div>'
    html += """
    <form action="/troco" method="post">
        <input name="valor" placeholder="Valor recebido">
        <button class="btn-verde">CALCULAR TROCO</button>
    </form>
    <a href="/pagamento"><button class="btn-preto">VOLTAR</button></a>
    """
    html += fim()
    return html

@app.route("/troco", methods=["POST"])
def troco():
    try:
        valor = float(request.form["valor"].replace(",", "."))
    except:
        valor = 0

    troco = valor - total_pedido()
    html = topo("TROCO")
    html += f'<div class="total">TROCO: R$ {troco:.2f}</div>'
    html += '<a href="/novo_pedido"><button class="btn-verde">NOVO PEDIDO</button></a>'
    html += fim()
    return html

@app.route("/finalizar/<forma>")
def finalizar(forma):
    total = total_pedido()
    pedido.clear()

    html = topo("FINALIZADO")
    html += f"""
    <div class="item">
        Pedido finalizado.<br>
        Pagamento: {forma.upper()}<br>
        Total: R$ {total:.2f}
    </div>
    <a href="/"><button class="btn-verde">NOVO PEDIDO</button></a>
    """
    html += fim()
    return html

@app.route("/novo_pedido")
def novo_pedido():
    pedido.clear()
    return redirect(url_for("inicio"))

@app.route("/admin")
def admin():
    html = topo("ADMIN")

    html += """
    <div class="admin-box">
        <a href="/admin/nova_categoria">
            <button class="btn-verde">CRIAR NOVO BOTÃO / CATEGORIA</button>
        </a>
    </div>

    <div class="admin-box">
        <a href="/admin/novo_item">
            <button class="btn-azul">ADICIONAR ITEM EM UMA CATEGORIA</button>
        </a>
    </div>
    """

    for categoria, itens in cardapio.items():
        html += f"""
        <div class="admin-box">
            <div class="titulo-sec">{categoria}</div>
            <a href="/admin/remover_categoria/{link(categoria)}">
                <button class="btn-laranja">REMOVER ESTE BOTÃO / CATEGORIA</button>
            </a>
            <br><br>
        """

        if not itens:
            html += "<p>Nenhum item cadastrado.</p>"
        else:
            for i, item in enumerate(itens):
                html += f"""
                <div class="item">
                    <div class="nome">{item['nome']}</div>
                    <div class="preco">R$ {item['preco']:.2f}</div>
                    <a href="/admin/remover_item/{link(categoria)}/{i}">
                        <button class="btn-cinza">REMOVER ITEM</button>
                    </a>
                </div>
                """

        html += "</div>"

    html += '<a href="/"><button class="btn-preto">VOLTAR PARA CLIENTE</button></a>'
    html += fim()
    return html

@app.route("/admin/nova_categoria")
def nova_categoria():
    html = topo("NOVA CATEGORIA")
    html += """
    <form action="/admin/salvar_categoria" method="post">
        <label>Nome do botão/categoria</label>
        <input name="categoria" placeholder="Ex: Bebidas, Doces, Combos">
        <button class="btn-verde">SALVAR CATEGORIA</button>
    </form>
    <a href="/admin"><button class="btn-preto">VOLTAR</button></a>
    """
    html += fim()
    return html

@app.route("/admin/salvar_categoria", methods=["POST"])
def salvar_categoria():
    categoria = request.form["categoria"].strip()

    if categoria and categoria not in cardapio:
        cardapio[categoria] = []
        salvar_cardapio()

    return redirect(url_for("admin"))

@app.route("/admin/novo_item")
def novo_item():
    html = topo("NOVO ITEM")

    html += """
    <form action="/admin/salvar_item" method="post">
        <label>Escolha a categoria/botão</label>
        <select name="categoria">
    """

    for categoria in cardapio.keys():
        html += f'<option value="{categoria}">{categoria}</option>'

    html += """
        </select>

        <label>Nome do item</label>
        <input name="nome" placeholder="Ex: X Bacon">

        <label>Preço</label>
        <input name="preco" placeholder="Ex: 17,00">

        <button class="btn-verde">SALVAR ITEM</button>
    </form>
    <a href="/admin"><button class="btn-preto">VOLTAR</button></a>
    """

    html += fim()
    return html

@app.route("/admin/salvar_item", methods=["POST"])
def salvar_item():
    categoria = request.form["categoria"].strip()
    nome = request.form["nome"].strip()
    preco_txt = request.form["preco"].strip().replace(",", ".")

    try:
        preco = float(preco_txt)
    except:
        preco = 0

    if categoria not in cardapio:
        cardapio[categoria] = []

    if nome:
        cardapio[categoria].append({"nome": nome, "preco": preco})
        salvar_cardapio()

    return redirect(url_for("admin"))

@app.route("/admin/remover_item/<categoria_url>/<int:indice>")
def remover_item(categoria_url, indice):
    categoria = abrir_link(categoria_url)

    if categoria in cardapio and 0 <= indice < len(cardapio[categoria]):
        cardapio[categoria].pop(indice)
        salvar_cardapio()

    return redirect(url_for("admin"))

@app.route("/admin/remover_categoria/<categoria_url>")
def remover_categoria(categoria_url):
    categoria = abrir_link(categoria_url)

    if categoria in cardapio:
        del cardapio[categoria]
        salvar_cardapio()

    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
