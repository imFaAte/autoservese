from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings

from .models import (Car, ServiceCategory, Service, Mechanic, ServiceOrder, OrderService, Review)

def index(request):
    categories = ServiceCategory.objects.all()
    services = Service.objects.all().order_by('-created_at')[:8]
    mechanics = Mechanic.objects.filter(is_active=True)[:4]

    context = {
        'categories': categories,
        'services': services,
        'mechanics': mechanics,
    }

    return render(request, 'index.html', context)

def service_list(request):
    services = Service.objects.all()

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_by = request.GET.get('sort')

    if min_price:
        try:
            min_price = int(min_price)
            services = services.filter(price__gte=min_price)
        except ValueError:
            pass

    if max_price:
        try:
            max_price = int(max_price)
            services = services.filter(price__lte=max_price)
        except ValueError:
            pass

    if sort_by == 'price_asc':
        services = services.order_by('price')
    elif sort_by == 'price_desc':
        services = services.order_by('-price')
    else:
        services = services.order_by('-created_at')

    paginator = Paginator(services, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'services/service_list.html', {'services': page_obj})

def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug)
    return render(request, 'services/service_detail.html', {'service': service})

def car_list(request):
    cars = Car.objects.all().order_by('-created_at')
    paginator = Paginator(cars, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'cars/car_list.html', {'cars': page_obj})

def car_detail(request, pk):
    car = get_object_or_404(Car, pk=pk)
    return render(request, 'cars/car_detail.html', {'car': car})

def mechanic_list(request):
    mechanics = Mechanic.objects.filter(is_active=True)
    paginator = Paginator(mechanics, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'mechanics/mechanic_list.html', {'mechanics': page_obj})

def mechanic_detail(request, pk):
    mechanic = get_object_or_404(Mechanic, pk=pk)
    reviews = Review.objects.filter(mechanic=mechanic).order_by('-created_at')
    context = {
        'mechanic': mechanic,
        'reviews': reviews,
    }
    return render(request, 'mechanics/mechanic_detail.html', context)

def order_list(request):
    # Показываем только заказы текущего пользователя
    if request.user.is_authenticated:
        orders = ServiceOrder.objects.filter(client=request.user).order_by('-created_at')
    else:
        orders = ServiceOrder.objects.none()

    return render(request, 'orders/order_list.html', {'orders': orders})

def order_detail(request, order_id):
    order = get_object_or_404(ServiceOrder, id=order_id)

    # Проверяем, что пользователь имеет доступ к заказу
    if request.user.is_authenticated and order.client == request.user:
        order_items = OrderService.objects.filter(order=order)
        context = {
            'order': order,
            'order_items': order_items,
        }
        return render(request, 'orders/order_detail.html', context)
    else:
        messages.error(request, 'У вас нет доступа к этому заказу')
        return redirect('order_list')

def service_cart(request):
    """Корзина с услугами"""
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for service_id, quantity in cart.items():
        try:
            service = Service.objects.get(id=service_id)
            subtotal = service.price * quantity
            total_price += subtotal
            cart_items.append({
                'service': service,
                'quantity': quantity,
                'subtotal': subtotal,
            })
        except Service.DoesNotExist:
            # Удаляем несуществующую услугу из корзины
            del cart[service_id]
            request.session['cart'] = cart
            continue

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'cart/cart_detail.html', context)

def add_to_cart(request, service_id):
    cart = request.session.get('cart', {})
    cart[str(service_id)] = cart.get(str(service_id), 0) + 1
    request.session['cart'] = cart
    messages.success(request, 'Услуга добавлена в корзину')

    next_url = request.META.get('HTTP_REFERER', '/')
    return redirect(next_url)

def remove_from_cart(request, service_id):
    cart = request.session.get('cart', {})
    if str(service_id) in cart:
        del cart[str(service_id)]
    request.session['cart'] = cart
    messages.info(request, 'Услуга удалена из корзины')
    return redirect('service_cart')

def update_cart_quantity(request, service_id):
    """Обновление количества услуги в корзине"""
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        cart = request.session.get('cart', {})

        try:
            quantity = int(quantity)
            if quantity > 0:
                cart[str(service_id)] = quantity
            else:
                if str(service_id) in cart:
                    del cart[str(service_id)]
        except (ValueError, TypeError):
            pass

        request.session['cart'] = cart
        messages.success(request, 'Корзина обновлена')

    return redirect('service_cart')

def review_list(request):
    reviews = Review.objects.all().order_by('-created_at')
    return render(request, 'reviews/review_list.html', {'reviews': reviews})

def contacts(request):
    return render(request, 'components/contacts.html')

@login_required
def create_order(request):
    cart = request.session.get('cart', {})

    if not cart:
        messages.warning(request, 'Корзина пуста')
        return redirect('service_list')

    # Проверяем, есть ли у пользователя автомобили
    cars = Car.objects.filter(owner=request.user)
    if not cars.exists():
        messages.warning(request, 'Сначала добавьте автомобиль в личном кабинете администратора')
        return redirect('car_list')

    if request.method == 'POST':
        car_id = request.POST.get('car')
        mechanic_id = request.POST.get('mechanic')
        appointment_date = request.POST.get('appointment_date')
        comment = request.POST.get('comment', '')

        if not car_id or not appointment_date:
            messages.error(request, 'Заполните все обязательные поля')
            return redirect('create_order')

        car = get_object_or_404(Car, id=car_id, owner=request.user)
        mechanic = get_object_or_404(Mechanic, id=mechanic_id) if mechanic_id else None

        order = ServiceOrder.objects.create(
            client=request.user,
            car=car,
            mechanic=mechanic,
            appointment_date=appointment_date,
            comment=comment,
            total_price=0
        )

        total = 0
        for service_id, quantity in cart.items():
            try:
                service = Service.objects.get(id=service_id)
                OrderService.objects.create(order=order, service=service, quantity=quantity)
                total += service.price * quantity
            except Service.DoesNotExist:
                continue

        order.total_price = total
        order.save()

        request.session['cart'] = {}
        messages.success(request, f'Заказ #{order.id} успешно создан!')
        return redirect('order_detail', order_id=order.id)

    mechanics = Mechanic.objects.filter(is_active=True)
    cart_items = []
    total_price = 0

    for service_id, quantity in cart.items():
        try:
            service = Service.objects.get(id=service_id)
            subtotal = service.price * quantity
            total_price += subtotal
            cart_items.append({
                'service': service,
                'quantity': quantity,
                'subtotal': subtotal
            })
        except Service.DoesNotExist:
            continue

    context = {
        'cars': cars,
        'mechanics': mechanics,
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'orders/create_order.html', context)

def send_feedback(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        try:
            send_mail(
                f'Обратная связь: {subject}',
                f'От: {name} ({email})\n\nСообщение:\n{message}',
                settings.DEFAULT_FROM_EMAIL,
                ['info@avtomaster.ru'],
                fail_silently=False,
            )
            messages.success(request, 'Ваше сообщение отправлено! Мы свяжемся с вами.')
        except:
            messages.error(request, 'Ошибка при отправке. Попробуйте позже.')

        return redirect('contacts')