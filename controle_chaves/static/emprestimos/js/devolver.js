
    let usuarioAtualId = null;
    let usuarioAtualNome = "";
    let debounceTimer; // Timer para o leitor de código de barras
    
    const inputLeitor = document.getElementById('input_leitor');
    const listaChaves = document.getElementById('lista_chaves');
    const formDevolucao = document.getElementById('formDevolucao');
    const btnConfirmar = document.getElementById('btn_confirmar');
    const painelUsuario = document.getElementById('painel_usuario');

    // Função que faz a requisição no backend
    function buscarChave(codigo) {
        if (codigo === '') return;

        inputLeitor.value = 'Buscando...';
        inputLeitor.disabled = true;

        fetch(`/api/buscar-chave-devolucao/?codigo=${codigo}`)
        .then(response => response.json())
        .then(data => {
            inputLeitor.value = '';
            inputLeitor.disabled = false;
            inputLeitor.focus();

            if (data.erro) {
                alert('ERRO: ' + data.erro);
                return;
            }

            if (usuarioAtualId === null) {
                usuarioAtualId = data.usuario_id;
                usuarioAtualNome = data.usuario_nome;
                
                document.getElementById('ui_usuario_nome').innerText = data.usuario_nome;
                document.getElementById('ui_usuario_matricula').innerText = data.usuario_matricula;
                painelUsuario.classList.remove('d-none');
                btnConfirmar.disabled = false; 
                
            } else if (usuarioAtualId !== data.usuario_id) {
                alert(`OPERAÇÃO BLOQUEADA!\nA chave lida pertence a ${data.usuario_nome}.\nVocê só pode devolver chaves do usuário ${usuarioAtualNome} nesta sessão.`);
                return;
            }

            if(document.getElementById('chave_hidden_' + data.chave_id)) {
                alert('Esta chave já foi adicionada na lista de devolução atual!');
                return;
            }

            let li = document.createElement('li');
            li.className = 'list-group-item d-flex justify-content-between align-items-center fs-5 py-3';
            li.innerHTML = `<span><i class="fas fa-key text-success me-3"></i> <strong>${data.chave_nome}</strong></span> <span class="badge bg-success rounded-pill">Selecionada</span>`;
            listaChaves.appendChild(li);

            let hidden = document.createElement('input');
            hidden.type = 'hidden';
            hidden.name = 'chaves_ids[]';
            hidden.id = 'chave_hidden_' + data.chave_id;
            hidden.value = data.chave_id;
            formDevolucao.appendChild(hidden);
        })
        .catch(error => {
            console.error('Erro:', error);
            alert("Erro ao conectar com o servidor.");
            inputLeitor.value = '';
            inputLeitor.disabled = false;
            inputLeitor.focus();
        });
    }

    // Regra 1: Se o leitor injetar os números rapidamente (Espera 300ms e busca)
    inputLeitor.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        let codigo = this.value.trim();
        
        if (codigo !== '' && codigo !== 'Buscando...') {
            debounceTimer = setTimeout(function() {
                buscarChave(codigo);
            }, 300);
        }
    });

    // Regra 2: Se o leitor for do tipo que envia a tecla "Enter" no final
    inputLeitor.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault(); 
            clearTimeout(debounceTimer); // Cancela o timer do 'input' para não buscar duas vezes
            let codigo = this.value.trim();
            buscarChave(codigo);
        }
    });
