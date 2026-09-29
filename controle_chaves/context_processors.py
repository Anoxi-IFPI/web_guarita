from .models import Notificacao

def notificacoes_guarita(request):
    # Se o usuário não estiver logado, não envia nada
    if not request.user.is_authenticated:
        return {}
    
    # Verifica se é admin/guarita
    eh_admin = False
    if request.user.is_superuser:
        eh_admin = True
    elif hasattr(request.user, 'perfil') and request.user.perfil.vinculo in ['GUARITA', 'ADMIN']:
        eh_admin = True
        
    # Se for admin, busca as notificações não lidas
    if eh_admin:
        nao_lidas = Notificacao.objects.filter(lida=False).order_by('-data_criacao')
        qtd_nao_lidas = nao_lidas.count()
        return {
            'notificacoes_nao_lidas': nao_lidas,
            'qtd_notificacoes': qtd_nao_lidas
        }
    
    # Se não for admin, não envia notificações
    return {}