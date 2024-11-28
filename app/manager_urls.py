from django.urls import path
from . import views

app_name = 'manager'

urlpatterns = [
    path('dashboard/', views.manager_dashboard, name='dashboard'),

    path('reservation_management/', views.reservation_management, name='reservation_management'),
    path('reservations/<int:reservation_id>/edit/', views.edit_reservation, name='edit_reservation'),
    path('reservations/<int:reservation_id>/delete/', views.delete_reservation, name='delete_reservation'),

    path('staff/<int:staff_id>/edit/', views.edit_staff, name='edit_staff'),
    path('staff/<int:staff_id>/delete/', views.delete_staff, name='delete_staff'),
    path('order/', views.order, name='order'),
    path('order_confirmation/', views.order_confirmation, name='order_confirmation'),

    path('rooms/', views.room_management, name='room_management'),
    path('rooms/<str:room_id>/delete/', views.delete_room, name='delete_room'),

path('items/', views.item_management, name='item_management'),
    path('menu_items/add/', views.add_menu_item, name='add_menu_item'),

    path('items/<int:item_id>/delete/', views.delete_item, name='delete_item'),
]