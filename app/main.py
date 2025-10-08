from flask import Flask, render_template, jsonify
import sqlite3
from database import get_db_connection

app = Flask(__name__)
DB_NAME = "produtos.db"

@app.route('/')
def home():
    """Renderiza a página inicial."""
    return render_template('index.html')

@app.route('/api/produtos')
def api_produtos():
    """Busca produtos no banco de dados e retorna como JSON."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    conn.close()
    # Converte a lista de objetos Row para uma lista de dicionários
    return jsonify([dict(row) for row in produtos])

if __name__ == '__main__':
    app.run(debug=True)