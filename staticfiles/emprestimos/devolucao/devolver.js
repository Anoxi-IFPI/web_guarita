let debounceTimer;
const inputLeitor = document.getElementById('input_leitor');
const listaChaves = document.getElementById('lista_chaves');
const painelUsuario = document.getElementById('painel_usuario');
const alertaContainer = document.getElementById('alerta_container');

// Função para mostrar o aviso verde na tela
function mostrarAlerta(mensagem, tipo) {
    alertaContainer.innerHTML = `
        <div class="alert alert-${tipo} alert-dismissible fade show fs-5 shadow-sm" role="alert">
            <i class="fas ${tipo === 'success' ? 'fa-check-circle' : 'fa-exclamation-triangle'} me-2"></i>
            <strong>${mensagem}</strong>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    // O aviso some sozinho depois de 4 segundos
    setTimeout(() => {
        alertaContainer.innerHTML = '';
    }, 4000);
}

function buscarChave(codigo) {
    if (codigo === '') return;

    inputLeitor.value = 'Processando...';
    inputLeitor.disabled = true;

    // Vai no banco e já DEVOLVE a chave
    fetch(`/api/buscar-chave-devolucao/?codigo=${codigo}`)
    .then(response => response.json())
    .then(data => {
        inputLeitor.value = '';
        inputLeitor.disabled = false;
        inputLeitor.focus();

        if (data.erro) {
            mostrarAlerta(data.erro, 'danger'); // Mostra alerta vermelho se der erro
            return;
        }

        // 1. Mostra a notificação verde de SUCESSO
        mostrarAlerta(`Chave ${data.chave_nome} devolvida com sucesso!`, 'success');

        // 2. Atualiza os dados do usuário no topo
        document.getElementById('ui_usuario_nome').innerText = data.usuario_nome;
        document.getElementById('ui_usuario_matricula').innerText = data.usuario_matricula;
        painelUsuario.classList.remove('d-none');

        // 3. Adiciona a chave na lista com o status DEVOLVIDA
        let li = document.createElement('li');
        li.className = 'list-group-item d-flex justify-content-between align-items-center fs-5 py-3 mb-2 shadow-sm border-success bg-light';
        li.innerHTML = `
            <span>
                <i class="fas fa-key text-success me-3"></i> 
                <strong>${data.chave_nome}</strong> 
                <small class="text-muted ms-2">(ID: ${data.chave_id})</small>
            </span> 
            <span class="badge bg-success rounded-pill px-3 py-2">
                <i class="fas fa-check-circle me-1"></i> Devolvida
            </span>
        `;
        
        
        // Joga a chave lida sempre para o topo da lista
        listaChaves.prepend(li);
    })
    .catch(error => {
        console.error('Erro:', error);
        // Mensagem alterada conforme seu pedido
        mostrarAlertaRapido("Erro: O código deve conter apenas números.", 'warning');
        inputDevolucao.value = '';
        inputDevolucao.disabled = false;
        inputDevolucao.focus();
    });
}

// Escuta a digitação ou o leitor rápido
inputLeitor.addEventListener('input', function() {
    clearTimeout(debounceTimer);
    let codigo = this.value.trim();
    
    if (codigo !== '' && codigo !== 'Processando...') {
        debounceTimer = setTimeout(function() {
            buscarChave(codigo);
        }, 300);
    }
});

// Impede o Enter de enviar o formulário e recarregar a tela à toa
inputLeitor.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault(); 
        clearTimeout(debounceTimer);
        let codigo = this.value.trim();
        buscarChave(codigo);
    }
});