let segundos = 5;
const timerElement = document.getElementById('timer');
const configUrls = document.getElementById('config-urls');

// Coleta as variáveis injetadas pelo Django no HTML
const origem = configUrls.getAttribute('data-origem');
const urlRapida = configUrls.getAttribute('data-url-rapida');
const urlCadastro = configUrls.getAttribute('data-url-cadastro');

const intervalo = setInterval(() => {
    segundos--;
    timerElement.innerText = segundos;
    
    if (segundos <= 0) {
        clearInterval(intervalo);
        
        // Verificação feita puramente em JavaScript
        if (origem === 'rapida') {
            window.location.href = urlRapida;
        } else {
            window.location.href = urlCadastro;
        }
    }
}, 1000);