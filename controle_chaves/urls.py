from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('usuarios/cadastrar/', views.cadastrar_usuario, name='cadastrar_usuario'),
    path('usuarios/listar/', views.listar_usuario, name='listar_usuario'),   
    path('usuarios/editar/<int:id>', views.editar_usuario, name='editar_usuario'),
    path('usuarios/remover/<int:id>/', views.remover_usuario, name='remover_usuario'),
    path('usuarios/detalhes/<int:id>/', views.detalhar_usuario, name='detalhar_usuario'),
    
]