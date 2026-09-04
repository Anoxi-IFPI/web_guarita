let debounceTimer;

function mostrarAlerta(mensagem, tipo) {
    const alertaContainer = document.getElementById('alerta_container');
    if(!alertaContainer) return;
    
    alertaContainer.innerHTML = `
        <div class="alert alert-${tipo} alert-dismissible fade show fs-5 shadow-sm" role="alert">
            <i class="fas ${tipo === 'success' ? 'fa-check-circle' : 'fa-exclamation-triangle'} me-2"></i>
            <strong>${mensagem}</strong>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    setTimeout(() => { alertaContainer.innerHTML = ''; }, 4000);
}

function adicionarChave(codigo) {
    const inputLeitor = document.getElementById('input_leitor');
    const tbodyChaves = document.getElementById('tbody_chaves');
    const elementoId = document.getElementById('hidden_usuario_id');
    const usuarioId = elementoId ? elementoId.value : null;

    if (codigo === '' || !usuarioId) return;

    inputLeitor.value = 'Processando...';
    inputLeitor.disabled = true;

    fetch(`/api/adicionar-chave-emprestimo/?codigo=${codigo}&usuario_id=${usuarioId}`)
    .then(response => response.json())
    .then(data => {
        inputLeitor.value = '';
        inputLeitor.disabled = false;
        inputLeitor.focus();

        if (data.erro) {
            mostrarAlerta(data.erro, 'danger');
            return; 
        }

        mostrarAlerta(`Chave ${data.chave_nome} ativada com sucesso!`, 'success');

        const linhaVazia = document.getElementById('linha_vazia');
        if (linhaVazia) linhaVazia.remove();

        let tr = document.createElement('tr');
        tr.innerHTML = `
            <td class="ps-4 fw-bold text-secondary">#${data.emprestimo_id}</td>
            <td>${String(data.chave_id).padStart(2, '0')}</td>
            <td class="fw-bold">${data.chave_nome}</td>
            <td>${data.chave_setor}</td>
            <td><span class="badge bg-primary">Ativa</span></td>
            <td class="text-center">
                <a href="/emprestimos/remover-chave/${data.emprestimo_id}/${data.chave_id}/" class="btn btn-sm btn-outline-danger" title="Remover">
                    <i class="fas fa-trash-alt"></i>
                </a>
            </td>
        `;
        
        tbodyChaves.prepend(tr);
    })
    .catch(error => {
        console.error('Erro:', error);
        mostrarAlerta("Falha no registro. Tente novamente.", 'warning');
        inputLeitor.value = '';
        inputLeitor.disabled = false;
        inputLeitor.focus();
    });
}

window.abrirModalFinalizar = function() {
    const tbody = document.getElementById('tbody_chaves');
    const linhas = tbody.querySelectorAll('tr:not(#linha_vazia)').length;
    
    if (linhas > 0) {
        document.getElementById('qtdModal').innerText = linhas;
        
        const modalElement = document.getElementById('modalConfirmacao');
        var myModal = new bootstrap.Modal(modalElement);
        myModal.show();
        
        // NOVIDADE AQUI: Assim que a animação do Modal terminar de abrir, foca no botão verde!
        modalElement.addEventListener('shown.bs.modal', function () {
            document.getElementById('btn_finalizar_modal').focus();
        }, { once: true }); // O { once: true } garante que o evento rode só 1 vez por abertura.
        
    } else {
        mostrarAlerta("Adicione pelo menos uma chave antes de finalizar!", "warning");
    }
};

document.addEventListener("DOMContentLoaded", function() {
    const inputLeitor = document.getElementById('input_leitor');
    const elementoId = document.getElementById('hidden_usuario_id');
    const usuarioId = elementoId ? elementoId.value : null;
    
    if (inputLeitor) {
        inputLeitor.focus();

        inputLeitor.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            let codigo = this.value.trim();
            if (codigo !== '' && codigo !== 'Processando...') {
                debounceTimer = setTimeout(function() {
                    adicionarChave(codigo);
                }, 300);
            }
        });

        inputLeitor.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault(); 
                clearTimeout(debounceTimer);
                let codigo = this.value.trim();
                
                if (codigo !== '' && codigo !== 'Processando...') {
                    adicionarChave(codigo);
                } else if (codigo === '' && usuarioId) {
                    abrirModalFinalizar();
                }
            }
        });
    }
    
    document.body.addEventListener('click', function(e) {
        if(e.target.tagName !== 'A' && e.target.tagName !== 'BUTTON' && !e.target.closest('.modal')) {
            if (inputLeitor) inputLeitor.focus();
        }
    });
});

