from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
def multiplicadinheiro(request):
    return render(request, 'mult.html')
    
def inserir(request):
    name = request.POST.get('novogasto')
    return HttpResponse(name)  