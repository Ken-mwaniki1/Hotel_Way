from django.db import models

from django.db import models
from typing import Any

import datetime

from django import forms

class MenuItem(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='menu_images/', blank=True)
    category = models.CharField(max_length=255, blank=True)
    availability = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Staff(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    contact_info = models.CharField(max_length=255)
    # add other fields as needed

    def __str__(self):
        return self.name

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['name', 'role', 'contact_info']



class Guest(models.Model):
    name = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=255)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Order(models.Model):
    customer_name = models.CharField(max_length=255, default="Unknown")  # Default value for new and existing rows
    order_items = models.TextField(blank=True)
    created_at = models.DateTimeField(default=datetime.datetime(2024, 1, 1))
    guest = models.ForeignKey('Guest', on_delete=models.CASCADE, null=True, blank=True)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, null=True, blank=True)
    items = models.TextField(default="Default item")
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('served', 'Served'),
            ('completed', 'Completed'),
        ],
        default='pending'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('order_not_served', 'Order Not Served'),
            ('pending', 'Pending'),
            ('ready', 'Ready'),
        ],
        default='order_not_served'
    )

class Room(models.Model):
    SINGLE = 'single'
    DOUBLE = 'double'
    SUITE = 'suite'

    ROOM_TYPE_CHOICES = [
        (SINGLE, 'Single'),
        (DOUBLE, 'Double'),
        (SUITE, 'Suite'),
    ]

    id = models.AutoField(primary_key=True)
    room_number = models.CharField(max_length=10)
    room_type = models.CharField(
        max_length=255,
        choices=ROOM_TYPE_CHOICES,  # Use the choices here
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"


class Reservation(models.Model):
    ROOM_TYPE_CHOICES = [
        ('single', 'Single'),
        ('double', 'Double'),
        ('suite', 'Suite'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('checked-in', 'Checked-in'),
        ('checked-out', 'Checked-out'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    check_in_date = models.DateField(null=True, blank=True)
    check_out_date = models.DateField(null=True, blank=True)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES, default='single')
    num_guests = models.PositiveIntegerField(default=1)
    special_requests = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return (
            f"Reservation by {self.name} | Guests: {self.num_guests} | "
            f"Room: {self.get_room_type_display()} | Status: {self.get_status_display()}"
        )

class Invoice(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice for {self.order}"

class Customer(models.Model):
    customer_name = models.CharField(max_length=100)
    guast_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.customer_name} {self.guast_name}"


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=255)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('order_not_served', 'Order Not Served'),
            ('pending', 'Pending'),
            ('ready', 'Ready'),
            ('paid', 'Paid'),
        ],
        default='order_not_served'
    )

    def __str__(self):
        return f"Payment for Order {self.order.id} - {self.payment_status}"

class Sum:
    pass