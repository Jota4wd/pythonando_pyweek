from django.shortcuts import render, redirect
from medico.models import DadosMedico, Especialidades, DatasAbertas, is_medico
from datetime import datetime
from .models import Consulta, Documento
from django.contrib import messages
from django.contrib.messages import constants
from django.db import transaction
# Create your views here.
def home(request):
    if request.method == "GET":
        medico_filtrar = request.GET.get('medico')
        especialidades_filtrar = request.GET.getlist('especialidades')
        medicos = DadosMedico.objects.all()

        if medico_filtrar:
            medicos = medicos.filter(nome__icontains = medico_filtrar)

        if especialidades_filtrar:
            medicos = medicos.filter(especialidade_id__in=especialidades_filtrar)
            medicos = DadosMedico.objects.all()

        especialidades = Especialidades.objects.all()
        return render(request, 'home.html', {'medicos': medicos, 'especialidades': especialidades, 'is_medico': is_medico(request.user)})

def escolher_horario(request, id_dados_medicos):
    if request.method == "GET":
        medico = DadosMedico.objects.get(id=id_dados_medicos)
        datas_abertas = DatasAbertas.objects.filter(user=medico.user).filter(data__gte=datetime.now()).filter(agendado=False)
        return render(request, 'escolher_horario.html', {'medico': medico, 'datas_abertas': datas_abertas, 'is_medico': is_medico(request.user)})

   
def agendar_horario(request, id_data_aberta):
    with transaction.Atomic():
        if request.method == "GET":
            data_aberta = DatasAbertas.objects.get(id=id_data_aberta)

            horario_agendado = Consulta(
                paciente=request.user,
                data_aberta=data_aberta
                )
            
            horario_agendado.save()
            
            data_aberta.agendado = True
            data_aberta.save()

            messages.add_message(request, constants.SUCCESS, 'Horário agendado com sucesso.')

            return redirect('/pacientes/minhas_consultas/')

       
def minhas_consultas(request):
    if request.method == "GET":
        
        #TODO: desenvolver filtros 
        #descobrir origem dos objetos e filtralos
        #mesmo q o projeto esteja bugado desde o app usuarios
        #e a cada novo cofigo bugue um pouco mais
        #se vire e continue debugando
        #mesmo pq vc ja entendeu q filtrar nada mais eh q criar as variaveis
        #a serem renderizadas, basta descobrir quais ele quer mesmo que no render 
        #soh exita o consulta e is_medico e elas ja estao filtradas
        #medico_filtrar = request.GET.get('medico')
        #

        minhas_consultas = Consulta.objects.filter(paciente=request.user).filter(data_aberta__data__gte=datetime.now())
        return render(request, 'minhas_consultas.html', {'minhas_consultas': minhas_consultas, 'is_medico': is_medico(request.user)})
    

def consulta(request, id_consulta):
    if request.method == 'GET':
        consulta = Consulta.objects.get(id=id_consulta)
        dado_medico = DadosMedico.objects.get(user=consulta.data_aberta.user)
        documentos = Documento.objects.filter(consulta=consulta)
        return render(request, 'consulta.html', {'consulta': consulta, 'dado_medico': dado_medico, 'is_medico': is_medico(request.user), 'documentos': documentos})

def cancelar_consulta(request, id_consulta):
    
    consulta = Consulta.objects.get(id=id_consulta)

    if request.user != consulta.data_aberta.user:
        messages.add_message(request, constants.ERROR, 'Essa consulta nao eh sua.')
        return redirect(f'/paciente/home/')

    consulta.status = 'C'
    consulta.save()
    return redirect(f'/paciente/consulta/{id_consulta}')