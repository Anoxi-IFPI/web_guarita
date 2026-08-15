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
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Laboratório de Informática'}),
            'setor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Bloco A / Sala 01'}),
            # 'disponivel': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        


class EmprestimoForm(forms.ModelForm):
    # Criamos um campo customizado para receber a matrícula,
    # já que a matrícula pertence ao Usuário e não diretamente ao Empréstimo.
    matricula = forms.CharField(
        label='Matrícula',
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'input-grande', 
            'placeholder': 'Ex: 2023112lcom0011',
            'autofocus': True,
            'id': 'matricula-input'
        })
    )

    class Meta:
        model = Emprestimo
        # O professor sugeriu colocar a matrícula nos fields. 
        # Como não vamos preencher o 'status', a 'data' nem o 'usuario' 
        # diretamente na tela (o sistema fará isso sozinho), deixamos apenas a matrícula.
        fields = ['matricula']