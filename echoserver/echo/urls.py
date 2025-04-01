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

    # Новые маршруты
    path('profile/', views.profile_view, name='profile'),  # Личный кабинет
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('cart/', views.cart_view, name='cart'),  # Просмотр корзины
    path('cart/add/<int:book_id>/', views.add_to_cart, name='add_to_cart'),  # Добавление в корзину
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),  # Оформление заказа
    path('orders/', views.orders_view, name='orders'),  # Просмотр заказов
]
