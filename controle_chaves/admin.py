from django.contrib import admin
from .models import Usuario, Chave, Emprestimo

# Register your models here.
admin.site.register(Usuario)
admin.site.register(Chave)
admin.site.register(Emprestimo)
