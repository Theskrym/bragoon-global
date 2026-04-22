/**
 * Gráfico de Preços para Produtos
 * Mostra: Preço Mínimo, Máximo, Médio e Histórico
 */

// Inclua o Chart.js em seu HTML: <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

async function loadPriceChart(productGroupId, canvasElement) {
    try {
        const response = await apiCall(`/api/product-groups/${productGroupId}/price_chart_data/`);
        
        if (!response || !response.chart_data) {
            console.error('Erro ao carregar dados do gráfico');
            return false;
        }

        const data = response.chart_data;
        const ctx = canvasElement.getContext('2d');

        // Destruir gráfico anterior se existir
        if (window.priceCharts && window.priceCharts[productGroupId]) {
            window.priceCharts[productGroupId].destroy();
        }

        if (!window.priceCharts) {
            window.priceCharts = {};
        }

        // Criar novo gráfico
        window.priceCharts[productGroupId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.dates,
                datasets: [
                    {
                        label: 'Preço Atual',
                        data: data.prices,
                        borderColor: '#251708',
                        backgroundColor: 'rgba(37, 23, 8, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 3,
                        pointBackgroundColor: '#251708'
                    },
                    {
                        label: 'Preço Mínimo',
                        data: data.lowest_prices,
                        borderColor: '#28a745',
                        borderDash: [5, 5],
                        borderWidth: 2,
                        fill: false,
                        tension: 0.4,
                        pointRadius: 0
                    },
                    {
                        label: 'Preço Máximo',
                        data: data.highest_prices,
                        borderColor: '#dc3545',
                        borderDash: [5, 5],
                        borderWidth: 2,
                        fill: false,
                        tension: 0.4,
                        pointRadius: 0
                    },
                    {
                        label: 'Preço Médio',
                        data: data.average_prices,
                        borderColor: '#b08c43',
                        borderDash: [2, 2],
                        borderWidth: 2,
                        fill: false,
                        tension: 0.4,
                        pointRadius: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: '#251708',
                            font: { size: 12, weight: 'bold' },
                            padding: 15
                        }
                    },
                    title: {
                        display: true,
                        text: `Histórico de Preços - ${response.group_name}`,
                        color: '#251708',
                        font: { size: 14, weight: 'bold' }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Preço (R$)',
                            color: '#251708'
                        },
                        ticks: {
                            color: '#251708',
                            callback: function(value) {
                                return 'R$ ' + value.toFixed(2);
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Data',
                            color: '#251708'
                        },
                        ticks: {
                            color: '#251708',
                            maxTicksLimit: 10
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    }
                },
                interaction: {
                    mode: 'index',
                    intersect: false
                }
            }
        });

        return true;
    } catch (error) {
        console.error('Erro ao carregar gráfico de preços:', error);
        return false;
    }
}

async function loadProductVariants(productGroupId, containerElement) {
    /**
     * Carrega as 5 variantes mais baratas e mostra opção de "ver mais"
     */
    try {
        const response = await apiCall(`/api/product-variants/by_group/?group_id=${productGroupId}`);
        
        if (!response) {
            console.error('Erro ao carregar variantes');
            return false;
        }

        const variants = response.slice(0, 5); // Top 5 variantes mais baratas
        const hasMore = response.length > 5;

        let html = '<div class="product-variants-list">';
        
        variants.forEach((variant, index) => {
            html += `
                <div class="variant-item">
                    <span class="variant-rank">#${index + 1}</span>
                    <div class="variant-info">
                        <p class="variant-store"><strong>${variant.store_name}</strong></p>
                        ${variant.variant_name ? `<p class="variant-detail">${variant.variant_name}</p>` : ''}
                        <p class="variant-price">R$ ${parseFloat(variant.price).toFixed(2)}</p>
                    </div>
                    <button class="btn btn-primary" onclick="addProductToCart({
                        product_ID: '${variant.product_details.product_ID}',
                        name: '${variant.product_details.name}',
                        price: ${variant.price},
                        image_url: '${variant.product_details.image_url}',
                        store: '${variant.store_name}',
                        affiliate_link: '${variant.product_details.affiliate_link}'
                    })">Adicionar</button>
                </div>
            `;
        });

        if (hasMore) {
            html += `
                <button class="btn btn-secondary" onclick="showAllVariants(${productGroupId})">
                    Ver mais opções (${response.length - 5} restantes)
                </button>
            `;
        }

        html += '</div>';
        containerElement.innerHTML = html;

        return true;
    } catch (error) {
        console.error('Erro ao carregar variantes:', error);
        return false;
    }
}

async function showAllVariants(productGroupId) {
    /**
     * Mostra modal com todas as variantes
     */
    try {
        const response = await apiCall(`/api/product-variants/by_group/?group_id=${productGroupId}`);
        
        if (!response) {
            showNotification('Erro', 'Não foi possível carregar as variantes', 'error');
            return;
        }

        let html = '<div class="all-variants-modal">';
        html += '<div class="variants-grid">';
        
        response.forEach((variant, index) => {
            html += `
                <div class="variant-card">
                    <span class="variant-rank">#${index + 1}</span>
                    <h4>${variant.store_name}</h4>
                    ${variant.variant_name ? `<p class="variant-detail">${variant.variant_name}</p>` : ''}
                    <p class="variant-price">R$ ${parseFloat(variant.price).toFixed(2)}</p>
                    <button class="btn btn-primary" onclick="addProductToCart({
                        product_ID: '${variant.product_details.product_ID}',
                        name: '${variant.product_details.name}',
                        price: ${variant.price},
                        image_url: '${variant.product_details.image_url}',
                        store: '${variant.store_name}',
                        affiliate_link: '${variant.product_details.affiliate_link}'
                    })">Adicionar ao Carrinho</button>
                </div>
            `;
        });

        html += '</div></div>';

        // Exibir em modal
        showModal('Todas as Opções de Preço', html);

    } catch (error) {
        console.error('Erro ao mostrar todas as variantes:', error);
        showNotification('Erro', 'Erro ao carregar variantes', 'error');
    }
}

function showModal(title, content) {
    /**
     * Função helper para exibir modal customizado
     */
    const modal = document.createElement('div');
    modal.className = 'modal-overlay show';
    modal.innerHTML = `
        <div class="modal-content">
            <button class="close-modal" onclick="this.parentElement.parentElement.remove()">&times;</button>
            <h2>${title}</h2>
            ${content}
        </div>
    `;
    document.body.appendChild(modal);
}
