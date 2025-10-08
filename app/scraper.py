from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Funções importadas do nosso novo arquivo de banco de dados
from database import init_db, salvar_produtos


def parse_card(card, vistos):
    """Extrai informações de um card de produto."""
    try:
        nome = card.find_element(By.CLASS_NAME, "htgicU").text
        if nome in vistos:
            return None
        vistos.add(nome)
    except:
        return None

    preco_texto, preco_num = "Sem preço", None
    try:
        preco_texto = card.find_element(By.CLASS_NAME, "PriceValue-sc-20azeh-4").text
        preco_num = float(preco_texto.replace("R$", "").replace(",", ".").strip())
    except:
        pass

    desconto, preco_antigo, qnt_desconto = "Sem desconto", None, 0
    try:
        desconto_texto = card.find_element(By.CLASS_NAME, "PercentSealLabel-sc-1cty9z3-4").text
        preco_antigo_texto = card.find_element(By.CLASS_NAME, "LineThroughValue-sc-1cty9z3-1").text
        preco_antigo_num = float(preco_antigo_texto.replace("R$", "").replace(",", ".").strip())
        qnt_desconto = round(preco_antigo_num - preco_num, 2)
        preco_antigo = preco_antigo_texto
        desconto = desconto_texto
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
    """
    Executa a raspagem no site e retorna uma lista de dicionários,
    cada um representando um produto.
    """
    print("Iniciando raspagem...")
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
        print(f"Buscando página: {pagina}...")
        navegador.get(url)
        try:
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "Card-sc-yvvqkp-0")))
        except Exception as e:
            print(f"Não foi possível carregar a página {pagina}. Erro: {e}")
            break

        cards = navegador.find_elements(By.CLASS_NAME, "Card-sc-yvvqkp-0")
        if not cards:
            print("Nenhum card de produto encontrado. Terminando.")
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
    print(f"{len(produtos)} produtos foram coletados com sucesso.")
    return produtos


# --- Bloco de Execução Principal ---
if __name__ == "__main__":
    # 1. Garante que o banco de dados e a tabela existam antes de tudo.
    init_db()

    # 2. Executa a raspagem para obter a lista de produtos.
    lista_de_produtos = raspagem()

    # 3. Se a lista não estiver vazia, manda salvar no banco de dados.
    if lista_de_produtos:
        salvar_produtos(lista_de_produtos)
    else:
        print("Nenhum produto foi coletado para salvar.")