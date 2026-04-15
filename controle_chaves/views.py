from django.shortcuts import render, HttpResponse, redirect
from .models import Chave, Usuario, Emprestimo
from .forms import UsuarioForm #importa o formulário
from django.contrib import messages  # <--- Faltava esta importação!

# Create your views here.
def home(request):
    
    #busca as chaves
    home = Chave.objects.all()
    
    return render(request, 'home/index.html', {'chaves': home})


# NOVA VIEW: Para o formulário de cadastro de utilizadores
def cadastrar_usuario(request):
    # Se o utilizador clicou no botão "Salvar" (enviou os dados)
    if request.method == 'POST':
        form = UsuarioForm(request.POST) # Pega nos dados que vieram do HTML
        
        # O Django verifica se preencheu tudo corretamente (se a matrícula não é repetida, etc)
        if form.is_valid():
            form.save() # Guarda automaticamente na base de dados!
            messages.success(request, 'Utilizador cadastrado com sucesso!')
            return redirect('home') # Volta para a página inicial após salvar
        else:
            # Se houver erro (ex: faltou o nome), recarrega a página mostrando o erro
            messages.error(request, 'Erro ao cadastrar. Por favor, verifica os dados.')
            
    # Se o utilizador apenas clicou no menu para ABRIR a página
    else:
        form = UsuarioForm() # Cria um formulário vazio
        
    # Mostra a página form.html, enviando o formulário (vazio ou com erros) para lá
    return render(request, 'home/usuarios/form.html', {'form': form})

#remover usuário, editar usuario, listar usuário
# controle_chaves/views.py

def listar_usuario(request): # <--- CERTIFIQUE-SE DE QUE O NOME É ESTE
    contexto = {
        'lista': Usuario.objects.all().order_by('-id'),
    }
    return render(request, 'home/usuarios/listagem.html', contexto)
