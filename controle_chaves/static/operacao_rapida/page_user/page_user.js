function atualizarRelogioRapida() {
            const agora = new Date();
            const data = agora.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' });
            const hora = agora.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            
            const spanTime = document.getElementById('currentTime');
            if (spanTime) {
                spanTime.textContent = data + ', ' + hora;
                spanTime.style.color = 'white'; 
                spanTime.style.fontWeight = 'bold'; 
                spanTime.style.marginRight = '15px'; 
            }
        }
        setInterval(atualizarRelogioRapida, 1000);
        atualizarRelogioRapida();