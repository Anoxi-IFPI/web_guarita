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
    

# class Emprestimo(models.Model):

#     class Status(models.TextChoices):
#         NOVO = 'NOVO', 'Novo'
#         SOLICITADO = 'SOLICITADO', 'Solicitado'
#         DEVOLVIDO = 'DEVOLVIDO', 'Devolvido'
#         REPASSADO = 'REPASSADO', 'Repassado'

#     usuario = models.ForeignKey(
#         Usuario,
#         on_delete=models.PROTECT,
#         related_name='emprestimos'
#     )
    
#     chaves = models.ManyToManyField(Chave, related_name='emprestimos', blank=True)

#     data = models.DateTimeField(
#         auto_now_add=True
#     )

#     status = models.CharField(
#         max_length=10,
#         choices=Status.choices,
#         default=Status.NOVO
#     )

#     class Meta:
#         ordering = ['-data']

#     def __str__(self):
#         return f'Empréstimo #{self.id} - {self.usuario}'

class Emprestimo(models.Model):
    class Status(models.TextChoices):
        NOVO = 'NOVO', 'Novo'
        SOLICITADO = 'SOLICITADO', 'Solicitado'
        DEVOLVIDO = 'DEVOLVIDO', 'Devolvido'
        REPASSADO = 'REPASSADO', 'Repassado'

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='emprestimos'
    )
    
    # ======= A MÁGICA ACONTECE AQUI =======
    # Substituímos o ManyToManyField por ForeignKey. 
    # O banco guardará o ID da chave diretamente aqui.
    chave = models.ForeignKey(
        Chave, 
        on_delete=models.PROTECT, 
        related_name='emprestimos', 
        null=True,  # Permite que não quebre ao fazer a migração dos dados antigos
        blank=True
    )

    # Este campo 'data' agora registrará a data e hora exata daquela ÚNICA chave
    data = models.DateTimeField(
        auto_now_add=True
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.NOVO
    )

    class Meta:
        ordering = ['-data']

    def __str__(self):
        return f'Empréstimo #{self.id} - {self.usuario}'