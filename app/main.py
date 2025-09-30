from flask import Flask, render_template, request, jsonify
from scraper import raspagem
import json

app = Flask(__name__)

# Constantes
API_KEY = "631b3d1b84c325f70b8a1ced5a35bbeb"

# Rota principal - página inicial
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/produtos.json')
def produtos_json():
    try:
        with open('produtos.json', 'r', encoding='utf-8') as f:
            produtos = json.load(f)
        return jsonify(produtos)
    except FileNotFoundError:
        return jsonify([])  # Se não existir ainda


if __name__ == '__main__':
    app.run(debug=True)