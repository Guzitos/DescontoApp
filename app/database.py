import sqlite3

DB_NAME = "produtos.db"  # Define o nome do arquivo aqui


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
            data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print(f"Banco de dados '{DB_NAME}' inicializado.")


def salvar_produtos(produtos):
    """Salva uma lista de produtos no banco de dados, limpando os antigos."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Limpa dados antigos
    cursor.execute("DELETE FROM produtos")

    # Insere os novos produtos
    for produto in produtos:
        cursor.execute("""
            INSERT INTO produtos (nome, preco, desconto, preco_antigo, qnt_desconto, imagem, UrlProduto) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            produto["nome"], produto["preco"], produto["desconto"],
            produto["preco_antigo"], produto["qnt_desconto"],
            produto["imagem"], produto["UrlProduto"]
        ))

    conn.commit()
    conn.close()
    print(f"{len(produtos)} produtos salvos no banco de dados.")