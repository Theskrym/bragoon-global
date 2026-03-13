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

    const firstName = document.getElementById('first-name').value;
    const lastName = document.getElementById('last-name').value;
    const email = document.getElementById('reg-email').value;
    const phone = document.getElementById('phone').value;
    const password = document.getElementById('password').value;
    const passwordConfirm = document.getElementById('password-confirm').value;
    const address = document.getElementById('address').value;
    const city = document.getElementById('city').value;
    const state = document.getElementById('state').value;
    const zip = document.getElementById('zip').value;
    const newsletter = document.getElementById('newsletter').checked;
    const terms = document.getElementById('terms-accept').checked;

    const messageBox = document.getElementById('register-message');

    // Validações
    if (!firstName || !lastName || !email || !password || !passwordConfirm || !address || !city || !state || !zip) {
        showMessage(messageBox, 'Por favor, preencha todos os campos obrigatórios.', 'error');
        return;
    }

    if (!isValidEmail(email)) {
        showMessage(messageBox, 'Email inválido.', 'error');
        return;
    }

    if (password.length < 6) {
        showMessage(messageBox, 'A senha deve ter no mínimo 6 caracteres.', 'error');
        return;
    }

    if (password !== passwordConfirm) {
        showMessage(messageBox, 'As senhas não conferem.', 'error');
        return;
    }

    if (!terms) {
        showMessage(messageBox, 'Você deve concordar com os Termos de Serviço.', 'error');
        return;
    }

    if (phone && !isValidPhone(phone)) {
        showMessage(messageBox, 'Telefone inválido.', 'error');
        return;
    }

    try {
        const userData = {
            first_name: firstName,
            last_name: lastName,
            email: email,
            phone: phone || null,
            password: password,
            address: address,
            city: city,
            state: state,
            zip: zip,
            newsletter: newsletter,
            terms_accepted: terms
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
