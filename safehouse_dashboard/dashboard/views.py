from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.core.mail import send_mail


@login_required(login_url='/dashboard/login/')
def dashboard_view(request):
    return render(request, 'dashboard/index.html')


def login_view(request):
    if request.user.is_authenticated:
        return HttpResponse("You are already logged in")
    else:
        return render(request, 'dashboard/login.html')


def register_view(request):
    return render(request, 'dashboard/register.html')


def register_confirmation_view(request):
    return render(request, 'dashboard/register_confirmation.html')


def error_view(request):
    return render(request, 'dashboard/error.html')


@login_required(login_url='/dashboard/login/')
def logout_view(request):
    logout(request)
    return redirect('/dashboard/login/')


def submit_login(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['email'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect('/dashboard/')
        else:
            return redirect('/dashboard/login/')


def confirm_register(request):
    if request.method == 'POST':
        try:
            user = User.objects.create_user(
                username=request.POST['email'],
                email=request.POST['email'],
                password=request.POST['password'],
                first_name=request.POST['name'],
                last_name=request.POST['surname'],
                is_active=1,
            )
            user.save()
            send_email(user.email)

            return render(request, 'dashboard/register_confirmation.html')
        except Exception as ex:
            return redirect('/dashboard/register/', exception=ex)
    else:
        return redirect('/dashboard/error/')


def confirm_email(request):
    pass


def send_email(email):
    send_mail('Auto-email',
              'Hello, this is automatic email',
              'danylo.shyshla.knm.2018@lpnu.ua',
              [email],
              fail_silently=False)
    return None
