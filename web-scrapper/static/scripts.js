document.addEventListener('DOMContentLoaded', async function() {
    // =============================================
    // Configuração Inicial
    // =============================================
    const initializeLayout = () => {
        const header = document.querySelector('header');
        const main = document.querySelector('main');
        if (header && main) {
            const headerHeight = header.offsetHeight;
            main.style.paddingTop = `${headerHeight}px`;
        }
    };

    // =============================================
    // Constantes e Variáveis Globais
    // =============================================
    const nvidiaGPUs = [
        "GT 210", "GT 220", "GT 240", "GTS 250", "GTX 260", "GTX 275", "GTX 280", "GTX 285", "GTX 295",
        "GT 430", "GT 440", "GTS 450", "GTX 460", "GTX 465", "GTX 470", "GTX 480",
        "GT 520", "GT 530", "GT 545", "GTS 550 Ti", "GTX 550 Ti", "GTX 560", "GTX 560 Ti", "GTX 570", "GTX 580", "GTX 590",
        "GT 610", "GT 620", "GT 630", "GT 640", "GTX 650", "GTX 650 Ti", "GTX 660", "GTX 660 Ti", "GTX 670", "GTX 680", "GTX 690",
        "GT 710", "GT 720", "GT 730", "GTX 740", "GTX 750", "GTX 750 Ti", "GTX 760", "GTX 760 Ti", "GTX 770", "GTX 780", "GTX 780 Ti", "GTX Titan", "GTX Titan Black", "GTX Titan Z",
        "GTX 950", "GTX 960", "GTX 970", "GTX 980", "GTX 980 Ti", "GTX Titan X",
        "GT 1010", "GT 1030", "GTX 1050", "GTX 1050 Ti", "GTX 1060 3GB", "GTX 1060 6GB", "GTX 1070", "GTX 1070 Ti", "GTX 1080", "GTX 1080 Ti", "GTX Titan X (Pascal)", "GTX Titan XP",
        "GTX 1650", "GTX 1650 Super", "GTX 1660", "GTX 1660 Super", "GTX 1660 Ti",
        "RTX 2060", "RTX 2060 Super", "RTX 2070", "RTX 2070 Super", "RTX 2080", "RTX 2080 Super", "RTX 2080 Ti", "RTX Titan",
        "RTX 3050", "RTX 3060", "RTX 3060 Ti", "RTX 3070", "RTX 3070 Ti", "RTX 3080", "RTX 3080 Ti", "RTX 3090", "RTX 3090 Ti",
        "RTX 4050", "RTX 4060", "RTX 4060 Ti", "RTX 4070", "RTX 4070 Ti", "RTX 4080", "RTX 4090", "RTX 5070", "RTX 5070 TI", "RTX 5080", "RTX 5090"
    ];

    const amdGPUs = [
        "RX 460", "RX 470", "RX 480",
        "RX 550", "RX 560", "RX 570", "RX 580", "RX 590",
        "RX Vega 56", "RX Vega 64", "RX Vega 64 Liquid Cooled",
        "RX 5300", "RX 5300 XT", "RX 5500", "RX 5500 XT", "RX 5600", "RX 5600 XT", "RX 5700", "RX 5700 XT",
        "RX 6400", "RX 6500 XT", "RX 6600", "RX 6600 XT", "RX 6700 XT", "RX 6800", "RX 6800 XT", "RX 6900 XT", "RX 6950 XT",
        "RX 7600", "RX 7700 XT", "RX 7800 XT","RX 7900 GRE", "RX 7900 XT", "RX 7900 XTX", "RX 9070", "RX 9070 XT"
    ];

    const intelGPUs = [
        "Arc A310", "Arc A380", "Arc A580", "Arc A750", "Arc A770",
        "Arc B570", "Arc B580", "Arc B580", "Arc B750", "Arc B770",
    ];

    let currentPage = 1;
    const itemsPerPage = 12;
    let priceAlerts = JSON.parse(localStorage.getItem('priceAlerts')) || [];

    // =============================================
    // Funções de UI
    // =============================================
    const showLoader = () => {
        const loader = document.getElementById('loading');
        if (loader) loader.style.display = 'flex';
    };

    const hideLoader = () => {
        const loader = document.getElementById('loading');
        if (loader) loader.style.display = 'none';
    };

    const renderRating = (ratingValue, reviewCount) => {
        const fullStars = Math.floor(ratingValue);
        const hasHalfStar = (ratingValue - fullStars) >= 0.5;
        const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
        
        let starsHTML = '';
        
        for (let i = 0; i < fullStars; i++) {
            starsHTML += '<i class="fas fa-star"></i>';
        }
        
        if (hasHalfStar) {
            starsHTML += '<i class="fas fa-star-half-alt"></i>';
        }
        
        for (let i = 0; i < emptyStars; i++) {
            starsHTML += '<i class="far fa-star"></i>';
        }
        
        return starsHTML + `<span>(${reviewCount})</span>`;
    };

    // =============================================
    // Funções de Filtro e Ordenação
    // =============================================
    const sortProducts = () => {
        const sortOrder = document.getElementById('sort-select').value;
        const container = document.getElementById('parts-container');
        const cards = Array.from(container.querySelectorAll('.part-card[style="display: block"]'));
        
        cards.sort((a, b) => {
            const priceA = parseFloat(a.getAttribute('data-price'));
            const priceB = parseFloat(b.getAttribute('data-price'));
            const ratingA = parseFloat(a.getAttribute('data-rating'));
            const ratingB = parseFloat(b.getAttribute('data-rating'));
            
            if (sortOrder === 'price_asc') return priceA - priceB;
            if (sortOrder === 'price_desc') return priceB - priceA;
            if (sortOrder === 'rating_desc') return ratingB - ratingA;
            return 0;
        });
        
        cards.forEach(card => container.appendChild(card));
    };

    const applyFilters = async (selectedMenu = '', selectedType = '') => {
        showLoader();
        
        // Usando setTimeout para permitir que a UI atualize antes do processamento pesado
        await new Promise(resolve => setTimeout(resolve, 0));
        
        const selectedStores = Array.from(document.querySelectorAll('input[name="store"]:checked')).map(el => el.value);
        const selectedFilters = Array.from(document.querySelectorAll('input[name="filter"]:checked')).map(el => el.value);
        const selectedSubfilters = Array.from(document.querySelectorAll('input[name="subfilter"]:checked')).map(el => ({
            value: el.value,
            parent: el.getAttribute('data-parent')
        }));
        const searchQuery = document.getElementById('search-input').value.toLowerCase();
        
        document.querySelectorAll('.part-card').forEach(card => {
            const cardMenu = card.getAttribute('data-menu');
            const cardType = card.getAttribute('data-type');
            const cardStore = card.getAttribute('data-store');
            const cardFilter = card.getAttribute('data-filter');
            const cardSubfilter = card.getAttribute('data-subfilter');
            const cardName = card.querySelector('h3').textContent.toLowerCase();
            
            const menuMatch = !selectedMenu || cardMenu === selectedMenu;
            const typeMatch = !selectedType || cardType === selectedType;
            const storeMatch = selectedStores.length === 0 || selectedStores.includes(cardStore);
            const nameMatch = !searchQuery || cardName.includes(searchQuery);
            
            let filterMatch = selectedFilters.length === 0 && selectedSubfilters.length === 0;
            
            if (!filterMatch && selectedFilters.length > 0) {
                filterMatch = selectedFilters.includes(cardFilter);
            }
            
            if (!filterMatch && selectedSubfilters.length > 0) {
                filterMatch = selectedSubfilters.some(
                    sub => sub.value === cardSubfilter && sub.parent === cardFilter
                );
            }
            
            card.style.display = (menuMatch && typeMatch && storeMatch && filterMatch && nameMatch) ? 'block' : 'none';
        });
        
        sortProducts();
        updatePagination();
        hideLoader();
    };

    // =============================================
    // Paginação (mantendo a original)
    // =============================================
    const updatePagination = () => {
        const visibleCards = document.querySelectorAll('.part-card[style="display: block"]');
        const totalPages = Math.ceil(visibleCards.length / itemsPerPage) || 1;
        
        document.getElementById('total-pages').textContent = totalPages;
        document.getElementById('current-page').textContent = currentPage;
        document.getElementById('prev-page').disabled = currentPage === 1;
        document.getElementById('next-page').disabled = currentPage >= totalPages;
        
        visibleCards.forEach((card, index) => {
            const page = Math.floor(index / itemsPerPage) + 1;
            card.style.display = page === currentPage ? 'block' : 'none';
        });
    };

    const goToPrevPage = () => {
        if (currentPage > 1) {
            currentPage--;
            updatePagination();
        }
    };

    const goToNextPage = () => {
        const totalPages = parseInt(document.getElementById('total-pages').textContent);
        if (currentPage < totalPages) {
            currentPage++;
            updatePagination();
        }
    };

    // =============================================
    // Filtros Dinâmicos
    // =============================================
    const updateDynamicFilters = (selectedType) => {
        const filterContainer = document.getElementById('filter-filters');
        const filterGroup = document.getElementById('filter-filters-container');
        
        if (!selectedType) {
            filterGroup.style.display = 'none';
            return;
        }
        
        const filterMap = new Map();
        
        document.querySelectorAll(`.part-card[data-type="${selectedType}"]`).forEach(card => {
            const filter = card.getAttribute('data-filter');
            const subfilter = card.getAttribute('data-subfilter');
            
            if (filter) {
                if (!filterMap.has(filter)) {
                    filterMap.set(filter, new Set());
                }
                if (subfilter) {
                    filterMap.get(filter).add(subfilter);
                }
            }
        });
        
        if (filterMap.size > 0) {
            filterContainer.innerHTML = '';
            
            filterMap.forEach((subfilters, filter) => {
                if (subfilters.size > 0) {
                    filterContainer.innerHTML += `
                        <div class="filter-group">
                            <button class="filter-dropdown-btn">${filter}</button>
                            <div class="filter-dropdown-content" id="dropdown-${filter.replace(/\s+/g, '-')}">
                                ${Array.from(subfilters).map(sub => `
                                    <label class="filter-subgroup">
                                        <input type="checkbox" name="subfilter" value="${sub}" data-parent="${filter}">
                                        ${sub}
                                    </label>
                                `).join('')}
                            </div>
                        </div>
                    `;
                } else {
                    filterContainer.innerHTML += `
                        <label>
                            <input type="checkbox" name="filter" value="${filter}">
                            ${filter}
                        </label><br>
                    `;
                }
            });
            
            filterGroup.style.display = 'block';
            setupFilterEvents();
        } else {
            filterGroup.style.display = 'none';
        }
    };

    const setupFilterDropdowns = () => {
        document.querySelectorAll('.filter-dropdown-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                this.classList.toggle('active');
                const dropdownId = `dropdown-${this.textContent.replace(/\s+/g, '-')}`;
                const dropdown = document.getElementById(dropdownId);
                if (dropdown) {
                    dropdown.classList.toggle('show');
                }
            });
        });
    };

    const setupFilterEvents = () => {
        document.querySelectorAll('input[name="filter"], input[name="subfilter"]').forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                currentPage = 1;
                applyFilters();
            });
        });
        setupFilterDropdowns();
    };

    // =============================================
    // Filtros Específicos para GPUs
    // =============================================
    const generateDynamicFilters = (selectedType) => {
        const dynamicFiltersContainer = document.getElementById('dynamic-filters');
        dynamicFiltersContainer.innerHTML = '';

        switch (selectedType) {
            case 'gpu':
                dynamicFiltersContainer.innerHTML = `
                    <div class="filter-group" data-brand="nvidia">
                        <h3>GPUs NVIDIA</h3>
                        ${generateGPUList(nvidiaGPUs, 'nvidia')}
                    </div>
                    <div class="filter-group" data-brand="amd">
                        <h3>GPUs AMD</h3>
                        ${generateGPUList(amdGPUs, 'amd')}
                    </div>
                    <div class="filter-group" data-brand="intel">
                        <h3>GPUs Intel</h3>
                        ${generateGPUList(intelGPUs, 'intel')}
                    </div>
                `;
                break;
        }

        setupCheckboxEvents();
    };

    const generateGPUList = (gpuList, brand) => {
        const visibleCount = 5;
        const reversedList = [...gpuList].reverse();
        const hiddenGPUs = reversedList.slice(visibleCount);
    
        const visibleHTML = reversedList.slice(0, visibleCount).map(gpu => `
            <label class="gpu-item"><input type="checkbox" name="gpu" value="${gpu.toLowerCase()}"> ${gpu}</label>
        `).join('');
    
        const hiddenHTML = hiddenGPUs.map(gpu => `
            <label class="gpu-item hidden-gpu" style="display:none;"><input type="checkbox" name="gpu" value="${gpu.toLowerCase()}"> ${gpu}</label>
        `).join('');
    
        const showMoreButton = hiddenGPUs.length > 0 ? `
            <button class="show-more" onclick="toggleMoreGPU('${brand}')">Mostrar mais ↑</button>
        ` : '';
    
        return `
            <div class="gpu-list">
                ${visibleHTML}
                <div class="hidden-gpus" id="hidden-gpus-${brand}" style="display:none;">
                    ${hiddenHTML}
                </div>
                ${showMoreButton}
            </div>
        `;
    };

    const setupCheckboxEvents = () => {
        document.querySelectorAll('#dynamic-filters input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                currentPage = 1;
                applyFilters();
            });
        });
    };

    // =============================================
    // Menu Dropdowns
    // =============================================
    const setupMenuDropdowns = () => {
        document.querySelectorAll('.type-dropdown a').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const menu = this.getAttribute('data-menu');
                const type = this.getAttribute('data-type');
                
                document.querySelectorAll('.type-dropdown a').forEach(item => {
                    item.classList.remove('active');
                });
                
                this.classList.add('active');
                applyFilters(menu, type);
                updateDynamicFilters(type);
                generateDynamicFilters(type);
            });
        });
    };

    // =============================================
    // Event Listeners
    // =============================================
    const setupEventListeners = () => {
        document.getElementById('search-input').addEventListener('input', () => {
            currentPage = 1;
            applyFilters();
        });

        document.getElementById('search-button').addEventListener('click', () => {
            currentPage = 1;
            applyFilters();
        });

        document.getElementById('sort-select').addEventListener('change', () => {
            currentPage = 1;
            sortProducts();
            updatePagination();
        });

        document.getElementById('prev-page').addEventListener('click', goToPrevPage);
        document.getElementById('next-page').addEventListener('click', goToNextPage);

        document.querySelectorAll('input[name="store"]').forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                currentPage = 1;
                applyFilters();
            });
        });
    };

    // =============================================
    // Inicialização
    // =============================================
    const initialize = async () => {
        initializeLayout();
        setupMenuDropdowns();
        setupEventListeners();
        updatePagination();
        
        // Mostrar todos os produtos inicialmente
        await applyFilters();
    };

    await initialize();
});

// =============================================
// Funções Globais
// =============================================
window.toggleMoreGPU = function(brand) {
    const hiddenContainer = document.querySelector(`#hidden-gpus-${brand}`);
    const button = hiddenContainer.nextElementSibling;

    if (hiddenContainer.style.display === 'none') {
        hiddenContainer.style.display = 'block';
        button.textContent = 'Mostrar menos ↓';
    } else {
        hiddenContainer.style.display = 'none';
        button.textContent = 'Mostrar mais ↑';
    }
};

window.createAlert = function(product, currentPrice) {
    const targetPrice = parseFloat(prompt(`Defina o preço alvo para ${product} (atual: R$ ${currentPrice.toFixed(2)}):`));

    if (isNaN(targetPrice)) {
        alert('Preço inválido!');
        return;
    }

    const newAlert = {
        id: crypto.randomUUID(),
        product,
        targetPrice,
        date: new Date().toISOString()
    };

    const priceAlerts = JSON.parse(localStorage.getItem('priceAlerts')) || [];
    priceAlerts.push(newAlert);
    localStorage.setItem('priceAlerts', JSON.stringify(priceAlerts));
    alert('Alerta criado com sucesso!');
};

window.removeAlert = function(alertId) {
    let priceAlerts = JSON.parse(localStorage.getItem('priceAlerts')) || [];
    priceAlerts = priceAlerts.filter(alert => alert.id !== alertId);
    localStorage.setItem('priceAlerts', JSON.stringify(priceAlerts));
};

window.showProductModal = function(productData) {
    const productName = productData.element.querySelector('h3').textContent;
    const productImage = productData.element.querySelector('img').src;
    const productPrice = productData.element.querySelector('.price').textContent;

    document.getElementById('modal-product-name').textContent = productName;
    document.getElementById('modal-product-image').src = productImage;
    document.getElementById('modal-product-price').textContent = `Preço: ${productPrice}`;
    document.getElementById('product-modal').style.display = 'flex';
};

window.closeProductModal = function() {
    document.getElementById('product-modal').style.display = 'none';
};

window.onclick = function(event) {
    const modal = document.getElementById('product-modal');
    if (event.target === modal) {
        closeProductModal();
    }
};