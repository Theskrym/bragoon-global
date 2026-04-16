// ===========================
// NAVBAR AUTHENTICATION STATE
// ===========================

document.addEventListener('DOMContentLoaded', () => {
    updateNavbarAuthState();
});

// Observar mudanças no localStorage
window.addEventListener('storage', () => {
    updateNavbarAuthState();
});

function updateNavbarAuthState() {
    const authToken = getAuthToken();
    const loginBtn = document.querySelector('.btn-login');
    
    if (!loginBtn) return;
    
    if (authToken) {
        // Usuário está autenticado - mostrar botão de perfil
        loginBtn.textContent = 'Perfil';
        loginBtn.href = 'perfil.html';
        loginBtn.classList.add('btn-profile');
    } else {
        // Usuário não autenticado - mostrar botão de login
        loginBtn.textContent = 'Login';
        loginBtn.href = 'login.html';
        loginBtn.classList.remove('btn-profile');
    }
}

// Helpers de autenticação
function getAuthToken() {
    try {
        return localStorage.getItem('authToken');
    } catch (error) {
        console.warn('⚠️ Erro ao acessar localStorage:', error);
        return null;
    }
}

function getCurrentUser() {
    try {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    } catch (error) {
        console.warn('⚠️ Erro ao recuperar usuário:', error);
        return null;
    }
}

function isAuthenticated() {
    return !!getAuthToken();
}
