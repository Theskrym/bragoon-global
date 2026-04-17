// ===========================
// AUTHENTICATION MANAGEMENT (LGPD-Compliant)
// ===========================

class AuthManager {
    constructor() {
        this.TOKEN_KEY = 'authToken';
        this.USER_KEY = 'user';
        this.CONSENT_KEY = 'consentimento_dados';
        this.listeners = [];
        
        // Sincronizar entre abas
        this.setupStorageSync();
        
        // Validar token ao carregar
        this.validateToken();
    }

    /**
     * Sincroniza autenticação entre múltiplas abas/janelas
     * Garante que logout/login em uma aba afeta as outras
     */
    setupStorageSync() {
        window.addEventListener('storage', (event) => {
            if (event.key === this.TOKEN_KEY || event.key === this.USER_KEY) {
                console.log('🔄 Sincronização de auth detectada entre abas');
                this.notifyListeners();
            }
        });
    }

    /**
     * Valida se o token armazenado ainda é válido
     * Verifica:
     * - Se token existe
     * - Se usuário consentiu com LGPD
     * - Se token não está vazio/undefined
     */
    validateToken() {
        try {
            const token = this.getToken();
            const user = this.getUser();
            const consent = this.getConsent();

            // Se não tem token, é normal (primeiro acesso)
            if (!token || token === 'undefined' || token.length === 0) {
                console.log('ℹ️ Sem token armazenado (usuário não autenticado)');
                return false;
            }

            // Se tem token mas não tem usuário, algo está errado
            if (token && !user) {
                console.warn('⚠️ Token existe mas não tem usuário - limpando');
                this.logout();
                return false;
            }

            // Verificar se usuário consentiu com LGPD
            if (user && !consent) {
                console.warn('⚠️ Usuário não consentiu com LGPD - requer nova autenticação');
                this.logout();
                return false;
            }

            console.log('✅ Token válido e usuário autenticado');
            return true;
        } catch (error) {
            console.error('❌ Erro ao validar token:', error);
            return false;
        }
    }

    /**
     * Obtém token de autenticação do localStorage
     * @returns {string|null} Token ou null se não existir
     */
    getToken() {
        try {
            return localStorage.getItem(this.TOKEN_KEY);
        } catch (error) {
            console.error('❌ Erro ao acessar token:', error);
            return null;
        }
    }

    /**
     * Obtém dados do usuário do localStorage
     * @returns {Object|null} Dados do usuário ou null
     */
    getUser() {
        try {
            const userData = localStorage.getItem(this.USER_KEY);
            return userData ? JSON.parse(userData) : null;
        } catch (error) {
            console.error('❌ Erro ao parsear dados do usuário:', error);
            return null;
        }
    }

    /**
     * Obtém consentimento LGPD
     * @returns {boolean} True se usuário consentiu
     */
    getConsent() {
        try {
            return localStorage.getItem(this.CONSENT_KEY) === 'true';
        } catch (error) {
            console.error('❌ Erro ao acessar consentimento:', error);
            return false;
        }
    }

    /**
     * Define token e dados de usuário após login bem-sucedido
     * Valida consentimento LGPD antes de armazenar
     * @param {string} token - Token JWT/Token do backend
     * @param {Object} user - Dados do usuário
     * @param {boolean} consent - Consentimento com LGPD
     */
    setAuth(token, user, consent = true) {
        try {
            if (!token || token.length === 0) {
                throw new Error('Token inválido');
            }

            console.log('💾 Salvando token:', token.substring(0, 20) + '...');
            console.log('👤 Salvando usuário:', user.email);

            localStorage.setItem(this.TOKEN_KEY, token);
            localStorage.setItem(this.USER_KEY, JSON.stringify(user));
            localStorage.setItem(this.CONSENT_KEY, consent ? 'true' : 'false');

            // Verificar se foi salvo corretamente
            const savedToken = localStorage.getItem(this.TOKEN_KEY);
            const savedUser = localStorage.getItem(this.USER_KEY);
            
            console.log('✅ Token salvo?', !!savedToken);
            console.log('✅ Usuário salvo?', !!savedUser);
            console.log('✅ Consentimento LGPD:', consent);

            this.notifyListeners();
        } catch (error) {
            console.error('❌ Erro ao armazenar autenticação:', error);
            throw error;
        }
    }

    /**
     * Verifica se usuário está autenticado
     * @returns {boolean} True se autenticado e válido
     */
    isAuthenticated() {
        const token = this.getToken();
        const user = this.getUser();
        return !!token && !!user && this.validateToken();
    }

    /**
     * Faz logout: limpa token, dados do usuário e consentimento
     * Em conformidade com LGPD: permite revogação de consentimento
     */
    logout() {
        try {
            console.log('🚪 Realizando logout...');
            localStorage.removeItem(this.TOKEN_KEY);
            localStorage.removeItem(this.USER_KEY);
            localStorage.removeItem(this.CONSENT_KEY);
            localStorage.removeItem('cart'); // Limpar carrinho também
            
            console.log('✅ Logout realizado - dados pessoais removidos');
            this.notifyListeners();
        } catch (error) {
            console.error('❌ Erro ao fazer logout:', error);
        }
    }

    /**
     * Revoga consentimento LGPD e faz logout
     * Usuário pode revogar dados a qualquer momento (direito LGPD)
     */
    revokeConsent() {
        try {
            const user = this.getUser();
            if (user) {
                console.log('📋 Revogando consentimento LGPD para:', user.email);
            }
            this.logout();
            // Aqui você poderia notificar o backend para deletar dados pessoais
            // await fetch('/api/gdpr/revoke-consent/', { method: 'POST', headers: authHeaders })
        } catch (error) {
            console.error('❌ Erro ao revogar consentimento:', error);
        }
    }

    /**
     * Obtém headers de autorização para requisições
     * Usa formato "Token" do Django REST Framework (não Bearer)
     * @returns {Object} Headers com token
     */
    getAuthHeaders() {
        const token = this.getToken();
        return {
            'Authorization': token ? `Token ${token}` : '',
            'Content-Type': 'application/json'
        };
    }

    /**
     * Registra listener para mudanças de autenticação
     * Permite que componentes reajam quando auth muda
     * @param {Function} callback - Função chamada quando auth muda
     */
    onChange(callback) {
        if (typeof callback === 'function') {
            this.listeners.push(callback);
        }
    }

    /**
     * Remove listener
     * @param {Function} callback - Função a remover
     */
    removeListener(callback) {
        this.listeners = this.listeners.filter(l => l !== callback);
    }

    /**
     * Notifica todos os listeners sobre mudança de autenticação
     */
    notifyListeners() {
        const isAuth = this.isAuthenticated();
        const user = this.getUser();
        this.listeners.forEach(callback => {
            try {
                callback(isAuth, user);
            } catch (error) {
                console.error('❌ Erro ao executar listener de auth:', error);
            }
        });
    }

    /**
     * Limpa dados expirados (limpeza periódica)
     * LGPD: Não manter dados por mais tempo que o necessário
     */
    cleanup() {
        try {
            // Se não há token válido há mais de 24h, limpar
            const lastValidated = localStorage.getItem('lastAuthValidation');
            if (lastValidated) {
                const ageMs = Date.now() - parseInt(lastValidated);
                const age24h = 24 * 60 * 60 * 1000;
                
                if (ageMs > age24h && !this.getToken()) {
                    console.log('🧹 Limpando dados de autenticação expirados');
                    this.logout();
                }
            }
        } catch (error) {
            console.error('⚠️ Erro ao limpar dados expirados:', error);
        }
    }

    /**
     * Exporta dados do usuário (direito LGPD de portabilidade)
     * @returns {Object} Todos os dados pessoais armazenados
     */
    exportUserData() {
        try {
            return {
                user: this.getUser(),
                consentimento: this.getConsent(),
                exportedAt: new Date().toISOString(),
                dataPortability: 'Este é um relatório de portabilidade de dados conforme LGPD Art. 20'
            };
        } catch (error) {
            console.error('❌ Erro ao exportar dados:', error);
            return null;
        }
    }
}

// Instância global do AuthManager
const auth = new AuthManager();

// Executar limpeza a cada hora
setInterval(() => {
    auth.cleanup();
}, 60 * 60 * 1000);

// Log inicial (development)
console.log('🔐 Auth Manager inicializado');

// Debug: verificar estado inicial do localStorage
try {
    const token = localStorage.getItem('authToken');
    const user = localStorage.getItem('user');
    const consent = localStorage.getItem('consentimento_dados');
    
    console.log('📊 Estado inicial do localStorage:');
    console.log('  - Token existe?', !!token);
    console.log('  - Tamanho token:', token ? token.length : 0);
    console.log('  - User existe?', !!user);
    console.log('  - Consent:', consent);
} catch (e) {
    console.error('Erro ao verificar localStorage:', e);
}

console.log('👤 Autenticado:', auth.isAuthenticated());
console.log('📋 Consentimento LGPD:', auth.getConsent());

// Helpers para compatibilidade com código existente
function getAuthToken() {
    return auth.getToken();
}

function getCurrentUser() {
    return auth.getUser();
}

function isAuthenticated() {
    return auth.isAuthenticated();
}

function logoutUser() {
    auth.logout();
    window.location.href = 'login.html';
}
