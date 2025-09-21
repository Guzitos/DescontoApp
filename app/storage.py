import csv

def salvar_csv(produtos, nome_arquivo="produtos.csv"):
    with open(nome_arquivo, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Nome", "Preço", "Desconto", "Preço Antigo", "Valor do Desconto ", "Imagem"])
        for p in produtos:
            writer.writerow([
                p["nome"],
                p["preco"],
                p["desconto"],
                p["preco_antigo"] or "",
                p["qnt_desconto"] or "",
                p["imagem"]
            ])
    print(f"Arquivo '{nome_arquivo}' salvo com sucesso!")
