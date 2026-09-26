import io
import base64
import json
import csv
from datetime import timedelta, datetime
import barcode
from barcode.writer import ImageWriter

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.shortcuts import get_object_or_404, render, HttpResponse, redirect
from django.http import JsonResponse
from django.db.models import Q
from django.db import transaction
from django.views.decorators.http import require_POST

from .models import Chave, Usuario, Emprestimo
from .forms import EmprestimoForm, UsuarioForm, ChaveForm


# ==========================================
# FUNÇÕES DE VALIDAÇÃO DE ACESSO
# ==========================================
def checar_admin(user):
    # 1. Se não estiver logado, bloqueia
    if not user.is_authenticated:
        return False
    
    # 2. Se for o superusuário (criado pelo terminal), libera acesso
    if user.is_superuser:
        return True
        
    # 3. Se for usuário comum, checa se o vínculo do perfil é GUARITA ou ADMIN
    if hasattr(user, 'perfil'):
        return user.perfil.vinculo in ['GUARITA', 'ADMIN']
        
    # 4. Se não se encaixar em nada acima, bloqueia
    return False
# ==========================================
# VIEWS DE OPERAÇÂO RAPIDA TELA INICIAL
# ==========================================


@login_required(login_url='/')
def operacao_rapida(request):
    # Verifica se quem está acessando é Admin ou usuário comum
    eh_admin = False
    if request.user.is_superuser:
        eh_admin = True
    elif hasattr(request.user, 'perfil') and request.user.perfil.vinculo in ['GUARITA', 'ADMIN']:
        eh_admin = True
        
    # Envia a variável para o HTML saber o que esconder ou mostrar
    return render(request, 'home/operacao_rapida.html', {'eh_admin': eh_admin})

# ==========================================
# VIEWS DE LOGIN E AUTENTICAÇÃO
# ==========================================
def login_usuario(request):
    # REGRA NOVA: Se já estiver logado, redireciona TODOS para a operação rápida
    if request.user.is_authenticated:
        return redirect('operacao_rapida')

    if request.method == 'POST':
        matricula = request.POST.get('matricula', '').strip()
        senha = request.POST.get('senha', '').strip()

        # O motor do Django verifica se o usuário e a senha criptografada batem
        user = authenticate(request, username=matricula, password=senha)

        if user is not None:
            # O Django cria a sessão segura automaticamente
            login(request, user) 

            # 1. Se for o superusuário do terminal
            if user.is_superuser:
                messages.success(request, 'Bem-vindo, Administrador do Sistema!')
                return redirect('operacao_rapida')

            # 2. Se for um usuário normal (cadastrado pelo sistema)
            try:
                perfil = user.perfil 
                messages.success(request, f'Bem-vindo, {perfil.nome}!')

                # ROTEAMENTO DE ACESSO: Todos vão para a tela de Operação Rápida
                return redirect('operacao_rapida')

            except:
                messages.error(request, 'Perfil de usuário não encontrado.')
                logout(request)
                return redirect('login_usuario')
        else:
            messages.error(request, 'Matrícula ou senha incorretos.')

    return render(request, 'home/login.html')

def logout_usuario(request):
    # O Django destrói a sessão com segurança
    logout(request)
    return redirect('login_usuario')



# ==========================================
# VIEWS PARA PAGINA INICIAL                     
# ========================================== 
# Nova tela inicial (Operação Rápida)
# ==========================================
# VIEWS PARA A TELA "MINHAS CHAVES" E BUSCA
# ==========================================
# ==========================================
# VIEWS PARA A TELA "MINHAS CHAVES" E BUSCA
# ==========================================


# ==========================================
# PAINEL ADM COM FUNCIONALIDADES INTERNAS 
# ==========================================
@user_passes_test(checar_admin, login_url='/operacao-rapida/')
def painel_admin(request):
    chaves = Chave.objects.all()
    return render(request, 'home/index.html', {'chaves': chaves})

# ==========================================
# TELAS PARA GERENCIA DE USUÁRIOS (CRUD)
# ==========================================
def cadastrar_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST) 
        
        if form.is_valid():
            # Inicia uma transação segura: ou salva tudo, ou não salva nada
            try:
                with transaction.atomic():
                    # 1. Pega os dados validados do formulário
                    matricula = form.cleaned_data.get('matricula')
                    nome = form.cleaned_data.get('nome')
                    email = form.cleaned_data.get('email', '')

                    # 2. Cria o usuário nativo do Django (Motor de Login)
                    # O username será a matrícula, e a senha também
                    novo_user_django = User.objects.create_user(
                        username=matricula,
                        password=matricula, 
                        email=email,
                        first_name=nome.split()[0] # Pega só o primeiro nome
                    )

                    # 3. Salva o SEU perfil de usuário e conecta com o do Django
                    perfil_usuario = form.save(commit=False) # Pausa o salvamento
                    perfil_usuario.user = novo_user_django   # Faz a conexão OneToOne
                    perfil_usuario.save()                    # Finaliza o salvamento no banco

                messages.success(request, 'Usuário cadastrado com sucesso!')
                return redirect('listar_usuario')
                
            except Exception as e:
                messages.error(request, f'Erro interno ao criar usuário: {str(e)}')
        else:
            messages.error(request, 'Erro ao cadastrar. Por favor, verifique os dados.')
            
    else:
        form = UsuarioForm()
        
    return render(request, 'home/usuarios/form.html', {'form': form})


@user_passes_test(checar_admin, login_url='/minhas-chaves/')
def listar_usuario(request): # <--- CERTIFIQUE-SE DE QUE O NOME É ESTE
    contexto = {
        'lista': Usuario.objects.all().order_by('-id'),
    }
    return render(request, 'home/usuarios/listagem.html', contexto)


def editar_usuario(request, id):
    try:
        usuario_instancia = Usuario.objects.get(pk=id)
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuário não encontrado')
        return redirect('listar_usuario')

    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario_instancia)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Atualiza o perfil (Usuario)
                    perfil_atualizado = form.save()
                    
                    # Atualiza também o User nativo do Django (se o nome ou e-mail mudou)
                    if perfil_atualizado.user:
                        perfil_atualizado.user.username = perfil_atualizado.matricula
                        perfil_atualizado.user.first_name = perfil_atualizado.nome.split()[0]
                        perfil_atualizado.user.email = perfil_atualizado.email
                        perfil_atualizado.user.save()
                        
                messages.success(request, 'Usuário atualizado com sucesso!')
                return redirect('listar_usuario')
            except Exception as e:
                messages.error(request, f'Erro ao atualizar: {str(e)}')
    else:
        form = UsuarioForm(instance=usuario_instancia)
    
    return render(request, 'home/usuarios/form.html', {'form': form})


def remover_usuario(request, id):
    try:
        usuario_instancia = Usuario.objects.get(pk=id)
        
        # Como o Django User é a base de tudo, deletamos ele primeiro.
        # O "on_delete=models.CASCADE" que colocamos no models.py vai deletar
        # o seu "Usuario" automaticamente junto com o "User" do Django.
        if usuario_instancia.user:
            usuario_instancia.user.delete()
        else:
            usuario_instancia.delete() # Caso seja um usuário antigo sem vínculo
            
        messages.success(request, 'Usuário removido com sucesso!')
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuário não encontrado.')

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

@user_passes_test(checar_admin, login_url='/minhas-chaves/')
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
@user_passes_test(checar_admin, login_url='/minhas-chaves/')
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

@user_passes_test(checar_admin, login_url='/minhas-chaves/')
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


@user_passes_test(checar_admin, login_url='/minhas-chaves/')
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

@user_passes_test(checar_admin, login_url='/minhas-chaves/')
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

@user_passes_test(checar_admin, login_url='/minhas-chaves/')
def listar_emprestimos(request):
    emprestimos = Emprestimo.objects.filter(status='NOVO')
    return render(request, 'home/emprestimos/listagem.html', {'lista': emprestimos})

def cadastrar_emprestimo(request):
    if request.method == 'POST':
        # SALVA A ORIGEM: Se vier da tela rápida, salva 'rapida'. Se não, o padrão é 'admin'.
        origem = request.POST.get('origem')
        if origem:
            request.session['origem_emprestimo'] = origem
        
        origem_atual = request.session.get('origem_emprestimo', 'admin')
        
        form = EmprestimoForm(request.POST)
        if form.is_valid():
            matricula_digitada = form.cleaned_data['matricula']
            try:
                usuario_encontrado = Usuario.objects.get(matricula=matricula_digitada)
            except Usuario.DoesNotExist:
                # Se veio da operação rápida e o usuário não existe, manda de volta para lá com erro
                if origem_atual == 'rapida':
                    messages.error(request, 'Usuário não encontrado.')
                    return redirect('operacao_rapida')
                
                form.add_error('matricula', 'Usuário não encontrado.')
            else:
                Emprestimo.objects.filter(usuario=usuario_encontrado, status='SOLICITADO').delete()
                return redirect('adicionar_chaves_emprestimo', id=usuario_encontrado.id)
        else:
            if origem_atual == 'rapida':
                messages.error(request, 'Matrícula inválida ou não preenchida.')
                return redirect('operacao_rapida')
                
    else:
        form = EmprestimoForm()
    
    return render(request, 'home/emprestimos/forms.html', {'form': form})



def adicionar_chaves_emprestimo(request, id):
    try:
        usuario = Usuario.objects.get(id=id)
    except Usuario.DoesNotExist:
        return redirect('listar_emprestimos')
        
    limite = timezone.now() - timedelta(minutes=30)
    # 1. Busca o que ele está bipando agora (Rascunho)
    emprestimos_em_andamento = Emprestimo.objects.filter(usuario=usuario, status='SOLICITADO', data__gte=limite).order_by('-id')

    # 2. NOVA BUSCA: Pega as chaves que JÁ ESTÃO com ele (Ativas)
    chaves_em_posse = Emprestimo.objects.filter(usuario=usuario, status='NOVO').order_by('-data')

    contexto = {
        'usuario': usuario,
        'emprestimos_em_andamento': emprestimos_em_andamento,
        'chaves_em_posse': chaves_em_posse, # Enviando para o HTML
    }
    return render(request, 'home/emprestimos/emprestimo.html', contexto)

def api_adicionar_chave_emprestimo(request):
    codigo = request.GET.get('codigo', '').strip()
    usuario_id = request.GET.get('usuario_id', '').strip()

    if not codigo or not usuario_id:
        return JsonResponse({'erro': 'Código ausente.'}, status=400)

    if not codigo.isdigit():
        return JsonResponse({'erro': 'Erro: Código inválido. Digite apenas números!'}, status=200)

    try:
        usuario = Usuario.objects.get(id=usuario_id)
        chave_encontrada = Chave.objects.get(id=codigo)

        # Ajustado de chaves= para chave=
        # chave_ativa = Emprestimo.objects.filter(chave=chave_encontrada, status__in=['NOVO', 'REPASSADO']).first()
        # if chave_ativa:
        #     return JsonResponse({'erro': f'Acesso negado: Chave já está com {chave_ativa.usuario.nome}!'}, status=200)
        
        # Ajustado de chaves= para chave=
        chave_ativa = Emprestimo.objects.filter(chave=chave_encontrada, status='NOVO').first()
        if chave_ativa:
            return JsonResponse({'erro': f'Acesso negado: Chave já está com {chave_ativa.usuario.nome}!'}, status=200)    
            
            
        # Ajustado de chaves= para chave=
        chave_rascunho = Emprestimo.objects.filter(chave=chave_encontrada, status='SOLICITADO').first()
        if chave_rascunho:
            return JsonResponse({'erro': 'Esta chave já está na sua lista!'}, status=200)

        # Criação direta na mesma linha, atribuindo a chave diretamente
        novo_emprestimo = Emprestimo.objects.create(
            usuario=usuario, 
            chave=chave_encontrada, 
            status=Emprestimo.Status.SOLICITADO
        )

        return JsonResponse({
            'sucesso': True,
            'emprestimo_id': novo_emprestimo.id,
            'chave_id': chave_encontrada.id,
            'chave_nome': chave_encontrada.nome,
            'chave_setor': chave_encontrada.setor
        })

    except Chave.DoesNotExist:
        return JsonResponse({'erro': 'Chave não encontrada!'}, status=200)
    except Usuario.DoesNotExist:
        return JsonResponse({'erro': 'Usuário não encontrado!'}, status=200)

def finalizar_emprestimo(request, id):
    try:
        usuario = Usuario.objects.get(id=id)
    except Usuario.DoesNotExist:
        return redirect('listar_emprestimos')
    
    rascunhos = Emprestimo.objects.filter(usuario=usuario, status='SOLICITADO')
    chaves_salvas = [emp.chave for emp in rascunhos if emp.chave]
    quantidade = len(chaves_salvas)

    if quantidade > 0:
        rascunhos.update(status='NOVO')
        
        # RECUPERA A ORIGEM DA SESSÃO
        origem = request.session.get('origem_emprestimo', 'admin')
        
        contexto = {
            'usuario': usuario,
            'chaves_salvas': chaves_salvas,
            'quantidade': quantidade,
            'data_atual': timezone.now(),
            'origem': origem  # <-- Envia a origem para o HTML
        }
        
        # Limpa a sessão para não interferir nas próximas ações
        if 'origem_emprestimo' in request.session:
            del request.session['origem_emprestimo']
            
        # Gera o alerta verde flutuante que aparecerá na tela inicial rápida
        if origem == 'rapida':
            messages.success(request, f'{quantidade} chave(s) emprestada(s) com sucesso!')
            
        return render(request, 'home/emprestimos/resumo_sucesso.html', contexto)
    else:
        # messages.error(request, 'Nenhuma chave encontrada para finalizar.')
        return redirect('listar_emprestimos')

def remover_emprestimo(request, id):
    Emprestimo.objects.filter(usuario_id=id, status='SOLICITADO').delete()
    
    origem = request.session.get('origem_emprestimo', 'admin')
    if origem == 'rapida':
        if 'origem_emprestimo' in request.session:
            del request.session['origem_emprestimo']
        return redirect('operacao_rapida')
        
    return redirect('listar_emprestimos')

def remover_chave_emprestimo(request, emprestimo_id, chave_id):
    try:
        emprestimo = Emprestimo.objects.get(id=emprestimo_id)
        usuario_id = emprestimo.usuario.id
        emprestimo.delete() 
        return redirect('adicionar_chaves_emprestimo', id=usuario_id)
    except Emprestimo.DoesNotExist:
        return redirect('listar_emprestimos')
    

# ==========================================
# VIEWS PARA NOVA DEVOLUÇÃO INSTANTÂNEA
# ==========================================

def api_buscar_chave_devolucao(request):
    codigo = request.GET.get('codigo', '').strip()
    
    if not codigo.isdigit():
        return JsonResponse({'erro': 'Código inválido. Digite apenas números!'}, status=200)

    if not codigo:
        return JsonResponse({'erro': 'Nenhum código lido.'}, status=400)

    # 1. Busca o empréstimo ativo (CORRIGIDO para chave__id)
    # emprestimo = Emprestimo.objects.filter( 
    #     chave__id=codigo,
    #     status__in=[Emprestimo.Status.NOVO, Emprestimo.Status.REPASSADO]
    # ).first()
    emprestimo = Emprestimo.objects.filter( 
        chave__id=codigo,
        status=Emprestimo.Status.NOVO
    ).first()

    if not emprestimo:
        return JsonResponse({'erro': 'Chave não encontrada ou não está emprestada.'}, status=404)

    # 2. DEVOLUÇÃO INSTANTÂNEA: Atualiza o banco na mesma hora
    emprestimo.status = Emprestimo.Status.DEVOLVIDO
    # REGITRAR A DATA DA DEVOLUÇÃO
    emprestimo.data_devolucao = timezone.now()  
    emprestimo.save()

    # CORRIGIDO para acessar a chave diretamente
    chave = emprestimo.chave

    # 3. Retorna os dados para a tela mostrar o card
    return JsonResponse({
        'sucesso': True,
        'chave_id': chave.id,
        'chave_nome': chave.nome,
        'usuario_id': emprestimo.usuario.id,
        'usuario_nome': emprestimo.usuario.nome,
        'usuario_matricula': emprestimo.usuario.matricula
    })


def devolver_emprestimo(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip()
        
        # 1. Captura a origem enviada pelo formulário (se não existir, assume 'admin')
        origem = request.POST.get('origem', 'admin')

        if not codigo:
            messages.error(request, 'Nenhum código foi lido ou digitado.')
            # Retorna para a tela certa se der erro de campo vazio
            if origem == 'rapida':
                return redirect('operacao_rapida')
            return redirect('devolver_emprestimo')

        # 2. Busca direta no banco
        # emprestimo = Emprestimo.objects.filter(
        #     chave__id=codigo,
        #     status__in=[Emprestimo.Status.NOVO, Emprestimo.Status.REPASSADO]
        # ).first()
        emprestimo = Emprestimo.objects.filter(
            chave__id=codigo,
            status=Emprestimo.Status.NOVO
        ).first()

        if emprestimo:
            # 3. Devolução
            emprestimo.status = Emprestimo.Status.DEVOLVIDO
            emprestimo.data_devolucao = timezone.now()
            emprestimo.save()
            messages.success(request, f'Chave {emprestimo.chave.nome} devolvida com sucesso!')
        else:
            messages.error(request, 'Chave não encontrada ou já devolvida.')
            
        # 4. Roteamento Inteligente: Volta para a tela de origem
        if origem == 'rapida':
            return redirect('operacao_rapida')
            
        return redirect('devolver_emprestimo')

    # Acesso normal à página dedicada de devolução (GET via Painel Admin)
    return render(request, 'home/emprestimos/devolver.html')

# ==========================================
# TELAs PARA ATALHO ADM E USUÁRIO EMPRESTIMO, RETORNO DE "MINHAS CHAVES" E BUSCA
# ==========================================

@login_required(login_url='/')
def tela_repasse(request):
    """
    Tela mista:
    - Se for usuário comum: mostra apenas as chaves dele.
    - Se for Admin/Guarita: mostra painel de pesquisa por código ou usuário.
    """
    eh_admin = False
    
    # Verifica se é superuser ou tem perfil Guarita/Admin
    if request.user.is_superuser:
        eh_admin = True
    elif hasattr(request.user, 'perfil') and request.user.perfil.vinculo in ['GUARITA', 'ADMIN']:
        eh_admin = True

    if eh_admin:
        # Se for admin, carrega todos os usuários para o Select de pesquisa
        usuarios_lista = Usuario.objects.all().order_by('nome')
        usuario_logado = getattr(request.user, 'perfil', request.user)
        
        contexto = {
            'usuario': usuario_logado,
            'eh_admin': True,
            'usuarios_lista': usuarios_lista,
        }
    else:
        # Se for usuário comum, carrega apenas as chaves dele
        usuario = request.user.perfil
        chaves_em_posse = Emprestimo.objects.filter(usuario=usuario, status='NOVO').order_by('-data')
        
        contexto = {
            'usuario': usuario,
            'eh_admin': False,
            'chaves_em_posse': chaves_em_posse,
        }
        
    return render(request, 'home/emprestimos/repassar.html', contexto)


# ==========================================
# NOVAS APIs PARA O PAINEL DE REPASSE DO ADMIN
# ==========================================

def api_admin_buscar_chave_repasse(request):
    """Busca quem está com a chave através do código de barras"""
    codigo = request.GET.get('codigo', '').strip()
    
    if not codigo.isdigit():
        return JsonResponse({'erro': 'Código inválido.'}, status=400)
        
    emprestimo = Emprestimo.objects.filter(chave__id=codigo, status='NOVO').first()
    
    if not emprestimo:
        return JsonResponse({'erro': 'Esta chave não está emprestada no momento.'}, status=404)
        
    return JsonResponse({
        'sucesso': True,
        'emprestimos': [{
            'id': emprestimo.id,
            'chave_id': emprestimo.chave.id,
            'chave_nome': emprestimo.chave.nome,
            'setor': emprestimo.chave.setor,
            'usuario_atual_id': emprestimo.usuario.id,
            'usuario_atual_nome': emprestimo.usuario.nome,
            'data_emprestimo': timezone.localtime(emprestimo.data).strftime('%d/%m/%Y %H:%M')
        }]
    })


def api_admin_buscar_chaves_usuario(request):
    """Busca todas as chaves em posse de um usuário selecionado no Select"""
    usuario_id = request.GET.get('usuario_id', '').strip()
    
    if not usuario_id:
        return JsonResponse({'erro': 'ID do usuário não fornecido.'}, status=400)
        
    emprestimos = Emprestimo.objects.filter(usuario_id=usuario_id, status='NOVO').order_by('-data')
    
    lista_chaves = []
    for emp in emprestimos:
        lista_chaves.append({
            'id': emp.id,
            'chave_id': emp.chave.id,
            'chave_nome': emp.chave.nome,
            'setor': emp.chave.setor,
            'usuario_atual_id': emp.usuario.id,
            'usuario_atual_nome': emp.usuario.nome,
            'data_emprestimo': timezone.localtime(emp.data).strftime('%d/%m/%Y %H:%M')
        })
        
    return JsonResponse({'sucesso': True, 'emprestimos': lista_chaves})


@require_POST
def api_confirmar_repasse(request):
    """
    Recebe os dados do modal via fetch (AJAX) e processa a troca da chave
    do usuário antigo para o novo usuário.
    """
    try:
        # Pega os dados enviados pelo JavaScript (modal)
        dados = json.loads(request.body)
        chave_id = dados.get('chave_id')
        novo_usuario_id = dados.get('novo_usuario_id')

        if not chave_id or not novo_usuario_id:
            return JsonResponse({'erro': 'Dados incompletos. Faltando chave ou usuário.'}, status=400)

        # 1. Busca o empréstimo ATUAL desta chave
        # emprestimo_atual = Emprestimo.objects.filter(
        #     chave_id=chave_id,
        #     status__in=['NOVO', 'REPASSADO']
        # ).first()
        
        emprestimo_atual = Emprestimo.objects.filter(
            chave_id=chave_id,
            status='NOVO'
        ).first()

        if not emprestimo_atual:
            return JsonResponse({'erro': 'Esta chave não está emprestada no momento.'}, status=404)

        if str(emprestimo_atual.usuario.id) == str(novo_usuario_id):
            return JsonResponse({'erro': 'A chave já está com este usuário.'}, status=400)

        # 2. Encerra o vínculo com o usuário antigo
        emprestimo_atual.status = 'REPASSADO'
        emprestimo_atual.data_devolucao = timezone.now() # Registra o momento exato do repasse
        emprestimo_atual.save()

        # 3. Cria o novo vínculo para o novo usuário
        novo_usuario = Usuario.objects.get(id=novo_usuario_id)
        
        novo_emprestimo = Emprestimo.objects.create(
            usuario=novo_usuario,
            chave=emprestimo_atual.chave,
            status='NOVO'
            # A data de criação já é salva automaticamente pelo auto_now_add no model
        )

        # 4. Retorna sucesso para o JavaScript mostrar a tela verde!
        return JsonResponse({
            'sucesso': True,
            'mensagem': 'Repasse concluído com sucesso!',
            'chave_nome': emprestimo_atual.chave.nome,
            'usuario_antigo': emprestimo_atual.usuario.nome,
            'usuario_novo': novo_usuario.nome,
            'data_repasse': timezone.localtime(novo_emprestimo.data).strftime('%d/%m/%Y %H:%M')
        })

    except Usuario.DoesNotExist:
        return JsonResponse({'erro': 'O usuário selecionado não foi encontrado.'}, status=404)
    except Exception as e:
        return JsonResponse({'erro': f'Erro interno: {str(e)}'}, status=500)


def api_buscar_usuarios(request):
    """
    Retorna uma lista de usuários em formato JSON baseada no termo de busca.
    Usado no campo de Autocomplete do Repasse.
    """
    termo = request.GET.get('q', '').strip()
    
    if len(termo) < 2:
        return JsonResponse({'usuarios': []})
    
    usuarios = Usuario.objects.filter(nome__icontains=termo)[:10]
    
    lista = []
    for u in usuarios:
        lista.append({
            'id': u.id,
            'nome': u.nome,
            'matricula': u.matricula,
            'vinculo': getattr(u, 'vinculo', 'Aluno') 
        })
        
    return JsonResponse({'usuarios': lista})

# ==========================================
# VIEWS PARA ACOMPANHAMENTO E HITÓRICO DE EMPRESTIMOS
# ==========================================

@login_required(login_url='/')
def painel_historico(request):
    """
    Histórico de movimentações.
    Admin vê tudo, usuário comum vê só o dele.
    Filtra as movimentações por data alvo (padrão = hoje) para evitar lentidão.
    """
    # Verifica se é admin
    eh_admin = request.user.is_superuser or (hasattr(request.user, 'perfil') and request.user.perfil.vinculo in ['GUARITA', 'ADMIN'])

    # Captura os parâmetros do filtro
    data_str = request.GET.get('data')
    usuario_id = request.GET.get('usuario')

    # Define a data alvo (se não vier no filtro, será o dia atual)
    if data_str:
        try:
            data_alvo = datetime.strptime(data_str, '%Y-%m-%d').date()
        except ValueError:
            data_alvo = timezone.now().date()
    else:
        data_alvo = timezone.now().date()

    # Prepara a QueryBase e a lista de usuários
    if eh_admin:
        qs = Emprestimo.objects.exclude(status='SOLICITADO')
        usuarios_lista = Usuario.objects.all().order_by('nome')
    else:
        qs = Emprestimo.objects.filter(usuario=request.user.perfil).exclude(status='SOLICITADO')
        usuarios_lista = []

    # Aplica o filtro de usuário (somente se for admin e tiver escolhido alguém)
    if eh_admin and usuario_id and usuario_id != 'Todos':
        qs = qs.filter(usuario_id=usuario_id)

    # A MÁGICA DA PERFORMANCE: Traz apenas o que foi EMPRESTADO na data_alvo OU DEVOLVIDO na data_alvo
    movimentacoes = qs.filter(
        Q(data__date=data_alvo) | Q(data_devolucao__date=data_alvo)
    ).select_related('chave', 'usuario')

    movimentos_list = []
    
    for mov in movimentacoes:
        # 1. EVENTO DE SAÍDA DA CHAVE (Ocorreu no dia alvo)
        if mov.data and mov.data.date() == data_alvo:
            hora_local = timezone.localtime(mov.data).strftime('%H:%M')
            texto_extra = ""
            
            veio_de_repasse = Emprestimo.objects.filter(
                chave=mov.chave,
                status='REPASSADO',
                data_devolucao__gte=mov.data - timedelta(minutes=2),
                data_devolucao__lte=mov.data + timedelta(minutes=2)
            ).exclude(id=mov.id).first()
            
            if veio_de_repasse:
                texto_extra = f"Recebido de: {veio_de_repasse.usuario.nome}"
            
            movimentos_list.append({
                'id': str(mov.id), 
                'cod': mov.chave.nome if mov.chave else 'S/N', 
                'setor': getattr(mov.chave, 'setor', 'Setor não informado'),
                'usuario': str(mov.usuario), 
                'matricula': getattr(mov.usuario, 'matricula', 'S/N'),
                'tipo': 'emprestimo',
                'hora': hora_local,
                'datetime_obj': mov.data,
                'info_repasse': texto_extra
            })

        # 2. EVENTO DE ENTRADA DA CHAVE (Devolução/Repasse ocorreu no dia alvo)
        if mov.data_devolucao and mov.data_devolucao.date() == data_alvo:
            tipo_evento = 'repassado' if mov.status == 'REPASSADO' else 'devolvido'
            hora_devolucao_local = timezone.localtime(mov.data_devolucao).strftime('%H:%M')
            
            texto_extra = ""
            if tipo_evento == 'repassado':
                foi_para = Emprestimo.objects.filter(
                    chave=mov.chave,
                    data__gte=mov.data_devolucao - timedelta(minutes=2),
                    data__lte=mov.data_devolucao + timedelta(minutes=2)
                ).exclude(id=mov.id).first()
                
                if foi_para:
                    texto_extra = f"Para: {foi_para.usuario.nome}"
            
            movimentos_list.append({
                'id': str(mov.id),
                'cod': mov.chave.nome if mov.chave else 'S/N', 
                'setor': getattr(mov.chave, 'setor', 'Setor não informado'),
                'usuario': str(mov.usuario), 
                'matricula': getattr(mov.usuario, 'matricula', 'S/N'),
                'tipo': tipo_evento,
                'hora': hora_devolucao_local,
                'datetime_obj': mov.data_devolucao,
                'info_repasse': texto_extra
            })

    # Ordena da mais recente para a mais antiga do dia
    movimentos_list.sort(key=lambda x: x['datetime_obj'], reverse=True)

    for m in movimentos_list:
        del m['datetime_obj']

    context = {
        'movimentos_json': movimentos_list,
        'eh_admin': eh_admin,
        'usuarios_lista': usuarios_lista,
        'data_filtrada': data_alvo.strftime('%Y-%m-%d'),
        'usuario_filtrado': usuario_id or 'Todos'
    }
    
    return render(request, 'home/historico/historico.html', context)

# ==========================================
# VIEWS PARA CONSULTA DE EMPRESTIMOS POR DATA E EXPORTAÇÃO PARA CSV
# ==========================================
@user_passes_test(checar_admin, login_url='/operacao-rapida/')
def relatorio_emprestimos_data(request):
    emprestimos_lista = []
    
    data_inicial = request.GET.get('data_inicial')
    data_final = request.GET.get('data_final')
    usuario_id = request.GET.get('usuario')
    status_filtro = request.GET.get('status')

    pesquisa_realizada = bool(request.GET)

    if pesquisa_realizada:
        qs = Emprestimo.objects.exclude(status='SOLICITADO').select_related('chave', 'usuario')
        
        if usuario_id and usuario_id != 'Todos':
            qs = qs.filter(usuario_id=usuario_id)
            
        d_inicial = datetime.strptime(data_inicial, '%Y-%m-%d').date() if data_inicial else None
        d_final = datetime.strptime(data_final, '%Y-%m-%d').date() if data_final else None

        for emp in qs:
            chave_nome = emp.chave.nome if emp.chave else '-'
            setor_nome = emp.chave.setor if emp.chave else '-'
            usr_nome = emp.usuario.nome if emp.usuario else '-'
            usr_mat = emp.usuario.matricula if emp.usuario else '-'

            if emp.data:
                data_valida = True
                if d_inicial and emp.data.date() < d_inicial: data_valida = False
                if d_final and emp.data.date() > d_final: data_valida = False
                
                if data_valida and (status_filtro in ['Todos', 'NOVO', None]):
                    emprestimos_lista.append({
                        'id': emp.id,
                        'chave_nome': chave_nome,
                        'setor': setor_nome,
                        'usuario_nome': usr_nome,
                        'matricula': usr_mat,
                        'data_hora': emp.data,
                        'status': 'NOVO' 
                    })

            if emp.data_devolucao:
                data_valida = True
                if d_inicial and emp.data_devolucao.date() < d_inicial: data_valida = False
                if d_final and emp.data_devolucao.date() > d_final: data_valida = False
                
                if data_valida:
                    evento_status = emp.status if emp.status in ['DEVOLVIDO', 'REPASSADO'] else 'DEVOLVIDO'
                    if (status_filtro in ['Todos', evento_status, None]):
                        emprestimos_lista.append({
                            'id': emp.id,
                            'chave_nome': chave_nome,
                            'setor': setor_nome,
                            'usuario_nome': usr_nome,
                            'matricula': usr_mat,
                            'data_hora': emp.data_devolucao,
                            'status': evento_status
                        })

        emprestimos_lista.sort(key=lambda x: x['data_hora'], reverse=True)

    if request.GET.get('exportar') == 'csv':
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="relatorio_chaves.csv"'
        
        writer = csv.writer(response, delimiter=';')
        writer.writerow(['ID', 'CHAVE', 'SETOR', 'USUÁRIO', 'MATRÍCULA', 'DATA/HORA', 'STATUS'])
        
        for emp in emprestimos_lista:
            data_formatada = emp['data_hora'].strftime('%d/%m/%Y %H:%M') if emp['data_hora'] else '-'
            status_texto = 'ATIVO' if emp['status'] == 'NOVO' else emp['status']
            
            writer.writerow([
                emp['id'],
                emp['chave_nome'],
                emp['setor'],
                emp['usuario_nome'],
                emp['matricula'],
                data_formatada,
                status_texto
            ])
            
        return response 

    usuarios_lista = Usuario.objects.all()

    context = {
        'emprestimos': emprestimos_lista,
        'usuarios_lista': usuarios_lista,
        'pesquisa_realizada': pesquisa_realizada 
    }
    
    return render(request, 'home/relatorio/relatorio.html', context)

