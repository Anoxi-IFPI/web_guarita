let debounceTimer;
const inputLeitor = document.getElementById('input_leitor');
const listaChaves = document.getElementById('lista_chaves');
const painelUsuario = document.getElementById('painel_usuario');
const alertaContainer = document.getElementById('alerta_container');

// Função para mostrar o aviso verde ou vermelho na tela
function mostrarAlerta(mensagem, tipo) {
    alertaContainer.innerHTML = `
        <div class="alert alert-${tipo} alert-dismissible fade show fs-5 shadow-sm" role="alert" style="position: relative; padding: 15px 15px 45px 15px; text-align: left !important;">
            <div class="d-flex align-items-start">
                <!-- Ícone alinhado no topo -->
                <i class="fas ${tipo === 'success' ? 'fa-check-circle' : 'fa-exclamation-triangle'} fs-3 me-3 flex-shrink-0" style="margin-top: 3px;"></i>
                
                <!-- Texto estritamente justificado à esquerda -->
                <div class="flex-grow-1 text-start" style="line-height: 1.4;">
                    <strong>${mensagem}</strong>
                </div>
            </div>
            
            <!-- Botão X movido para o canto inferior direito -->
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close" style="position: absolute; top: auto; bottom: 10px; right: 10px; padding: 0.5rem;"></button>
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

        // 3. Adiciona a chave na lista SEM O ID, e configurado para descer no mobile
        let li = document.createElement('li');
        li.className = 'list-group-item d-flex flex-wrap justify-content-between align-items-center fs-5 py-3 mb-2 shadow-sm border-success bg-light gap-2';
        li.innerHTML = `
            <div class="d-flex align-items-center flex-grow-1" style="min-width: 60%;">
                <i class="fas fa-key text-success me-3 mt-1 align-self-start"></i> 
                <strong class="text-break text-start">${data.chave_nome}</strong> 
            </div> 
            <span class="badge bg-success rounded-pill px-3 py-2 mt-2 mt-sm-0">
                <i class="fas fa-check-circle me-1"></i> Devolvida
            </span>
        `;
        
        // Joga a chave lida sempre para o topo da lista
        listaChaves.prepend(li);
    })
    .catch(error => {
        console.error('Erro:', error);
        mostrarAlerta("Erro: O código deve conter apenas números.", 'warning');
        inputLeitor.value = '';
        inputLeitor.disabled = false;
        inputLeitor.focus();
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