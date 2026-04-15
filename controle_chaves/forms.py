from django import forms
from .models import Usuario, Chave, Emprestimo

# Criamos uma classe de formulário baseada no nosso Modelo Usuario
from django import forms
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nome', 'matricula', 'senha_embarcado', 'vinculo', 'email', 'telefone']
        
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome Completo'}),
            'matricula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Matrícula'}),
            'senha_embarcado': forms.PasswordInput(render_value=True, attrs={
                'class': 'form-control', 
                'placeholder': '8 dígitos numéricos',
                'maxlength': '8',
                'type': 'number' # Garante que o teclado no celular seja numérico
            }),
            'vinculo': forms.Select(attrs={'class': 'form-select'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@ifpi.edu.br'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(86) 99999-9999'}),
        }

    # Validação customizada para a senha de 8 dígitos
    def clean_senha_embarcado(self):
        senha = self.cleaned_data.get('senha_embarcado')
        if len(senha) != 8:
            raise forms.ValidationError("A senha deve ter exatamente 8 dígitos.")
        if not senha.isdigit():
            raise forms.ValidationError("A senha deve conter apenas números.")
        return senha