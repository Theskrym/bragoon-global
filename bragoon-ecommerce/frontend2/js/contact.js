// ===========================
// CONTACT PAGE SCRIPT
// ===========================

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('contact-form');
    if (form) {
        form.addEventListener('submit', handleContactSubmit);
    }
});

async function handleContactSubmit(e) {
    e.preventDefault();

    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const phone = document.getElementById('phone').value;
    const subject = document.getElementById('subject').value;
    const message = document.getElementById('message').value;
    const terms = document.getElementById('terms').checked;

    const messageBox = document.getElementById('contact-message');

    // Validações
    if (!name || !email || !subject || !message) {
        showMessage(messageBox, 'Por favor, preencha todos os campos obrigatórios.', 'error');
        return;
    }

    if (name.length < 3) {
        showMessage(messageBox, 'Nome deve ter no mínimo 3 caracteres.', 'error');
        return;
    }

    if (!isValidEmail(email)) {
        showMessage(messageBox, 'Email inválido.', 'error');
        return;
    }

    if (message.length < 10) {
        showMessage(messageBox, 'Mensagem deve ter no mínimo 10 caracteres.', 'error');
        return;
    }

    if (phone && !isValidPhone(phone)) {
        showMessage(messageBox, 'Telefone inválido.', 'error');
        return;
    }

    if (!terms) {
        showMessage(messageBox, 'Você deve concordar em receber respostas por email.', 'error');
        return;
    }

    try {
        // Desabilitar botão durante envio
        const submitBtn = document.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = 'Enviando...';

        const formData = {
            name: name,
            email: email,
            phone: phone || null,
            subject: subject,
            message: message,
            consent: terms
        };

        const result = await submitContactForm(formData);

        if (result.success) {
            showMessage(messageBox, 'Mensagem enviada com sucesso! Entraremos em contato em breve.', 'success');
            
            // Limpar formulário
            document.getElementById('contact-form').reset();

            // Reabilitar botão
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;

            // Auto-hide mensagem após 5 segundos
            setTimeout(() => {
                messageBox.style.display = 'none';
            }, 5000);
        } else {
            showMessage(messageBox, result.error || 'Erro ao enviar mensagem. Tente novamente.', 'error');
            
            // Reabilitar botão
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    } catch (error) {
        console.error('Erro:', error);
        showMessage(messageBox, 'Erro ao conectar com o servidor.', 'error');

        // Reabilitar botão
        const submitBtn = document.querySelector('button[type="submit"]');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Enviar Mensagem';
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidPhone(phone) {
    // Validação simples para telefone brasileiro
    const phoneRegex = /^\(?(\d{2})\)?\s?(\d{4,5})-?(\d{4})$/;
    return phoneRegex.test(phone.replace(/\s/g, ''));
}

function showMessage(element, message, type) {
    if (!element) return;

    element.textContent = message;
    element.className = `message-box ${type}`;
    element.style.display = 'block';

    // Scroll até a mensagem
    element.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}
