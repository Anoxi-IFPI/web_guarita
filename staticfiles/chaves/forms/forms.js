document.addEventListener("DOMContentLoaded", function() {
    
    // Função pura em JS para criar o alerta visual flutuante
    function mostrarAlertaFlutuante(mensagem, tipo) {
        let container = document.getElementById('container-alertas-globais');
        
        // Se o container não existir, cria e injeta no body
        if (!container) {
            container = document.createElement('div');
            container.id = 'container-alertas-globais';
            container.style.cssText = "position: fixed; top: 20px; right: 20px; z-index: 9999; display: flex; flex-direction: column; gap: 10px; max-width: 350px;";
            document.body.appendChild(container);
        }

        const alerta = document.createElement('div');
        alerta.className = `alert alert-${tipo} alert-dismissible fade show shadow-sm mb-0`;
        alerta.role = 'alert';
        
        const icone = tipo === 'success' ? 'fa-check-circle' : 'fa-exclamation-triangle';
        
        alerta.innerHTML = `
            <i class="fas ${icone} me-2"></i> ${mensagem}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        container.appendChild(alerta);

        // Remove da tela após 4 segundos
        setTimeout(() => {
            alerta.classList.remove('show');
            setTimeout(() => alerta.remove(), 150);
        }, 4000);
    }

    // --- A mágica acontece aqui: O JS "lê" os atributos do HTML gerado pelo Django ---
    const messageElements = document.querySelectorAll('.django-message');
    
    if (messageElements.length > 0) {
        messageElements.forEach(msgElement => {
            // Lê o texto e as tags do Django (success, error, etc)
            const msgText = msgElement.getAttribute('data-text');
            const msgTags = msgElement.getAttribute('data-tags') || '';
            
            if (msgText) {
                let tipoAlerta = 'info'; // Classe padrão do Bootstrap

                // Converte as tags do Django para as classes do Bootstrap
                if (msgTags.includes('error')) {
                    tipoAlerta = 'danger'; // Vermelho
                } else if (msgTags.includes('success')) {
                    tipoAlerta = 'success'; // Verde
                } else if (msgTags.includes('warning')) {
                    tipoAlerta = 'warning'; // Amarelo
                }
                
                // Dispara o alerta na tela
                mostrarAlertaFlutuante(msgText, tipoAlerta);
            }
        });
    }
});