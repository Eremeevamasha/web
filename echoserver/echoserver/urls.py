from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Панель администратора Django
    path('', include('echo.urls')),  # Подключаем маршруты из приложения echo
]
