from django.shortcuts import render

from django.http import HttpResponse


def dashboard(request):
    return HttpResponse("Hello, world. You're at the dashboard safehouse page.")


def login(request):
    return render(request, 'dashboard/login.html')


def register(request):
    return render(request, 'landing/index.html')
