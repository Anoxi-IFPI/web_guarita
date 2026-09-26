const movimentosData = JSON.parse(document.getElementById('movimentos-data').textContent);
let filtroAtual = 'todos';
let filtroTexto = ''; 

document.getElementById('pesquisa-texto').addEventListener('input', function(e) {
    filtroTexto = e.target.value.toLowerCase().trim();
    renderizarHistorico(); 
});

function renderizarHistorico() {
    const feed = document.getElementById('historicoFeed');
    let dados = movimentosData;

    // 1. Aplica o filtro dos botões
    if (filtroAtual !== 'todos') {
        dados = dados.filter(m => m.tipo === filtroAtual);
    }

    // 2. Aplica o filtro da barra de pesquisa de texto
    if (filtroTexto !== '') {
        dados = dados.filter(m => 
            m.cod.toLowerCase().includes(filtroTexto) || 
            m.setor.toLowerCase().includes(filtroTexto) ||
            m.usuario.toLowerCase().includes(filtroTexto)
        );
    }

    // Caso a busca não retorne nada
    if (dados.length === 0) {
        feed.innerHTML = `
            <div class="text-center p-5 bg-white rounded-3 border-0 shadow-sm text-muted">
                <i class="fas fa-search mb-3 d-block text-light" style="font-size: 3rem;"></i>
                <strong class="fs-5">Nenhum movimento encontrado</strong>
                <p class="mt-2 mb-0 small text-muted">Nenhuma chave foi movimentada nos filtros selecionados.</p>
            </div>
        `;
        return;
    }

    // Descobre a data que está no input de filtro do backend para mostrar corretamente
    const inputData = document.querySelector('input[name="data"]');
    let dataTexto = "Data selecionada";
    
    if (inputData && inputData.value) {
        const partes = inputData.value.split('-');
        if(partes.length === 3) {
            dataTexto = `${partes[2]}/${partes[1]}/${partes[0]}`; // Formato BR
            
            // Verifica se é o dia de hoje
            const hoje = new Date();
            const hojeFormatado = `${String(hoje.getDate()).padStart(2, '0')}/${String(hoje.getMonth() + 1).padStart(2, '0')}/${hoje.getFullYear()}`;
            
            if (dataTexto === hojeFormatado) {
                dataTexto = `Hoje, ${dataTexto}`;
            }
        }
    }
    
    let html = `
        <div class="d-flex align-items-center gap-3 py-2 text-muted fw-semibold small">
            <span><i class="fas fa-calendar-day"></i> Movimentações: ${dataTexto}</span>
            <span class="badge bg-secondary rounded-pill">${dados.length} resultados</span>
            <hr class="flex-grow-1 opacity-25 m-0">
        </div>
    `;

    dados.forEach(m => {
        let tipoLabel, bgBadge, borderColor;
        
        if (m.tipo === 'emprestimo') {
            tipoLabel = 'Empréstimo';
            bgBadge = 'bg-primary-subtle text-primary';
            borderColor = 'border-primary';
        } else if (m.tipo === 'devolvido') {
            tipoLabel = 'Devolução';
            bgBadge = 'bg-success-subtle text-success';
            borderColor = 'border-success';
        } else if (m.tipo === 'repassado') {
            tipoLabel = 'Repasse';
            bgBadge = 'bg-warning-subtle text-warning-emphasis';
            borderColor = 'border-warning';
        }

        // LÓGICA DO REPASSE
        let htmlRepasse = '';
        if (m.info_repasse) {
            htmlRepasse = `
                <div class="mt-2 d-inline-block px-2 py-1 rounded" style="background-color: #fff3e0; border: 1px solid #ffe0b2;">
                    <i class="fas fa-level-up-alt fa-rotate-90 me-1" style="color: #f57c00;"></i>
                    <span style="color: #e65100; font-size: 0.75rem; font-weight: 700;">${m.info_repasse}</span>
                </div>
            `;
        }

        html += `
            <div class="card border-0 border-start border-4 ${borderColor} shadow-sm mb-1">
                <div class="card-body d-flex align-items-center gap-3 p-3 flex-wrap bg-white">
                    <div class="text-muted fw-bold" style="min-width: 50px; font-size: 0.9rem;">
                        ${m.hora}
                    </div>
                    
                    <div style="min-width: 95px;" class="text-center">
                        <span class="badge ${bgBadge} text-uppercase rounded-pill w-100" style="font-size: 0.7rem; letter-spacing: 0.5px;">
                            ${tipoLabel}
                        </span>
                    </div>
                    
                    <div class="flex-grow-1">
                        <h6 class="mb-1 fw-bold text-dark" style="font-size: 0.95rem;">${m.usuario}</h6>
                        <div class="text-muted d-flex flex-column gap-1" style="font-size: 0.8rem;">
                            <span><i class="fas fa-key fa-fw"></i> ${m.cod} - ${m.setor}</span>
                            <span><i class="fas fa-id-badge fa-fw"></i> ${m.matricula}</span>
                        </div>
                        ${htmlRepasse}
                    </div>
                    
                    <div class="text-muted small fw-semibold">
                        ${m.id}
                    </div>
                </div>
            </div>
        `;
    });

    feed.innerHTML = html;
}

function filtrarHistorico(tipo, btnClicado) {
    filtroAtual = tipo;
    
    const botoes = document.querySelectorAll('#container-filtros .btn');
    botoes.forEach(b => {
        b.classList.remove('btn-success');
        b.classList.add('btn-outline-secondary', 'bg-white');
    });
    
    btnClicado.classList.remove('btn-outline-secondary', 'bg-white');
    btnClicado.classList.add('btn-success');
    
    renderizarHistorico();
}

renderizarHistorico();