        document.getElementById('toggle-sidebar').addEventListener('click', function() {
            document.getElementById('sidebar').classList.toggle('active');
            document.getElementById('content').classList.toggle('active');
        });
// =======================================================
// SCRIPT DO RELÓGIO GLOBAL (BASE.HTML)                   
// =======================================================
function atualizarRelogioBase() {
    const agora = new Date();
    const data = agora.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' });
    const hora = agora.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    
    const spanTime = document.getElementById('currentTimeBase');
    if (spanTime) {
        spanTime.textContent = data + ', ' + hora;
    }
}
setInterval(atualizarRelogioBase, 1000);
atualizarRelogioBase();