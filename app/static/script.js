const produtosContainer = document.getElementById('produtosContainer');
const verMaisBtn = document.getElementById('verMais');
let todosOsProdutos = [];
let produtosVisiveis = 0;
const quantidadePorClique = 8;

// --- LÓGICA DE RASPAGEM E FILTRO ---
async function iniciarRaspagem(mercado) {
    produtosContainer.innerHTML = `<p class="aviso-carregando">Buscando novas ofertas no ${mercado}... Isso pode levar até um minuto, por favor aguarde.</p>`;
    verMaisBtn.style.display = 'none';
    try {
        const response = await fetch(`/api/raspar/${mercado}`, { method: 'POST' });
        const result = await response.json();
        if (!response.ok) throw new Error(result.message);
        
        console.log(result.message);
        filtrarPorMercado(mercado);
    } catch (error) {
        console.error("Erro ao iniciar raspagem:", error);
        produtosContainer.innerHTML = `<p class="aviso-vazio">Ocorreu um erro ao buscar as ofertas de ${mercado}. Tente novamente. Detalhe: ${error.message}</p>`;
    }
}

function filtrarPorMercado(mercado) {
    carregarProdutos(mercado);
}

// --- LÓGICA DE CARREGAMENTO E EXIBIÇÃO DE PRODUTOS ---
async function carregarProdutos(mercado = null) {
    produtosContainer.innerHTML = `<p class="aviso-carregando">Carregando ofertas salvas...</p>`;
    verMaisBtn.style.display = 'none';
    try {
        let url = '/api/produtos';
        if (mercado) {
            url += `?mercado=${encodeURIComponent(mercado)}`;
        }
        const response = await fetch(url);
        todosOsProdutos = await response.json();
        produtosVisiveis = 0;
        produtosContainer.innerHTML = '';

        if (!todosOsProdutos.length) {
            produtosContainer.innerHTML = '<p class="aviso-vazio">Nenhuma oferta encontrada. Tente buscar em um dos mercados acima.</p>';
            return;
        }
        renderizarProdutos();
    } catch (error) {
        console.error("Erro ao carregar produtos:", error);
        produtosContainer.innerHTML = '<p class="aviso-vazio">Erro ao carregar as ofertas.</p>';
    }
}

function renderizarProdutos() {
    const proximoLote = todosOsProdutos.slice(produtosVisiveis, produtosVisiveis + quantidadePorClique);
    proximoLote.forEach(produto => {
        produtosContainer.insertAdjacentHTML('beforeend', criarCardProduto(produto));
    });
    produtosVisiveis += proximoLote.length;
    verMaisBtn.style.display = produtosVisiveis >= todosOsProdutos.length ? 'none' : 'inline-block';
}

function criarCardProduto(produto) {
    const nome = produto.nome || 'Produto Sem Nome';
    const preco = produto.preco || '0.00';
    const desconto = produto.desconto || '0% OFF';
    const preco_antigo = produto.preco_antigo || '';
    const mercado = produto.mercado || 'Mercado Local';
    const imagemUrl = produto.imagem || '/static/imagens/placeholder.png';
    const url_produto = produto.UrlProduto || '#';

    return `
        <div class="produto-card">
            <span class="desconto-tag-produto">${desconto}</span>
            <img src="${imagemUrl}" alt="${nome}" class="produto-imagem" />
            <div class="produto-info">
                <span class="produto-mercado">${mercado}</span>
                <span class="produto-nome">${nome}</span>
                <span class="produto-preco_antigo">${preco_antigo}</span>
                <span class="produto-preco">${preco}</span>
            </div>
            <button class="produto-btn" onclick="window.open('${url_produto}', '_blank')">Ver Oferta</button>
        </div>
    `;
}

verMaisBtn.addEventListener('click', renderizarProdutos);
document.addEventListener('DOMContentLoaded', () => carregarProdutos());