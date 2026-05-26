from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('services/', views.service_list, name='service_list'),
    path('services/<slug:slug>/', views.service_detail, name='service_detail'),
    path('cars/', views.car_list, name='car_list'),
    path('cars/<int:pk>/', views.car_detail, name='car_detail'),
    path('mechanics/', views.mechanic_list, name='mechanic_list'),
    path('mechanics/<int:pk>/', views.mechanic_detail, name='mechanic_detail'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('reviews/', views.review_list, name='review_list'),
    path('contacts/', views.contacts, name='contacts'),
    path('cart/', views.service_cart, name='service_cart'),
    path('add-to-cart/<int:service_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:service_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:service_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('create-order/', views.create_order, name='create_order'),
    path('create-order/', views.create_order, name='create_order'),
    path('send-feedback/', views.send_feedback, name='send_feedback'),
]