# BRAGOON - Novas Funcionalidades Implementadas

## 1. Deduplicação de Produtos (Product Grouping)

### Backend
- **Modelo: ProductGroup** - Agrupa produtos que são o mesmo item
  - `canonical_name` - Nome único do produto (ex: "AMD Ryzen 5 5500")
  - `canonical_product` - Produto com o menor preço do grupo
  - `lowest_price`, `highest_price`, `average_price` - Estatísticas de preço
  - `variant_count` - Número de variantes/lojas

- **Modelo: ProductVariant** - Representa uma variante do produto em uma loja
  - Vinculado a um ProductGroup
  - Armazena: store_name, variant_name (cor, tamanho, etc), price, is_available
  - Ordenado por preço (mais barato primeiro)

### API Endpoints
- `GET /api/product-groups/` - Lista todos os grupos de produtos
- `GET /api/product-groups/{id}/` - Detalhes do grupo com todas as variantes
- `GET /api/product-groups/{id}/price_chart_data/` - Dados para gráfico (até 360 pontos)
- `GET /api/product-variants/` - Lista variantes
- `GET /api/product-variants/by_group/?group_id={id}` - Variantes de um grupo

### Frontend (js/chart.js)
- `loadPriceChart(productGroupId, canvasElement)` - Renderiza gráfico de preços
- `loadProductVariants(productGroupId, containerElement)` - Exibe top 5 variantes
- `showAllVariants(productGroupId)` - Modal com todas as variantes

## 2. Gráfico de Preços

### Características
- **Tipo:** Gráfico de linhas com 4 séries
- **Dados:** Até 360 pontos históricos
- **Séries:**
  1. Preço Atual (linha sólida)
  2. Preço Mínimo (linha pontilhada verde)
  3. Preço Máximo (linha pontilhada vermelha)
  4. Preço Médio (linha tracejada dourada)

### Biblioteca
- Chart.js (CDN)
- URL: `https://cdn.jsdelivr.net/npm/chart.js`

### Dados Retornados pela API
```json
{
  "group_id": 1,
  "group_name": "AMD Ryzen 5 5500",
  "chart_data": {
    "dates": ["2026-04-22 10:30", ...],
    "prices": [1200.00, ...],
    "lowest_prices": [1100.00, ...],
    "highest_prices": [1500.00, ...],
    "average_prices": [1300.00, ...]
  },
  "current_lowest": 1100.00,
  "current_highest": 1500.00,
  "current_average": 1300.00,
  "variant_count": 5,
  "last_updated": "2026-04-22T15:30:00Z"
}
```

## 3. Sistema de Alertas de Preço

### Backend
- **Modelo: Alert** - Alerta de preço para um produto
  - `user` - Usuário que criou o alerta
  - `product` - Produto a monitorar
  - `target_price` - Preço alvo
  - `notification_type` - Tipo: 'price_below' ou 'lowest_6_months'
  - `is_active` - Se o alerta está ativo
  - `triggered_at` - Quando foi acionado

### API Endpoints
- `POST /api/alerts/` - Criar novo alerta
- `GET /api/alerts/` - Listar alertas do usuário
- `DELETE /api/alerts/{id}/` - Deletar alerta
- `POST /api/alerts/{id}/check_price/` - Verificar se alerta foi acionado

### Frontend (js/alerts.js)
- `createPriceAlert(productId, targetPrice)` - Criar alerta
- `getMyAlerts()` - Obter alertas do usuário
- `deleteAlert(alertId)` - Deletar alerta
- `displayAlertsPage()` - Renderizar página de alertas
- `showCreateAlertModal(productId, productName, currentPrice)` - Modal para criar alerta
- `startAlertChecker(intervalSeconds)` - Verificar alertas periodicamente

### Notificações
- Notificações in-app (UI customizada)
- Notificações do navegador (se permissão concedida)
- Intervalo de verificação: configurável (padrão: 5 minutos)

### Página de Alertas
- URL: `/alertas.html`
- Mostra todos os alertas do usuário
- Exibe progresso (quanto falta em R$ para atingir o preço alvo)
- Opção para deletar ou abrir o produto

## 4. Banco de Dados

### Migração: 0005_product_deduplication_alerts.py

Implementa:
- Tabela `ProductGroup` com índices
- Tabela `ProductVariant` com constraint única (group, store_name)
- Campos novos em `PriceHistory`: group, store, is_lowest, is_highest
- Índices para otimização de queries

### Modelos Relacionados
```
Product
  ├── variants (ProductVariant)
  │   └── group (ProductGroup)
  │       └── price_history (PriceHistory)
  │
  ├── price_history (PriceHistory)
  └── alert_set (Alert)

User
  └── alert_set (Alert)
```

## 5. Atualização da Paleta de Cores

Frontend2 agora usa as cores do Frontend1:
- **Background:** #d3c5aa (bege/marrom claro)
- **Header:** #251708 (marrom escuro)
- **Texto primário:** #251708 (marrom escuro)
- **Destaque:** #b08c43 (dourado/laranja)
- **Alerta:** #f7e07e (amarelo claro)

## 6. Como Usar

### Exibir Produtos Deduplilicados
```javascript
// No HTML da página de produtos
<div id="price-chart-container"></div>
<div id="variants-container"></div>

// No JavaScript
await loadPriceChart(productGroupId, document.getElementById('price-chart-container'));
await loadProductVariants(productGroupId, document.getElementById('variants-container'));
```

### Criar Alerta
```javascript
// Botão no detalhe do produto
button.onclick = () => {
  showCreateAlertModal(productId, productName, currentPrice);
};
```

### Verificar Alertas
```javascript
// Executado automaticamente no DOMContentLoaded da página
startAlertChecker(300); // 5 minutos
```

## 7. Próximos Passos

1. Executar migração: `python manage.py migrate`
2. Atualizar scraper para popular ProductGroup e ProductVariant
3. Integrar gráficos nas páginas de produto
4. Adicionar links para alertas no navbar
5. Testar notificações do navegador

## 8. Notas de Segurança

- Alertas só podem ser acessados pelo usuário que os criou
- ProductVariant usa índice único (group, store_name)
- PriceHistory rastreia alterações para auditoria
- Conformidade LGPD mantida nos perfis de usuário
