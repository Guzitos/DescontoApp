import sqlite3, requests,json
#from scraper import scraper
con = sqlite3.connect("produtos.db")
cursor = con.cursor()

cursor.execute(""" CREATE TABLE IF NOT EXISTS produtos(
id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    preco TEXT,
    desconto TEXT,
    preco_antigo TEXT,
    qnt_desconto REAL,
    imagem TEXT,
    UrlProduto URL TEXT,
    data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
def salvar_dados(scraper, produto=None):
    con = sqlite3.connect("produtos.db")
    cursor = con.cursor()

    for nome, preco in scraper:
        cursor.execute("""INSERT INTO produtos (nome,preco,desconto,qnt_desconto,preco_antigo,imagem,Urlproduto) 
        VALUES (?,?,?,?,?,?)""",(
                       produto["nome"],
                       produto["preco"],
                       produto["preco_antigo"],
                       produto["qnt_desconto"],
                       produto["imagem"],
                       produto["Urlproduto"]
                       ))



con.commit()
con.close()


