import secrets

from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render
from django.contrib.auth import logout, authenticate, login
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.core.mail import send_mail

from dashboard.lib import sql

DOMAIN_NAME = "127.0.0.1:8000/"





def login_view(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    else:
        return render(request, 'dashboard/login.html')


def register_view(request):
    return render(request, 'dashboard/register.html')


def register_confirmation_view(request):
    return render(request, 'dashboard/register_confirmation.html')


def error_view(request):
    return render(request, 'dashboard/error.html')


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('/dashboard/login/')
    else:
        return redirect('/dashboard/error/')


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
                is_active=0,
            )
            user.save()
            house = sql.create_house()
            sql.create_user_has_house(user.id, house)
            sql.set_default_house(user.id, house)
            token = secrets.token_urlsafe(32)
            sql.save_token(user.id, token)
            send_email(user.email, DOMAIN_NAME + "dashboard/" + str(user.id) + "/confirm/" + token)
            return render(request, 'dashboard/register_confirmation.html')
        except Exception as ex:
            return redirect('/dashboard/register/', exception=ex)
    else:
        return redirect('/dashboard/error/')


def confirm_email(request, user_id, token):
    authentication = sql.check_token(user_id, token)
    if authentication:
        sql.activate_user(user_id)
        return redirect('/dashboard/login')
    else:
        return redirect('/dashboard/error/')


def send_email(email, message):
    send_mail('Auto-email',
              message,
              'mail.safehouse@gmail.com',
              [email],
              fail_silently=False)
    return None


def dashboard_view(request):
    if request.user.is_authenticated:
        house_id = sql.get_default_house(request.user.id)
        return render(request, 'dashboard/index.html',
                      {'valves_list': sql.get_house_valves(house_id),
                       'sensors_list': sql.get_house_sensors(house_id),
                       'locations_list': ("", "Kitchen", "Bathroom", "Living room", "Dining room",
                                          "Bedroom", "Utility room", "Other")})
    else:
        return redirect('/dashboard/login/')


# def get_senors_and_valves(request):
#     if request.user.is_authenticated:
#         house_id = sql.get_default_house(request.user.id)
#         return render(request, 'dashboard/index.html',
#                       {'valves_list': sql.get_house_valves(house_id),
#                        'sensors_list': sql.get_house_sensors(house_id),
#                        'locations_list': ("", "Kitchen", "Bathroom", "Living room", "Dining room",
#                                           "Bedroom", "Utility room", "Other")})
#     else:
#         return redirect('/dashboard/login/')


def update_sensors_and_valves(request):
    if request.is_ajax() and request.user.is_authenticated:
        house_id = sql.get_default_house(request.user.id)
        response = {"valves": sql.get_house_valves_update(house_id),
                    "sensors": sql.get_house_sensors_update(house_id)}
        return JsonResponse(response)
    else:
        raise Http404
