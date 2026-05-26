from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=200,verbose_name='Название категории',help_text='Максимум 200 символов')
    slug = models.SlugField(max_length=200,unique=True,verbose_name='URL-адрес',help_text='URL-friendly название (латинские буквы, цифры, дефисы)')
    description = models.TextField(blank=True,null=True,verbose_name='Описание',help_text='Необязательное описание категории')
    is_active = models.BooleanField(default=True,verbose_name='Активна',help_text='Отображается ли категория на сайте')
    created_at = models.DateTimeField(auto_now_add=True,verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True,)
    icon_image = models.ImageField(
        upload_to='category_icons/',
        blank=True,
        null=True,
        verbose_name='Иконка (изображение)',
        help_text='Загрузите свою иконку (рекомендуемый размер: 64x64 пикселей)'
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"

    def __str__(self):
        return self.name

class CarBrand(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Марка автомобиля'
    )

    class Meta:
        verbose_name = 'марка автомобиля'
        verbose_name_plural = 'марки автомобилей'

    def __str__(self):
        return self.name


class Car(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cars',
        verbose_name='Владелец'
    )

    brand = models.ForeignKey(
        CarBrand,
        on_delete=models.CASCADE,
        related_name='cars',
        verbose_name='Марка'
    )

    model = models.CharField(
        max_length=100,
        verbose_name='Модель'
    )

    year = models.PositiveIntegerField(
        verbose_name='Год выпуска'
    )

    plate_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Гос номер'
    )

    image = models.ImageField(
        upload_to='car_images/',
        blank=True,
        null=True,
        verbose_name='Фото автомобиля'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'автомобиль'
        verbose_name_plural = 'автомобили'

    def __str__(self):
        return f"{self.brand} {self.model}"

class ServiceCategory(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Категория услуги'
    )

    class Meta:
        verbose_name = 'категория услуги'
        verbose_name_plural = 'категории услуг'

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(
        max_length=150,
        verbose_name='Название услуги'
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    description = models.TextField(
        verbose_name='Описание услуги'
    )

    price = models.IntegerField(
        verbose_name='Цена'
    )

    duration = models.PositiveIntegerField(
        verbose_name='Длительность (минуты)'
    )

    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.CASCADE,
        related_name='services'
    )

    image = models.ImageField(
        upload_to='service_images/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'услуга'
        verbose_name_plural = 'услуги'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.name.lower().replace(' ', '-')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.price}₽"

class Mechanic(models.Model):
    full_name = models.CharField(
        max_length=150,
        verbose_name='ФИО механика'
    )

    specialization = models.CharField(
        max_length=150,
        verbose_name='Специализация'
    )

    experience = models.PositiveIntegerField(
        verbose_name='Опыт работы'
    )

    phone = models.CharField(
        max_length=20,
        verbose_name='Телефон'
    )

    photo = models.ImageField(
        upload_to='mechanic_photos/',
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )

    class Meta:
        verbose_name = 'механик'
        verbose_name_plural = 'механики'

    def __str__(self):
        return self.full_name

class ServiceOrder(models.Model):

    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает'
        IN_PROGRESS = 'in_progress', 'В работе'
        COMPLETED = 'completed', 'Завершен'
        CANCELLED = 'cancelled', 'Отменен'

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='service_orders'
    )

    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    mechanic = models.ForeignKey(
        Mechanic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )

    appointment_date = models.DateTimeField(
        verbose_name='Дата записи'
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    total_price = models.IntegerField(
        default=0,
        verbose_name='Общая стоимость'
    )

    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name='Комментарий'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f"Заказ #{self.id}"

class OrderService(models.Model):
    order = models.ForeignKey(
        ServiceOrder,
        on_delete=models.CASCADE,
        related_name='order_services'
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='order_services'
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    class Meta:
        verbose_name = 'услуга в заказе'
        verbose_name_plural = 'услуги в заказах'
        unique_together = ['order', 'service']

    def __str__(self):
        return f"{self.order.id} - {self.service.name}"

class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    mechanic = models.ForeignKey(
        Mechanic,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    text = models.TextField()

    rating = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзывы'

    def __str__(self):
        return f"{self.user} - {self.rating}"