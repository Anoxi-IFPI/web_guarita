from django.db import models
from django.utils import timezone
# Create your models here.

#classe para o usuário
from django.db import models

class Usuario(models.Model):
    # Opções para o Select de Vínculo
    VINCULO_CHOICES = [
        ('ALUNO', 'Aluno'),
        ('PROFESSOR', 'Professor'),
        ('SERVIDOR', 'Servidor'),
        ('TERCEIRIZADO', 'Terceirizado'),
    ]

    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_length=20, unique=True)
    # Senha de 8 dígitos para o hardware/embarcado
    senha_embarcado = models.CharField(max_length=8, help_text="Senha numérica de 8 dígitos")
    vinculo = models.CharField(max_length=20, choices=VINCULO_CHOICES, default='ALUNO')
    email = models.EmailField()
    telefone = models.CharField(max_length=15)

    def __str__(self):
        return self.nome
    
    
#classe para as chaves
class Chave(models.Model):
    nome = models.CharField(max_length=50) # Ex: Chave 01
    setor = models.CharField(max_length=100) # Ex: Laboratório de Informática
    disponivel = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome} - {self.setor}"

#classe de emprestimos 
class Emprestimo(models.Model):
    chave = models.ForeignKey(Chave, on_delete=models.CASCADE)
    funcionario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    data_retirada = models.DateTimeField(default=timezone.now)
    data_devolucao = models.DateTimeField(null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.chave} com {self.funcionario}"
    
    