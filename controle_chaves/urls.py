from django.urls import path
from . import views

urlpatterns = [
    
    # --- ROTAS DE USUÁRIOS ---
# --- ROTA INICIAL (OPERAÇÃO RÁPIDA) ---
    path('', views.operacao_rapida, name='operacao_rapida'),
    
    # --- ROTA DO PAINEL ADMIN (Antiga Home) ---
    path('painel/', views.painel_admin, name='painel_admin'),
    
    path('usuarios/cadastrar/', views.cadastrar_usuario, name='cadastrar_usuario'),
    path('usuarios/listar/', views.listar_usuario, name='listar_usuario'),   
    path('usuarios/editar/<int:id>', views.editar_usuario, name='editar_usuario'),
    path('usuarios/remover/<int:id>/', views.remover_usuario, name='remover_usuario'),
    path('usuarios/detalhes/<int:id>/', views.detalhar_usuario, name='detalhar_usuario'),
    
    # --- NOVAS ROTAS DE CHAVES ---
    path('chaves/listar/', views.listar_chave, name='listar_chave'),
    path('chaves/cadastrar/', views.cadastrar_chave, name='cadastrar_chave'),
    path('chaves/detalhes/<int:id>/', views.detalhar_chave, name='detalhar_chave'),
    path('chaves/remover/<int:id>/', views.remover_chave, name='remover_chave'),
    path('chaves/editar/<int:id>/', views.editar_chave, name='editar_chave'),
    path("barcode/<int:id>/",views.gerar_codigo_barras,name="gerar_barcode"),

   # --- ROTAS DE EMPRÉSTIMOS ---
   path('emprestimos/', views.listar_emprestimos, name='listar_emprestimos'),
    path('emprestimos/cadastrar/', views.cadastrar_emprestimo, name='cadastrar_emprestimo'),
    path('emprestimos/registro/<int:id>/', views.adicionar_chaves_emprestimo, name='adicionar_chaves_emprestimo'),
    path('api/adicionar-chave-emprestimo/', views.api_adicionar_chave_emprestimo, name='api_adicionar_chave_emprestimo'), 
    path('emprestimos/finalizar/<int:id>/', views.finalizar_emprestimo, name='finalizar_emprestimo'),   
    path('emprestimos/remover-chave/<int:emprestimo_id>/<int:chave_id>/', views.remover_chave_emprestimo, name='remover_chave_emprestimo'),
    path('emprestimos/remover/<int:id>/', views.remover_emprestimo, name='remover_emprestimo'),
    
    # NOVAS ROTAS
    path('api/buscar-chave-devolucao/', views.api_buscar_chave_devolucao, name='api_buscar_chave_devolucao'),
    path('emprestimos/devolver/', views.devolver_emprestimo, name='devolver_emprestimo'),
    # path('emprestimos/repassar/<int:id>/', views.repassar_emprestimo, name='repassar_emprestimo'),
]