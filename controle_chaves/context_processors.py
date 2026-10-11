from .models import Notificacao

def notificacoes_guarita(request):
    if not request.user.is_authenticated:
        return {}
    
    eh_admin = request.user.is_superuser or (hasattr(request.user, 'perfil') and request.user.perfil.vinculo in ['GUARITA', 'ADMIN'])
    
    # Se for admin, busca as notificações gerais (sem destinatário específico)
    if eh_admin:
        nao_lidas = Notificacao.objects.filter(lida=False, destinatario__isnull=True).order_by('-data_criacao')
    
    # Se for aluno/usuário comum, busca APENAS as notificações dele
    elif hasattr(request.user, 'perfil'):
        nao_lidas = Notificacao.objects.filter(lida=False, destinatario=request.user.perfil).order_by('-data_criacao')
    
    else:
        nao_lidas = Notificacao.objects.none()

    return {
        'notificacoes_nao_lidas': nao_lidas[:10], # Mostra no máximo as 10 mais recentes
        'qtd_notificacoes': nao_lidas.count()
    }