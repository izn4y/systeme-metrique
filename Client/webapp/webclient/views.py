from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    data = {'nom':'albert'}
    return render(request, 'webclient/index.html', data)
