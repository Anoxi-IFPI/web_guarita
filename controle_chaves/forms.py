from django import forms
from .models import Usuario, Chave, Emprestimo

# Criamos uma classe de formulário baseada no nosso Modelo Usuario
class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        # Quais campos queremos que apareçam na tela?
        fields = ['nome', 'matricula']
        
        # Widgets servem para injetarmos classes CSS (Bootstrap) no HTML gerado pelo Django
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: João da Silva'}),
            'matricula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 2024123456'}),
        }
        
        # Podemos mudar os nomes das etiquetas (labels) se quisermos
        labels = {
            'nome': 'Nome Completo',
            'matricula': 'Matrícula SIAPE/RA'
        }