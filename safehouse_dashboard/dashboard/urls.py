from django.urls import path


from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('login/submit_login/', views.submit_login, name='submit_login'),
    path('register/', views.register_view, name='register'),
    path('register/confirm/', views.confirm_register, name='confirm_register'),
    path('<int:user_id>/confirm/<str:token>', views.confirm_email, name='confirm_email'),
    path('logout/', views.logout_view, name='logout_view'),
    path('error/', views.error_view, name='error_view'),
    path('update/', views.update_sensors_and_valves, name='update_sensors_and_valves'),
    path('test/', views.create_valve, name='create_valve'),
    path('test/confirm', views.create_valve_confirm, name='create_valve_confirm'),

]
