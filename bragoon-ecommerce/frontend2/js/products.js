// ===========================
// PRODUTOS GLOBAIS
// ===========================

let currentPage = 1;
let totalPages = 1;
let allProducts = [];
let filterOptionsCache = null; // Cache para filtros

// Enable debug mode in console
console.clear();
console.log('%c🎮 BRAGOON Store - Products Page Initialized', 'color: #00aa00; font-size: 16px; font-weight: bold;');
console.log('%cDebug mode ON - Check console for filter cascade logs', 'color: #0088ff;');

// Detectar tentativas de reload não intencional
window.addEventListener('beforeunload', (e) => {
    console.warn('⚠️ Página está tentando recarregar!');
    if (e.returnValue) {
        console.error('🚨 ALERTA: Reload não intencional detectado!');
    }
});

document.addEventListener('DOMContentLoaded', async () => {
    console.log('%c🔄 [INIT] Página de Produtos - Iniciando carregamento...', 'color: #0088ff; font-weight: bold;');
    
    try {
        console.log('%c[STEP 1] Carregando opções de filtros...', 'color: #ff8800;');
        const filterResult = await loadFilterOptions();
        
        if (!filterResult || !filterResult.success) {
            console.warn('%c⚠️ [WARNING] Filtros não carregaram completamente, continuando mesmo assim...', 'color: #ffaa00;');
        } else {
            console.log('%c✅ [OK] Filtros carregados com sucesso', 'color: #00aa00;');
        }
        
        console.log('%c[STEP 2] Carregando produtos iniciais...', 'color: #ff8800;');
        await loadProducts();
        console.log('%c✅ [COMPLETE] Página de Produtos carregada com sucesso!', 'color: #00aa00; font-weight: bold;');
    } catch (error) {
        console.error('%c❌ [ERROR] Erro ao inicializar página de produtos:', 'color: #ff0000;', error);
    }
});

// ===========================
// LOAD FILTER OPTIONS
// ===========================

async function loadFilterOptions() {
    try {
        console.log('🔄 Carregando opções de filtro...');
        const result = await getFilterOptions();

        console.log('✅ Filtros recebidos:', result);

        if (result.success && result.data) {
            const data = result.data;
            filterOptionsCache = data; // Armazenar em cache global

            // Preencher categoria (menu)
            const menuSelect = document.getElementById('menu-select');
            if (menuSelect && data.menus) {
                console.log('📂 Menus disponíveis:', data.menus);
                menuSelect.innerHTML = '<option value="">-- Selecione Menu --</option>';
                data.menus.forEach(menu => {
                    const option = document.createElement('option');
                    option.value = menu;
                    option.textContent = menu;
                    menuSelect.appendChild(option);
                });
                // Adicionar listener para resetar filtros menores quando menu muda
                menuSelect.addEventListener('change', () => {
                    console.log('🔄 Menu mudou para:', menuSelect.value);
                    // Reset subordinados
                    const typeSelect = document.getElementById('type-select');
                    const filterSelect = document.getElementById('filter-select');
                    const subfilterSelect = document.getElementById('subfilter-select');
                    if (typeSelect) typeSelect.value = '';
                    if (filterSelect) filterSelect.value = '';
                    if (subfilterSelect) subfilterSelect.value = '';
                    // Popular tipos
                    updateTypeSelect();
                    // Depois aplica filtros
                    applyFilters();
                });
            }

            // Preencher loja (store)
            const storeSelect = document.getElementById('store-select');
            if (storeSelect && data.stores) {
                console.log('🏪 Lojas disponíveis:', data.stores);
                storeSelect.innerHTML = '<option value="">-- Todas as Lojas --</option>';
                data.stores.forEach(store => {
                    const option = document.createElement('option');
                    option.value = store;
                    option.textContent = store;
                    storeSelect.appendChild(option);
                });
            }
            console.log('✅ Todos os listeners iniciais configurados');
            return { success: true, data };
        } else {
            console.warn('⚠️ Formato de resposta inesperado:', result);
            return { success: false };
        }
    } catch (error) {
        console.error('❌ Erro ao carregar opções de filtro:', error);
        return { success: false, error: error.message };
    }
}

// ===========================
// LOAD PRODUCTS
// ===========================

async function loadProducts() {
    const container = document.getElementById('products-grid');
    
    if (!container) {
        console.error('❌ [ERROR] Elemento #products-grid não encontrado no DOM!');
        return;
    }
    
    container.innerHTML = '<p class="loading"><div class="spinner"></div>Carregando produtos...</p>';

    const params = {
        search: document.getElementById('search')?.value || '',
        store: document.getElementById('store-select')?.value || '',
        menu: document.getElementById('menu-select')?.value || '',
        type: document.getElementById('type-select')?.value || '',
        filter: document.getElementById('filter-select')?.value || '',
        subfilter: document.getElementById('subfilter-select')?.value || '',
        sort: document.getElementById('sort')?.value || 'price_asc',
        page: currentPage,
        limit: 52
    };

    console.log('📋 Parâmetros de busca:', params);

    try {
        const result = await searchProducts(params);

        console.log('✅ Resultado recebido:', result);
        console.log('📊 Dados:', result.data);

        if (result.success && result.data) {
            const data = result.data;
            allProducts = data.products || [];
            
            console.log('✨ Produtos carregados:', allProducts.length);
            
            if (allProducts.length === 0) {
                console.warn('⚠️ Nenhum produto retornado pela API');
                container.innerHTML = '<p class="loading">Nenhum produto encontrado.</p>';
            } else {
                displayProducts(allProducts);

                // Atualizar paginação
                if (data.pagination) {
                    totalPages = data.pagination.total_pages || 1;
                    console.log('📄 Total de páginas:', totalPages);
                    updatePagination();
                } else if (data.total_pages) {
                    totalPages = data.total_pages;
                    console.log('📄 Total de páginas (alt):', totalPages);
                    updatePagination();
                } else {
                    console.log('⚠️ Informações de paginação não encontradas na resposta');
                }
            }
        } else {
            console.error('❌ Erro na resposta:', result.error);
            container.innerHTML = `<p class="loading">Nenhum produto encontrado. ${result.error ? '(' + result.error + ')' : ''}</p>`;
        }
    } catch (error) {
        console.error('💥 Erro ao carregar produtos:', error);
        container.innerHTML = '<p class="loading">Erro ao carregar produtos. Verifique a conexão com o servidor.</p>';
    }
}

// ===========================
// DISPLAY PRODUCTS
// ===========================

function displayProducts(products) {
    const container = document.getElementById('products-grid');
    container.innerHTML = '';

    if (products.length === 0) {
        container.innerHTML = '<p class="loading">Nenhum produto encontrado com os filtros selecionados.</p>';
        return;
    }

    products.forEach(product => {
        const productCard = createProductCard(product);
        container.appendChild(productCard);
    });
}

function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';

    const isUnavailable = parseFloat(product.price) === 0 || product.price === "0,00" || parseFloat(product.price) < 0;
    
    if (isUnavailable) {
        card.classList.add('unavailable');
    }

    const imageUrl = product.image_url || product.image || 'https://via.placeholder.com/200x200?text=Sem+Imagem';
    
    card.innerHTML = `
        <img src="${imageUrl}" alt="${product.name}" class="product-image" onerror="this.src='https://via.placeholder.com/200x200?text=Sem+Imagem'" style="cursor: pointer;" onclick="window.location.href='produto-detalhes.html?id=${product.product_ID}'">
        <div class="product-info">
            <h3 class="product-name" style="cursor: pointer;" onclick="window.location.href='produto-detalhes.html?id=${product.product_ID}'">${truncateText(product.name, 60)}</h3>
            <span class="product-store">${product.store || 'Loja'}</span>
            ${isUnavailable ? '<span class="unavailable-badge">INDISPONÍVEL</span>' : ''}
            <div class="product-price ${isUnavailable ? 'unavailable' : ''}">
                ${isUnavailable ? 'Indisponível' : formatPrice(product.price)}
            </div>
            <div class="product-actions">
                <a 
                    href="produto-detalhes.html?id=${product.product_ID}"
                    class="btn btn-primary product-button" 
                    style="text-decoration: none; display: inline-block;"
                >
                    📋 Ver Detalhes
                </a>
                <button 
                    class="btn btn-secondary product-button add-to-cart-btn"
                    onclick="addProductToCart(${JSON.stringify(product).replace(/"/g, '&quot;')})"
                    ${isUnavailable ? 'disabled' : ''}
                >
                    🛒 Adicionar
                </button>
            </div>
        </div>
    `;

    return card;
}

function addProductToCart(product) {
    const isAdded = addToCart(product);
    
    if (isAdded) {
        // Atualizar contagem do carrinho (aguardar para garantir que sincronizou)
        setTimeout(() => {
            updateCartCount();
        }, 300);
        
        // Mostrar notificação personalizada
        if (typeof showNotification === 'function') {
            showNotification(
                '✅ Adicionado ao Carrinho',
                `"${truncateText(product.name, 40)}" foi adicionado!`,
                'success',
                3000
            );
        } else {
            // Fallback para o modal se a notificação não estiver disponível
            showCartModal(product.name);
        }
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
    alert('Página de carrinho em desenvolvimento!');
}

// ===========================
// FILTERS
// ===========================

/**
 * Reseta e atualiza filtros quando tipo muda
 */
function handleTypeChange() {
    console.log('🏷️ Type mudou para:', document.getElementById('type-select').value);
    try {
        // Reset subordinados
        const filterSelect = document.getElementById('filter-select');
        const subfilterSelect = document.getElementById('subfilter-select');
        if (filterSelect) filterSelect.value = '';
        if (subfilterSelect) subfilterSelect.value = '';
        
        // Popular filtros
        updateFilterSelect();
        
        // Depois aplica filtros
        applyFilters();
    } catch (error) {
        console.error('❌ Erro em handleTypeChange:', error);
    }
}

/**
 * Reseta e atualiza subfiltros quando filtro muda
 */
function handleFilterChange() {
    console.log('🎯 Filter mudou para:', document.getElementById('filter-select').value);
    try {
        // Reset subfiltro
        const subfilterSelect = document.getElementById('subfilter-select');
        if (subfilterSelect) subfilterSelect.value = '';
        
        // Popular subfiltros
        updateSubfilterSelect();
        
        // Depois aplica filtros
        applyFilters();
    } catch (error) {
        console.error('❌ Erro em handleFilterChange:', error);
    }
}

/**
 * Atualiza o select de tipo baseado no menu selecionado
 */
function updateTypeSelect() {
    const menuValue = document.getElementById('menu-select')?.value;
    const typeSelect = document.getElementById('type-select');

    if (!typeSelect) {
        console.log('❌ typeSelect não encontrado');
        return;
    }

    // Limpar tipos anteriores
    typeSelect.innerHTML = '<option value="">-- Selecione Tipo --</option>';

    if (!menuValue) {
        console.log('⚠️ Nenhum menu selecionado');
        return;
    }

    console.log('🔧 Atualizando tipos para menu:', menuValue);

    // Se temos cache, usar ele
    if (filterOptionsCache && filterOptionsCache.type && filterOptionsCache.type[menuValue]) {
        console.log('💾 Tipos disponíveis:', filterOptionsCache.type[menuValue]);
        const types = filterOptionsCache.type[menuValue];
        
        types.forEach(type => {
            const option = document.createElement('option');
            option.value = type;
            option.textContent = type;
            typeSelect.appendChild(option);
        });
        console.log('✅ Tipos carregados');
    } else {
        console.log('❌ Tipo não encontrado para menu:', menuValue);
    }
}

/**
 * Atualiza o select de filtro baseado no menu e type selecionados
 */
function updateFilterSelect() {
    const menuValue = document.getElementById('menu-select')?.value;
    const typeValue = document.getElementById('type-select')?.value;
    const filterSelect = document.getElementById('filter-select');

    if (!filterSelect) {
        console.log('❌ filterSelect não encontrado');
        return;
    }

    filterSelect.innerHTML = '<option value="">-- Selecione Filtro --</option>';

    if (!menuValue || !typeValue) {
        console.log('⚠️ Menu ou Type não selecionados');
        return;
    }

    // Usar underscore para a chave
    const key = `${menuValue}_${typeValue}`;
    console.log('🔧 Procurando filtros com chave:', key);
    console.log('📊 Chaves disponíveis:', filterOptionsCache?.filter ? Object.keys(filterOptionsCache.filter).slice(0, 5) : 'Nenhuma');

    // Se temos cache, usar ele
    if (filterOptionsCache && filterOptionsCache.filter && filterOptionsCache.filter[key]) {
        console.log('💾 Filtros encontrados:', filterOptionsCache.filter[key]);
        const filters = filterOptionsCache.filter[key];
        
        filters.forEach(filter => {
            const option = document.createElement('option');
            option.value = filter;
            option.textContent = filter;
            filterSelect.appendChild(option);
        });
        console.log('✅ Filtros carregados');
    } else {
        console.log('❌ Nenhum filtro encontrado para:', key);
    }
}

/**
 * Atualiza o select de subfiltro baseado em menu, type e filter
 */
function updateSubfilterSelect() {
    const menuValue = document.getElementById('menu-select')?.value;
    const typeValue = document.getElementById('type-select')?.value;
    const filterValue = document.getElementById('filter-select')?.value;
    const subfilterSelect = document.getElementById('subfilter-select');
    const subfilterGroup = document.getElementById('subfilter-group');

    if (!subfilterSelect) {
        console.log('❌ subfilterSelect não encontrado');
        return;
    }

    subfilterSelect.innerHTML = '<option value="">-- Selecione Subfiltro --</option>';

    if (!menuValue || !typeValue || !filterValue) {
        console.log('⚠️ Menu, Type ou Filter não selecionados');
        // Esconder grupo se não há dados
        if (subfilterGroup) subfilterGroup.style.display = 'none';
        return;
    }

    // Usar underscore para a chave
    const key = `${menuValue}_${typeValue}_${filterValue}`;
    console.log('🔧 Procurando subfiltros com chave:', key);

    // Se temos cache, usar ele
    if (filterOptionsCache && filterOptionsCache.subfilter && filterOptionsCache.subfilter[key]) {
        const subfilters = filterOptionsCache.subfilter[key];
        console.log('💾 Subfiltros encontrados:', subfilters);
        
        // Se array está vazio, esconder
        if (!subfilters || subfilters.length === 0) {
            console.log('ℹ️ Nenhum subfiltro disponível para esta combinação');
            if (subfilterGroup) subfilterGroup.style.display = 'none';
            return;
        }

        // Se tem dados, mostrar e popular
        if (subfilterGroup) subfilterGroup.style.display = 'block';
        
        subfilters.forEach(subfilter => {
            const option = document.createElement('option');
            option.value = subfilter;
            option.textContent = subfilter;
            subfilterSelect.appendChild(option);
        });
        console.log('✅ Subfiltros carregados e visíveis');
    } else {
        console.log('❌ Nenhum subfiltro encontrado para:', key);
        // Esconder grupo se não há dados
        if (subfilterGroup) subfilterGroup.style.display = 'none';
    }
}

async function applyFilters() {
    console.log('📌 Aplicando filtros e carregando produtos...');
    currentPage = 1; // Reset para primeira página

    // Atualizar preço máximo (se existir slider)
    const priceRange = document.getElementById('price-range');
    const priceValue = document.getElementById('price-value');
    if (priceRange && priceValue) {
        priceValue.textContent = parseInt(priceRange.value).toLocaleString('pt-BR');
    }

    await loadProducts();
}

function resetFilters() {
    console.log('🔄 Resetando todos os filtros...');
    document.getElementById('search').value = '';
    document.getElementById('sort').value = 'price_asc';
    document.getElementById('menu-select').value = '';
    document.getElementById('type-select').value = '';
    document.getElementById('type-select').innerHTML = '<option value="">-- Selecione Tipo --</option>';
    document.getElementById('store-select').value = '';
    document.getElementById('filter-select').value = '';
    document.getElementById('filter-select').innerHTML = '<option value="">-- Selecione Filtro --</option>';
    document.getElementById('subfilter-select').value = '';
    document.getElementById('subfilter-select').innerHTML = '<option value="">-- Selecione Subfiltro --</option>';
    document.getElementById('price-range').value = '10000';
    currentPage = 1;

    applyFilters();
}

// ===========================
// PAGINATION
// ===========================

function updatePagination() {
    const paginationContainer = document.getElementById('pagination');
    paginationContainer.innerHTML = '';

    // Botão "Anterior"
    if (currentPage > 1) {
        const prevBtn = document.createElement('button');
        prevBtn.textContent = '← Anterior';
        prevBtn.onclick = () => {
            currentPage--;
            loadProducts();
            window.scrollTo(0, 0);
        };
        paginationContainer.appendChild(prevBtn);
    }

    // Números de página
    const maxPagesToShow = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxPagesToShow / 2));
    let endPage = Math.min(totalPages, startPage + maxPagesToShow - 1);

    if (endPage - startPage < maxPagesToShow - 1) {
        startPage = Math.max(1, endPage - maxPagesToShow + 1);
    }

    // Botão primeira página
    if (startPage > 1) {
        const firstBtn = document.createElement('button');
        firstBtn.textContent = '1';
        firstBtn.onclick = () => {
            currentPage = 1;
            loadProducts();
            window.scrollTo(0, 0);
        };
        paginationContainer.appendChild(firstBtn);

        if (startPage > 2) {
            const dots = document.createElement('span');
            dots.textContent = '...';
            dots.style.padding = '0.5rem';
            paginationContainer.appendChild(dots);
        }
    }

    // Página atual e vizinhas
    for (let i = startPage; i <= endPage; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.textContent = i;
        pageBtn.onclick = () => {
            currentPage = i;
            loadProducts();
            window.scrollTo(0, 0);
        };

        if (i === currentPage) {
            pageBtn.classList.add('active');
        }

        paginationContainer.appendChild(pageBtn);
    }

    // Botão última página
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            const dots = document.createElement('span');
            dots.textContent = '...';
            dots.style.padding = '0.5rem';
            paginationContainer.appendChild(dots);
        }

        const lastBtn = document.createElement('button');
        lastBtn.textContent = totalPages;
        lastBtn.onclick = () => {
            currentPage = totalPages;
            loadProducts();
            window.scrollTo(0, 0);
        };
        paginationContainer.appendChild(lastBtn);
    }

    // Botão "Próximo"
    if (currentPage < totalPages) {
        const nextBtn = document.createElement('button');
        nextBtn.textContent = 'Próximo →';
        nextBtn.onclick = () => {
            currentPage++;
            loadProducts();
            window.scrollTo(0, 0);
        };
        paginationContainer.appendChild(nextBtn);
    }

    // Informação de páginas
    const info = document.createElement('span');
    info.textContent = `Página ${currentPage} de ${totalPages}`;
    info.style.padding = '0.5rem 1rem';
    info.style.color = '#666';
    paginationContainer.appendChild(info);
}

// Fechar modal ao clicar fora
document.addEventListener('click', (e) => {
    const modal = document.getElementById('cart-modal');
    if (modal && e.target === modal) {
        closeCartModal();
    }
});
