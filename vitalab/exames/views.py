from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import TiposExames, PedidosExames, SolicitacaoExame
from django.utils import timezone
from django.contrib import messages
from django.contrib.messages import constants
# Create your views here.

@login_required
def solicitar_exames(request):
    tipos_exames = TiposExames.objects.all()
    if request.method == "GET":
        return render(request, 'solicitar_exames.html', {'tipos_exames': tipos_exames})
    elif request.method == "POST":
        tipos_exames = TiposExames.objects.all()
        exames_id = request.POST.getlist('exames')

        solicitacao_exames = TiposExames.objects.filter(id__in=exames_id)

        preco_total = 0.00
        for i in solicitacao_exames:
            if i.disponivel:
                preco_total += i.preco

        now = timezone.now()
        data_formatada = now.strftime('%d de %B')

        return render(request, 'solicitar_exames.html', {'tipos_exames': tipos_exames,
                                                         'solicitacao_exames': solicitacao_exames,
                                                         'preco_total': preco_total,
                                                         'data_formatada': data_formatada})
    

@login_required
def fechar_pedido(request):
    exames_id = request.POST.getlist('exames')

    pedidos_exames = PedidosExames(
        usuario=request.user,
        data=timezone.now()
    )
    pedidos_exames.save()

    solicitacao_exames = TiposExames.objects.filter(id__in=exames_id)

    for exame in solicitacao_exames:
        solicitacao_exame_temp = SolicitacaoExame(
            usuario=request.user,
            exame=exame,
            status="E"
        )
        solicitacao_exame_temp.save()
        pedidos_exames.exames.add(solicitacao_exame_temp)

    pedidos_exames.save()
    messages.add_message(request, constants.SUCCESS, 'Pedido de exame cadastrado com sucesso!')
    return redirect('/exames/gerenciar_pedidos/')
    # return HttpResponse('deubom')

@login_required
def gerenciar_pedidos(request):
    pedidos_exames = PedidosExames.objects.filter(usuario=request.user)
    return render(request, 'gerenciar_pedidos.html', {'pedidos_exames': pedidos_exames})

@login_required
def cancelar_pedido(request, pedido_id):
    pedido = PedidosExames.objects.get(id=pedido_id)
    if not pedido.usuario == request.user:
        messages.add_message(request, constants.ERROR, 'Esse pedido não é seu, portanto, não pode cancelar!')
        return redirect('/exames/gerenciar_pedidos/')
    pedido.agendado = False
    pedido.save()
    messages.add_message(request, constants.SUCCESS, 'Pedido de exame cancelado com sucesso!')
    return redirect('/exames/gerenciar_pedidos/')

@login_required
def gerenciar_exames(request):
    exames = SolicitacaoExame.objects.filter(usuario=request.user)
    return render(request, 'gerenciar_exames.html', {'exames': exames})

@login_required
def permitir_abrir_exame(request, exame_id):
    exame = SolicitacaoExame.objects.get(id=exame_id)

    if not exame.requer_senha:
        # verificar se tem pdf
        return redirect(exame.resultado.url)
    
    return redirect(f'/exames/solicitar_senha_exame/{exame_id}')

@login_required
def solicitar_senha_exame(request, exame_id):
    exame = SolicitacaoExame.objects.get(id=exame_id)
    if request.method == "GET":
        if not exame.usuario == request.user:
            messages.add_message(request, constants.ERROR, 'Esse pedido não é seu!')
            return redirect('/exames/gerenciar_exames/')
        return render(request, 'solicitar_senha_exame.html', {'exame': exame})
    elif request.method == "POST":
        senha = request.POST.get("senha")
        if senha == exame.senha:
            return redirect(exame.resultado.url)
        else:
            messages.add_message(request, constants.ERROR, 'Senha inválida')
            return redirect(f'/exames/solicitar_senha_exame/{exame.id}')