    const containerResultados = document.getElementById('lista-resultados-admin');
    const inputCodigo = document.getElementById('codigo-chave-admin');
    const selectUsuario = document.getElementById('select-usuario-admin');
    const contadorResultados = document.getElementById('contador-resultados-admin');
    const alertaContainer = document.getElementById('alerta_container');
    
    let debounceTimerRepasse;

    // Função de Alerta idêntica à da Devolução
    function mostrarAlerta(mensagem, tipo) {
        alertaContainer.innerHTML = `
            <div class="alert alert-${tipo} alert-dismissible fade show fs-5 shadow-sm" role="alert" style="position: relative; padding: 15px 15px 45px 15px;">
                <div class="d-flex align-items-start">
                    <i class="fas ${tipo === 'success' ? 'fa-check-circle' : (tipo === 'warning' ? 'fa-exclamation-triangle' : 'fa-info-circle')} fs-3 me-3 flex-shrink-0" style="margin-top: 3px;"></i>
                    <div class="flex-grow-1 text-start" style="line-height: 1.4;">
                        <strong>${mensagem}</strong>
                    </div>
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close" style="position: absolute; top: auto; bottom: 10px; right: 10px; padding: 0.5rem;"></button>
            </div>
        `;
        
        setTimeout(() => {
            alertaContainer.innerHTML = '';
        }, 4000);
    }

    // Escuta a digitação rápida no leitor de código (idêntico à devolução)
    if (inputCodigo) {
        inputCodigo.addEventListener('input', function() {
            clearTimeout(debounceTimerRepasse);
            let codigo = this.value.trim();
            
            if (codigo !== '' && codigo !== 'Processando...') {
                debounceTimerRepasse = setTimeout(function() {
                    buscarChavePorCodigo(codigo);
                }, 300);
            }
        });

        // Impede o Enter de enviar o form
        inputCodigo.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                clearTimeout(debounceTimerRepasse);
                let codigo = this.value.trim();
                buscarChavePorCodigo(codigo);
            }
        });
    }

// Substitua a função renderizarCardsAdmin por esta:
function renderizarCardsAdmin(emprestimos) {
    if (!containerResultados) return;
    
    containerResultados.innerHTML = '';
    if (contadorResultados) contadorResultados.textContent = emprestimos.length;

    if (emprestimos.length === 0) {
        containerResultados.innerHTML = `
            <div class="text-center p-5 bg-white rounded-3 border-0 shadow-sm text-muted">
                <i class="fas fa-check-circle mb-3 d-block text-success" style="font-size: 3rem; opacity: 0.5;"></i>
                <strong class="fs-5 text-dark">Tudo limpo!</strong>
                <p class="mt-2 mb-0 small text-muted">Nenhuma chave encontrada em posse para esta pesquisa.</p>
            </div>`;
        return;
    }

    emprestimos.forEach(emp => {
        const item = document.createElement('div');
        item.className = 'card border-0 border-start border-4 border-success shadow-sm mb-3'; 
        
        item.innerHTML = `
            <div class="card-body p-3 bg-white">
                
                <!-- Parte de Cima: Ícone e Dados -->
                <div class="d-flex align-items-start gap-3">
                    <div class="bg-success bg-opacity-10 text-success rounded p-2 d-flex align-items-center justify-content-center flex-shrink-0" style="width: 45px; height: 45px;">
                        <i class="fas fa-key fs-5"></i>
                    </div>
                    
                    <div class="flex-grow-1">
                        <h6 class="mb-1 fw-bold text-dark" style="font-size: 0.95rem;">${emp.chave_nome}</h6>
                        
                        <!-- Setor e Código lado a lado -->
                        <div class="text-muted d-flex flex-wrap gap-3 mb-2" style="font-size: 0.85rem;">
                            <span><i class="fas fa-map-marker-alt fa-fw"></i> ${emp.setor}</span>
                            <span><i class="fas fa-barcode fa-fw"></i> #${String(emp.chave_id).padStart(2, '0')}</span>
                        </div>
                        
                        <!-- Usuário isolado para não amassar -->
                        <div class="text-primary fw-semibold" style="font-size: 0.85rem; line-height: 1.3;">
                            <i class="fas fa-user fa-fw"></i> Com: ${emp.usuario_atual_nome}
                        </div>
                    </div>
                </div>
                
                <!-- Parte de Baixo: Data e Botão em coluna -->
                <div class="d-flex flex-column border-top pt-3 mt-3 gap-2">
                    <div class="text-muted fw-bold small">
                        <i class="far fa-clock"></i> ${emp.data_emprestimo}
                    </div>
                    
                    <button type="button" 
                            class="btn text-white fw-bold d-flex align-items-center justify-content-center gap-2 px-3 py-2 border-0 shadow-sm w-100"
                            style="background-color: #f58623; border-radius: 6px; font-size: 0.9rem;"
                            data-emprestimo-id="${emp.id}"
                            data-chave-nome="${emp.chave_nome}"
                            data-chave-setor="${emp.setor}"
                            data-chave-id="${emp.chave_id}"
                            data-usuario-nome="${emp.usuario_atual_nome}"
                            onclick="abrirModalRepasse(this)">
                        <i class="fas fa-exchange-alt"></i> Repassar
                    </button>
                </div>

            </div>
        `;
        containerResultados.appendChild(item);
    });
}


    // Busca bipe do código
    function buscarChavePorCodigo(codigo) {
        if (!codigo) return;
        
        inputCodigo.value = 'Processando...';
        inputCodigo.disabled = true;
        selectUsuario.value = ""; // Reseta o select

        // Nota: Certifique-se que o caminho '/api/admin/buscar-chave-repasse/' está no seu urls.py
        fetch(`/api/admin/buscar-chave-repasse/?codigo=${codigo}`)
            .then(response => response.json())
            .then(data => {
                inputCodigo.value = ''; 
                inputCodigo.disabled = false;
                inputCodigo.focus();

                if (data.erro) {
                    mostrarAlerta(data.erro, 'danger');
                    return;
                }
                
                mostrarAlerta('Chave encontrada. Pronta para o repasse!', 'success');
                renderizarCardsAdmin(data.emprestimos);
            })
            .catch(err => {
                console.error(err);
                mostrarAlerta("Erro: O código deve conter apenas números.", 'warning');
                inputCodigo.value = ''; 
                inputCodigo.disabled = false;
                inputCodigo.focus();
            });
    }

    // Busca pela caixa de listagem (Select)
    function buscarChavesPorUsuario() {
        const usuarioId = selectUsuario.value;
        if (!usuarioId) {
            containerResultados.innerHTML = `
                <div class="text-center p-5 bg-white rounded-3 border-0 shadow-sm text-muted">
                    <i class="fas fa-search mb-3 d-block" style="font-size: 3rem; color: #d0d0d0;"></i>
                    <strong class="fs-5 text-dark">Nenhuma pesquisa realizada</strong>
                    <p class="mt-2 mb-0 small text-muted">Utilize o leitor ou selecione um usuário acima para buscar.</p>
                </div>`;
            contadorResultados.textContent = "0";
            return;
        }
        
        inputCodigo.value = ""; // Reseta o input

        // Nota: Certifique-se que o caminho '/api/admin/buscar-chaves-usuario/' está no seu urls.py
        fetch(`/api/admin/buscar-chaves-usuario/?usuario_id=${usuarioId}`)
            .then(res => res.json())
            .then(data => {
                if (data.erro) {
                    mostrarAlerta(data.erro, 'danger');
                    return;
                }
                renderizarCardsAdmin(data.emprestimos);
            })
            .catch(err => console.error(err));
    }
