document.addEventListener("DOMContentLoaded", function() {
    
    // 1. SISTEMA GLOBAL DE NOTIFICAÇÕES
    const containerMensagens = document.getElementById('django-mensagens-sistema');
    
    if (containerMensagens) {
        const mensagens = containerMensagens.querySelectorAll('.msg-item');
        
        mensagens.forEach(msg => {
            const tag = msg.getAttribute('data-tag');
            const texto = msg.getAttribute('data-text');

            let tipoIcone = 'info';
            let titulo = 'Atenção';

            if (tag.includes('success')) {
                tipoIcone = 'success';
                titulo = 'Sucesso!';
            } else if (tag.includes('error')) {
                tipoIcone = 'error';
                titulo = 'Erro!';
            }

            Swal.fire({
                icon: tipoIcone,
                title: titulo,
                text: texto,
                confirmButtonColor: '#28a745',
                timer: 3500,
                timerProgressBar: true
            });
        });
    }

    // 2. TRAVA DE BOTÃO (Evita salvar duas vezes)
    const formularios = document.querySelectorAll('.form-processando');
    
    formularios.forEach(form => {
        form.addEventListener('submit', function() {
            let btnSubmit = this.querySelector('button[type="submit"]');
            if (btnSubmit) {
                btnSubmit.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Processando...';
                btnSubmit.disabled = true;
            }
        });
    });
});