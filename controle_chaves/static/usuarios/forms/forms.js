document.addEventListener("DOMContentLoaded", function() {
    
    // ==========================================
    // 1. LÓGICA DO ALERTA FLUTUANTE
    // ==========================================
    function mostrarAlertaFlutuante(mensagem, tipo) {
        let container = document.getElementById('container-alertas-globais');
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

        setTimeout(() => {
            alerta.classList.remove('show');
            setTimeout(() => alerta.remove(), 150);
        }, 4000);
    }

    const messageElements = document.querySelectorAll('.django-message');
    if (messageElements.length > 0) {
        const msgElement = messageElements[0];
        const msgText = msgElement.getAttribute('data-text');
        const msgTags = msgElement.getAttribute('data-tags') || '';
        
        if (msgText) {
            const tipoAlerta = msgTags.includes('error') ? 'danger' : 'success';
            mostrarAlertaFlutuante(msgText, tipoAlerta);
        }
    }

    // ==========================================
    // 2. LÓGICA DA MÁSCARA DE TELEFONE
    // ==========================================
    // Agora procura pelo name em vez do ID (muito mais seguro no Django)
    const inputTelefone = document.querySelector('input[name="telefone"]');
    
    if (inputTelefone) {
        // Limita o tamanho máximo para 15 caracteres: (XX) XXXXX-XXXX
        inputTelefone.setAttribute('maxlength', '15');
        
        inputTelefone.addEventListener('input', function(e) {
            // Remove tudo o que não for número
            let value = e.target.value.replace(/\D/g, ''); 
            
            // Aplica a formatação
            value = value.replace(/^(\d{2})(\d)/g, '($1) $2'); // Coloca parênteses no DDD
            value = value.replace(/(\d)(\d{4})$/, '$1-$2');   // Coloca o hífen antes dos 4 últimos dígitos
            
            // Atualiza o valor do input com a máscara
            e.target.value = value;
        });
    } else {
        console.warn("Campo de telefone não foi encontrado na página.");
    }

});