from django import forms
from .models import Usuario, Chave, Emprestimo

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nome', 'matricula', 'vinculo', 'email', 'telefone']
        
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome Completo'}),
            'matricula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Matrícula'}),
            'vinculo': forms.Select(attrs={'class': 'form-select'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@ifpi.edu.br'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(86) 99999-9999'}),
        }

class ChaveForm(forms.ModelForm):
    class Meta:
        model = Chave
        fields = ['nome', 'setor',]
        
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Chave 01'}),
            'setor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Laboratório de Informática'}),
            # 'disponivel': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }