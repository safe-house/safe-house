from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard_view'),

    path('login/', views.login_view, name='login'),
    path('login/submit_login/', views.dashboard_login, name='dashboard_login'),
    path('logout/', views.logout_view, name='logout_view'),

    path('register/', views.register_view, name='register'),
    path('register/confirm/', views.confirm_register, name='confirm_register'),
    path('<int:user_id>/confirm/<str:token>', views.confirm_email, name='confirm_email'),

    path('users', views.users_view, name='users_view'),
    path('users/users_access_enable', views.enable_user_invitation, name='enable_user_invitation'),
    path('users/users_access_disable', views.disable_user_invitation, name='disable_user_invitation'),
    path('users/user_invitation_mail', views.invite_user_to_house, name='invite_user_to_house'),

    path('error/', views.error_view, name='error_view'),
    path('update/', views.update_dashboard, name='update_dashboard'),

    path('valves/', views.valves_view, name='valves_view'),
    path('valves/new', views.create_new_valve, name='create_new_valve'),
    path('valves/delete', views.delete_valve, name='delete_valve'),
    # path('valves/instruction', views.valves_instruction_view, name='valves_instruction_view'),

    path('telegram_notification/', views.telegram_notifications_view, name='telegram_notifications_view'),
    path('telegram_notification/new', views.telegram_new_user, name='telegram_new_user'),
    path('telegram_notification/delete', views.telegram_delete_user, name='telegram_delete_user'),

    path('api/update/<str:token>', views.api_update, name='api_update'),

]
