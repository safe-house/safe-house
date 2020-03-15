
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('dashboard/', include('dashboard.urls')),
    path('', include('landing.urls')),
    path('admin/', admin.site.urls),
]
