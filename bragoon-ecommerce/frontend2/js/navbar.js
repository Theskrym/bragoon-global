// ===========================
// NAVBAR AUTHENTICATION STATE
// ===========================

document.addEventListener('DOMContentLoaded', () => {
    // Esperar um pouco para auth.js inicializar
    setTimeout(() => {
        updateNavbarAuthState();
        // Carregar avatar após 500ms para garantir que DOM está pronto
        if (isAuthenticated()) {
            setTimeout(() => loadUserAvatar(), 500);
        }
    }, 100);
});

// Observar mudanças no localStorage
window.addEventListener('storage', () => {
    updateNavbarAuthState();
});

function updateNavbarAuthState() {
    // Usar auth.isAuthenticated() do AuthManager
    const isAuth = typeof auth !== 'undefined' ? auth.isAuthenticated() : !!getAuthToken();
    const loginBtn = document.querySelector('.btn-login');
    
    if (!loginBtn) return;
    
    if (isAuth) {
        // Usuário está autenticado - ocultar botão de login padrão
        const liElement = loginBtn.closest('li');
        if (liElement) {
            liElement.style.display = 'none';
        }
        
        // Criar container de perfil se não existir
        let profileContainer = document.querySelector('.navbar-profile-container');
        if (!profileContainer) {
            const navMenu = document.querySelector('.nav-menu');
            const cartIcon = document.querySelector('.cart-icon');
            
            profileContainer = document.createElement('div');
            profileContainer.className = 'navbar-profile-container';
            profileContainer.innerHTML = `
                <a href="perfil.html" class="navbar-profile-avatar" title="Meu Perfil">
                    <img src="https://via.placeholder.com/40" alt="Perfil" class="navbar-avatar-img" />
                </a>
            `;
            
            // Inserir antes do cart-icon
            if (cartIcon) {
                cartIcon.parentElement.insertBefore(profileContainer, cartIcon);
            } else {
                navMenu.parentElement.appendChild(profileContainer);
            }
        }
        
        // Carregar avatar
        loadUserAvatar();
    } else {
        // Usuário não autenticado - mostrar botão de login
        loginBtn.textContent = 'Login';
        loginBtn.href = 'login.html';
        
        const liElement = loginBtn.closest('li');
        if (liElement) {
            liElement.style.display = 'block';
        }
        
        // Remover container de perfil
        const profileContainer = document.querySelector('.navbar-profile-container');
        if (profileContainer) {
            profileContainer.remove();
        }
    }
}

async function loadUserAvatar() {
    const token = getAuthToken();
    if (!token) return;
    
    try {
        // Buscar dados do perfil do backend
        const apiUrl = typeof API_BASE_URL !== 'undefined' ? API_BASE_URL : 'http://localhost:8000/api';
        const response = await fetch(apiUrl + '/perfil/', {
            method: 'GET',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            updateNavbarAvatar(data);
        } else {
            updateNavbarAvatarFallback();
        }
    } catch (error) {
        console.warn('⚠️ Erro ao carregar avatar:', error);
        updateNavbarAvatarFallback();
    }
}

function updateNavbarAvatar(profileData) {
    const avatarImg = document.querySelector('.navbar-avatar-img');
    if (avatarImg && profileData.avatar_url) {
        avatarImg.src = profileData.avatar_url;
        avatarImg.alt = 'Foto de perfil';
    } else {
        updateNavbarAvatarFallback();
    }
}

function updateNavbarAvatarFallback() {
    const user = getCurrentUser();
    const avatarImg = document.querySelector('.navbar-avatar-img');
    
    if (avatarImg && user) {
        // Usar iniciais do usuário como fallback
        const firstName = user.first_name || '';
        const lastName = user.last_name || '';
        const fullName = (firstName + ' ' + lastName).trim();
        avatarImg.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(fullName)}&background=667eea&color=fff&bold=true&size=40`;
    }
}

function refreshNavbarAvatar() {
    // Recarregar avatar da navbar (chamado após upload de foto em perfil.js)
    loadUserAvatar();
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
