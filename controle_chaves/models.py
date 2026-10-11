from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User 

# ==========================================
# MODEL DE USUÁRIO (Perfil)
# ==========================================
class Usuario(models.Model):
    VINCULO_CHOICES = [
        ('ALUNO', 'Aluno'),
        ('PROFESSOR', 'Professor'),
        ('SERVIDOR', 'Servidor'),
        ('TERCEIRIZADO', 'Terceirizado'),
        ('GUARITA', 'Guarita'),
        ('ADMIN', 'Administrador'),
    ]

    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='perfil'
    )
    
    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_length=20, unique=True)
    vinculo = models.CharField(max_length=20, choices=VINCULO_CHOICES, default='ALUNO')
    email = models.EmailField()
    telefone = models.CharField(max_length=15)

    def __str__(self):
        return self.nome
    
# ==========================================
# MODEL DE CHAVE
# ==========================================
class Chave(models.Model):
    nome = models.CharField(max_length=50) # Ex: Chave 01
    setor = models.CharField(max_length=100) # Ex: Laboratório de Informática
    disponivel = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome} - {self.setor}"
    
# ==========================================
# MODEL DE EMPRÉSTIMO
# ==========================================
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
    
    chave = models.ForeignKey(
        Chave, 
        on_delete=models.PROTECT, 
        related_name='emprestimos', 
        null=True, 
        blank=True
    )

    data = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.NOVO
    )
    
    data_devolucao = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-data']

    def __str__(self):
        return f'Empréstimo #{self.id} - {self.usuario.nome}'
    
# ==========================================
# MODEL DE NOTIFICAÇÃO
# ==========================================
class Notificacao(models.Model):
    mensagem = models.CharField(max_length=255)
    chave = models.ForeignKey(Chave, on_delete=models.CASCADE, null=True, blank=True)
    
    # Novo campo para definir de quem é a notificação
    destinatario = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='notificacoes'
    )
    
    lida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.mensagem} - {'Lida' if self.lida else 'Não Lida'}"