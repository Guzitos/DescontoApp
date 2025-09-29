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

      // Esconde input após sucesso
      inputEnderecoDiv.style.display = 'none';

      // **CHAMADA DE PRODUTOS RELACIONADA AO ENDEREÇO (OPCIONAL)**
      // Se você quiser que o CEP filtre os produtos, chame a função aqui:
      // carregarProdutos(cep);
    })
    .catch(() => {
      document.getElementById('enderecoCompleto').textContent = 'Erro ao buscar endereço';
    });
}

function enviarCep() {
  const cepInput = document.getElementById('cepInput');
  // Remove caracteres que não sejam números
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

// Adiciona o evento de clique na lupa
document.querySelector('.icone-lupa').addEventListener('click', enviarCep);


// ==========================================================
// LÓGICA DE PRODUTOS (API + RENDERIZAÇÃO)
// ==========================================================

const produtosContainer = document.getElementById('produtosContainer');
const verMaisBtn = document.getElementById('verMais');
const verOfertaBtn = document.getElementById('verMais');

let todosOsProdutos = []; // Armazena todos os produtos buscados da API
let produtosVisiveis = 0;
const quantidadePorClique = 4; // Quantos cards carregar por vez

/**
 * Cria a estrutura HTML de um único card de produto.
 * @param {Object} produto - O objeto do produto retornado pela raspagem.
 */
function criarCardProduto(produto) {
    // ATENÇÃO: As chaves (e.g., nome, preco, imagem_url) devem ser EXATAS
    // em relação ao que sua função 'raspagem' retorna.

    // Usa '||' (OR lógico) para fornecer valores padrão caso a chave não exista no objeto
    const nome = produto.nome || 'Produto Sem Nome';
    const preco = produto.preco || '0.00';
    const desconto = produto.desconto || '20';
    const mercado = produto.mercado || 'Mercado Local';
    const imagemUrl = produto.imagem || '/static/imagens/placeholder.png';
    const url_produto = produto.UrlProduto || '#';

    return `
        <div class="produto-card">
            <span class="desconto-tag-produto">
                ${desconto}% OFF
            </span>
             <img src="${imagemUrl}" alt="${nome}" class="produto-imagem" />

            <div class="produto-info">
                <span class="produto-nome">${nome}</span>
                <span class="produto-preco">R$ ${preco}</span>
                <span class="produto-mercado">${mercado}</span>
            </div>
            <button class="produto-btn" onclick="window.open('${url_produto}', '_blank')">Ver Oferta</button>
        </div>
    `;
}

/**
 * Renderiza o próximo lote de produtos na tela (lógica "Ver Mais").
 */
function renderizarProdutos() {
    const proximoLote = todosOsProdutos.slice(
        produtosVisiveis,
        produtosVisiveis + quantidadePorClique
    );

    proximoLote.forEach(produto => {
        // Insere o HTML criado no final do container
        produtosContainer.insertAdjacentHTML('beforeend', criarCardProduto(produto));
    });

    produtosVisiveis += proximoLote.length;

    // Lógica para esconder/mostrar o botão "Ver Mais"
    if (produtosVisiveis >= todosOsProdutos.length) {
        verMaisBtn.style.display = 'none';
    } else {
        verMaisBtn.style.display = 'inline';
    }
}


/**
 * Busca todos os produtos na API do Flask.
 */
async function carregarProdutos(cep = null) {
    // Você pode construir a URL de busca de forma mais complexa aqui (ex: adicionar CEP como filtro)
    const apiURL = `/produtos?limite=20`;

    try {
        produtosContainer.innerHTML = '<p class="aviso-carregando">Carregando ofertas...</p>'; // Feedback
        verMaisBtn.style.display = 'none';

        const response = await fetch(apiURL);
        const data = await response.json();

        // Salva os produtos e reseta a paginação
        todosOsProdutos = data.produtos || [];
        produtosVisiveis = 0;

        produtosContainer.innerHTML = ''; // Limpa o aviso de carregamento

        if (todosOsProdutos.length === 0) {
            produtosContainer.innerHTML = '<p class="aviso-vazio">Nenhuma oferta de produto encontrada no momento.</p>';
            return;
        }

        // Renderiza o primeiro lote
        renderizarProdutos();

    } catch (error) {
        console.error("Erro ao carregar produtos:", error);
        produtosContainer.innerHTML = '<p class="aviso-vazio">Erro ao carregar as ofertas. Verifique o console ou a API.</p>';
    }
}


// ==========================================================
// INICIALIZAÇÃO
// ==========================================================
const linkOferta =
// Adiciona evento de clique ao botão "Ver Mais"
verMaisBtn.addEventListener('click', renderizarProdutos);

// Inicia o carregamento dos produtos quando o script é executado
carregarProdutos();