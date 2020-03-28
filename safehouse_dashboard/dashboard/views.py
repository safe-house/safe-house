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
    if request.method == 'POST':
        return render(request, 'dashboard/register_confirmation.html')


def error_view(request):
    return render(request, 'dashboard/error.html')


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('/dashboard/login/')
    else:
        return redirect('/dashboard/error/')


def dashboard_login(request):
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


def update_sensors_and_valves(request):
    if request.is_ajax() and request.user.is_authenticated:
        house_id = sql.get_default_house(request.user.id)
        response = {"valves": sql.get_house_valves_update(house_id),
                    "sensors": sql.get_house_sensors_update(house_id)}
        return JsonResponse(response)
    else:
        raise Http404


def create_valve_confirm(request):
    if request.user.is_authenticated and request.method == 'POST':
        try:
            name = request.POST['name']
            location = request.POST['location']
            token = secrets.token_urlsafe(4)
            locations_dict = {"Kitchen": 1, "Bathroom": 2, "Living room": 3, "Dining room": 4,
                              "Bedroom": 5, "Utility room": 6, "Other": 7}
            sql.create_valve(locations_dict[location], name, sql.get_default_house(request.user.id), 1, token)
            return HttpResponse(token)
        except Exception as ex:
            return redirect('/dashboard/', exception=ex)


def create_valve(request):
    return render(request, "dashboard/create_valve.html", {"locations": sql.get_locations()})


def add_user_to_telegram_bot(request):
    house_id = sql.get_default_house(request.user.id)
    return render(request, "dashboard/telegram_bot_add.html",
                  {"users": sql.get_house_users(house_id),
                   "telegram": sql.get_telegram_users(house_id)})


def confirm_telegram(request):
    if request.user.is_authenticated and request.method == 'POST':
        try:
            user_name = request.POST['username']
            nickname = request.POST.get('user')
            result = sql.add_telegram_bot(user_name, sql.get_default_house(request.user.id), nickname)
            return redirect('/dashboard/telegram-bot/')
        except Exception as ex:
            return redirect('/dashboard/telegram-bot/', exception=ex)
