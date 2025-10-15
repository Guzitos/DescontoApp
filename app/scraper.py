from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

MERCADOS_CONFIG = {
    "Pão de Açúcar": {
        "url_base": "https://www.paodeacucar.com/especial/ofertasdodia-pao2023?page={pagina}",
        "card_class": "Card-sc-yvvqkp-0",
        "nome_class": "htgicU",
        "preco_class": "PriceValue-sc-20azeh-4",
        "desconto_class": "PercentSealLabel-sc-1cty9z3-4",
        "preco_antigo_class": "LineThroughValue-sc-1cty9z3-1",
        "link_selector": "a.Link-sc-j02w35-0",
        "img_selector": "a img"
    } ,
    "Carrefour": {
        "url_base": "https://www.paodeacucar.com/especial/ofertasdodia-pao2023?page={pagina}",
        "card_class": "Card-sc-yvvqkp-0",
        "nome_class": "htgicU",
        "preco_class": "PriceValue-sc-20azeh-4",
        "desconto_class": "PercentSealLabel-sc-1cty9z3-4",
        "preco_antigo_class": "LineThroughValue-sc-1cty9z3-1",
        "link_selector": "a.Link-sc-j02w35-0",
        "img_selector": "a img"
    },
    # Adicione aqui as configurações para outros mercados (Carrefour, Extra, etc.)
    # "Carrefour": { ... }
}


def parse_card(card, vistos, config, nome_mercado):
    try:
        nome = card.find_element(By.CLASS_NAME, config["nome_class"]).text
        if nome in vistos: return None
        vistos.add(nome)
    except:
        return None

    preco_texto, preco_num = "Sem preço", None
    try:
        preco_texto = card.find_element(By.CLASS_NAME, config["preco_class"]).text
        preco_num = float(preco_texto.replace("R$", "").replace(",", ".").strip())
    except:
        pass

    desconto, preco_antigo, qnt_desconto = "Sem desconto", None, 0
    try:
        desconto = card.find_element(By.CLASS_NAME, config["desconto_class"]).text
        preco_antigo_texto = card.find_element(By.CLASS_NAME, config["preco_antigo_class"]).text
        preco_antigo_num = float(preco_antigo_texto.replace("R$", "").replace(",", ".").strip())
        qnt_desconto = round(preco_antigo_num - preco_num, 2)
        preco_antigo = preco_antigo_texto
    except:
        pass

    url_produto = "#"
    try:
        url_produto = card.find_element(By.CSS_SELECTOR, config["link_selector"]).get_attribute("href")
    except:
        pass

    imagem = "/static/imagens/placeholder.png"
    try:
        imagem = card.find_element(By.CSS_SELECTOR, config["img_selector"]).get_attribute("src")
    except:
        pass

    return {
        "nome": nome, "preco": preco_texto, "desconto": desconto,
        "preco_antigo": preco_antigo, "qnt_desconto": qnt_desconto,
        "imagem": imagem, "UrlProduto": url_produto, "mercado": nome_mercado
    }


def raspagem(nome_mercado, limite=30):
    if nome_mercado not in MERCADOS_CONFIG:
        print(f"Erro: Mercado '{nome_mercado}' não configurado.")
        return []

    config = MERCADOS_CONFIG[nome_mercado]
    print(f"Iniciando raspagem para: {nome_mercado}...")

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    navegador = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(navegador, 10)

    produtos, vistos, pagina = [], set(), 1

    while len(produtos) < limite and pagina <= 5:
        url = config["url_base"].format(pagina=pagina)
        navegador.get(url)
        try:
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, config["card_class"])))
            cards = navegador.find_elements(By.CLASS_NAME, config["card_class"])
            if not cards: break
            for card in cards:
                if len(produtos) >= limite: break
                produto = parse_card(card, vistos, config, nome_mercado)
                if produto: produtos.append(produto)
            pagina += 1
        except Exception as e:
            print(f"Erro na página {pagina} do {nome_mercado}: {e}")
            break

    navegador.quit()
    print(f"{len(produtos)} produtos coletados de {nome_mercado}.")
    return produtos