from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('usuarios/cadastrar/', views.cadastrar_usuario, name='cadastrar_usuario'),
    
]