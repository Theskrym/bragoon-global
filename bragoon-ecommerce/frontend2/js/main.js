// ===========================
// HOME PAGE MAIN SCRIPT
// ===========================

document.addEventListener('DOMContentLoaded', async () => {
    await loadFeaturedProducts();
});

// ===========================
// FEATURED PRODUCTS LOADING
// ===========================

async function loadFeaturedProducts() {
    const container = document.getElementById('featured-products');
    
    if (!container) return;

    container.innerHTML = '<p class="loading">Carregando produtos em destaque...</p>';

    try {
        const result = await searchProducts({
            page: 1,
            limit: 8,
            sort: 'price_asc'
        });

        if (result.success && result.data && result.data.products && result.data.products.length > 0) {
            displayFeaturedProducts(result.data.products);
        } else {
            container.innerHTML = '<p class="loading">Nenhum produto disponível no momento.</p>';
        }
    } catch (error) {
        console.error('Erro ao carregar produtos:', error);
        container.innerHTML = '<p class="loading">Erro ao carregar produtos.</p>';
    }
}

function displayFeaturedProducts(products) {
    const container = document.getElementById('featured-products');
    container.innerHTML = '';

    products.forEach(product => {
        const productCard = createProductCard(product);
        container.appendChild(productCard);
    });
}

function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';

    // Determinar ID do produto (fallback para múltiplos formatos)
    const productId = product.product_ID || product.id || product.product_id || product.productId;

    // Verificar se produto está indisponível
    const isUnavailable = parseFloat(product.price) === 0 || product.price === "0,00" || parseFloat(product.price) < 0;
    
    if (isUnavailable) {
        card.classList.add('unavailable');
    }

    const imageUrl = product.image_url || product.image || 'https://via.placeholder.com/200x200?text=Sem+Imagem';
    
    card.innerHTML = `
        <img src="${imageUrl}" alt="${product.name}" class="product-image" onerror="this.src='https://via.placeholder.com/200x200?text=Sem+Imagem'" style="cursor: pointer;" onclick="window.location.href='produto-detalhes.html?id=${productId}'">
        <div class="product-info">
            <h3 class="product-name" style="cursor: pointer;" onclick="window.location.href='produto-detalhes.html?id=${productId}'">${truncateText(product.name, 60)}</h3>
            <span class="product-store">${product.store || 'Loja'}</span>
            ${isUnavailable ? '<span class="unavailable-badge">INDISPONÍVEL</span>' : ''}
            <div class="product-price ${isUnavailable ? 'unavailable' : ''}">
                ${isUnavailable ? 'Indisponível' : formatPrice(product.price)}
            </div>
            <a 
                href="produto-detalhes.html?id=${productId}"
                class="btn btn-primary product-button" 
                style="text-decoration: none; display: inline-block;"
            >
                📋 Ver Detalhes
            </a>
        </div>
    `;

    return card;
}

function addProductToCart(product) {
    const isAdded = addToCart(product);
    
    if (isAdded) {
        showCartModal(product.name);
    }
}

function showCartModal(productName) {
    const modal = document.getElementById('cart-modal');
    if (modal) {
        const message = document.getElementById('modal-message');
        message.textContent = `"${productName}" foi adicionado ao carrinho!`;
        modal.style.display = 'flex';
    }
}

function closeCartModal() {
    const modal = document.getElementById('cart-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function viewCart() {
    // Redirect to cart page (será criada depois)
    alert('Página de carrinho em desenvolvimento!');
}

// Fechar modal ao clicar fora (overlay)
document.addEventListener('click', (e) => {
    const modal = document.getElementById('cart-modal');
    if (modal && e.target === modal) {
        closeCartModal();
    }
});
