from django.contrib import admin
from .models import TiposExames, SolicitacaoExame, PedidosExames, AcessoMedico

# Register your models here.
admin.site.register(TiposExames)
admin.site.register(SolicitacaoExame)
admin.site.register(PedidosExames)
admin.site.register(AcessoMedico)