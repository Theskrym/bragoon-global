# 📹 ROTEIRO PARA VÍDEO - CÓDIGO E LOCALIZAÇÃO

---

## ✅ REQUISITO 1: 10 TELAS/ROTAS (Peso 3) - MÁXIMA PRIORIDADE

### 🔵 BACKEND - URLS E ENDPOINTS
**Localização:** `backend/config/urls.py`
- **Linha 8:** Registro do router para Products (GET, POST, PUT, DELETE)
- **Linha 9:** Registro do router para Alerts (GET, POST, PUT, DELETE)
- **Linha 14-15:** Rota de histórico de preços (GET)
- **Linha 17-19:** Rotas de autenticação (Login, Register, Perfil)

**Endpoints Totais Criados:**
```
✅ GET    /api/products/                    [Listar produtos]
✅ POST   /api/products/                    [Criar produto]
✅ GET    /api/products/{id}/               [Detalhe produto]
✅ PUT    /api/products/{id}/               [Atualizar produto]
✅ DELETE /api/products/{id}/               [Deletar produto]
✅ GET    /api/alerts/                      [Listar alertas]
✅ POST   /api/alerts/                      [Criar alerta]
✅ PUT    /api/alerts/{id}/                 [Atualizar alerta]
✅ DELETE /api/alerts/{id}/                 [Deletar alerta]
✅ POST   /api/login/                       [Autenticação]
✅ POST   /api/register/                    [Registro]
✅ GET    /api/user/me/                     [Perfil usuário]
✅ GET    /api/products/filter_options/     [Filtros]
✅ GET    /api/products/search/             [Busca]
✅ GET    /api/products/{id}/price-history/ [Histórico preços]
```

### 🟢 FRONTEND REACT - ROTAS
**Localização:** `frontend/src/App.js`
- **Linha 13:** Rota / (Home - Lista de produtos)
- **Linha 14:** Rota /product/:id (Detalhe do produto)
- **Linha 15:** Rota /alerts (Página de alertas)

### 🟡 FRONTEND2 HTML - PÁGINAS
**Localização:** `frontend2/`
```
✅ index.html              [Home]
✅ produtos.html           [Lista de produtos]
✅ produto-detalhes.html  [Detalhe produto]
✅ carrinho.html          [Carrinho de compras]
✅ login.html             [Login]
✅ register.html          [Registro]
✅ perfil.html            [Perfil do usuário]
✅ contato.html           [Contato]
✅ sobre.html             [Sobre nós]
✅ (8+ páginas com integração API)
```

**Total: 15 endpoints backend + 3 rotas React + 9+ páginas HTML = 27+ telas/rotas** ✅

---

## 📁 REQUISITO 2: ORGANIZAÇÃO DO PROJETO - MVC (Peso 2)

### Backend - Estrutura Django (Excelente)
**Localização:** `backend/`
```
backend/
├── config/          [CONFIGS - settings.py, urls.py, wsgi.py]
│   ├── settings.py  (Linha 35-44: INSTALLED_APPS com Django REST, CORS, Filters)
│   ├── urls.py      (Linha 8-9: Routers registrados)
│   └── asgi.py, wsgi.py
├── products/        [APP - Models, Views, Serializers]
│   ├── models.py    (Linha 1-63: Product, PriceHistory, Alert, UserProfile)
│   ├── views.py     (Linha 19-46: UserProfileView com upload)
│   ├── serializers.py (Linha 1-50: Serializers com validação)
│   ├── auth_views.py  (Autenticação e validação)
│   ├── admin.py     (Admin interface)
│   └── migrations/  (Database migrations)
├── manage.py        (Django command center)
└── db.sqlite3       (Banco de dados)
```

### Frontend React - Estrutura por Features
**Localização:** `frontend/src/`
```
src/
├── components/      [Componentes reutilizáveis]
│   ├── Navbar.js, MenuBar.js
│   ├── ProductCard.js, ProductDetail.js
│   ├── AlertForm.js, AlertButton.js
│   ├── Filters.js, Rating.js
│   └── PriceChart.js
├── pages/          [Páginas/Rotas]
│   ├── Home.js
│   ├── ProductPage.js
│   └── AlertsPage.js
├── services/       [Camada de dados - API]
│   ├── api.js      [Requisições HTTP]
│   ├── auth.js     [Autenticação]
│   └── alertService.js
├── utils/          [Funções utilitárias]
│   └── productUtils.js
├── App.js          [Roteador principal]
└── styles/         [CSS]
```

### Frontend2 HTML - Estrutura Organizada
**Localização:** `frontend2/`
```
frontend2/
├── *.html          [Páginas principais]
├── js/             [JavaScript - Lógica]
│   ├── api.js      [Integração com API]
│   ├── main.js     [Scripts gerais]
│   ├── login.js    [Validação login]
│   ├── register.js [Validação registro]
│   ├── products.js [Produtos]
│   └── ...
├── css/            [Styles]
│   └── styles.css
└── testes/         [Testes - debug.html, health-check.html]
```

---

## 🎨 REQUISITO 3: VISUAL E QUALIDADE DO PROJETO (Peso 2)

### CSS Principal
**Localização:** `frontend2/css/styles.css`

**Localização:** `frontend/src/styles.css`

**Localização (por componente):** 
- `frontend/src/components/Filters.css`
- `frontend/src/pages/ProductPage.css`
- `frontend/src/App.css`

### HTML Semantic
**Localização:** `frontend2/index.html` - Estrutura HTML5 com navbar, footer, seções

---

## ✔️ REQUISITO 4: VALIDAÇÃO DE FORMULÁRIO (Peso 2)

### Backend - Validação de Email e Senha
**Localização:** `backend/products/auth_views.py`
- **Linha 19:** `validate_email()` - Regex validação de email
- **Linha 24-39:** `validate_password()` - Validação com:
  - Mínimo 4 caracteres
  - Pelo menos 1 letra
  - Pelo menos 1 número

**Localização:** `backend/products/serializers.py`
- **Linha 30-35:** AlertSerializer com validações required

### Frontend2 - Validação de Formulário (Login)
**Localização:** `frontend2/js/login.js`
- **Linha 15-23:** Validações básicas (campos vazios)
- **Linha 25-28:** `isValidEmail()` - Regex validação email (Linha 59-61)
- **Linha 53-61:** Função `isValidEmail()` com regex: `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`

**Localização:** `frontend2/js/register.js`
- Validações semelhantes para registro

### Backend Models - Validação de Campos
**Localização:** `backend/products/models.py`
- **Linha 5:** `product_ID` - CharField unique (validação de duplicata)
- **Linha 8:** `price` - DecimalField com max_digits/decimal_places
- **Linha 34:** `target_price` - DecimalField validado

---

## 📤 REQUISITO 5: UPLOAD DE ARQUIVOS (Peso 1)

### Backend Models - Campo de Upload
**Localização:** `backend/products/models.py`
- **Linha 51:** `avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)`
  - Upload de imagem de perfil do usuário

### Backend Views - Parser para Upload
**Localização:** `backend/products/views.py`
- **Linha 7:** `parser_classes = (MultiPartParser, FormParser)`
  - Permite receber arquivos multipart/form-data
- **Linha 20-45:** `UserProfileView` - PUT/PATCH para atualizar perfil com avatar

### Backend Serializer - Upload
**Localização:** `backend/products/serializers.py`
- **Linha 37-50:** `UserProfileSerializer` com campo 'avatar'

### Backend Settings - Media Files
**Localização:** `backend/config/settings.py`
- Configurado para receber uploads de arquivos (ImageField automático do Django)

---

## 🔒 BÔNUS: AUTENTICAÇÃO COM TOKEN

**Localização:** `backend/products/auth_views.py`
- **Linha 40+:** `LoginView` - Implementa autenticação com Token JWT
- **Linha 70+:** `RegisterView` - Registro com validação

**Localização:** `backend/config/settings.py`
- **Linha 40:** `'rest_framework.authtoken'` - Token authentication instalado

---

## 📊 RESUMO - CAMINHO RÁPIDO PARA GRAVAÇÃO

```
1️⃣  TELAS/ROTAS
   └─ Mostrar: backend/config/urls.py (linhas 8-19)
   └─ Mostrar: frontend/src/App.js (linhas 13-15)
   └─ Mostrar: frontend2/*.html (listar os 9+ arquivos)

2️⃣  ORGANIZAÇÃO MVC
   └─ Mostrar: Estrutura de pastas (backend/config, backend/products, frontend/src)
   └─ Mostrar: backend/products/models.py (linhas 1-63)
   └─ Mostrar: backend/products/views.py (linhas 19-46)

3️⃣  VISUAL E QUALIDADE
   └─ Mostrar: frontend2/css/styles.css
   └─ Mostrar: frontend/src/styles.css
   └─ Mostrar: frontend2/index.html (renderização no browser)

4️⃣  VALIDAÇÃO
   └─ Mostrar: backend/products/auth_views.py (linhas 19-39: validate functions)
   └─ Mostrar: frontend2/js/login.js (linhas 15-61: validações)

5️⃣  UPLOAD
   └─ Mostrar: backend/products/models.py (linha 51: avatar field)
   └─ Mostrar: backend/products/views.py (linhas 1-45: UserProfileView)
   └─ Mostrar: backend/products/serializers.py (linhas 37-50: upload mapping)
```

---

## ⏱️ TEMPO ESTIMADO POR REQUISITO

- **Req 1 (Telas):** 2-3 minutos
- **Req 2 (MVC):** 2 minutos  
- **Req 3 (Visual):** 1 minuto
- **Req 4 (Validação):** 2 minutos
- **Req 5 (Upload):** 1-2 minutos
- **TOTAL:** ~10 minutos de vídeo

---

**Dica:** Abra os arquivos em VS Code enquanto grava, use Ctrl+G para ir às linhas rapidamente!
