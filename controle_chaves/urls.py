from django.urls import path
from . import views

urlpatterns = [
    
    # --- ROTAS DE USUÁRIOS ---
    path('', views.home, name='home'),
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
    
]