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

    setTimeout(() => {
        alerta.classList.remove('show');
        setTimeout(() => alerta.remove(), 150);
    }, 4000);
}

function processarDevolucaoRapida(codigo) {
    if (codigo === '') return;

    // 1. TRAVA DE SEGURANÇA: Bloqueia se tiver letras ou símbolos
    if (!/^\d+$/.test(codigo)) {
        mostrarAlertaRapido("Código inválido. Digite apenas números!", "warning");
        inputDevolucao.value = '';
        return;
    }

    inputDevolucao.value = 'Processando...';
    inputDevolucao.disabled = true;

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

        mostrarAlertaRapido(`Chave ${data.chave_nome} devolvida com sucesso!`, 'success');

        const msgVazia = document.getElementById('msg-lista-vazia');
        if (msgVazia) msgVazia.remove();

        let card = document.createElement('div');
        // Adicionada transição suave no CSS do card para a hora de sumir
        card.style.cssText = "padding: 12px 16px; border: 1px solid #c3e6cb; border-radius: 8px; background: #d4edda; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.05); transition: opacity 0.5s ease, transform 0.5s ease;";
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
        
        listaDevolvidas.prepend(card);

        // 2. TEMPORIZADOR: Remove o card após 5 segundos
        setTimeout(() => {
            card.style.opacity = "0";
            card.style.transform = "scale(0.95)";
            
            setTimeout(() => {
                card.remove();
                // Se a lista ficar vazia de novo, devolve o texto padrão
                if (listaDevolvidas.children.length === 0) {
                    listaDevolvidas.innerHTML = '<div class="lista-vazia" id="msg-lista-vazia">Nenhuma chave devolvida ainda</div>';
                }
            }, 500); // Aguarda o fim da animação de sumir
        }, 5000);

    })
    .catch(error => {
        console.error('Erro:', error);
        mostrarAlertaRapido("Falha na comunicação com o servidor.", 'danger');
        inputDevolucao.value = '';
        inputDevolucao.disabled = false;
        inputDevolucao.focus();
    });
}

inputDevolucao.addEventListener('input', function() {
    clearTimeout(debounceTimerDevolucao);
    let codigo = this.value.trim();
    
    if (codigo !== '' && codigo !== 'Processando...') {
        debounceTimerDevolucao = setTimeout(function() {
            processarDevolucaoRapida(codigo);
        }, 300);
    }
});

inputDevolucao.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault(); 
        clearTimeout(debounceTimerDevolucao);
        let codigo = this.value.trim();
        processarDevolucaoRapida(codigo);
    }
});

formDevolucao.addEventListener('submit', function(e) {
    e.preventDefault();
    clearTimeout(debounceTimerDevolucao);
    let codigo = inputDevolucao.value.trim();
    if(codigo && codigo !== 'Processando...') {
        processarDevolucaoRapida(codigo);
    }
});