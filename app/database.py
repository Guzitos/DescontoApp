import sqlite3

DB_NAME = "produtos.db"


def get_db_connection():
    """Cria uma conexão com o banco de dados."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Cria a tabela de produtos se ela não existir."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco TEXT,
            desconto TEXT,
            preco_antigo TEXT,
            qnt_desconto REAL,
            imagem TEXT,
            UrlProduto TEXT,
            mercado TEXT,
            data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print(f"Banco de dados '{DB_NAME}' inicializado com sucesso.")


def salvar_produtos(produtos):
    """Salva uma lista de produtos no banco de dados."""
    if not produtos:
        return

    # Limpa apenas os produtos do mesmo mercado antes de inserir os novos
    mercado_dos_produtos = produtos[0]['mercado']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM produtos WHERE mercado = ?", (mercado_dos_produtos,))

    for produto in produtos:
        cursor.execute("""
            INSERT INTO produtos (nome, preco, desconto, preco_antigo, qnt_desconto, imagem, UrlProduto, mercado) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            produto["nome"], produto["preco"], produto["desconto"],
            produto["preco_antigo"], produto["qnt_desconto"],
            produto["imagem"], produto["UrlProduto"],
            produto["mercado"]
        ))

    conn.commit()
    conn.close()
    print(f"{len(produtos)} produtos de '{mercado_dos_produtos}' salvos no banco de dados.")