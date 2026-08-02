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
    vinculo = models.CharField(max_length=20, choices=VINCULO_CHOICES, default='ALUNO')
    email = models.EmailField()
    telefone = models.CharField(max_length=15)

    def __str__(self):
        return self.nome
    
    
# models.py
from django.db import models

class Chave(models.Model):
    # Criamos uma lista de tuplas. 
    # O primeiro valor ('A') é o que vai para o banco de dados.
    # O segundo valor ('Bloco A') é o que aparece na tela para o usuário.
    OPCOES_BLOCO = [
        ('A', 'Bloco A'),
        ('B', 'Bloco B'),
        ('C', 'Bloco C'),
        ('D', 'Bloco D'),
    ]

    nome = models.CharField(max_length=100)
    setor = models.CharField(max_length=100)
    # Adicionamos o novo campo aqui:
    bloco = models.CharField(
        max_length=1, 
        choices=OPCOES_BLOCO, 
        default='A',
        verbose_name="Bloco/Local"
    )

    def __str__(self):
        return self.nome

#classe de emprestimos 
class Emprestimo(models.Model):
    chave = models.ForeignKey(Chave, on_delete=models.CASCADE)
    funcionario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    data_retirada = models.DateTimeField(default=timezone.now)
    data_devolucao = models.DateTimeField(null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.chave} com {self.funcionario}"
    
    