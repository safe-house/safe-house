from django.urls import path, re_path

from .views import IndexView, SendEmailView

urlpatterns = [
    path('', IndexView.as_view()),
    re_path(r'^email-users/$', SendEmailView.as_view(), name='email')
]
