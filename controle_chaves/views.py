from django.shortcuts import render, HttpResponse, redirect
from .models import Chave, Usuario, Emprestimo
from .forms import UsuarioForm, ChaveForm # <--- Adicionamos o ChaveForm aqui
from django.contrib import messages  # <--- Faltava esta importação!
import io
import base64
import json
from django.http import JsonResponse
import barcode
from barcode.writer import ImageWriter
from django.shortcuts import render
from .models import Chave, Emprestimo, Usuario



# Create your views here.

# ==========================================
# VIEWS PARA PAGINA INICIAL
# ========================================== 
def home(request):
    
    #busca as chaves
    home = Chave.objects.all()
    
    return render(request, 'home/index.html', {'chaves': home})

#Viws da pagina de usuários
# NOVA VIEW: Para o formulário de cadastro de utilizadores
def cadastrar_usuario(request):
    # Se o utilizador clicou no botão "Salvar" (enviou os dados)
    if request.method == 'POST':
        form = UsuarioForm(request.POST) # Pega nos dados que vieram do HTML
        
        # O Django verifica se preencheu tudo corretamente (se a matrícula não é repetida, etc)
        if form.is_valid():
            form.save() # Guarda automaticamente na base de dados!
            messages.success(request, 'Utilizador cadastrado com sucesso!')
            return redirect('listar_usuario') # Volta para a página de listagem após salvar
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


# ==========================================
# VIEWS PARA GESTÃO DE CHAVES
# ==========================================

def listar_chave(request):
    # 1. Busca todas as chaves no banco e ordena da mais nova para a mais velha
    contexto = {
        'lista': Chave.objects.all().order_by('-id'),
    }
    # 2. Envia os dados para a sala de leitura (template)
    return render(request, 'home/chaves/listagem.html', contexto)

def cadastrar_chave(request):
    # 1. Se os dados vieram do botão "Salvar" (POST)
    if request.method == 'POST':
        form = ChaveForm(request.POST) 
        if form.is_valid():
            form.save() # Mágica: salva a chave no banco!
            messages.success(request, 'Chave cadastrada com sucesso!')
            return redirect('listar_chave') # Após salvar, vai para a listagem
        else:
            messages.error(request, 'Erro ao cadastrar a chave. Verifique os campos.')
            
    # 2. Se o usuário só abriu a página (GET)
    else:
        form = ChaveForm() # Formulário em branco
        
    # 3. Desenha a tela de formulário
    return render(request, 'home/chaves/form.html', {'form': form})

# Função para detalhar chaves
def detalhar_chave(request, id):
    try:
        Chave_instancia = Chave.objects.get(pk=id)
    except Chave.DoesNotExist:
        messages.error(request, 'Chave não encontrada.')
        return redirect('listar_chave')

    # 2. Envia os dados desse usuário para uma página HTML nova chamada 'detalhes.html'
    contexto = {
        'chave': Chave_instancia
    }
    return render(request, 'home/chaves/detalhes.html', contexto)

def remover_chave(request, id):
    # 1. Tenta encontrar a "pasta" no arquivo usando o ID
    try:
        chave_instancia = Chave.objects.get(pk=id)
        # 2. Se encontrou, joga no lixo (deleta do banco)
        chave_instancia.delete()
        # 3. Manda uma mensagem de sucesso para a tela
        messages.success(request, 'Chave removida com sucesso!')
    except Chave.DoesNotExist:
        # Se alguém tentar apagar um ID que não existe (ex: digitou na URL)
        messages.error(request, 'Chave não encontrada.')

    # 4. Redireciona de volta para a tabela de listagem
    return redirect('listar_chave')


def editar_chave(request, id):
    # 1. Busca a chave pelo ID ou retorna erro se não existir
    try:
        chave_instancia = Chave.objects.get(pk=id)
    except Chave.DoesNotExist:
        messages.error(request, 'Chave não encontrada')
        return redirect('listar_chave')

    # 2. Se o usuário enviou o formulário (Clicou em Salvar)
    if request.method == 'POST':
        # Passamos os dados do POST E a instância que queremos atualizar
        form = ChaveForm(request.POST, instance=chave_instancia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Chave atualizada com sucesso!')
            return redirect('listar_chave')
    
    # 3. Se ele apenas entrou na página (GET), carrega o form com os dados atuais
    else:
        form = ChaveForm(instance=chave_instancia)
    
    # Reutilizamos o mesmo form.html do cadastro!
    return render(request, 'home/chaves/form.html', {'form': form})

def gerar_codigo_barras(request, id):
    # 1. PRIMEIRO PASSO: Buscar o objeto diretamente no banco de dados!
    # É isso que estava faltando para a variável existir na memória.
    chave_instancia = Chave.objects.get(pk=id)

    # 2. Valor que será codificado
    codigo = str(id)

    # 3. Cria Code128
    code128 = barcode.get(
        'code128',
        codigo,
        writer=ImageWriter()
    )

    # 4. Gera imagem em memória
    buffer = io.BytesIO()
    code128.write(buffer)

    # 5. Converte para base64
    imagem_base64 = base64.b64encode(
        buffer.getvalue()
    ).decode('utf-8')

    # 6. Agora o contexto consegue encontrar a 'chave_instancia' declarada lá na primeira linha
    contexto = {
        "id": id,
        "nome": chave_instancia.nome,
        "setor": chave_instancia.setor,
        "barcode": imagem_base64,
    }

    return render(
        request, "home/cod_barras/codigo_barras.html", contexto
    )

# ==========================================
# VIEWS PARA GESTÃO DE EMPRÉSTIMOS
# ========================================== 
# 1. View que envia os dados pro seu Front-end (Para não usar Banco de Dados toda hora)
def pagina_emprestimos(request):
    # Buscamos apenas os campos necessários, exatamente com os nomes que seu JS espera
    usuarios = list(Usuario.objects.values('id', 'nome', 'matricula', 'vinculo'))
    chaves = list(Chave.objects.values('id', 'nome', 'setor'))

    context = {
        'usuarios_json': json.dumps(usuarios),
        'chaves_json': json.dumps(chaves),
    }
    return render(request, 'home/emprestimos/emprestimos.html', context)

# 2. View que recebe o JSON do JavaScript e salva no Banco de Dados
def salvar_emprestimo(request):
    # Só aceitamos requisições do tipo POST (envio de dados)
    if request.method == 'POST':
        try:
            # json.loads "traduz" o pacote que o JavaScript enviou para um Dicionário Python
            dados = json.loads(request.body)
            
            # Passo A: Buscamos o usuário no banco usando a matrícula que veio do JS
            usuario_obj = Usuario.objects.get(matricula=dados['usuario']['matricula'])
            
            # Passo B: Criamos a "pasta" do empréstimo (ainda sem as chaves)
            novo_emprestimo = Emprestimo.objects.create(usuario=usuario_obj)
            
            # Passo C: Lemos a lista de chaves do JS e guardamos uma a uma dentro do empréstimo
            for chave_dado in dados['chaves']:
                chave_obj = Chave.objects.get(id=chave_dado['id'])
                novo_emprestimo.chaves.add(chave_obj) # O .add() é usado para ManyToMany
                
            # Tudo deu certo! Retornamos sucesso para o JavaScript mostrar o Card Verde.
            return JsonResponse({"status": "sucesso"})
            
        # Boas Práticas: Tratamento de Erros (Debugging pro Front-end)
        except Usuario.DoesNotExist:
            return JsonResponse({"erro": "Usuário não localizado no banco"}, status=404)
        except Chave.DoesNotExist:
            return JsonResponse({"erro": "Chave não localizada no banco"}, status=404)
        except Exception as e:
            return JsonResponse({"erro": str(e)}, status=500)

    # Se alguém tentar acessar a URL diretamente pelo navegador (GET), damos erro.
    return JsonResponse({"erro": "Método não permitido"}, status=405)