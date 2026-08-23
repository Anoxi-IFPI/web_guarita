let debounceTimer;
const inputLeitor = document.getElementById('input_leitor');
const tbodyChaves = document.getElementById('tbody_chaves');
const alertaContainer = document.getElementById('alerta_container');
const btnAdicionarManual = document.getElementById('btn_adicionar_manual');
const usuarioId = document.getElementById('hidden_usuario_id').value;

function mostrarAlerta(mensagem, tipo) {
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
    if (codigo === '') return;

    inputLeitor.value = 'Buscando chave...';
    inputLeitor.disabled = true;

    fetch(`/api/adicionar-chave-emprestimo/?codigo=${codigo}&usuario_id=${usuarioId}`)
    .then(response => response.json())
    .then(data => {
        inputLeitor.value = '';
        inputLeitor.disabled = false;
        inputLeitor.focus();

        // 🛑 TRAVA DE SEGURANÇA: Se a chave estiver ocupada, para aqui e não lista!
        if (data.erro) {
            mostrarAlerta(data.erro, 'danger');
            return; 
        }

        // Se passar da trava, a chave tá livre, mostra verde e desenha a linha.
        mostrarAlerta(`Chave ${data.chave_nome} ativa!`, 'success');

        const linhaVazia = document.getElementById('linha_vazia');
        if (linhaVazia) linhaVazia.remove();

        let tr = document.createElement('tr');
        tr.innerHTML = `
            <td class="ps-4 fw-bold text-secondary">#${data.emprestimo_id}</td>
            
            <!-- NOVA COLUNA INSERIDA AQUI PARA NÃO DESALINHAR A TABELA -->
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
        if(btnAdicionarManual) btnAdicionarManual.classList.remove('d-none');
        inputLeitor.value = codigo;
        inputLeitor.disabled = false;
        inputLeitor.focus();
    });
}

inputLeitor.addEventListener('input', function() {
    clearTimeout(debounceTimer);
    let codigo = this.value.trim();
    if (codigo !== '' && codigo !== 'Buscando chave...') {
        debounceTimer = setTimeout(function() {
            adicionarChave(codigo);
        }, 300);
    }
});

inputLeitor.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault(); 
        clearTimeout(debounceTimer);
        let codigo = this.value.trim();
        adicionarChave(codigo);
    }
});

// FECHA AUTOMATICAMENTE OS ALERTAS VERDES DO DJANGO (GERADOS PELO BOTÃO MANUAL)
document.addEventListener("DOMContentLoaded", function() {
    const alertasDjango = document.querySelectorAll('.alert-success');
    alertasDjango.forEach(function(alerta) {
        setTimeout(function() {
            let alertInstance = new bootstrap.Alert(alerta);
            alertInstance.close();
        }, 7000); 
    });
});