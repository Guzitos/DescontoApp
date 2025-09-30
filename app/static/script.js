// ==========================================================
// LÓGICA DE ENDEREÇO (CEP)
// ==========================================================

function getQueryParam(param) {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(param);
}

function buscarEndereco(cep) {
  fetch(`https://viacep.com.br/ws/${cep}/json/`)
    .then(res => res.json())
    .then(data => {
      const enderecoSpan = document.getElementById('enderecoCompleto');
      const inputEnderecoDiv = document.getElementById('inputEndereco');

      if (data.erro) {
        enderecoSpan.textContent = 'Endereço não encontrado';
        inputEnderecoDiv.style.display = 'block';
        return;
      }

      const endereco = `${data.logradouro}, ${data.bairro} - ${data.localidade}/${data.uf}`;
      enderecoSpan.textContent = endereco;
      enderecoSpan.classList.add('endereco-centralizado');
      inputEnderecoDiv.style.display = 'none';
    })
    .catch(() => {
      document.getElementById('enderecoCompleto').textContent = 'Erro ao buscar endereço';
    });
}

function enviarCep() {
  const cepInput = document.getElementById('cepInput');
  const cep = cepInput.value.replace(/\D/g, '').trim();

  if (cep.length === 8) {
    buscarEndereco(cep);
  } else {
    alert("Por favor, digite um CEP válido com 8 dígitos.");
  }
}

// Permitir Enter
document.getElementById("cepInput").addEventListener("keypress", function(event) {
  if (event.key === "Enter") {
    event.preventDefault();
    enviarCep();
  }
});

// Checagem inicial
const cepUrl = getQueryParam('cep');
if (cepUrl) {
  buscarEndereco(cepUrl);
} else {
  document.getElementById('enderecoCompleto').textContent = 'Digite seu CEP';
}

// Ícone de lupa
document.querySelector('.icone-lupa').addEventListener('click', enviarCep);

// ==========================================================
// LÓGICA DE PRODUTOS (JSON LOCAL + RENDERIZAÇÃO)
// ==========================================================

const produtosContainer = document.getElementById('produtosContainer');
const verMaisBtn = document.getElementById('verMais');

let todosOsProdutos = [];
let produtosVisiveis = 0;
const quantidadePorClique = 4;

// Cria o HTML de um card de produto
function criarCardProduto(produto) {
    const nome = produto.nome || 'Produto Sem Nome';
    const preco = produto.preco || '0.00';
    const desconto = produto.desconto || '0';
    const preco_antigo = produto.preco_antigo || 'sem desconto';
    const mercado = produto.mercado || 'Mercado Local';
    const imagemUrl = produto.imagem || '/static/imagens/placeholder.png';
    const url_produto = produto.UrlProduto || '#';

    return `
        <div class="produto-card">
            <span class="desconto-tag-produto">${desconto}% OFF</span>
            <img src="${imagemUrl}" alt="${nome}" class="produto-imagem" />
            <div class="produto-info">
                <span class="produto-nome">${nome}</span><br>
                <span class="produto-preco">R$ ${preco}</span><br>
                <span class="produto-preco_antigo">R$ ${preco_antigo}</span><br>
                <span class="produto-mercado">${mercado}</span>
            </div>
            <button class="produto-btn" onclick="window.open('${url_produto}', '_blank')">Ver Oferta</button>
        </div>
    `;
}

// Renderiza próximo lote de produtos
function renderizarProdutos() {
    const proximoLote = todosOsProdutos.slice(produtosVisiveis, produtosVisiveis + quantidadePorClique);
    proximoLote.forEach(produto => {
        produtosContainer.insertAdjacentHTML('beforeend', criarCardProduto(produto));
    });
    produtosVisiveis += proximoLote.length;
    verMaisBtn.style.display = produtosVisiveis >= todosOsProdutos.length ? 'none' : 'inline';
}

// Carrega produtos do JSON local
async function carregarProdutos() {
    try {
        produtosContainer.innerHTML = '<p class="aviso-carregando">Carregando ofertas...</p>';
        verMaisBtn.style.display = 'none';

        const response = await fetch('/produtos.json');
        todosOsProdutos = await response.json();
        produtosVisiveis = 0;

        produtosContainer.innerHTML = '';
        if (!todosOsProdutos.length) {
            produtosContainer.innerHTML = '<p class="aviso-vazio">Nenhuma oferta encontrada.</p>';
            return;
        }

        renderizarProdutos();
    } catch (error) {
        console.error("Erro ao carregar produtos:", error);
        produtosContainer.innerHTML = '<p class="aviso-vazio">Erro ao carregar as ofertas.</p>';
    }
}

// Evento do botão "Ver Mais"
verMaisBtn.addEventListener('click', renderizarProdutos);

// Inicializa
carregarProdutos();
