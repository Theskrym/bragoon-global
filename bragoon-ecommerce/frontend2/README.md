# Frontend2 - HTML5 + CSS + JavaScript Vanilla

Versão redesenvolvida do frontend BRAGOON Store usando HTML5 semântico, CSS responsivo e JavaScript vanilla (sem frameworks).

## ✅ Requisitos Atendidos

- ✅ **4 pontos**: 6 páginas (Home, Login, Produtos, Sobre, Contato, Cadastro)
- ✅ **1 ponto**: Tela de Login com formulário POST
- ✅ **3 pontos**: Visual amigável com design moderno e responsivo
- ✅ **1 ponto**: HTML5 semântico (DIV, SPAN, NAV, HEADER, FOOTER, SECTION, ARTICLE)
- ✅ **1 ponto**: Formulários corretos com tipos de campos (email, password, tel, select, textarea) e envio POST/GET

## 📁 Estrutura do Projeto

```
frontend2/
├── index.html              # Página Home
├── login.html              # Página Login
├── register.html           # Página Cadastro (6ª página)
├── produtos.html           # Página Produtos com filtros
├── sobre.html              # Página Sobre
├── contato.html            # Página Contato com formulário
├── css/
│   └── styles.css          # Estilos responsivos
├── js/
│   ├── api.js              # Funções de API + Carrinho
│   ├── main.js             # Home page logic
│   ├── products.js         # Filtros + Paginação
│   ├── login.js            # Login logic
│   ├── register.js         # Cadastro logic
│   └── contact.js          # Contato logic
└── images/                 # Pasta para imagens
```

## 🚀 Como Usar

### 1. Abrir no Navegador

Simplesmente abra `index.html` em um navegador moderno (Chrome, Firefox, Safari, Edge).

### 2. Conectar ao Backend Django

O frontend2 **já está configurado** para se conectar ao backend! A URL é detectada automaticamente:

- **Local Development**: `http://localhost:8000/api`
- **Production**: Usa protocolo relativo `/api`

#### Iniciar o Backend Django

```bash
# Navegue até a pasta backend
cd bragoon-ecommerce/backend

# Inicie o servidor Django
python manage.py runserver 0.0.0.0:8000
```

**Importante**: O backend está configurado com CORS habilitado (`CORS_ALLOW_ALL_ORIGINS = True`), então qualquer frontend pode se conectar sem problemas.

#### Verificar Conexão

Abra o console do navegador (F12) e veja se há erros durante o carregamento de produtos. Você deve ver mensagens como:
```
API_BASE_URL: http://localhost:8000/api
```

### 3. Funcionalidades Principais

#### Home Page (`index.html`)
- Seção hero com call-to-action
- Produtos em destaque carregados da API
- Informações sobre a loja
- Adicionar ao carrinho

#### Produtos (`produtos.html`)
- Filtros dinâmicos (Categoria, Tipo, Loja)
- Busca em tempo real
- Ordenação (Preço, Avaliação)
- Paginação
- Produtos indisponíveis marcados e movidos para o final
- Carrinho local (localStorage)

#### Login (`login.html`)
- Formulário POST com validação
- Autenticação com backend
- "Lembrar de mim" feature
- Armazenamento de token/usuário

#### Cadastro (`register.html`)
- Formulário POST completo
- Validação de senha
- Campos obrigatórios e opcionais
- Newsletter opt-in
- Aceitação de termos

#### Contato (`contato.html`)
- Formulário POST com tipos de campos variados
- Dropdown de assunto
- Textarea para mensagem
- Validações
- FAQ integrada

#### Sobre (`sobre.html`)
- Informações da empresa
- Estatísticas
- Parceiros
- Equipe

## � API Endpoints - Conectados ao Backend Django

O frontend2 **já está conectado e funcionando** com os seguintes endpoints do backend:

```
GET  /api/products/                     - Lista todos os produtos com filtros
GET  /api/products/search/              - Busca com paginação e ordenação
GET  /api/products/{product_ID}/        - Detalhes de um produto
GET  /api/products/{product_ID}/price-history/ - Histórico de preços (6 meses)
GET  /api/products/filter_options/      - Opções de filtro (menus, tipos, lojas)
```

### Parâmetros de Filtro Disponíveis

```
?menu=        - Categoria (ex: Nobreak)
?type=        - Tipo (ex: 600W)
?store=       - Loja (ex: Pichau)
?filter=      - Filtro (ex: Inteligente)
?subfilter=   - Sub-filtro (ex: 220V)
?search=      - Buscar por nome
?sort=        - price_asc, price_desc, rating_desc
?page=        - Página (padrão: 1)
?page_size=   - Itens por página (padrão: 12)
```

### Status de Integração

- ✅ **Produtos**: Conectado ao backend Django
- ✅ **Filtros**: Dinâmicos via API
- ✅ **Carrinho**: LocalStorage (frontend)
- ✅ **Login/Cadastro**: LocalStorage (simulado)
- ✅ **Contato**: LocalStorage (simulado)

## �💾 Armazenamento Local

- **Carrinho**: Salvo em `localStorage` como `cart` (JSON)
- **Auth Token**: Salvo em `localStorage` como `authToken`
- **Usuário**: Salvo em `localStorage` como `user` (JSON)

## 📱 Responsividade

O design é totalmente responsivo com breakpoints em:
- Desktop: 1200px+
- Tablet: 768px - 1199px
- Mobile: < 768px

## 🎨 Design

- **Cores**: Gradiente roxo/azul (#667eea - #764ba2)
- **Font**: Segoe UI / Tahoma
- **Ícones**: Emojis Unicode

## ⚙️ Funcionalidades JavaScript

### api.js
- `searchProducts(params)` - Busca com filtros e paginação
- `getFilterOptions()` - Carrega opções de filtro da API
- `getProductDetail(productId)` - Detalhes de um produto
- `getPriceHistory(productId)` - Histórico de preços
- `loginUser(email, password)` - Login (simulado)
- `registerUser(userData)` - Cadastro (simulado)
- `submitContactForm(formData)` - Submete contato (simulado)
- `addToCart(product)` - Adiciona ao carrinho
- `getCart()` / `saveCart()` - Gerencia carrinho
- `formatPrice(price)` - Formata preço em BRL

### products.js
- `loadProducts()` - Carrega produtos com filtros aplicados
- `applyFilters()` - Aplica filtros selecionados
- `resetFilters()` - Limpa todos os filtros
- `updatePagination()` - Gera botões de paginação
- `updateTypeSelect()` - Atualiza tipos baseado na categoria

### login.js
- `handleLoginSubmit()` - Processa login
- `isValidEmail()` - Valida formato de email

### register.js
- `handleRegisterSubmit()` - Processa cadastro
- `isValidPhone()` - Valida formato de telefone

### contact.js
- `handleContactSubmit()` - Processa contato
- Validações de email e telefone

## 📝 Validações de Formulários

- **Email**: Padrão RFC5322 simplificado
- **Telefone**: (XX) 9XXXX-XXXX ou similar
- **Senha**: Mínimo 6 caracteres
- **Texto**: Comprimento mínimo/máximo

## 🌐 Recursos HTML5

- `<header>` - Cabeçalho com navegação
- `<nav>` - Menu de navegação
- `<main>` - Conteúdo principal
- `<section>` - Seções de conteúdo
- `<article>` - Artigos/cards
- `<aside>` - Sidebar de filtros
- `<footer>` - Rodapé
- `<form>` - Formulários com tipos corretos
- `<input type="email">`, `type="password"`, `type="tel"`, `type="range"`, `type="checkbox"`
- `<select>` - Dropdowns
- `<textarea>` - Áreas de texto

## 🔐 Segurança

- Validação de entrada no cliente
- HTTP (ajustar para HTTPS em produção)
- CORS deve estar configurado no backend

## 📦 Compatibilidade

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🎯 Próximos Passos

1. Conectar ao backend Django real
2. Implementar carrinho/checkout
3. Histórico de pedidos
4. Perfil de usuário
5. Avaliações de produtos
6. Wishlist

---

**Desenvolvido em**: Março 2026
**Versão**: 1.0.0
