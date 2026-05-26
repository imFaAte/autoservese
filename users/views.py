from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, CarForm
from serves.models import Car

def register(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('index')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = RegistrationForm()

    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'С возвращением, {user.username}!')
            next_url = request.GET.get('next', 'index')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')

    return render(request, 'users/login.html')

def user_logout(request):
    logout(request)
    messages.info(request, 'Вы вышли из аккаунта')
    return redirect('index')

@login_required
def profile(request):
    cars = Car.objects.filter(owner=request.user)

    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save(commit=False)
            car.owner = request.user
            car.save()
            messages.success(request, 'Автомобиль добавлен!')
            return redirect('profile')
    else:
        form = CarForm()

    context = {
        'cars': cars,
        'form': form,
    }
    return render(request, 'users/profile.html', context)

@login_required
def delete_car(request, car_id):
    car = Car.objects.get(id=car_id, owner=request.user)
    car.delete()
    messages.success(request, 'Автомобиль удален')
    return redirect('profile')