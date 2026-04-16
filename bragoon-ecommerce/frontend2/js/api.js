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

    // Adicionar token de autenticação se existir - com tratamento de erro
    try {
        const authToken = localStorage.getItem('authToken');
        if (authToken && authToken !== 'undefined' && authToken.length > 0) {
            finalOptions.headers['Authorization'] = `Bearer ${authToken}`;
        }
    } catch (storageError) {
        console.warn('⚠️ Erro ao acessar localStorage para authToken:', storageError);
    }

    try {
        console.log('🌐 Fazendo requisição para:', url);
        const response = await fetch(url, finalOptions);
        
        if (!response.ok) {
            if (response.status === 401 && retries > 0) {
                // Token expirado ou inválido
                try {
                    localStorage.removeItem('authToken');
                    localStorage.removeItem('user');
                } catch (e) {
                    console.warn('⚠️ Erro ao limpar localStorage:', e);
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
// SEARCH & PRODUCT ENDPOINTS
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
        const result = await apiCall('/login/', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        
        if (result.success && result.data.token) {
            // Armazenar token e usuário
            try {
                localStorage.setItem('authToken', result.data.token);
                localStorage.setItem('user', JSON.stringify(result.data.user));
            } catch (storageError) {
                console.warn('⚠️ Erro ao armazenar no localStorage:', storageError);
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
// CART MANAGEMENT (LocalStorage)
// ===============================

function getCart() {
    try {
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

function saveCart(cart) {
    try {
        localStorage.setItem('cart', JSON.stringify(cart));
        updateCartCount();
    } catch (error) {
        console.error('⚠️ Erro ao salvar carrinho no localStorage:', error);
        try {
            localStorage.clear();
            localStorage.setItem('cart', JSON.stringify(cart));
        } catch (e) {
            console.error('⚠️ Erro ao limpar e resalvar no localStorage:', e);
        }
    }
}

function addToCart(product) {
    const cart = getCart();
    const existingItem = cart.find(item => 
        item.product_ID === product.product_ID || 
        item.id === product.id
    );

    if (existingItem) {
        existingItem.quantity = (existingItem.quantity || 1) + 1;
    } else {
        cart.push({
            ...product,
            quantity: 1
        });
    }

    saveCart(cart);
    return true;
}

function removeFromCart(productId) {
    let cart = getCart();
    cart = cart.filter(item => 
        item.product_ID !== productId && item.id !== productId
    );
    saveCart(cart);
}

function updateCartItemQuantity(productId, quantity) {
    const cart = getCart();
    const item = cart.find(item => 
        item.product_ID === productId || item.id === productId
    );

    if (item) {
        if (quantity <= 0) {
            removeFromCart(productId);
        } else {
            item.quantity = quantity;
            saveCart(cart);
        }
    }
}

function clearCart() {
    localStorage.removeItem('cart');
    updateCartCount();
}

// ===============================
// CART UI UPDATES
// ===============================

function updateCartCount() {
    try {
        const cart = getCart();
        const totalItems = cart.reduce((sum, item) => sum + (item.quantity || 1), 0);
        
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
