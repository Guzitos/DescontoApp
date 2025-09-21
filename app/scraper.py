# app/scraper.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .utils import normalizar


def parse_card(card, filtro, filtro_desconto, filtro_preco, vistos):
    """Extrai informações de um card de produto"""
    try:
        nome = card.find_element(By.CLASS_NAME, "htgicU").text
    except:
        nome = "Nome não encontrado"

    if filtro and normalizar(filtro) not in normalizar(nome):
        return None
    if nome in vistos:
        return None
    vistos.add(nome)

    try:
        preco_texto = card.find_element(By.CLASS_NAME, "PriceValue-sc-20azeh-4").text
        preco_num = float(preco_texto.replace("R$", "").replace(",", ".").strip())
    except:
        preco_texto, preco_num = "Sem preço", None

    desconto, preco_antigo, qnt_desconto, desconto_num = "Sem desconto", None, None, 0
    try:
        desconto = card.find_element(By.CLASS_NAME, "PercentSealLabel-sc-1cty9z3-4").text
        preco_antigo_texto = card.find_element(By.CLASS_NAME, "LineThroughValue-sc-1cty9z3-1").text
        preco_antigo_num = float(preco_antigo_texto.replace("R$", "").replace(",", ".").strip())
        qnt_desconto = round(preco_antigo_num - preco_num, 2)
        desconto_num = int(desconto.replace("-", "").replace("%", "").strip())
        preco_antigo = preco_antigo_texto
    except:
        pass

    try:
        imagem = card.find_element(By.CLASS_NAME, "TPDLc").get_attribute("src")
    except:
        imagem = None

    if desconto_num < filtro_desconto:
        return None
    if filtro_preco and preco_num and preco_num > filtro_preco:
        return None

    return {
        "nome": nome,
        "preco": preco_texto,
        "desconto": desconto,
        "preco_antigo": preco_antigo,
        "qnt_desconto": qnt_desconto,
        "imagem": imagem
    }


def raspagem(limite=0, filtro=None, filtro_desconto=0, filtro_preco=None, verbose=False):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    navegador = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(navegador, 10)

    pagina, coletados = 1, 0
    produtos, vistos = [], set()

    while coletados < limite and pagina <= 10:
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

            produto = parse_card(card, filtro, filtro_desconto, filtro_preco, vistos)
            if produto:
                produtos.append(produto)
                coletados += 1
                if verbose:
                    print(f"{coletados}: {produto['nome']} - {produto['preco']} - {produto['desconto']}")

        pagina += 1

    navegador.quit()
    return produtos
