from django.db import models
from django.utils import timezone
# Create your models here.

#classe para o usuário
class Usuario(models.Model):
    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return f"{self.nome}  ({self.matricula})"
    
    
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
    
    