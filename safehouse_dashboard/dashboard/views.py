import secrets
import json

from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render
from django.contrib.auth import logout, authenticate, login
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt

from dashboard.lib import sql, telegram, messenger

DOMAIN_NAME = "127.0.0.1:8000/"


# ----------------------------------------------------------------------
# page rendering functions
# ----------------------------------------------------------------------

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


def profile_view(request):
    if request.user.is_authenticated:
        return render(request, 'dashboard/profile.html',
                      {'user': request.user.first_name + " " + request.user.last_name,
                       'user_info': [request.user.first_name, request.user.last_name]})
    else:
        return render(request, 'dashboard/login.html')


def error_view(request):
    return render(request, 'dashboard/error.html')


# ----------------------------------------------------------------------
# user creation, login, logout related functions
# ----------------------------------------------------------------------


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
        # else:
        #     return redirect('/dashboard/login/')


def confirm_register(request):
    if request.method == 'POST':
        # try:

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
        sql.create_user_has_house(user.id, house, 1)
        sql.set_default_house(user.id, house)
        token = secrets.token_urlsafe(32)
        sql.save_token(user.id, token)
        send_email(user.email, DOMAIN_NAME + "dashboard/" + str(user.id) + "/confirm/" + token)
        return render(request, 'dashboard/register_confirmation.html')
        # except Exception as ex:
        #     return redirect('/dashboard/register/', exception=ex)
    else:
        return redirect('/dashboard/error/')


def confirm_email(request, user_id, token):
    authentication = sql.check_token(user_id, token)
    if authentication:
        sql.activate_user(user_id)
        return redirect('/dashboard/login')
    else:
        return redirect('/dashboard/error/')


def users_view(request):
    if request.user.is_authenticated:
        house_id = sql.get_default_house(request.user.id)[0]
        token = sql.get_invitation_token(house_id)
        user_id = request.user.id
        if token:
            url = DOMAIN_NAME + "dashboard/users/" + str(house_id) + "/add/" + token[0]
            print(url)
        else:
            url = None
        return render(request, 'dashboard/users.html',
                      {'token': url,
                       'user': request.user.first_name + " " + request.user.last_name,
                       'users': sql.get_house_users(house_id),
                       'number': 0,
                       'preferences': sql.check_user_preferences(user_id)
                       })
    else:
        return render(request, 'dashboard/index.html')


def enable_user_invitation(request):
    if request.user.is_authenticated and request.is_ajax():
        token = secrets.token_urlsafe(32)
        house_id = sql.get_default_house(request.user.id)[0]
        sql.create_user_invitation_token(house_id, token)
        url = DOMAIN_NAME + "dashboard/users/" + str(house_id) + "/add/" + token
        response = {"token": url}
        return JsonResponse(response)
    else:
        raise Http404


def disable_user_invitation(request):
    if request.user.is_authenticated and request.is_ajax():
        house_id = sql.get_default_house(request.user.id)
        sql.delete_user_invitation_token(house_id)
        response = {"token": 0}
        return JsonResponse(response)
    else:
        raise Http404


def invite_user_to_house(request):
    if request.user.is_authenticated and request.method == 'POST':
        token = secrets.token_urlsafe(32)
        password = secrets.token_urlsafe(8)
        house_id = sql.get_default_house(request.user.id)[0]
        user = User.objects.create_user(
            username=request.POST['email'],
            email=request.POST['email'],
            password=password,
            first_name="Name",
            last_name="Surname",
            is_active=0,
        )
        user.save()
        is_admin = request.POST.get('admin', "false")
        print(is_admin)
        if is_admin == "on":
            is_admin = 1
        else:
            is_admin = 0
        sql.create_user_has_house(user.id, house_id, is_admin)
        sql.set_default_house(user.id, house_id)
        sql.save_token(user.id, token)
        text = 'Hello there,\n You were added to the house! Please click the link to continue registration \n' + DOMAIN_NAME + "dashboard/" + str(
            user.id) + "/confirm/" + token + '\nYour login is your current email and password is:  ' + password
        send_email(user.email, text)
        return redirect('/dashboard/users')


def send_email(email, message):
    send_mail('Auto-email',
              message,
              'mail.safehouse@gmail.com',
              [email],
              fail_silently=False)
    return None


# ----------------------------------------------------------------------
# Dashboard related functions
# ----------------------------------------------------------------------


def dashboard_view(request):
    if request.user.is_authenticated:
        house_id = sql.get_default_house(request.user.id)
        user_id = request.user.id
        return render(request, 'dashboard/index.html',
                      {'valves_list': sql.get_house_valves(house_id),
                       'sensors_list': sql.get_house_sensors(house_id),
                       'locations_list': ("", "Kitchen", "Bathroom", "Living room", "Dining room",
                                          "Bedroom", "Utility room", "Other"),
                       'user': request.user.first_name + " " + request.user.last_name,
                       'preferences': sql.check_user_preferences(user_id)
                       })
    else:
        return redirect('/dashboard/login/')


def update_dashboard(request):
    if request.is_ajax() and request.user.is_authenticated:
        house_id = sql.get_default_house(request.user.id)
        response = {"valves": sql.get_house_valves_update(house_id),
                    "sensors": sql.get_house_sensors(house_id)}
        return JsonResponse(response)
    else:
        raise Http404


# ----------------------------------------------------------------------
# Valves related functions
# ----------------------------------------------------------------------


def valves_view(request):
    if request.user.is_authenticated:
        house_id = sql.get_default_house(request.user.id)
        user_id = request.user.id
        return render(request, "dashboard/valve.html",
                      {"locations": sql.get_locations(),
                       "valves": sql.get_house_valves_all(house_id),
                       'user': request.user.first_name + " " + request.user.last_name,
                       'preferences': sql.check_user_preferences(user_id)})


def create_new_valve(request):
    if request.user.is_authenticated and request.method == 'POST':
        try:
            name = request.POST['name']
            location = request.POST['location']
            token = secrets.token_urlsafe(4)
            locations_dict = {"Kitchen": 1, "Bathroom": 2, "Living room": 3, "Dining room": 4,
                              "Bedroom": 5, "Utility room": 6, "Other": 7}
            sql.create_valve(locations_dict[location], name, sql.get_default_house(request.user.id), 1, token)
            return render(request, "dashboard/valve_instruction.html", {"token": token})
        except Exception as ex:
            return redirect('/dashboard/', exception=ex)


def delete_valve(request):
    if request.user.is_authenticated and request.method == 'POST':
        try:
            valve_id = request.POST['id']
            sql.delete_valve(valve_id)
            return redirect('/dashboard/valves')
        except Exception as ex:
            return redirect('/dashboard/valves', exception=ex)


# ----------------------------------------------------------------------
# Telegram bot related functions
# ----------------------------------------------------------------------


def telegram_notifications_view(request):
    if request.user.is_authenticated:
        house_id = sql.get_default_house(request.user.id)
        user_id = request.user.id
        return render(request, "dashboard/telegram_notification.html",
                      {"users": sql.get_house_users(house_id),
                       "telegram": sql.get_telegram_users(house_id),
                       "messenger": sql.get_messenger_users_by_house(house_id),
                       "user": request.user.first_name + " " + request.user.last_name,
                       'preferences': sql.check_user_preferences(user_id)})


def telegram_new_user(request):
    if request.user.is_authenticated and request.method == 'POST':
        try:
            user_name = request.POST['username']
            nickname = request.POST.get('user')
            if user_name[0] == "@":
                print(user_name)
                user_name = user_name[1:]
            sql.create_telegram(user_name, sql.get_default_house(request.user.id), nickname)
            return redirect('/dashboard/telegram_notification/')
        except Exception as ex:
            return redirect('/dashboard/telegram_notification/', exception=ex)


def telegram_delete_user(request):
    if request.user.is_authenticated and request.method == 'POST':
        try:
            username = request.POST['username']
            house_id = sql.get_default_house(request.user.id)
            sql.delete_telegram(username, house_id)
            return redirect('/dashboard/telegram_notification/')
        except Exception as ex:
            return redirect('/dashboard/telegram_notification/', exception=ex)


# ----------------------------------------------------------------------
# API related functions
# ----------------------------------------------------------------------
# POST data example:
#  {
#     "valve": "zk12G8",
#     "closed": 1,
#     "type": 2,
#     "new_request": 0,
#     "leakage": 0,
#     "sensors": [{
#     	"sensor": "2k4523",
#     	"value": "1111",
#     	"last_updated": "2020-03-21 18:41:01",
#     	"battery": 10,
#     	"value_exceeded": "",
#     	"time_exceeded": ""
#     }, {
#     	"sensor": "k4H769",
#     	"value": "111",
#     	"last_updated": "2020-03-31 18:41:01",
#     	"battery": 10,
#     	"value_exceeded": "",
#     	"time_exceeded": ""
#     },
#     {
#     	"sensor": "111123",
#     	"value": "71",
#     	"last_updated": "2020-03-21 16:41:17",
#     	"battery": 10,
#     	"value_exceeded": "",
#     	"time_exceeded": ""
#     }]
# }


@csrf_exempt
def api_update(request, token):
    if request.method == 'POST':
        # try:
        json_data = json.loads(request.body)
        if json_data['new_request']:
            names = ["Gas sensor", "Water sensor"]
            sensor_type = json_data['type']
            sensor_names = names[sensor_type - 1]
            valve = sql.activate_valve(token)
            for sensor in json_data['sensors']:
                print(sensor['last_updated'], sensor['value'])
                sql.create_sensor(sensor_names, valve[1], sensor_type, valve[0], sensor['sensor'],
                                  sensor['last_updated'], sensor['value'])
        else:
            if json_data['leakage']:
                chats = sql.get_chat_id(token)
                for chat_id in chats:
                    telegram.send_message("Leakage!", chat_id)
            sql.update_valve(token, json_data['closed'])
            for sensor in json_data['sensors']:
                sql.update_sensor(sensor['last_updated'], sensor['value'], sensor['sensor'])
        # except Exception as ex:
        return HttpResponse("true")


def edit_user(request):
    if request.user.is_authenticated and request.method == 'POST':
        # try:
        name = request.POST['FirstName']
        surname = request.POST['LastName']
        password1 = request.POST['newPassword1']
        password2 = request.POST['newPassword2']
        user = request.user
        if password1 == password2 and len(password1) > 0:
            user.set_password(password1)
        user.save()
        sql.update_user(name, surname, request.user.id)
        return redirect('/dashboard/')

        # except Exception as ex:
        #     return redirect('/dashboard/', exception=ex)


def delete_user(request):
    if request.user.is_authenticated and request.method == 'POST':
        # try:
        user_id = request.POST['id']
        house_id = sql.get_default_house(request.user.id)
        sql.delete_user(user_id, house_id)
        user = User.objects.get(id=user_id)
        user.delete()
        return redirect('/dashboard/users')
    # except Exception as ex:
    #     return redirect('/dashboard/telegram_notification/', exception=ex)


def messenger_new_user(request):
    pass
    if request.user.is_authenticated and request.method == 'POST':
        try:
            url = request.POST['facebook_url']
            user = request.POST.get('user')
            facebook_id = messenger.get_facebook_id(url)
            house_id = sql.get_default_house(request.user.id)
            sql.create_messenger_user(user, facebook_id, house_id)
            msg = "Hello test message!"
            messenger.send_message(msg, facebook_id)
            return redirect('/dashboard/telegram_notification/')
        except Exception as ex:
            return redirect('/dashboard/telegram_notification/', exception=ex)


def messenger_delete_user(request):
    pass
    if request.user.is_authenticated and request.method == 'POST':
        try:
            username = request.POST['username']
            house_id = sql.get_default_house(request.user.id)
            sql.delete_messenger_user(username)
            return redirect('/dashboard/telegram_notification/')
        except Exception as ex:
            return redirect('/dashboard/telegram_notification/', exception=ex)
