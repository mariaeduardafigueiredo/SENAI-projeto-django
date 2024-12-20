from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from app.forms import EquipamentoForm
from app.models import Equipamento, Usuario
from app.utils import obter_data_resumida
from app.utils.enums import CategoriaEPI

from .base import home, logar


@login_required()
def obter_equipamentos(request: WSGIRequest) -> HttpResponse:
    user = request.user

    # O Usuário está autenticado?
    if not user.is_authenticated:
        messages.error(request, 'Você não está logado!')
        return redirect(logar)

    # Verifica se o 'ROLE' do 'Usuário' não é 'Admin' ou 'Supervisor'
    if not user.groups.filter(name__in=['Admin', 'Supervisor']).exists():
        messages.warning(request, 'Você não possui permissão!')
        return redirect(home)   

    query = request.GET.get('search')
    if query:
        equipamentos: list[Equipamento] = Equipamento.objects.filter(nome__icontains=query)
    else:
        equipamentos: list[Equipamento] = Equipamento.objects.all()

    user_groups = request.user.groups.values_list('name', flat=True)
    foto = Usuario.objects.filter(id=request.user.pk).values_list('foto', flat=True).first()

    # Formata a 'validade' e 'categoria' para exibição
    for equipamento in equipamentos:
        equipamento.validade = obter_data_resumida(equipamento.validade)
        equipamento.categoria = CategoriaEPI(equipamento.categoria).label

    context = {
        'user_groups': user_groups,
        'equipamentos': equipamentos,
        'foto': foto,
        'MEDIA_URL': settings.MEDIA_URL
    }

    return render(request, 'pages/interno/equipamento/listar_equipamentos.html', context)


@login_required()
def criar_equipamento(request: WSGIRequest) -> HttpResponse:
    user = request.user

    # O Usuário está autenticado?
    if not user.is_authenticated:
        messages.error(request, 'Você não está logado!')
        return redirect(logar)

    # Verifica se o 'ROLE' do 'Usuário' não é 'Admin' ou 'Supervisor'
    if not user.groups.filter(name__in=['Admin', 'Supervisor']).exists():
        messages.warning(request, 'Você não possui permissão!')
        return redirect(home)

    if request.method == 'POST':
        form = EquipamentoForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Equipamento criado com sucesso!')
            return redirect(obter_equipamentos)
    else:
        form = EquipamentoForm()

    user_groups = request.user.groups.values_list('name', flat=True)
    foto = Usuario.objects.filter(id=request.user.pk).values_list('foto', flat=True).first()

    context = {
        'user_groups': user_groups,
        'form': form,
        'foto': foto,
        'MEDIA_URL': settings.MEDIA_URL
    }

    return render(request, 'pages/interno/equipamento/criar_equipamento.html', context)


@login_required()
def deletar_equipamento(request: WSGIRequest, slug: str) -> HttpResponse:
    user = request.user

    # O Usuário está autenticado?
    if not user.is_authenticated:
        messages.error(request, 'Você não está logado!')
        return redirect(logar)

    # Verifica se o 'ROLE' do 'Usuário' não é 'Admin' ou 'Supervisor'
    if not user.groups.filter(name__in=['Admin', 'Supervisor']).exists():
        messages.warning(request, 'Você não possui permissão!')
        return redirect(home)    

    equipamento = get_object_or_404(Equipamento, slug=slug)
    equipamento.delete()
    messages.success(request, 'Equipamento deletado com sucesso!')

    return redirect(obter_equipamentos)


@login_required()
def atualizar_equipamento(request: WSGIRequest, slug: str) -> HttpResponse:
    user = request.user

    # O Usuário está autenticado?
    if not user.is_authenticated:
        messages.error(request, 'Você não está logado!')
        return redirect(logar)

    # Verifica se o 'ROLE' do 'Usuário' não é 'Admin' ou 'Supervisor'
    if not user.groups.filter(name__in=['Admin', 'Supervisor']).exists():
        messages.warning(request, 'Você não possui permissão!')
        return redirect(home)

    equipamento: Equipamento = get_object_or_404(Equipamento, slug=slug) 

    if request.method == 'POST':
        permitir_atualicao = True

        # Sobreescreve a 'quantidade_total' e acessa a propriedade 'quantidade_disponivel' para validar
        equipamento.quantidade_total = int(request.POST.get('quantidade_total'))
        quantidade_disponivel = equipamento.quantidade_disponivel

        if quantidade_disponivel < 0:
            permitir_atualicao = False
            messages.info(request, f"O Equipamento não pode ter a quantidade total modificada pois não terá quantidade disponível suficiente!")

        form = EquipamentoForm(request.POST, instance=equipamento)
        if permitir_atualicao and form.is_valid():
            form.save()  
            messages.success(request, 'Equipamento atualizado com sucesso!')
            return redirect(obter_equipamentos)
    else:
        form = EquipamentoForm(instance=equipamento)

    user_groups = request.user.groups.values_list('name', flat=True)
    foto = Usuario.objects.filter(id=request.user.pk).values_list('foto', flat=True).first()

    context = {
        'user_groups': user_groups,
        'form': form,
        'equipamento': equipamento,
        'foto': foto,
        'MEDIA_URL': settings.MEDIA_URL
    }

    return render(request, 'pages/interno/equipamento/atualizar_equipamento.html', context)
