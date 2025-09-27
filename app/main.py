from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
from scraper import raspagem

app = Flask(__name__)

# Constantes
API_KEY = "631b3d1b84c325f70b8a1ced5a35bbeb"

# Rota principal - página inicial
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/produtos', methods=['GET'])
def get_produtos():
    # Pega parâmetros da URL (ex: /produtos?limite=5&filtro=...)
    limite = request.args.get('limite', default=10, type=int)
    filtro = request.args.get('filtro', default=None, type=str)
    desconto_min = request.args.get('desconto_min', default=0, type=int)
    preco_max = request.args.get('preco_max', default=None, type=float)

    produtos = raspagem(
        limite=limite,
        filtro=filtro,
        filtro_desconto=desconto_min,
        filtro_preco=preco_max
    )

    # Retorna o dicionário como JSON
    return jsonify({"produtos": produtos, "quantidade": len(produtos)})


if __name__ == '__main__':
    app.run(debug=True)