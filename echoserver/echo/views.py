from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Book
from .forms import BookForm, RegisterForm


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


def logout_view(request):
    """Выход из системы."""
    logout(request)
    messages.success(request, "Вы успешно вышли из системы.")
    return redirect(reverse('book_list'))
