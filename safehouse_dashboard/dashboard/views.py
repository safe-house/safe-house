from django.shortcuts import render
from django.http import HttpResponse
from dashboard.lib import sql


def dashboard(request):
    return HttpResponse("Hello, world. You're at the dashboard safehouse page.")


def login(request):
    return render(request, 'dashboard/login.html')


def submit_login(request):
    result = sql.login(request.POST['email'], request.POST['password'])
    if result:
        return HttpResponse(result)
    else:
        return render(request, 'dashboard/login.html')


def register(request):
    sql.create_user(request)
    return render(request, 'dashboard/login.html')
