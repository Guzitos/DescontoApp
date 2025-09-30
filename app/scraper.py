from flask import Flask, render_template, jsonify
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

# ------------------------
# Funções Selenium
# ------------------------

def parse_card(card, vistos=set()):
    try:
        nome = card.find_element(By.CLASS_NAME, "htgicU").text
    except:
        return None
    if nome in vistos:
        return None
    vistos.add(nome)

    preco_texto, preco_num = "Sem preço", None
    try:
        preco_texto = card.find_element(By.CLASS_NAME, "PriceValue-sc-20azeh-4").text
        preco_num = float(preco_texto.replace("R$", "").replace(",", ".").strip())
    except:
        pass

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

    url_produto = "#"
    try:
        link_element = card.find_element(By.CSS_SELECTOR, "a.Link-sc-j02w35-0")
        url_produto = link_element.get_attribute("href")
    except:
        pass

    imagem = "/static/imagens/placeholder.png"
    try:
        img_element = card.find_element(By.CSS_SELECTOR, "a img")
        imagem = img_element.get_attribute("src")
    except:
        pass

    return {
        "nome": nome,
        "preco": preco_texto,
        "desconto": desconto,
        "preco_antigo": preco_antigo,
        "qnt_desconto": qnt_desconto,
        "imagem": imagem,
        "UrlProduto": url_produto,
    }

def raspagem(limite=50):
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
            produto = parse_card(card, vistos)
            if produto:
                produtos.append(produto)
                coletados += 1
        pagina += 1

    navegador.quit()
    # Salva JSON
    with open("produtos.json", "w", encoding="utf-8") as f:
        json.dump(produtos, f, ensure_ascii=False, indent=2)

    return produtos

# ------------------------
# Rotas Flask
# ------------------------

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/produtos.json')
def produtos_json():
    try:
        with open("produtos.json", "r", encoding="utf-8") as f:
            produtos = json.load(f)
        if not produtos:  # Se estiver vazio, atualiza
            produtos = raspagem()
    except FileNotFoundError:
        produtos = raspagem()
    return jsonify(produtos)

# ------------------------
# Main
# ------------------------

if __name__ == "__main__":
    app.run(debug=True)
