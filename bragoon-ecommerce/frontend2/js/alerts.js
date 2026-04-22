/**
 * Sistema de Alertas de Preço
 * Permite ao usuário criar alertas para quando um produto atinge um preço específico
 */

async function createPriceAlert(productId, targetPrice) {
    /**
     * Cria um novo alerta de preço
     * POST /api/alerts/
     */
    try {
        if (!localStorage.getItem('authToken')) {
            showNotification('Login Necessário', 'Você precisa estar logado para criar alertas', 'info');
            return false;
        }

        const result = await apiCall('/api/alerts/', {
            method: 'POST',
            body: JSON.stringify({
                product: productId,
                target_price: parseFloat(targetPrice),
                notification_type: 'price_below',
                is_active: true
            })
        });

        if (result.success || result.id) {
            showNotification(
                '🔔 Alerta Criado',
                `Você será notificado quando o preço chegar a R$ ${targetPrice}`,
                'success'
            );
            return true;
        } else {
            showNotification('Erro', 'Erro ao criar alerta', 'error');
            return false;
        }
    } catch (error) {
        console.error('Erro ao criar alerta:', error);
        showNotification('Erro', 'Erro ao criar alerta', 'error');
        return false;
    }
}

async function getMyAlerts() {
    /**
     * Obtém todos os alertas do usuário
     * GET /api/alerts/
     */
    try {
        if (!localStorage.getItem('authToken')) {
            return [];
        }

        const response = await apiCall('/api/alerts/');
        return response.results || response || [];
    } catch (error) {
        console.error('Erro ao obter alertas:', error);
        return [];
    }
}

async function deleteAlert(alertId) {
    /**
     * Deleta um alerta existente
     * DELETE /api/alerts/{id}/
     */
    try {
        const result = await apiCall(`/api/alerts/${alertId}/`, {
            method: 'DELETE'
        });

        showNotification(
            '🔔 Alerta Removido',
            'O alerta foi removido com sucesso',
            'success'
        );
        return true;
    } catch (error) {
        console.error('Erro ao deletar alerta:', error);
        showNotification('Erro', 'Erro ao remover alerta', 'error');
        return false;
    }
}

async function displayAlertsPage() {
    /**
     * Exibe a página de gerenciamento de alertas
     */
    const alerts = await getMyAlerts();
    const container = document.getElementById('alerts-container');

    if (!container) {
        console.error('Container de alertas não encontrado');
        return;
    }

    if (alerts.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <h2>🔔 Nenhum Alerta Criado</h2>
                <p>Crie alertas para receber notificações quando produtos atingem preços específicos</p>
                <button class="btn btn-primary" onclick="location.href='produtos.html'">
                    Ver Produtos
                </button>
            </div>
        `;
        return;
    }

    let html = '<div class="alerts-list">';
    
    for (const alert of alerts) {
        const product = alert.product;
        const alertDate = new Date(alert.created_at).toLocaleDateString('pt-BR');
        
        html += `
            <div class="alert-card ${!alert.is_active ? 'inactive' : ''}">
                <div class="alert-header">
                    <h3>${product.name}</h3>
                    <span class="alert-status ${alert.is_active ? 'active' : 'inactive'}">
                        ${alert.is_active ? '🟢 Ativo' : '⚪ Inativo'}
                    </span>
                </div>
                
                <div class="alert-body">
                    <div class="alert-info">
                        <p><strong>Preço Alvo:</strong> R$ ${parseFloat(alert.target_price).toFixed(2)}</p>
                        <p><strong>Loja:</strong> ${product.store}</p>
                        <p><strong>Preço Atual:</strong> R$ ${parseFloat(product.price).toFixed(2)}</p>
                        <p><strong>Criado em:</strong> ${alertDate}</p>
                    </div>
                    
                    <div class="alert-progress">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${Math.min((parseFloat(alert.target_price) / parseFloat(product.price)) * 100, 100)}%"></div>
                        </div>
                        <p class="progress-text">
                            ${parseFloat(product.price) <= parseFloat(alert.target_price) 
                                ? '✅ Alerta acionado!' 
                                : `Faltam R$ ${(parseFloat(product.price) - parseFloat(alert.target_price)).toFixed(2)}`
                            }
                        </p>
                    </div>
                </div>
                
                <div class="alert-actions">
                    <a href="produto-detalhes.html?id=${product.product_ID}" class="btn btn-secondary">
                        Ver Produto
                    </a>
                    <button class="btn btn-danger" onclick="deleteAlert(${alert.id})">
                        Remover Alerta
                    </button>
                </div>
            </div>
        `;
    }

    html += '</div>';
    container.innerHTML = html;
}

async function showCreateAlertModal(productId, productName, currentPrice) {
    /**
     * Exibe modal para criar novo alerta
     */
    const modal = document.createElement('div');
    modal.className = 'modal-overlay show';
    modal.innerHTML = `
        <div class="modal-content">
            <button class="close-modal" onclick="this.parentElement.parentElement.remove()">&times;</button>
            <h2>🔔 Criar Alerta de Preço</h2>
            
            <div class="alert-form">
                <p class="product-name"><strong>${productName}</strong></p>
                <p class="current-price">Preço atual: <strong>R$ ${parseFloat(currentPrice).toFixed(2)}</strong></p>
                
                <div class="form-group">
                    <label for="target-price">Preço Alvo (R$)</label>
                    <input 
                        type="number" 
                        id="target-price" 
                        min="0" 
                        step="0.01" 
                        max="${currentPrice}"
                        value="${(parseFloat(currentPrice) * 0.9).toFixed(2)}"
                        placeholder="Ex: 1000.00"
                    >
                    <small>Você será notificado quando o preço cair para este valor ou menos</small>
                </div>
                
                <div class="form-actions">
                    <button class="btn btn-secondary" onclick="this.parentElement.parentElement.parentElement.parentElement.remove()">
                        Cancelar
                    </button>
                    <button class="btn btn-primary" onclick="
                        createPriceAlert('${productId}', document.getElementById('target-price').value);
                        this.parentElement.parentElement.parentElement.parentElement.remove();
                    ">
                        Criar Alerta
                    </button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

// Verificar alertas acionados periodicamente
function startAlertChecker(intervalSeconds = 300) {
    /**
     * Verifica alertas a cada X segundos
     * Padrão: 5 minutos (300 segundos)
     */
    setInterval(async () => {
        if (!localStorage.getItem('authToken')) return;

        const alerts = await getMyAlerts();
        
        for (const alert of alerts) {
            if (!alert.is_active) continue;

            // Verificar se o preço atual é menor ou igual ao preço alvo
            if (parseFloat(alert.product.price) <= parseFloat(alert.target_price)) {
                // Disparar notificação
                showNotification(
                    '🎉 Alerta de Preço Acionado!',
                    `${alert.product.name} atingiu o preço de R$ ${parseFloat(alert.target_price).toFixed(2)}`,
                    'success',
                    10000 // 10 segundos
                );

                // Mostrar notificação do navegador se permitido
                if (Notification.permission === 'granted') {
                    new Notification('🎉 Alerta BRAGOON', {
                        body: `${alert.product.name} atingiu R$ ${parseFloat(alert.target_price).toFixed(2)}!`,
                        icon: '📊'
                    });
                }
            }
        }
    }, intervalSeconds * 1000);
}

// Solicitar permissão para notificações do navegador
if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
}
