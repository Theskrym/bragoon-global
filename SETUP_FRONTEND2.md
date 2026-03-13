# 🚀 Setup Frontend2 com Backend Django

## ✅ O que foi feito

O frontend2 foi totalmente conectado ao backend Django sem quebrar o frontend React. Ambos podem coexistir apontando para o mesmo backend.

## 📋 Alterações Realizadas

### 1. **api.js** - Endpoints Atualizados
- ✅ URL dinâmica (detecta localhost ou usa /api)
- ✅ Endpoints reais do backend implementados
- ✅ Auth simulado em localStorage (backend não tem endpoints)
- ✅ Contact simulado em localStorage
- ✅ Suporte a token Bearer

### 2. **products.js** - Parâmetros Corrigidos
- ✅ `stores` → `store` (singular)
- ✅ `page_size` → `limit`
- ✅ Estrutura de resposta alinhada com backend

### 3. **main.js** - Home Page
- ✅ `page_size` → `limit`

### 4. **README.md** - Documentação Atualizada
- ✅ Instruções de conexão com backend
- ✅ Endpoints reais documentados
- ✅ Parâmetros de filtro explicados

---

## 🔧 Como Testar

### Passo 1: Iniciar o Backend Django

```bash
cd a:\wind\coisas minhas\BRAGOON STORE\bragoon-ecommerce\backend

# Se tiver venv
.\.venv\Scripts\activate

# Ou no backend, rodar:
python manage.py runserver 0.0.0.0:8000
```

**Esperado**: Backend rodando em `http://localhost:8000`

### Passo 2: Abrir Frontend2

```bash
# Opção 1: Abrir direto no navegador
# Clique em: a:\wind\coisas minhas\BRAGOON STORE\bragoon-ecommerce\frontend2\index.html

# Opção 2: Usar Live Server (VS Code)
# Right-click em index.html > Open with Live Server
```

### Passo 3: Testar Funcionalidades

#### ✅ Testar Carregamento de Produtos
1. Abra `produtos.html`
2. Verifique no Dev Tools (F12) → Console
3. Deve aparecer: `API_BASE_URL: http://localhost:8000/api`
4. Produtos devem carregar na página
5. Filtros devem ser preenchidos dinamicamente

#### ✅ Testar Filtros
1. Selecione uma Categoria (menu)
2. Selecione uma Loja (store)
3. Use a busca
4. Ordene por preço/avaliação
5. Pagine entre resultados

#### ✅ Testar Home Page
1. Abra `index.html`
2. Verifique se os produtos em destaque carregam

#### ✅ Testar Carrinho (LocalStorage)
1. Clique em "Adicionar" em qualquer produto
2. Verifique o contador no topo (🛒)
3. Abra Dev Tools → Storage → LocalStorage
4. Veja a chave `cart` com os produtos

#### ✅ Testar Formulários
1. **Login**: Preenchimento livre (simulado)
2. **Cadastro**: Preenchimento livre (simulado)
3. **Contato**: Preenchimento livre (simulado)
4. Dev Tools → Storage → LocalStorage → `authToken`, `user`, `contacts`

---

## 🔍 Debugging

### Se Produtos Não Carregarem

1. **Verificar Console** (F12 → Console):
   ```
   API_BASE_URL devem aparecer
   Erros de CORS? Verificar backend settings.py
   ```

2. **Verificar Backend**:
   ```bash
   # Acessar diretamente
   curl http://localhost:8000/api/products/
   # Ou no navegador: http://localhost:8000/api/products/
   ```

3. **CORS Habilitado?**:
   - ✅ Backend tem `CORS_ALLOW_ALL_ORIGINS = True`
   - ✅ Middleware CORS está ativo

4. **Produtos no Banco?**
   - Execute: `python manage.py import_products.py` no backend

### Se Filtros Não Funcionarem

1. Verificar no Console do navegador se há erros
2. Testar endpoint: `http://localhost:8000/api/products/filter_options/`
3. Deve retornar JSON com: `stores`, `menus`, `type`, `filter`, `subfilter`

---

## 📊 Estrutura de Dados

### Response de Produtos (`/api/products/search/`)

```json
{
  "products": [
    {
      "product_ID": "prod-123",
      "name": "Nobreak 600W",
      "price": 299.99,
      "rating": 4.5,
      "review_count": 10,
      "store": "Pichau",
      "image_url": "https://...",
      "product_link": "https://...",
      "affiliate_link": "https://...",
      "menu": "Nobreak",
      "type": "600W",
      "filter": "Inteligente",
      "subfilter": "220V"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 48,
    "page_size": 12
  }
}
```

---

## 🎯 Frontend React (Sem Alterações)

O frontend React original (`bragoon-ecommerce/frontend/`) **não foi modificado**.

Ele pode continuar funcionando apontando para:
- Seu próprio environment (se tiver)
- O mesmo backend (compatível)

---

## 📝 Notas Importantes

1. **Dupla Autenticação**: O backend não tem endpoints de auth, então login/cadastro são simulados no localStorage

2. **Coexistência**: Ambos os frontends podem rodar simultaneamente:
   - Frontend React: `npm start` (porta 3000)
   - Frontend2 (vanilla): Apenas abrir os HTML files
   - Backend: Django runserver (porta 8000)

3. **Segurança**: Em produção:
   - Usar HTTPS
   - Restringir CORS_ALLOWED_ORIGINS
   - Implementar endpoints reais de auth

4. **Dados de Teste**:
   - Teste com o arquivo `products.csv` existente
   - Execute `import_products.py` se necessário

---

## 🐛 Possíveis Problemas & Soluções

### "Nenhum produto encontrado"
- ✅ Verificar se backend está rodando
- ✅ Verificar se há produtos no banco de dados
- ✅ Executar `python manage.py import_products.py`

### "Erro CORS"
- ✅ Backend tem `CORS_ALLOW_ALL_ORIGINS = True`? SIM ✓
- ✅ Backend middleware contém CorsMiddleware? SIM ✓

### "API retorna erro 404"
- ✅ Endpoint está registrado em `urls.py`? SIM ✓
- ✅ ViewSet está implementado? SIM ✓

### Filtros vazios
- ✅ `GET /api/products/filter_options/` funciona?
- ✅ Produtos têm campos `menu`, `type`, `store` preenchidos?

---

## ✨ Próximos Passos Opcionais

1. **Real Authentication**: Implementar endpoints de auth no backend
2. **Carrinho Completo**: Criar endpoint `/api/cart/` para sincronizar
3. **Checkout**: Implementar processo de compra
4. **Histórico de Pedidos**: Relacionar com usuário
5. **Avaliações**: Implementar sistema de reviews

---

**Status**: ✅ Frontend2 totalmente conectado ao backend Django
**Data**: Março 2026
**Versão**: 2.0.0 (com API backend integrada)
