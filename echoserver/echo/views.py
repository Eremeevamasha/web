from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Book, Cart, Order, OrderItem, CartItem
from .forms import BookForm, RegisterForm, UserProfileForm, PasswordForm


def book_list(request):
    """Главная страница: список книг с пагинацией."""
    books = Book.objects.all()
    paginator = Paginator(books, 5)  # 5 книг на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'book_list.html', {'page_obj': page_obj})


@login_required
def add_book(request):
    """Добавление новой книги (доступно пользователям и администраторам)."""
    if request.user.role in ['admin', 'user']:
        if request.method == 'POST':
            form = BookForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Книга успешно добавлена!")
                return redirect(reverse('book_list'))
        else:
            form = BookForm()
        return render(request, 'add_book.html', {'form': form})
    messages.error(request, "У вас нет прав для добавления книг.")
    return redirect(reverse('book_list'))


@login_required
def edit_book(request, book_id):
    """Редактирование книги (доступно только администраторам)."""
    book = get_object_or_404(Book, id=book_id)
    if request.user.role == 'admin':
        if request.method == 'POST':
            form = BookForm(request.POST, instance=book)
            if form.is_valid():
                form.save()
                messages.success(request, "Книга успешно обновлена!")
                return redirect(reverse('book_list'))
        else:
            form = BookForm(instance=book)
        return render(request, 'edit_book.html', {'form': form, 'book': book})

    messages.error(request, "У вас нет прав для редактирования книг.")
    return redirect(reverse('book_list'))


@login_required
def delete_book(request, book_id):
    """Удаление книги (доступно только администраторам)."""
    book = get_object_or_404(Book, id=book_id)
    if request.user.role == 'admin':
        book.delete()
        messages.success(request, "Книга успешно удалена!")
    else:
        messages.error(request, "У вас нет прав для удаления книг.")

    return redirect(reverse('book_list'))


def register_view(request):
    """Регистрация нового пользователя."""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация успешна! Добро пожаловать!")
            return redirect(reverse('book_list'))
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    """Авторизация пользователя."""
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Вы успешно вошли в систему!")
            return redirect(reverse('book_list'))
        else:
            messages.error(request, "Ошибка авторизации. Проверьте логин и пароль.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


@login_required
def profile_view(request):
    """Личный кабинет пользователя."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Данные обновлены!")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'profile.html', {'form': form})

@login_required
def add_to_cart(request, book_id):
    """Добавление книги в корзину."""
    book = get_object_or_404(Book, pk=book_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')  # Исправлено с 'cart_view' на 'cart'

@login_required
def cart_view(request):
    """Просмотр корзины пользователя."""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()  # исправлено cart.cartitem_set -> cart.items
    total_price = sum(item.book.price * item.quantity for item in cart_items)

    return render(request, 'cart.html', {'cart': cart, 'cart_items': cart_items, 'total_price': total_price})

@login_required
def remove_from_cart(request, item_id):
    """Удаление книги из корзины"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Книга удалена из корзины!")
    return redirect('cart')

@login_required
def checkout(request):
    """Оформление заказа."""
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()  # исправлено cart.cartitem_set -> cart.items

    if cart_items.exists():
        order = Order.objects.create(
            user=request.user,
            total_price=sum(item.book.price * item.quantity for item in cart_items)
        )
        for item in cart_items:
            OrderItem.objects.create(order=order, book=item.book, quantity=item.quantity)

        cart_items.delete()  # Очищаем корзину
        messages.success(request, "Заказ оформлен!")
    else:
        messages.error(request, "Ваша корзина пуста!")

    return redirect('orders')


@login_required
def edit_profile(request):
    """Редактирование профиля пользователя, включая смену пароля."""
    if request.method == 'POST':
        # Обрабатываем форму для изменения профиля
        profile_form = UserProfileForm(request.POST, instance=request.user)
        password_form = PasswordForm(user=request.user, data=request.POST)

        # Сначала пытаемся сохранить форму изменения профиля
        if 'save_profile' in request.POST and profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Профиль успешно обновлен!")
            return redirect(
                'edit_profile')  # После успешного сохранения перенаправляем на страницу редактирования профиля

        # Затем пытаемся сохранить форму изменения пароля
        elif 'change_password' in request.POST and password_form.is_valid():
            user = password_form.save()  # Сохраняем новый пароль
            update_session_auth_hash(request, user)  # Обновляем сессию, чтобы не разлогинило
            messages.success(request, "Пароль успешно изменен!")
            return redirect('edit_profile')  # Перенаправляем обратно

        # Если обе формы невалидны, выводим ошибку
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")

    else:
        profile_form = UserProfileForm(instance=request.user)
        password_form = PasswordForm(user=request.user)

    return render(request, 'edit_profile.html', {'profile_form': profile_form, 'password_form': password_form})

@login_required
def orders_view(request):
    """Просмотр всех заказов пользователя."""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders.html', {'orders': orders})

def logout_view(request):
    """Выход из системы."""
    logout(request)
    messages.success(request, "Вы успешно вышли из системы.")
    return redirect(reverse('book_list'))
