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
    
    
class Chave(models.Model):
    # Novo campo para a Tag RFID
    nome = models.CharField(max_length=50) # Ex: Chave 01
    setor = models.CharField(max_length=100) # Ex: Laboratório de Informática
    disponivel = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome} - {self.setor}"
    

class Emprestimo(models.Model):
    # O Empréstimo une o Usuário, as Chaves e o momento (Data/Hora)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    chaves = models.ManyToManyField(Chave)
    
    # default=timezone.now preenche a data e hora automaticamente no momento do registro
    data_hora = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Empréstimo de {self.usuario.nome} em {self.data_hora.strftime('%d/%m/%Y %H:%M')}"