let debounceTimerDevolucao;
const inputDevolucao = document.getElementById('input-codigo-devolucao');
const listaDevolvidas = document.getElementById('lista-chaves-devolvidas');
const containerMensagens = document.querySelector('.mensagens-flutuantes');
const formDevolucao = document.getElementById('form-devolucao-rapida');

// Função para injetar alertas flutuantes dinamicamente no canto superior direito
function mostrarAlertaRapido(mensagem, tipo) {
    const alerta = document.createElement('div');
    alerta.className = `alert alert-${tipo} alert-dismissible fade show shadow`;
    alerta.role = 'alert';
    alerta.innerHTML = `
        <i class="fas ${tipo === 'success' ? 'fa-check-circle' : 'fa-exclamation-triangle'} me-2"></i> ${mensagem}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    containerMensagens.appendChild(alerta);

    // O aviso some sozinho depois de 4 segundos
    setTimeout(() => {
        alerta.classList.remove('show');
        setTimeout(() => alerta.remove(), 150); // Aguarda a animação do Bootstrap terminar
    }, 4000);
}

function processarDevolucaoRapida(codigo) {
    if (codigo === '') return;

    inputDevolucao.value = 'Processando...';
    inputDevolucao.disabled = true;

    // Vai no banco e já DEVOLVE a chave
    fetch(`/api/buscar-chave-devolucao/?codigo=${codigo}`)
    .then(response => response.json())
    .then(data => {
        inputDevolucao.value = '';
        inputDevolucao.disabled = false;
        inputDevolucao.focus();

        if (data.erro) {
            mostrarAlertaRapido(data.erro, 'danger');
            return;
        }

        // 1. Mostra a notificação verde
        mostrarAlertaRapido(`Chave ${data.chave_nome} devolvida com sucesso!`, 'success');

        // 2. Remove o texto "Nenhuma chave devolvida" se existir
        const msgVazia = document.getElementById('msg-lista-vazia');
        if (msgVazia) msgVazia.remove();

        // 3. Cria o card de devolução compacto e injeta na tela inicial
        let card = document.createElement('div');
        card.style.cssText = "padding: 12px 16px; border: 1px solid #c3e6cb; border-radius: 8px; background: #d4edda; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.05);";
        card.innerHTML = `
            <div>
                <strong style="color: #155724; font-size: 15px;">
                    <i class="fas fa-key me-2"></i> ${data.chave_nome} <small>(ID: ${data.chave_id})</small>
                </strong><br>
                <small style="color: #28a745; font-weight: 600;">
                    <i class="fas fa-user-check me-1"></i> ${data.usuario_nome}
                </small>
            </div>
            <span class="badge bg-success px-3 py-2" style="font-size: 13px;">
                <i class="fas fa-check-circle me-1"></i> Devolvida
            </span>
        `;
        
        // Joga a chave lida sempre para o topo da lista
        listaDevolvidas.prepend(card);
    })
    .catch(error => {
        console.error('Erro:', error);
        mostrarAlertaRapido("Falha na comunicação com o servidor.", 'danger');
        inputDevolucao.value = '';
        inputDevolucao.disabled = false;
        inputDevolucao.focus();
    });
}

// Escuta a digitação ou o leitor rápido de código de barras
inputDevolucao.addEventListener('input', function() {
    clearTimeout(debounceTimerDevolucao);
    let codigo = this.value.trim();
    
    if (codigo !== '' && codigo !== 'Processando...') {
        debounceTimerDevolucao = setTimeout(function() {
            processarDevolucaoRapida(codigo);
        }, 300);
    }
});

// Intercepta o Enter para não recarregar a tela
inputDevolucao.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault(); 
        clearTimeout(debounceTimerDevolucao);
        let codigo = this.value.trim();
        processarDevolucaoRapida(codigo);
    }
});

// Intercepta o clique manual no botão "Confirmar Devolução"
formDevolucao.addEventListener('submit', function(e) {
    e.preventDefault();
    clearTimeout(debounceTimerDevolucao);
    let codigo = inputDevolucao.value.trim();
    if(codigo && codigo !== 'Processando...') {
        processarDevolucaoRapida(codigo);
    }
});