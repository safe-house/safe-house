from django.urls import path


from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard_view'),
    path('login/', views.login_view, name='login'),
    path('login/submit_login/', views.dashboard_login, name='dashboard_login'),
    path('register/', views.register_view, name='register'),
    path('register/confirm/', views.confirm_register, name='confirm_register'),
    path('<int:user_id>/confirm/<str:token>', views.confirm_email, name='confirm_email'),
    path('logout/', views.logout_view, name='logout_view'),
    path('error/', views.error_view, name='error_view'),
    path('update/', views.update_sensors_and_valves, name='update_sensors_and_valves'),
    path('new-valve/', views.create_valve, name='create_valve'),
    path('new-valve/confirm', views.create_valve_confirm, name='create_valve_confirm'),
    path('telegram-bot/', views.add_user_to_telegram_bot, name='add_user_to_telegram_bot'),
    path('telegram-bot/new', views.confirm_telegram, name='confirm_telegram'),

]
