from datetime import timedelta
from django.utils import timezone
from django.shortcuts import get_object_or_404, render, HttpResponse, redirect
from django.utils import timezone
from .models import Chave, Usuario, Emprestimo
from .forms import EmprestimoForm, UsuarioForm, ChaveForm # <--- Adicionamos o ChaveForm aqui
from django.contrib import messages  # <--- Faltava esta importação!
import io
import base64
import json
from django.http import JsonResponse
import barcode
from barcode.writer import ImageWriter
from django.shortcuts import render
from django.db.models import Q
from datetime import datetime
import csv


# ==========================================
# VIEWS PARA PAGINA INICIAL
# ========================================== 
# Nova tela inicial (Operação Rápida)
def operacao_rapida(request):
    return render(request, 'home/operacao_rapida.html')

# Antiga home, agora será o painel Admin
def painel_admin(request):
    chaves = Chave.objects.all()
    return render(request, 'home/index.html', {'chaves': chaves})


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

def listar_emprestimos(request):
    emprestimos = Emprestimo.objects.filter(status__in=['NOVO', 'REPASSADO'])
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

# def adicionar_chaves_emprestimo(request, id):
#     try:
#         usuario = Usuario.objects.get(id=id)
#     except Usuario.DoesNotExist:
#         return redirect('listar_emprestimos')
        
#     limite = timezone.now() - timedelta(minutes=30)
#     emprestimos_em_andamento = Emprestimo.objects.filter(usuario=usuario, status='SOLICITADO', data__gte=limite).order_by('-id')

#     contexto = {
#         'usuario': usuario,
#         'emprestimos_em_andamento': emprestimos_em_andamento,
#     }
#     return render(request, 'home/emprestimos/emprestimo.html', contexto)

def adicionar_chaves_emprestimo(request, id):
    try:
        usuario = Usuario.objects.get(id=id)
    except Usuario.DoesNotExist:
        return redirect('listar_emprestimos')
        
    limite = timezone.now() - timedelta(minutes=30)
    # 1. Busca o que ele está bipando agora (Rascunho)
    emprestimos_em_andamento = Emprestimo.objects.filter(usuario=usuario, status='SOLICITADO', data__gte=limite).order_by('-id')

    # 2. NOVA BUSCA: Pega as chaves que JÁ ESTÃO com ele (Ativas)
    chaves_em_posse = Emprestimo.objects.filter(usuario=usuario, status__in=['NOVO', 'REPASSADO']).order_by('-data')

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
        chave_ativa = Emprestimo.objects.filter(chave=chave_encontrada, status__in=['NOVO', 'REPASSADO']).first()
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
    emprestimo = Emprestimo.objects.filter( 
        chave__id=codigo,
        status__in=[Emprestimo.Status.NOVO, Emprestimo.Status.REPASSADO]
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
        emprestimo = Emprestimo.objects.filter(
            chave__id=codigo,
            status__in=[Emprestimo.Status.NOVO, Emprestimo.Status.REPASSADO]
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
# VIEWS PARA ACOMPANHAMENTO E HITÓRICO DE EMPRESTIMOS
# ==========================================

# def painel_historico(request):
#     hoje = timezone.now().date()
    
#     # Busca registros que foram CRIADOS hoje OU DEVOLVIDOS hoje
#     movimentacoes_do_dia = Emprestimo.objects.filter(
#         Q(data__date=hoje) | Q(data_devolucao__date=hoje)
#     ).exclude(status='SOLICITADO')

#     movimentos_list = []
    
#     for mov in movimentacoes_do_dia:
        
#         # 1. EVENTO DE SAÍDA DA CHAVE (Empréstimo ou Repasse recebido)
#         if mov.data and mov.data.date() == hoje:
#             movimentos_list.append({
#                 'id': str(mov.id), 
#                 'cod': mov.chave.nome if mov.chave else 'S/N', # CORRIGIDO AQUI PARA .nome
#                 'setor': getattr(mov.chave, 'setor', 'Setor não informado'),
#                 'usuario': str(mov.usuario), 
#                 'matricula': getattr(mov.usuario, 'matricula', 'S/N'),
#                 'tipo': 'emprestimo',
#                 'hora': mov.data.strftime('%H:%M'),
#                 'datetime_obj': mov.data 
#             })

#         # 2. EVENTO DE ENTRADA DA CHAVE (Devolução para guarita ou Repasse para outro)
#         if mov.data_devolucao and mov.data_devolucao.date() == hoje:
#             tipo_evento = 'repassado' if mov.status == 'REPASSADO' else 'devolvido'
            
#             movimentos_list.append({
#                 'id': str(mov.id),
#                 'cod': mov.chave.nome if mov.chave else 'S/N', # JÁ ESTAVA CORRETO AQUI
#                 'setor': getattr(mov.chave, 'setor', 'Setor não informado'),
#                 'usuario': str(mov.usuario), 
#                 'matricula': getattr(mov.usuario, 'matricula', 'S/N'),
#                 'tipo': tipo_evento,
#                 'hora': mov.data_devolucao.strftime('%H:%M'),
#                 'datetime_obj': mov.data_devolucao
#             })

#     movimentos_list.sort(key=lambda x: x['datetime_obj'], reverse=True)

#     for m in movimentos_list:
#         del m['datetime_obj']

#     context = {
#         'movimentos_json': movimentos_list
#     }
    
#     return render(request, 'home/historico/historico.html', context)


def painel_historico(request):
    hoje = timezone.now().date()
    
    # Busca registros que foram CRIADOS hoje OU DEVOLVIDOS hoje
    movimentacoes_do_dia = Emprestimo.objects.filter(
        Q(data__date=hoje) | Q(data_devolucao__date=hoje)
    ).exclude(status='SOLICITADO')

    movimentos_list = []
    
    for mov in movimentacoes_do_dia:
        
        # 1. EVENTO DE SAÍDA DA CHAVE (Empréstimo ou Repasse recebido)
        if mov.data and mov.data.date() == hoje:
            
            # CONVERSÃO AQUI: timezone.localtime() converte o UTC para o horário local
            hora_local = timezone.localtime(mov.data).strftime('%H:%M')
            
            movimentos_list.append({
                'id': str(mov.id), 
                'cod': mov.chave.nome if mov.chave else 'S/N', 
                'setor': getattr(mov.chave, 'setor', 'Setor não informado'),
                'usuario': str(mov.usuario), 
                'matricula': getattr(mov.usuario, 'matricula', 'S/N'),
                'tipo': 'emprestimo',
                'hora': hora_local, # Variável convertida inserida aqui
                'datetime_obj': mov.data 
            })

        # 2. EVENTO DE ENTRADA DA CHAVE (Devolução para guarita ou Repasse para outro)
        if mov.data_devolucao and mov.data_devolucao.date() == hoje:
            tipo_evento = 'repassado' if mov.status == 'REPASSADO' else 'devolvido'
            
            # CONVERSÃO AQUI TAMBÉM
            hora_devolucao_local = timezone.localtime(mov.data_devolucao).strftime('%H:%M')
            
            movimentos_list.append({
                'id': str(mov.id),
                'cod': mov.chave.nome if mov.chave else 'S/N', 
                'setor': getattr(mov.chave, 'setor', 'Setor não informado'),
                'usuario': str(mov.usuario), 
                'matricula': getattr(mov.usuario, 'matricula', 'S/N'),
                'tipo': tipo_evento,
                'hora': hora_devolucao_local, # Variável convertida inserida aqui
                'datetime_obj': mov.data_devolucao
            })

    movimentos_list.sort(key=lambda x: x['datetime_obj'], reverse=True)

    for m in movimentos_list:
        del m['datetime_obj']

    context = {
        'movimentos_json': movimentos_list
    }
    
    return render(request, 'home/historico/historico.html', context)

# ==========================================
# VIEWS PARA CONSULTA DE EMPRESTIMOS POR DATA E EXPORTAÇÃO PARA CSV
# ==========================================

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

            # EVENTO 1: SAÍDA
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

            # EVENTO 2: ENTRADA
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

        # Ordena a lista
        emprestimos_lista.sort(key=lambda x: x['data_hora'], reverse=True)

    # ==========================================
    # LÓGICA DE EXPORTAÇÃO PARA EXCEL/CSV
    # ==========================================
    if request.GET.get('exportar') == 'csv':
        # UTF-8 com assinatura (BOM) para o Excel reconhecer acentos
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="relatorio_chaves.csv"'
        
        # Ponto e vírgula separa as colunas no Excel brasileiro
        writer = csv.writer(response, delimiter=';')
        
        # Cabeçalho da Tabela
        writer.writerow(['ID', 'CHAVE', 'SETOR', 'USUÁRIO', 'MATRÍCULA', 'DATA/HORA', 'STATUS'])
        
        # Linhas de Dados
        for emp in emprestimos_lista:
            data_formatada = emp['data_hora'].strftime('%d/%m/%Y %H:%M') if emp['data_hora'] else '-'
            
            # Ajuste amigável do status
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
    # ==========================================

    usuarios_lista = Usuario.objects.all()

    context = {
        'emprestimos': emprestimos_lista,
        'usuarios_lista': usuarios_lista,
        'pesquisa_realizada': pesquisa_realizada 
    }
    
    return render(request, 'home/relatorio/relatorio.html', context)

