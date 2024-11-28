
from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('menu/', views.menu, name='menu'),
    path('contact/', views.contact, name='contact'),
    # Order-related views
    path('reservation/', views.add_reservation, name='add_reservation'),
    path('order/', views.order, name='order'),
    path('order/<int:reservation_id>/', views.order, name='order_with_reservation'),  # For reservation users
    path('order/confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    # Correct pattern to handle order ID
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),

    path('add_to_order/<int:item_id>/', views.add_to_order, name='add_to_order'),
    path('full_order/', views.full_order, name='full_order'),
    path('process_payment/<int:order_id>/', views.process_payment, name='process_payment'),

    path('reservations/', views.add_reservation, name='add_reservation'),
    path('get_available_rooms/', views.get_available_rooms, name='get_available_rooms'),  # New URL for room type selection
    path('reservations/success/', views.reservation_success, name='reservation_success'),
]
