// ===========================
// PROFILE PAGE SCRIPT
// ===========================

const API_URL = 'http://localhost:8000/api/perfil/';

document.addEventListener('DOMContentLoaded', () => {
    loadUserProfile();
    setupAvatarUpload();
    setupFormSubmit();
    updateCartCount();
});

// Load user profile data
async function loadUserProfile() {
    const token = getAuthToken();
    
    if (!token) {
        showMessage('Você precisa estar logado para acessar o perfil.', 'error');
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 2000);
        return;
    }

    try {
        const response = await fetch(API_URL, {
            method: 'GET',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            populateProfileForm(data);
        } else if (response.status === 401) {
            showMessage('Sessão expirada. Faça login novamente.', 'error');
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
        }
    } catch (error) {
        console.error('Erro ao carregar perfil:', error);
        showMessage('Erro ao carregar dados do perfil.', 'error');
    }

    // Load user info from localStorage
    const user = getCurrentUser();
    if (user) {
        document.getElementById('user-name').textContent = 
            `${user.first_name || user.username} ${user.last_name || ''}`.trim();
        document.getElementById('user-email').textContent = user.email;
        document.getElementById('email').value = user.email;
        
        // Format date
        const joinDate = new Date(user.id);
        document.getElementById('user-since').textContent = 
            joinDate.toLocaleDateString('pt-BR', { year: 'numeric', month: 'long', day: 'numeric' });
    }
}

// Populate form with profile data
function populateProfileForm(data) {
    if (data.bio) document.getElementById('bio').value = data.bio;
    if (data.telefone) document.getElementById('telefone').value = data.telefone;
    if (data.endereco) document.getElementById('endereco').value = data.endereco;
    if (data.cidade) document.getElementById('cidade').value = data.cidade;
    if (data.estado) document.getElementById('estado').value = data.estado;
    if (data.cep) document.getElementById('cep').value = data.cep;

    // Load avatar if exists
    if (data.avatar) {
        const avatarPreview = document.getElementById('avatar-preview');
        avatarPreview.innerHTML = '';
        const img = document.createElement('img');
        img.src = data.avatar;
        img.alt = 'Avatar do usuário';
        avatarPreview.appendChild(img);
        
        // Store avatar URL in session
        sessionStorage.setItem('userAvatar', data.avatar);
    }
}

// Setup avatar upload
function setupAvatarUpload() {
    const avatarInput = document.getElementById('avatar-input');
    
    avatarInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        // Validate file type
        if (!file.type.startsWith('image/')) {
            showMessage('Por favor, selecione uma imagem válida.', 'error');
            return;
        }

        // Validate file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            showMessage('A imagem deve ter no máximo 5MB.', 'error');
            return;
        }

        // Preview image
        const reader = new FileReader();
        reader.onload = (event) => {
            const avatarPreview = document.getElementById('avatar-preview');
            avatarPreview.innerHTML = '';
            const img = document.createElement('img');
            img.src = event.target.result;
            img.alt = 'Preview da nova avatar';
            avatarPreview.appendChild(img);
            
            // Auto-save avatar
            uploadAvatar(file);
        };
        reader.readAsDataURL(file);
    });
}

// Upload avatar to server
async function uploadAvatar(file) {
    const token = getAuthToken();
    const formData = new FormData();
    formData.append('avatar', file);

    try {
        const response = await fetch(API_URL, {
            method: 'PATCH',
            headers: {
                'Authorization': `Token ${token}`
            },
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            showMessage('✅ Foto de perfil atualizada com sucesso!', 'success');
            sessionStorage.setItem('userAvatar', data.avatar);
        } else {
            showMessage('Erro ao fazer upload da foto.', 'error');
        }
    } catch (error) {
        console.error('Erro ao fazer upload:', error);
        showMessage('Erro ao conectar com o servidor.', 'error');
    }
}

// Remove avatar
async function removeAvatar() {
    const token = getAuthToken();
    
    try {
        const response = await fetch(API_URL, {
            method: 'PATCH',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ avatar: null })
        });

        if (response.ok) {
            const avatarPreview = document.getElementById('avatar-preview');
            avatarPreview.innerHTML = '👤';
            showMessage('✅ Foto de perfil removida!', 'success');
            sessionStorage.removeItem('userAvatar');
        } else {
            showMessage('Erro ao remover foto.', 'error');
        }
    } catch (error) {
        console.error('Erro ao remover avatar:', error);
        showMessage('Erro ao conectar com o servidor.', 'error');
    }
}

// Setup form submission
function setupFormSubmit() {
    const form = document.getElementById('profile-form');
    form.addEventListener('submit', handleProfileSubmit);
}

// Handle profile form submission
async function handleProfileSubmit(e) {
    e.preventDefault();

    const token = getAuthToken();
    
    const profileData = {
        bio: document.getElementById('bio').value,
        telefone: document.getElementById('telefone').value,
        endereco: document.getElementById('endereco').value,
        cidade: document.getElementById('cidade').value,
        estado: document.getElementById('estado').value,
        cep: document.getElementById('cep').value
    };

    try {
        const response = await fetch(API_URL, {
            method: 'PATCH',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(profileData)
        });

        if (response.ok) {
            showMessage('✅ Perfil atualizado com sucesso!', 'success');
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            const error = await response.json();
            showMessage('Erro ao atualizar perfil: ' + JSON.stringify(error), 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showMessage('Erro ao conectar com o servidor.', 'error');
    }
}

// Change password
function changePassword() {
    const newPassword = prompt('Digite sua nova senha:');
    if (!newPassword) return;

    if (newPassword.length < 4) {
        showMessage('A senha deve ter pelo menos 4 caracteres.', 'error');
        return;
    }

    // Validate password requirements
    const hasLetter = /[a-zA-Z]/.test(newPassword);
    const hasNumber = /[0-9]/.test(newPassword);

    if (!hasLetter || !hasNumber) {
        showMessage('Senha deve conter pelo menos 1 letra e 1 número.', 'error');
        return;
    }

    showMessage('Para alterar a senha, você será desconectado.', 'info');
    // Na prática, você precisaria criar um endpoint para mudar senha no backend
}

// Logout
function logout() {
    const confirm = window.confirm('Tem certeza que deseja sair da conta?');
    if (confirm) {
        localStorage.removeItem('authToken');
        localStorage.removeItem('currentUser');
        sessionStorage.removeItem('userAvatar');
        window.location.href = 'index.html';
    }
}

// Show message helper
function showMessage(message, type) {
    const messageBox = document.getElementById('message');
    messageBox.textContent = message;
    messageBox.className = `message ${type}`;
    
    if (type === 'success') {
        setTimeout(() => {
            messageBox.style.display = 'none';
        }, 5000);
    }
}

// Helper functions from auth.js
function getAuthToken() {
    return localStorage.getItem('authToken');
}

function getCurrentUser() {
    const userStr = localStorage.getItem('currentUser');
    return userStr ? JSON.parse(userStr) : null;
}

// Update cart count
function updateCartCount() {
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    const count = cart.length;
    document.getElementById('cart-count').textContent = count;
}
