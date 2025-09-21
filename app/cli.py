from app.scraper import raspagem
from app.storage import salvar_csv

def run_cli():
    palavra_chave = input("Digite o item desejado (ou vazio p/ todos): ").strip()
    desconto_desejavel = input("Desconto mínimo (%) (ou vazio p/ 0): ").strip()
    preco_maximo = input("Preço máximo (ou vazio p/ sem limite): ").strip()

    filtro_desconto = int(desconto_desejavel) if desconto_desejavel.isdigit() else 0
    filtro_preco = float(preco_maximo.replace(",", ".")) if preco_maximo else None

    resultado = raspagem(
        limite=10,
        filtro=palavra_chave or None,
        filtro_desconto=filtro_desconto,
        filtro_preco=filtro_preco
    )

    for p in resultado:
        print(p)
    salvar_csv(resultado)
