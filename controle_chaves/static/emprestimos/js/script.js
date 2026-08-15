
    const codigoInput = document.getElementById('codigo');
    
    if (codigoInput) {
        const form = codigoInput.closest('form');
        let debounceTimer;

        // Regra 1: Se o usuário ou o leitor digitar os números (Espera 300ms e submete)
        codigoInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            if (codigoInput.value.trim() !== '') {
                debounceTimer = setTimeout(function() {
                    form.submit();
                }, 300);
            }
        });

        // Regra 2: Se o leitor for do tipo que envia a tecla "Enter" no final
        codigoInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault(); // Bloqueia o enter padrão do navegador
                if (codigoInput.value.trim() !== '') {
                    form.submit();
                }
            }
        });
    }
