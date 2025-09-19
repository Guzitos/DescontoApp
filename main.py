from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import unicodedata
import re


def normalizar(texto):
    """Remove acentos, deixa minúsculo e limpa caracteres estranhos"""
    if not texto:
        return ""
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    texto = texto.lower()
    texto = re.sub(r'[^a-z0-9\s]', '', texto)
    return texto.strip()


def raspagem(limite=0, filtro=None, filtro_desconto=0, filtro_preco=None):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # ou "--headless" se der erro
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    navegador = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(navegador, 10)

    pagina = 1
    coletados = 0
    produtos = []
    vistos = set()

    while coletados < limite:
        if pagina > 10:
            print("Limite de 50 páginas atingido, encerrando a raspagem.")
            break

        url = f"https://www.paodeacucar.com/especial/ofertasdodia-pao2023?page={pagina}"
        navegador.get(url)

        try:
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "Card-sc-yvvqkp-0")))
        except:
            break

        cards = navegador.find_elements(By.CLASS_NAME, "Card-sc-yvvqkp-0")
        if not cards:
            break

        for card in cards:
            if coletados >= limite:
                break

            try:
                nome = card.find_element(By.CLASS_NAME, "htgicU").text
            except:
                nome = "Nome não encontrado"

            print(f"Nome capturado: '{nome}'")

            if filtro and normalizar(filtro) not in normalizar(nome):
                print(f"Filtro '{filtro}' não encontrado em '{nome}'")
                continue

            if nome in vistos:
                continue
            vistos.add(nome)

            try:
                preco_texto = card.find_element(By.CLASS_NAME, "PriceValue-sc-20azeh-4").text
                preco_num = float(preco_texto.replace("R$", "").replace(",", ".").strip())
            except:
                preco_texto = "Sem preço"
                preco_num = None

            desconto = "Sem desconto"
            preco_antigo = None
            qnt_desconto = None
            desconto_num = 0

            try:
                desconto = card.find_element(By.CLASS_NAME, "PercentSealLabel-sc-1cty9z3-4").text
                preco_antigo_texto = card.find_element(By.CLASS_NAME, "LineThroughValue-sc-1cty9z3-1").text

                preco_antigo_num = float(preco_antigo_texto.replace("R$", "").replace(",", ".").strip())
                qnt_desconto = round(preco_antigo_num - preco_num, 2)

                desconto_num = int(desconto.replace("-", "").replace("%", "").strip())
                preco_antigo = preco_antigo_texto
            except:
                pass

            # Aplica filtros
            if desconto_num < filtro_desconto:
                # Não atende filtro de desconto
                continue

            if filtro_preco is not None and preco_num is not None:
                # Filtra preço máximo (se filtro_preco for 0 ou None, ignora)
                if preco_num > filtro_preco:
                    continue

            produtos.append({
                "nome": nome,
                "preco": preco_texto,
                "desconto": desconto,
                "preco_antigo": preco_antigo,
                "qnt_desconto": qnt_desconto
            })

            coletados += 1
            print(f"Coletados: {coletados} - {nome} - {preco_texto} - {desconto}")

        pagina += 1
        print(f"Indo para página {pagina}")

    navegador.quit()
    return produtos


def salvar_csv(produtos, nome_arquivo="produtos.csv"):
    with open(nome_arquivo, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Nome", "Preço", "Desconto", "Preço Antigo", "Valor do Desconto"])
        for p in produtos:
            writer.writerow([
                p["nome"],
                p["preco"],
                p["desconto"],
                p["preco_antigo"] if p["preco_antigo"] else "",
                p["qnt_desconto"] if p["qnt_desconto"] else ""
            ])
    print(f"Arquivo '{nome_arquivo}' salvo com sucesso!")


if __name__ == "__main__":
    palavra_chave = input("Digite o item que deseja escolher (ou deixe vazio para todos): ").strip()
    desconto_desejavel = input("Desconto mínimo (%) (ou deixe vazio para 0): ").strip()
    preco_maximo = input("Preço máximo desejado (ou deixe vazio para sem limite): ").strip()

    filtro_desconto = int(desconto_desejavel) if desconto_desejavel.isdigit() else 0
    filtro_preco = float(preco_maximo.replace(",", ".")) if preco_maximo else None

    resultado = raspagem(
        limite=10,
        filtro=palavra_chave if palavra_chave else None,
        filtro_desconto=filtro_desconto,
        filtro_preco=filtro_preco
    )

    for p in resultado:
        print(f'Nome: {p["nome"]}')
        print(f'Preço: {p["preco"]}')
        print(f'Desconto: {p["desconto"]}')
        print(f'Preço antigo: {p["preco_antigo"]}')
        print(f'Valor do desconto: {p["qnt_desconto"]}')
        print("-" * 50)

    salvar_csv(resultado)
