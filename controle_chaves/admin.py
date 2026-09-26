# from django.contrib import admin
# from .models import Usuario, Chave, Emprestimo

# # Register your models here.
# admin.site.register(Usuario)
# admin.site.register(Chave)
# admin.site.register(Emprestimo)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Usuario, Chave, Emprestimo

# 1. Dizemos ao Django para colocar o nosso "Usuario" (Perfil) como um anexo (Inline)
class UsuarioInline(admin.StackedInline):
    model = Usuario
    can_delete = False
    verbose_name_plural = 'Informações Adicionais (Perfil)'

# 2. Criamos um novo modelo de Admin que junta o User padrão com o nosso Inline
class UserAdmin(BaseUserAdmin):
    inlines = (UsuarioInline,)

# 3. Desregistramos o User antigo e registramos o novo turbinado
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Registra as outras tabelas normalmente
admin.site.register(Chave)
admin.site.register(Emprestimo)