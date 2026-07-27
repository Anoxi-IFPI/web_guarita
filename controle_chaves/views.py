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


# função para editar 
def editar_usuario(request, id):
    # 1. Busca o usuário pelo ID ou retorna erro se não existir
    try:
        usuario_instancia = Usuario.objects.get(pk=id)
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuário não encontrado')
        return redirect('listar_usuario')

    # 2. Se o usuário enviou o formulário (Clicou em Salvar)
    if request.method == 'POST':
        # Passamos os dados do POST E a instância que queremos atualizar
        form = UsuarioForm(request.POST, instance=usuario_instancia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário atualizado com sucesso!')
            return redirect('listar_usuario')
    
    # 3. Se ele apenas entrou na página (GET), carrega o form com os dados atuais
    else:
        form = UsuarioForm(instance=usuario_instancia)
    
    # Reutilizamos o mesmo form.html do cadastro!
    return render(request, 'home/usuarios/form.html', {'form': form})


#Função para remover usuário
def remover_usuario(request, id):
    # 1. Tenta encontrar a "pasta" no arquivo usando o ID
    try:
        usuario_instancia = Usuario.objects.get(pk=id)
        # 2. Se encontrou, joga no lixo (deleta do banco)
        usuario_instancia.delete()
        # 3. Manda uma mensagem de sucesso para a tela
        messages.success(request, 'Usuário removido com sucesso!')
    except Usuario.DoesNotExist:
        # Se alguém tentar apagar um ID que não existe (ex: digitou na URL)
        messages.error(request, 'Usuário não encontrado.')

    # 4. Redireciona de volta para a tabela de listagem
    return redirect('listar_usuario')

# Função para detalhar usuário
def detalhar_usuario(request, id):
    # 1. Busca o usuário específico pelo ID
    try:
        usuario_instancia = Usuario.objects.get(pk=id)
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuário não encontrado.')
        return redirect('listar_usuario')

    # 2. Envia os dados desse usuário para uma página HTML nova chamada 'detalhes.html'
    contexto = {
        'usuario': usuario_instancia
    }
    return render(request, 'home/usuarios/detalhes.html', contexto)