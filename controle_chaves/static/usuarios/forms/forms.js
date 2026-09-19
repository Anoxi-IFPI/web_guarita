document.addEventListener("DOMContentLoaded", function() {
    
    // Função para mostrar o alerta exatamente no padrão que você já usa
    function mostrarAlertaFlutuante(mensagem, tipo) {
        // 1. Procura o container na página. Se não existir, cria e joga no body
        let container = document.getElementById('container-alertas-globais');
        if (!container) {
            container = document.createElement('div');
            container.id = 'container-alertas-globais';
            // Estilos embutidos para garantir que flutue no topo direito independente do HTML da tela
            container.style.cssText = "position: fixed; top: 20px; right: 20px; z-index: 9999; display: flex; flex-direction: column; gap: 10px; max-width: 350px;";
            document.body.appendChild(container);
        }

        // 2. Cria o alerta usando classes nativas do Bootstrap
        const alerta = document.createElement('div');
        alerta.className = `alert alert-${tipo} alert-dismissible fade show shadow-sm mb-0`;
        alerta.role = 'alert';
        
        // Define o ícone com base no tipo
        const icone = tipo === 'success' ? 'fa-check-circle' : 'fa-exclamation-triangle';
        
        // Insere o HTML igualzinho ao seu código original
        alerta.innerHTML = `
            <i class="fas ${icone} me-2"></i> ${mensagem}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // 3. Joga o alerta na tela
        container.appendChild(alerta);

        // 4. Temporizador: some suavemente em 4 segundos
        setTimeout(() => {
            alerta.classList.remove('show');
            setTimeout(() => alerta.remove(), 150); // espera o CSS de fade out terminar
        }, 4000);
    }

    // --- Lógica para pegar mensagens geradas pelo Python/Django ---
    const messageElements = document.querySelectorAll('.django-message');
    
    if (messageElements.length > 0) {
        // Pega a primeira mensagem
        const msgElement = messageElements[0];
        const msgText = msgElement.getAttribute('data-text');
        const msgTags = msgElement.getAttribute('data-tags') || '';
        
        if (msgText) {
            // Se as tags do Django tiverem 'error', usa danger (vermelho do Bootstrap), senão success (verde)
            const tipoAlerta = msgTags.includes('error') ? 'danger' : 'success';
            
            // Chama a nova função que acabamos de criar
            mostrarAlertaFlutuante(msgText, tipoAlerta);
        }
    }
});