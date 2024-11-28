from django.urls import path
from . import views

app_name = 'reception'  # This is important for namespacing

urlpatterns = [
    path('dashboard/', views.dashboard, name='reception_dashboard'),
path('dashboard/', views.dashboard, name='dashboard'),

    path('reservations/', views.reservation_management, name='reservation_management'),
    path('reservations/edit/<int:reservation_id>/', views.edit_reservation, name='edit_reservation'),
# reception/urls.py
path('reservations/<int:reservation_id>/cancel/', views.cancel_reservation, name='cancel_reservation'),

    path('orders/', views.order_management, name='order_management'),
    path('orders/send_to_kitchen/<int:order_id>/', views.send_to_kitchen, name='send_to_kitchen'),
    path('orders/mark_as_complete/<int:order_id>/', views.mark_as_complete, name='mark_as_complete'),

    path('status/', views.status_management, name='status_management'),
    path('checkin_checkout/<int:reservation_id>/', views.checkin_checkout, name='checkin_checkout'),
    path('check_in_success/', views.check_in_success, name='check_in_success'),
    path('check_in_error/', views.check_in_error, name='check_in_error'),
    path('check_in_error/<str:error_message>/', views.check_in_error, name='check_in_error'),
    path('reservation_cancelled/<int:reservation_id>/', views.reservation_cancelled, name='reservation_cancelled'),
    path('payment_billing_summary/<int:reservation_id>/', views.payment_billing_summary, name='payment_billing_summary'),
]
