from flask import Flask, render_template, jsonify, request
from database import init_db, salvar_produtos, get_db_connection
from scraper import raspagem

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/produtos')
def api_produtos():
    mercado_filtrado = request.args.get('mercado')
    conn = get_db_connection()
    cursor = conn.cursor()
    sql_query = "SELECT * FROM produtos"
    params = []
    if mercado_filtrado:
        sql_query += " WHERE mercado = ?"
        params.append(mercado_filtrado)
    cursor.execute(sql_query, params)
    produtos = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in produtos])

@app.route('/api/raspar/<nome_mercado>', methods=['POST'])
def api_raspar(nome_mercado):
    try:
        print(f"Recebida requisição para raspar dados de: {nome_mercado}")
        produtos_coletados = raspagem(nome_mercado)
        if not produtos_coletados:
            return jsonify({"status": "warning", "message": "Nenhum produto novo encontrado."}), 200
        salvar_produtos(produtos_coletados)
        return jsonify({"status": "success", "message": f"{len(produtos_coletados)} produtos de {nome_mercado} salvos."})
    except Exception as e:
        print(f"Erro durante a raspagem de {nome_mercado}: {e}")
        return jsonify({"status": "error", "message": "Ocorreu um erro no servidor durante a raspagem."}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)