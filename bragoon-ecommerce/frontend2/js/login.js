// ===========================
// LOGIN PAGE SCRIPT
// ===========================

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('login-form');
    if (form) {
        form.addEventListener('submit', handleLoginSubmit);
    }
});

async function handleLoginSubmit(e) {
    e.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const remember = document.getElementById('remember').checked;

    const messageBox = document.getElementById('login-message');

    // Validações básicas
    if (!email || !password) {
        showMessage(messageBox, 'Por favor, preencha todos os campos.', 'error');
        return;
    }

    if (!isValidEmail(email)) {
        showMessage(messageBox, 'Email inválido.', 'error');
        return;
    }

    try {
        const result = await loginUser(email, password);

        if (result.success && result.data) {
            // Armazenar token e dados do usuário
            if (result.data.token) {
                setAuthToken(result.data.token);
            }

            if (result.data.user) {
                setCurrentUser(result.data.user);
            }

            // Se marcou "lembrar de mim"
            if (remember) {
                localStorage.setItem('rememberUser', email);
            }

            showMessage(messageBox, 'Login realizado com sucesso! Redirecionando...', 'success');

            // Redirecionar após 2 segundos
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 2000);
        } else {
            showMessage(messageBox, result.error || 'Erro ao fazer login. Verifique suas credenciais.', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showMessage(messageBox, 'Erro ao conectar com o servidor.', 'error');
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function showMessage(element, message, type) {
    if (!element) return;

    element.textContent = message;
    element.className = `message-box ${type}`;
    element.style.display = 'block';

    // Auto-hide mensagens de sucesso após 5 segundos
    if (type === 'success') {
        setTimeout(() => {
            element.style.display = 'none';
        }, 5000);
    }
}

// Auto-preencher email se estava marcado "lembrar de mim"
document.addEventListener('DOMContentLoaded', () => {
    const rememberUser = localStorage.getItem('rememberUser');
    if (rememberUser) {
        const emailInput = document.getElementById('email');
        if (emailInput) {
            emailInput.value = rememberUser;
        }
    }
});
