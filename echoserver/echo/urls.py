from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),  # Главная страница со списком книг
    path('book/add/', views.add_book, name='add_book'),  # Добавление книги
    path('book/edit/<int:book_id>/', views.edit_book, name='edit_book'),  # Редактирование книги
    path('book/delete/<int:book_id>/', views.delete_book, name='delete_book'),  # Удаление книги
    path('register/', views.register_view, name='register'),  # Регистрация
    path('login/', views.login_view, name='login'),  # Вход
    path('logout/', views.logout_view, name='logout'),  # Выход
]
