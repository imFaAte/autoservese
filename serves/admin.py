from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (Category, CarBrand, Car, ServiceCategory,Service, Mechanic, ServiceOrder, OrderService, Review)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at', 'icon_preview']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']

    def icon_preview(self, obj):
        if obj.icon_image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />',
                               obj.icon_image.url)
        return "Нет иконки"

    icon_preview.short_description = 'Иконка'

@admin.register(CarBrand)
class CarBrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'cars_count']
    search_fields = ['name']
    ordering = ['name']

    def cars_count(self, obj):
        count = obj.cars.count()
        url = reverse('admin:serves_car_changelist') + f'?brand__id__exact={obj.id}'
        return format_html('<a href="{}">{} автомобилей</a>', url, count)

    cars_count.short_description = 'Количество автомобилей'

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner_info', 'car_info', 'plate_number', 'year', 'orders_count', 'created_at']
    list_filter = ['brand', 'year', 'created_at']
    search_fields = ['plate_number', 'model', 'owner__username', 'owner__email']
    readonly_fields = ['created_at', 'image_preview']
    raw_id_fields = ['owner']
    list_select_related = ['owner', 'brand']
    date_hierarchy = 'created_at'

    def owner_info(self, obj):
        return format_html(
            '<strong>{}</strong><br/><small>{}</small>',
            obj.owner.username,
            obj.owner.email
        )

    owner_info.short_description = 'Владелец'

    def car_info(self, obj):
        return format_html('<strong>{} {}</strong>', obj.brand.name, obj.model)

    car_info.short_description = 'Автомобиль'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" style="border-radius: 10px;" />', obj.image.url)
        return "Нет фото"

    image_preview.short_description = 'Просмотр фото'

    def orders_count(self, obj):
        count = obj.orders.count()
        if count > 0:
            url = reverse('admin:serves_serviceorder_changelist') + f'?car__id__exact={obj.id}'
            return format_html('<a href="{}" style="font-weight: bold;">{} заказов</a>', url, count)
        return '0'

    orders_count.short_description = 'Заказов'

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'services_count']
    search_fields = ['name']

    def services_count(self, obj):
        return obj.services.count()

    services_count.short_description = 'Количество услуг'

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price_display', 'duration', 'created_at', 'status_badge']
    list_filter = ['category', 'created_at', 'price']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'image_preview']
    ordering = ['-created_at']

    def price_display(self, obj):
        return format_html('<span style="color: green; font-weight: bold;">{} ₽</span>', obj.price)

    price_display.short_description = 'Цена'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" style="border-radius: 5px;" />', obj.image.url)
        return "Нет изображения"

    image_preview.short_description = 'Просмотр'

    def status_badge(self, obj):
        if obj.price > 10000:
            color = 'red'
        elif obj.price > 5000:
            color = 'orange'
        else:
            color = 'green'
        return format_html('<span style="color: {}; font-weight: bold;">●</span>', color)

    status_badge.short_description = 'Статус'

@admin.register(Mechanic)
class MechanicAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'specialization', 'experience', 'phone', 'is_active', 'reviews_count']
    list_filter = ['specialization', 'is_active', 'experience']
    search_fields = ['full_name', 'phone', 'specialization']
    list_editable = ['is_active']
    readonly_fields = ['photo_preview']

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="150" style="border-radius: 10px;" />', obj.photo.url)
        return "Нет фото"

    photo_preview.short_description = 'Просмотр фото'

    def reviews_count(self, obj):
        count = obj.reviews.count()
        url = reverse('admin:serves_review_changelist') + f'?mechanic__id__exact={obj.id}'
        return format_html('<a href="{}">{} отзывов</a>', url, count)

    reviews_count.short_description = 'Отзывов'

class OrderServiceInline(admin.TabularInline):
    model = OrderService
    extra = 1
    raw_id_fields = ['service']
    readonly_fields = ['subtotal']

    def subtotal(self, obj):
        if obj.service_id and obj.quantity:
            return f"{obj.service.price * obj.quantity} ₽"
        return "0 ₽"

    subtotal.short_description = 'Сумма'

@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'client_info', 'car_info', 'mechanic_info', 'appointment_date', 'total_price_display',
                    'status_colored', 'created_at']
    list_filter = ['status', 'created_at', 'appointment_date']
    search_fields = ['id', 'client__username', 'car__plate_number', 'comment']
    readonly_fields = ['created_at', 'total_price']
    raw_id_fields = ['client', 'car', 'mechanic']
    list_select_related = ['client', 'car', 'mechanic']
    date_hierarchy = 'appointment_date'
    inlines = [OrderServiceInline]
    actions = ['mark_as_in_progress', 'mark_as_completed', 'mark_as_cancelled']

    def client_info(self, obj):
        return format_html(
            '<strong>{}</strong><br/><small>{}</small>',
            obj.client.username,
            obj.client.email
        )

    client_info.short_description = 'Клиент'

    def car_info(self, obj):
        return format_html(
            '{} {}<br/><small>{}</small>',
            obj.car.brand.name,
            obj.car.model,
            obj.car.plate_number
        )

    car_info.short_description = 'Автомобиль'

    def mechanic_info(self, obj):
        if obj.mechanic:
            return format_html(
                '<strong>{}</strong><br/><small>{}</small>',
                obj.mechanic.full_name,
                obj.mechanic.specialization
            )
        return 'Не назначен'

    mechanic_info.short_description = 'Механик'

    def total_price_display(self, obj):
        return format_html('<span style="color: green; font-weight: bold;">{} ₽</span>', obj.total_price)

    total_price_display.short_description = 'Сумма'

    def status_colored(self, obj):
        colors = {
            'pending': 'orange',
            'in_progress': 'blue',
            'completed': 'green',
            'cancelled': 'red'
        }
        status_names = {
            'pending': 'Ожидает',
            'in_progress': 'В работе',
            'completed': 'Завершен',
            'cancelled': 'Отменен'
        }
        color = colors.get(obj.status, 'gray')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color,
                           status_names.get(obj.status, obj.status))

    status_colored.short_description = 'Статус'

    @admin.action(description='Изменить статус на "В работе"')
    def mark_as_in_progress(self, request, queryset):
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'{updated} заказ(ов) переведен(о) в статус "В работе"')

    @admin.action(description='Изменить статус на "Завершен"')
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} заказ(ов) завершен(о)')

    @admin.action(description='Изменить статус на "Отменен"')
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} заказ(ов) отменен(о)')


@admin.register(OrderService)
class OrderServiceAdmin(admin.ModelAdmin):
    list_display = ['order', 'service', 'quantity', 'subtotal']
    list_filter = ['order__status']
    search_fields = ['order__id', 'service__name']
    raw_id_fields = ['order', 'service']
    readonly_fields = ['subtotal']

    def subtotal(self, obj):
        if obj.service and obj.quantity:
            return f"{obj.service.price * obj.quantity} ₽"
        return "0 ₽"

    subtotal.short_description = 'Сумма'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'mechanic', 'rating_stars', 'short_text', 'created_at']
    list_filter = ['rating', 'created_at', 'mechanic']
    search_fields = ['user__username', 'mechanic__full_name', 'text']
    readonly_fields = ['created_at']
    raw_id_fields = ['user', 'mechanic']
    date_hierarchy = 'created_at'

    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: gold; font-size: 16px;">{}</span> <span>({}/5)</span>', stars,
                           obj.rating)

    rating_stars.short_description = 'Оценка'

    def short_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text

    short_text.short_description = 'Текст отзыва'

admin.site.site_header = 'Автосервис "Мастер" - Панель управления'
admin.site.site_title = 'Админка автосервиса'
admin.site.index_title = 'Добро пожаловать в систему управления автосервисом'