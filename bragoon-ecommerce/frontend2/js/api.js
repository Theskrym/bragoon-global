// ===========================
// API Configuration & Utilities
// ===========================

// Configuração flexível para diferentes ambientes
const API_BASE_URL = (() => {
    // Se for localhost ou 127.0.0.1 (rodando em servidor local)
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.hostname === '') {
        return 'http://localhost:8000/api';
    }
    // Quando deployado em produção, usar protocolo relativo
    return '/api';
})();

console.log('🔌 API_BASE_URL:', API_BASE_URL);
console.log('📍 Hostname:', window.location.hostname);
console.log('🌍 Protocol:', window.location.protocol);

// Limpar localStorage corrompido no inicializador
try {
    const testKey = '__test_ls_' + Date.now();
    localStorage.setItem(testKey, 'test');
    localStorage.removeItem(testKey);
    console.log('✅ localStorage está funcionando');
} catch (error) {
    console.error('⚠️ localStorage pode estar corrompido ou desabilitado:', error);
    console.warn('💡 Sugestão: Se estiver usando file://, serve os arquivos via HTTP em vez disso');
}

// Função genérica para fazer requisições à API com retry
async function apiCall(endpoint, options = {}, retries = 2) {
    const url = `${API_BASE_URL}${endpoint}`;
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        }
    };

    const finalOptions = { ...defaultOptions, ...options };

    // Adicionar token de autenticação usando AuthManager
    try {
        if (typeof auth !== 'undefined') {
            const isAuth = auth.isAuthenticated();
            console.log('🔐 AuthManager disponível. Autenticado?', isAuth);
            
            if (isAuth) {
                const authHeaders = auth.getAuthHeaders();
                finalOptions.headers['Authorization'] = authHeaders['Authorization'];
                console.log('✅ Token adicionado:', authHeaders['Authorization'].substring(0, 30) + '...');
            } else {
                console.warn('⚠️ Não autenticado no AuthManager');
            }
        } else {
            console.warn('⚠️ AuthManager não disponível');
            // Fallback para localStorage se auth não estiver disponível
            try {
                const authToken = localStorage.getItem('authToken');
                if (authToken && authToken !== 'undefined' && authToken.length > 0) {
                    finalOptions.headers['Authorization'] = `Token ${authToken}`;
                    console.log('✅ Token do localStorage:', authToken.substring(0, 30) + '...');
                }
            } catch (storageError) {
                console.warn('⚠️ Erro ao acessar localStorage:', storageError);
            }
        }
    } catch (error) {
        console.warn('⚠️ Erro ao obter token:', error);
    }

    try {
        console.log('🌐 Fazendo requisição para:', url);
        console.log('📤 Headers:', finalOptions.headers);
        const response = await fetch(url, finalOptions);
        
        if (!response.ok) {
            if (response.status === 401 && retries > 0) {
                // Token expirado ou inválido - fazer logout via AuthManager
                console.warn('⚠️ Unauthorized (401) - Token inválido');
                if (typeof auth !== 'undefined') {
                    auth.logout();
                } else {
                    try {
                        localStorage.removeItem('authToken');
                        localStorage.removeItem('user');
                    } catch (e) {
                        console.warn('⚠️ Erro ao limpar localStorage:', e);
                    }
                }
                return { success: false, error: 'Autenticação expirada' };
            }
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('✅ Resposta recebida:', data);
        return { success: true, data };
    } catch (error) {
        console.error(`❌ API Error (${endpoint}):`, error);
        return { success: false, error: error.message };
    }
}

// ===============================
// FORM DATA UPLOAD HELPER
// ===============================

/**
 * Faz upload de FormData (para imagens, arquivos, etc)
 * NÃO adiciona Content-Type application/json
 * Deixa o navegador configurar multipart/form-data automaticamente
 */
async function formDataCall(endpoint, formData) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const options = {
        method: 'PATCH'
    };

    // Adicionar token mas SEM definir Content-Type
    // O navegador automaticamente configura multipart/form-data
    const headers = {};
    try {
        if (typeof auth !== 'undefined' && auth.isAuthenticated()) {
            const authHeaders = auth.getAuthHeaders();
            headers['Authorization'] = authHeaders['Authorization'];
        } else {
            const authToken = localStorage.getItem('authToken');
            if (authToken) {
                headers['Authorization'] = `Token ${authToken}`;
            }
        }
    } catch (error) {
        console.warn('⚠️ Erro ao obter token:', error);
    }

    if (Object.keys(headers).length > 0) {
        options.headers = headers;
    }
    
    options.body = formData;

    try {
        console.log('🌐 FormData upload para:', url);
        const response = await fetch(url, options);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('✅ Upload sucesso:', data);
        return { success: true, data };
    } catch (error) {
        console.error(`❌ Upload Error (${endpoint}):`, error);
        return { success: false, error: error.message };
    }
}

// ===============================

async function searchProducts(params) {
    // Construir query string dinamicamente
    const queryParams = new URLSearchParams();
    
    // Adicionar filtros
    if (params.menu) queryParams.append('menu', params.menu);
    if (params.type) queryParams.append('type', params.type);
    if (params.store) queryParams.append('store', params.store);
    if (params.filter) queryParams.append('filter', params.filter);
    if (params.subfilter) queryParams.append('subfilter', params.subfilter);
    
    // Adicionar busca
    if (params.search) queryParams.append('search', params.search);
    
    // Adicionar paginação
    queryParams.append('page', params.page || 1);
    queryParams.append('page_size', params.limit || 12);
    
    // Adicionar ordenação
    queryParams.append('sort', params.sort || 'price_asc');
    
    const queryString = queryParams.toString();
    const endpoint = `/products/search/?${queryString}`;
    
    console.log('🔍 Buscando produtos com endpoint:', endpoint);
    const result = await apiCall(endpoint);
    console.log('📦 Resultado da busca:', result);
    
    return result;
}

async function getFilterOptions() {
    return apiCall('/products/filter_options/');
}

async function getProductDetail(productId) {
    return apiCall(`/products/${productId}/`);
}

async function getPriceHistory(productId) {
    return apiCall(`/products/${productId}/price-history/`);
}

// ===============================
// AUTHENTICATION (Real Backend)
// ===============================

// Função para limpar localStorage corrompido
function cleanCorruptedStorage() {
    try {
        console.log('🧹 Limpando localStorage corrompido...');
        localStorage.clear();
        console.log('✅ localStorage limpo com sucesso');
        window.location.reload();
    } catch (error) {
        console.error('❌ Erro ao limpar localStorage:', error);
        alert('Erro ao limpar localStorage. Tente limpar o cache do navegador manualmente.');
    }
}

// Como o backend tem endpoints de auth, usar endpoints reais
async function loginUser(email, password) {
    if (!email || !password) {
        return { success: false, error: 'Email e senha são obrigatórios' };
    }
    
    try {
        console.log('🔑 Iniciando login para:', email);
        const result = await apiCall('/login/', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        
        console.log('📨 Resposta do login:', result);
        
        if (result.success && result.data) {
            console.log('✅ Login bem-sucedido. Dados recebidos:', result.data);
            
            if (!result.data.token) {
                console.error('❌ Resposta não contém token!', result.data);
                return { success: false, error: 'Token não recebido do servidor' };
            }
            
            // Armazenar usando AuthManager (com suporte LGPD)
            try {
                console.log('💾 Salvando via AuthManager');
                if (typeof auth !== 'undefined') {
                    auth.setAuth(result.data.token, result.data.user, true);
                    console.log('✅ Dados salvos via AuthManager');
                } else {
                    console.warn('⚠️ AuthManager não disponível, usando fallback localStorage');
                    // Fallback se auth não estiver carregado
                    localStorage.setItem('authToken', result.data.token);
                    localStorage.setItem('user', JSON.stringify(result.data.user));
                    localStorage.setItem('consentimento_dados', 'true');
                    console.log('✅ Dados salvos em localStorage (fallback)');
                }
            } catch (storageError) {
                console.warn('⚠️ Erro ao armazenar autenticação:', storageError);
            }
            
            console.log('✅ Login bem-sucedido:', result.data.user.email);
            return { success: true, data: result.data };
        } else {
            console.error('❌ Erro no login:', result.error);
            return result;
        }
    } catch (error) {
        console.error('❌ Erro ao fazer login:', error);
        return { success: false, error: error.message };
    }
}

async function registerUser(userData) {
    if (!userData.email || !userData.password || !userData.username) {
        return { success: false, error: 'Usuário, email e senha são obrigatórios' };
    }
    
    try {
        const result = await apiCall('/register/', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
        
        if (result.success && result.data.token) {
            // Armazenar token e usuário
            try {
                localStorage.setItem('authToken', result.data.token);
                localStorage.setItem('user', JSON.stringify(result.data.user));
            } catch (storageError) {
                console.warn('⚠️ Erro ao armazenar no localStorage:', storageError);
            }
            
            console.log('✅ Registro bem-sucedido:', result.data.user.email);
            return { success: true, data: result.data };
        } else {
            console.error('❌ Erro no registro:', result.error);
            return result;
        }
    } catch (error) {
        console.error('❌ Erro ao registrar:', error);
        return { success: false, error: error.message };
    }
}

async function logoutUser() {
    try {
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
        console.log('✅ Logout bem-sucedido');
    } catch (error) {
        console.warn('⚠️ Erro ao fazer logout:', error);
    }
    return { success: true };
}

// ===============================
// CONTACT FORM (Simulado com LocalStorage)
// ===============================

async function submitContactForm(formData) {
    // Simular submissão - em produção, conectar a endpoint real
    if (!formData.email || !formData.message) {
        return { success: false, error: 'Email e mensagem são obrigatórios' };
    }
    
    try {
        // Armazenar localmente (em produção seria enviado ao backend)
        let contacts = [];
        try {
            const stored = localStorage.getItem('contacts');
            contacts = stored ? JSON.parse(stored) : [];
        } catch (parseError) {
            console.warn('⚠️ Erro ao ler contacts do localStorage, iniciando vazio:', parseError);
            contacts = [];
            localStorage.removeItem('contacts');
        }
        
        contacts.push({
            ...formData,
            id: Date.now(),
            createdAt: new Date().toISOString()
        });
        localStorage.setItem('contacts', JSON.stringify(contacts));
        
        console.log('✅ Contato salvo:', formData);
        return { success: true, data: { message: 'Contato recebido com sucesso!' } };
    } catch (error) {
        console.error('❌ Erro ao salvar contato:', error);
        return { success: false, error: error.message };
    }
}

// ===============================
// CART MANAGEMENT (Backend Sync)
// ===============================

/**
 * Sincroniza carrinho local com backend quando autenticado
 * Se não autenticado, usa localStorage
 */
function getCart() {
    try {
        // Se tem token, usar carrinho do backend
        if (localStorage.getItem('authToken')) {
            return getBackendCart();
        }
        // Caso contrário, usar localStorage
        const cart = localStorage.getItem('cart');
        return cart ? JSON.parse(cart) : [];
    } catch (error) {
        console.error('⚠️ Erro ao ler carrinho do localStorage, limpando...', error);
        try {
            localStorage.removeItem('cart');
        } catch (e) {
            console.error('⚠️ Erro ao limpar localStorage:', e);
        }
        return [];
    }
}

async function getBackendCart() {
    try {
        const result = await apiCall('/carrinho/');
        if (result.success && result.data && result.data.itens) {
            // Converter itens do backend para formato do frontend
            return result.data.itens.map(item => ({
                product_ID: item.product.product_ID,
                name: item.product.name,
                price: item.product.price,
                image_url: item.product.image_url,
                store: item.product.store,
                affiliate_link: item.product.affiliate_link,
                quantity: item.quantidade
            }));
        }
        return [];
    } catch (error) {
        console.warn('⚠️ Erro ao obter carrinho do backend:', error);
        return [];
    }
}

function saveCart(cart) {
    try {
        const isAuthenticated = localStorage.getItem('authToken');
        
        if (isAuthenticated) {
            // Se autenticado, sincronizar com backend
            saveBackendCart(cart);
        } else {
            // Se não, salvar em localStorage
            localStorage.setItem('cart', JSON.stringify(cart));
        }
        updateCartCount();
    } catch (error) {
        console.error('⚠️ Erro ao salvar carrinho:', error);
        try {
            localStorage.clear();
            localStorage.setItem('cart', JSON.stringify(cart));
        } catch (e) {
            console.error('⚠️ Erro ao limpar e resalvar no localStorage:', e);
        }
    }
}

async function saveBackendCart(cart) {
    try {
        // Limpar carrinho backend
        await apiCall('/carrinho/limpar/', { method: 'POST' });
        
        // Readicionar todos os itens
        for (const item of cart) {
            await apiCall('/carrinho/adicionar/', {
                method: 'POST',
                body: JSON.stringify({
                    product_ID: item.product_ID,
                    quantidade: item.quantity
                })
            });
        }
        console.log('✅ Carrinho sincronizado com backend');
    } catch (error) {
        console.error('⚠️ Erro ao sincronizar carrinho com backend:', error);
    }
}

function addToCart(product) {
    // Validar que o produto tem um product_ID
    if (!product || !product.product_ID) {
        console.error('❌ Erro: Produto sem product_ID', product);
        return false;
    }

    const isAuthenticated = localStorage.getItem('authToken');
    
    if (isAuthenticated) {
        // Adicionar no backend
        addToBackendCart(product);
    } else {
        // Adicionar no localStorage
        addToLocalCart(product);
    }
    
    return true;
}

async function addToBackendCart(product) {
    try {
        const result = await apiCall('/carrinho/adicionar/', {
            method: 'POST',
            body: JSON.stringify({
                product_ID: product.product_ID,
                quantidade: 1
            })
        });
        
        if (result.success) {
            console.log(`✅ Produto "${product.name}" adicionado ao carrinho do backend`);
            updateCartCount();
        } else {
            console.error('❌ Erro ao adicionar ao carrinho:', result.error);
        }
    } catch (error) {
        console.error('❌ Erro ao adicionar ao carrinho do backend:', error);
    }
}

function addToLocalCart(product) {
    const cart = getCart();
    
    // Procurar apenas por product_ID (campo único)
    const existingItem = cart.find(item => 
        item.product_ID === product.product_ID
    );

    if (existingItem) {
        // DEDUPLICATION: Increment quantity instead of adding duplicate
        existingItem.quantity = (existingItem.quantity || 1) + 1;
        console.log(`✅ Produto "${product.name}" incrementado para quantidade ${existingItem.quantity}`);
    } else {
        // New item - adicionar com product_ID como identificador único
        const cartItem = {
            product_ID: product.product_ID,
            name: product.name,
            price: product.price,
            image_url: product.image_url,
            store: product.store,
            affiliate_link: product.affiliate_link,
            quantity: 1
        };
        cart.push(cartItem);
        console.log(`✅ Novo produto "${product.name}" adicionado ao carrinho`);
    }

    saveCart(cart);
}

function removeFromCart(productId) {
    const isAuthenticated = localStorage.getItem('authToken');
    
    if (isAuthenticated) {
        removeFromBackendCart(productId);
    } else {
        removeFromLocalCart(productId);
    }
}

async function removeFromBackendCart(productId) {
    try {
        const result = await apiCall('/carrinho/remover/', {
            method: 'POST',
            body: JSON.stringify({
                product_ID: productId
            })
        });
        
        if (result.success) {
            console.log(`✅ Produto ${productId} removido do carrinho do backend`);
            updateCartCount();
        } else {
            console.error('❌ Erro ao remover do carrinho:', result.error);
        }
    } catch (error) {
        console.error('❌ Erro ao remover do carrinho do backend:', error);
    }
}

function removeFromLocalCart(productId) {
    let cart = getCart();
    const initialLength = cart.length;
    cart = cart.filter(item => 
        item.product_ID !== productId
    );
    if (cart.length < initialLength) {
        console.log(`✅ Produto ${productId} removido do carrinho`);
    } else {
        console.warn(`⚠️ Produto ${productId} não encontrado no carrinho`);
    }
    saveCart(cart);
}

function updateCartItemQuantity(productId, quantity) {
    const isAuthenticated = localStorage.getItem('authToken');
    
    if (isAuthenticated) {
        updateBackendCartQuantity(productId, quantity);
    } else {
        updateLocalCartQuantity(productId, quantity);
    }
}

async function updateBackendCartQuantity(productId, quantity) {
    try {
        if (quantity <= 0) {
            removeFromBackendCart(productId);
        } else {
            // Remover e re-adicionar com nova quantidade
            await apiCall('/carrinho/remover/', {
                method: 'POST',
                body: JSON.stringify({ product_ID: productId })
            });
            
            for (let i = 0; i < quantity; i++) {
                await apiCall('/carrinho/adicionar/', {
                    method: 'POST',
                    body: JSON.stringify({
                        product_ID: productId,
                        quantidade: 1
                    })
                });
            }
            console.log(`✅ Quantidade do produto ${productId} atualizada para ${quantity}`);
            updateCartCount();
        }
    } catch (error) {
        console.error('❌ Erro ao atualizar quantidade no backend:', error);
    }
}

function updateLocalCartQuantity(productId, quantity) {
    const cart = getCart();
    const item = cart.find(item => 
        item.product_ID === productId
    );

    if (item) {
        if (quantity <= 0) {
            removeFromCart(productId);
        } else {
            item.quantity = quantity;
            console.log(`✅ Quantidade do produto ${productId} atualizada para ${quantity}`);
            saveCart(cart);
        }
    } else {
        console.warn(`⚠️ Produto ${productId} não encontrado no carrinho`);
    }
}

function clearCart() {
    const isAuthenticated = localStorage.getItem('authToken');
    
    if (isAuthenticated) {
        clearBackendCart();
    } else {
        localStorage.removeItem('cart');
        updateCartCount();
    }
}

async function clearBackendCart() {
    try {
        const result = await apiCall('/carrinho/limpar/', {
            method: 'POST'
        });
        
        if (result.success) {
            console.log('✅ Carrinho do backend foi limpo');
        }
    } catch (error) {
        console.error('❌ Erro ao limpar carrinho do backend:', error);
    }
    updateCartCount();
}

// ===============================
// CART UI UPDATES
// ===============================

async function updateCartCount() {
    try {
        // Se autenticado, pegar do backend; caso contrário, do localStorage
        let totalItems = 0;
        
        if (localStorage.getItem('authToken')) {
            // Pegar do backend
            const cart = await getCart();
            if (Array.isArray(cart)) {
                totalItems = cart.length;
            }
        } else {
            // Pegar do localStorage
            const cartData = localStorage.getItem('cart');
            const items = cartData ? JSON.parse(cartData) : [];
            if (Array.isArray(items)) {
                totalItems = items.reduce((sum, item) => sum + (item.quantity || 1), 0);
            }
        }
        
        const cartCountElements = document.querySelectorAll('#cart-count');
        cartCountElements.forEach(el => {
            el.textContent = totalItems;
        });
    } catch (error) {
        console.error('⚠️ Erro ao atualizar contagem do carrinho:', error);
        const cartCountElements = document.querySelectorAll('#cart-count');
        cartCountElements.forEach(el => {
            el.textContent = '0';
        });
    }
}

// ===============================
// AUTHENTICATION STATE
// ===============================

function getAuthToken() {
    return localStorage.getItem('authToken');
}

function setAuthToken(token) {
    localStorage.setItem('authToken', token);
}

function isUserLoggedIn() {
    return !!getAuthToken();
}

function getCurrentUser() {
    try {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    } catch (error) {
        console.error('⚠️ Erro ao ler usuário do localStorage:', error);
        return null;
    }
}

function setCurrentUser(user) {
    try {
        localStorage.setItem('user', JSON.stringify(user));
    } catch (error) {
        console.error('⚠️ Erro ao salvar usuário no localStorage:', error);
    }
}

// ===============================
// UTILITY FUNCTIONS
// ===============================

function formatPrice(price) {
    const num = parseFloat(price);
    return isNaN(num) ? 'R$ 0,00' : num.toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    });
}

function truncateText(text, maxLength = 100) {
    if (text.length > maxLength) {
        return text.substring(0, maxLength) + '...';
    }
    return text;
}

// Inicializar contagem do carrinho ao carregar a página
document.addEventListener('DOMContentLoaded', updateCartCount);
