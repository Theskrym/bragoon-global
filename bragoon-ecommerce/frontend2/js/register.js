// ===========================
// REGISTER PAGE SCRIPT
// ===========================

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('register-form');
    if (form) {
        form.addEventListener('submit', handleRegisterSubmit);
    }

    // Validação de senhas em tempo real
    const passwordInput = document.getElementById('password');
    const passwordConfirm = document.getElementById('password-confirm');

    if (passwordInput && passwordConfirm) {
        passwordConfirm.addEventListener('change', () => {
            if (passwordInput.value !== passwordConfirm.value) {
                passwordConfirm.setCustomValidity('As senhas não conferem');
            } else {
                passwordConfirm.setCustomValidity('');
            }
        });
    }
});

async function handleRegisterSubmit(e) {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('password').value;
    const passwordConfirm = document.getElementById('password-confirm').value;

    const messageBox = document.getElementById('register-message');

    // Validações
    if (!username || !email || !password || !passwordConfirm) {
        showMessage(messageBox, 'Por favor, preencha todos os campos obrigatórios.', 'error');
        return;
    }

    if (!isValidEmail(email)) {
        showMessage(messageBox, 'Email inválido.', 'error');
        return;
    }

    if (password.length < 4) {
        showMessage(messageBox, 'A senha deve ter no mínimo 4 caracteres.', 'error');
        return;
    }

    // Verificar se a senha tem letra e número (requisito do backend)
    const hasLetter = /[a-zA-Z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    
    if (!hasLetter || !hasNumber) {
        showMessage(messageBox, 'A senha deve conter letras e números.', 'error');
        return;
    }

    if (password !== passwordConfirm) {
        showMessage(messageBox, 'As senhas não conferem.', 'error');
        return;
    }

    try {
        const userData = {
            username: username,
            email: email,
            password: password,
            first_name: '',
            last_name: ''
        };

        const result = await registerUser(userData);

        if (result.success) {
            showMessage(messageBox, 'Cadastro realizado com sucesso! Redirecionando para login...', 'success');

            // Auto-preencher email no login
            localStorage.setItem('rememberUser', email);

            // Redirecionar após 2 segundos
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
        } else {
            showMessage(messageBox, result.error || 'Erro ao criar a conta. Tente novamente.', 'error');
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

function isValidPhone(phone) {
    // Simples validação: deve ter entre 10 e 15 dígitos
    const phoneRegex = /^\(?(\d{2})\)?\s?(\d{4,5})-?(\d{4})$/;
    return phoneRegex.test(phone.replace(/\s/g, ''));
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
