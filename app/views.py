import json
import random
import threading
from django.db import IntegrityError
from . import models
from .models import Order, Reservation, Room, Invoice, Guest, Staff, MenuItem, Customer
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import OrderForm, MenuItemForm, GuestForm, RoomForm, PaymentForm, StaffForm ,Guest,Payment, Staff, Room, Reservation, ReservationForm  # Assuming you have a ReservationForm
from django.db.models import Sum, Count, Avg
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.timezone import now as timezone_now
from django.http import HttpResponse, JsonResponse


def add_menu_item(request):
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('manager:item_management')  # Redirect to item management page
    else:
        form = MenuItemForm()
    return render(request, 'manager/add_menu_item.html', {'form': form})


def item_management(request):
    menu_items = MenuItem.objects.all()

    if request.method == 'POST':
        if 'add_item' in request.POST:
            form = MenuItemForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('manager:item_management')
        elif 'edit_item' in request.POST:
            item_id = request.POST.get('item_id')
            menu_item = get_object_or_404(MenuItem, id=item_id)
            form = MenuItemForm(request.POST, request.FILES, instance=menu_item)
            if form.is_valid():
                form.save()
                return redirect('manager:item_management')
    else:
        form = MenuItemForm()

    context = {
        'menu_items': menu_items,
        'form': form,
    }
    return render(request, 'manager/item_management.html', context)


def delete_item(request, item_id):
    menu_item = get_object_or_404(MenuItem, id=item_id)
    if request.method == 'POST':
        menu_item.delete()
        return redirect('manager:item_management')
    context = {'item': menu_item}
    return render(request, 'manager/delete_item.html', context)

def add_to_order(request, item_id):
    order_items = request.session.get('order_items', {})
    item = MenuItem.objects.get(pk=item_id)

    if item_id in order_items:
        order_items[item_id] += 1
    else:
        order_items[item_id] = 1

    request.session['order_items'] = order_items
    return redirect('full_order')

def menu(request):
    menu_items = MenuItem.objects.filter(availability=True)
    menu_items_json = []
    for item in menu_items:
        menu_items_json.append({
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'price': float(item.price),  # Convert Decimal to float
            'image': item.image.url if item.image else None,
        })

    if request.method == 'POST':
        selected_items_json = request.POST.get('order_items')

        try:
            selected_items = json.loads(selected_items_json)

            order = Order()
            order.customer_name = request.POST.get('customer_name', '')
            if request.user.is_authenticated:
                order.customer_id = 32 * random.randint(153, 999)

                while True:
                    guest_id = random.randint(1855, 9999)
                    if Guest.objects.filter(id=guest_id).exists():
                        break
                order.guest_id = guest_id
            else:
                order.customer_id = order.customer_name
                order.guest_id = None

            order.created_at = timezone.now()
            order.order_items = selected_items
            order.save()

            response = redirect('main:order_confirmation', order_id=order.id)
            response.set_cookie('selected_items', json.dumps(selected_items))
            return response

        except json.JSONDecodeError as e:
            print(f"Error parsing selected_items: {e}")


    response = render(request, 'main/menu.html', {
        'menu_items': menu_items,
        'menu_items_json': json.dumps(menu_items_json),
    })

    request.session['menu_items'] = menu_items_json

    return response


def order(request, reservation_id=None):
    """
    Handles order creation with or without a reservation.
    """
    reservation = Reservation.objects.get(id=reservation_id) if reservation_id else None

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')

        order_items_str = request.POST.get('order_items', '{}')
        try:
            order_items = json.loads(order_items_str)
        except json.JSONDecodeError:
            order_items = {}

        # Initialize form data
        initial_data = {
            'customer_name': customer_name,
            'order_items': json.dumps(order_items),
        }
        form = OrderForm(initial=initial_data)

        # Generate guest_id and customer_id if not in session
        guest_id = request.session.get('guest_id', None)
        customer_id = request.session.get('customer_id', None)

        if not guest_id:
            guest_id = 'guest_' + str(random.randint(1000, 9999))  # Generate guest ID
            request.session['guest_id'] = guest_id


        if not customer_id:
            customer_id = 32 * random.randint(1867, 9999)  # Generate customer ID
            request.session['customer_id'] = customer_id

        room_status = "General"  # Default status for new reservations

        if reservation:
            room_status = reservation.status

        # Store the generated customer_id and guest_id in the context
        context = {
            'guest_id': guest_id,
            'customer_id': customer_id,
            'room_status': room_status,
            'form': form,
            'reservation': reservation,
            'items_data': order_items,  # Ensure order items are passed
        }

        return render(request, 'main/order.html', context)
    else:
        return render(request, 'main/order.html', {'form': OrderForm()})


def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    selected_items_json = request.COOKIES.get('selected_items')
    selected_items = json.loads(selected_items_json) if selected_items_json else []

    # Check if guest ID exists, otherwise generate one and create guest
    if not order.guest:
        guest_id = 'guest_' + str(random.randint(1000, 9999))
        guest_email = "guest_" + str(guest_id) + "@hotel.com"
        guest = Guest.objects.create(
            name="Guest " + str(guest_id),
            first_name="Guest",
            last_name=str(guest_id),
            email=guest_email,
            phone_number="032" + str(random.randint(1000000, 9999999)),
            address="General"
        )
        order.guest = guest

    # Check if customer_id exists, otherwise generate one and create customer
    customer_id = request.session.get('customer_id')
    if customer_id:
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            # If no customer exists with this ID, generate a new one
            customer_id = 32 * random.randint(1867, 9999)  # Generate customer_id based on your formula
            customer = Customer.objects.create(
                customer_name="Customer",  # Corrected field name
                guast_name=str(customer_id),  # Corrected field name
                email="customer_" + str(customer_id) + "@hotel.com",  # Assign an email to this customer
                phone_number="032" + str(random.randint(1000000, 9999999))  # Generate a random phone number
            )
        order.customer = customer
        order.customer_id = customer.id  # Assign customer_id to the order

    try:
        order.save()
    except IntegrityError as e:
        print(f"Error saving order: {e}")
        return redirect('error_page')  # Redirect to an error page or handle the error gracefully

    # Parse the order_items JSON stored in the order object
    try:
        # Ensure the JSON string in the order is valid and parsed correctly
        raw_order_items = order.order_items.replace("'", '"')  # Fix for potential single-quote issues
        order_items = json.loads(raw_order_items)
    except (json.JSONDecodeError, TypeError):
        order_items = []  # Set to empty list if parsing fails

        # Prepare the order items for display
    order_items_display = []
    total_price = 0
    for item_data in order_items:
        try:
            # Fetch the MenuItem from the database using the ID in the JSON
            menu_item = MenuItem.objects.get(id=item_data['id'])
            item_total = menu_item.price * int(item_data['quantity'])  # Convert quantity to int for calculations

            # Add item details to the display list
            order_items_display.append({
                'name': menu_item.name,
                'quantity': item_data['quantity'],
                'price': menu_item.price,
                'total': item_total,
            })
            total_price += item_total
        except MenuItem.DoesNotExist:
            # Log the missing item or handle gracefully
            print(f"Menu item with ID {item_data['id']} not found in the database.")

    # Add context data for rendering the template
    context = {
        'order': order,
        'order_items_display': order_items_display,
        'total_price': total_price,
    }
    return render(request, 'main/order_success.html', context)


def full_order(request):
    order = None
    if request.method == 'POST':
        track_id = request.POST.get('track_id')
        try:
            order = Order.objects.get(customer_id=track_id)
        except Order.DoesNotExist:
            messages.error(request, 'Invalid Track ID') # Handle invalid track ID
    context = {'order': order}
    return render(request, 'main/full_order.html', context)

def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.order = order  # Associate payment with the order
            payment.payment_status = 'pending'  # Initial status
            payment.save()

            order.status = 'completed'
            order.save()

            messages.success(request, f"Payment for Order {order_id} has been processed successfully.")
            return redirect('main:order_success', order_id=order.id)
    else:
        form = PaymentForm()

    # Parse the JSON string and calculate the total amount
    try:
        raw_order_items = order.order_items.replace("'", '"')  # Correct invalid JSON format
        order_items = json.loads(raw_order_items)  # Parse JSON
    except (json.JSONDecodeError, TypeError):
        order_items = []

    order_items_display = []
    total_amount_due = 0

    for item_data in order_items:
        try:
            menu_item = MenuItem.objects.get(id=item_data['id'])
            item_total = menu_item.price * item_data['quantity']
            order_items_display.append({
                'name': menu_item.name,
                'quantity': item_data['quantity'],
                'price': menu_item.price,
                'total': item_total,
            })
            total_amount_due += item_total
        except MenuItem.DoesNotExist:
            pass

    # Context for the template
    context = {
        'order': order,
        'total_amount_due': total_amount_due,
        'order_items_display': order_items_display,
    }

    return render(request, 'main/payment_page.html', context)

def calculate_total_amount(item_ids, quantities):
    total_amount = 0
    for item_id, quantity in zip(item_ids, quantities):
        try:
            item = MenuItem.objects.get(pk=item_id)
            total_amount += item.price * quantity
        except MenuItem.DoesNotExist:
            pass  # Handle invalid item IDs
    return total_amount

def order_success(request, order_id):
    """
    Displays the order success page with the order details and payment status.
    """
    # Retrieve the order
    order = get_object_or_404(Order, id=order_id)

    # Parse the JSON string stored in the order's `order_items` field
    try:
        raw_order_items = order.order_items.replace("'", '"')  # Correct invalid JSON format if necessary
        order_items = json.loads(raw_order_items)
    except (json.JSONDecodeError, TypeError):
        order_items = []

    # Fetch menu item details for the order summary
    order_items_display = []
    total_amount_paid = 0
    for item_data in order_items:
        try:
            menu_item = MenuItem.objects.get(id=item_data['id'])
            item_total = menu_item.price * item_data['quantity']
            order_items_display.append({
                'name': menu_item.name,
                'quantity': item_data['quantity'],
                'price': menu_item.price,
                'total': item_total,
            })
            total_amount_paid += item_total
        except MenuItem.DoesNotExist:
            pass  # this will handle the case where the menu item doesn't exist

    # Fetch the associated payment details if available
    payment = Payment.objects.filter(order=order).last()  # Get the latest payment record for the order
    payment_status = payment.payment_status if payment else "No payment record found"

    context = {
        'order': order,
        'order_items_display': order_items_display,
        'total_amount_paid': total_amount_paid,
        'payment_status': payment_status,
    }

    return render(request, 'main/order_success.html', context)


def add_reservation(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            room = form.cleaned_data.get('room')

            if room:
                reservation = form.save()

                order_items_json = json.dumps([{
                    'id': room.id,
                    'name': f"{room.room_type} Room",
                    'quantity': int(1),
                    'price': str(room.price),
                }])

                while True:
                    customer_id = random.randint(1000, 9999)
                    if not Customer.objects.filter(id=customer_id).exists():
                        break

                while True:
                    guest_id = random.randint(1000, 9999)
                    if not Guest.objects.filter(id=guest_id).exists():
                        break

                customer_email = f"customer_{customer_id}@hotel.com"
                guest_email = f"guest_{guest_id}@hotel.com"

                customer, created = Customer.objects.get_or_create(
                    id=customer_id,
                    defaults={'customer_name': reservation.name, 'email': customer_email}
                )

                guest, created = Guest.objects.get_or_create(
                    id=guest_id,
                    defaults={'first_name': reservation.name, 'email': guest_email}
                )

                order = Order.objects.create(
                    customer_name=reservation.name,
                    order_items=order_items_json,
                    items=f"Reservation for {reservation.room_type} Room",
                    status='pending',
                    payment_status='order_not_served',
                    guest=guest,
                    customer=customer
                )

                messages.success(request, "Reservation made successfully. Redirecting to order confirmation...")
                return redirect('main:order_confirmation', order_id=order.id)

            else:
                messages.error(request, "Please select a room.")
                return render(request, 'main/reservations.html', {'form': form})

        else:
            messages.error(request, "There was an error with your reservation form.")
            return render(request, 'main/reservations.html', {'form': form})

    else:
        form = ReservationForm()
        return render(request, 'main/reservations.html', {'form': form})


def get_available_rooms(request):
    room_type = request.GET.get('room_type')
    available_rooms = Room.objects.filter(room_type=room_type, availability=True)

    rooms_data = [{'id': room.id, 'room_number': room.room_number} for room in available_rooms]
    return JsonResponse({'rooms': rooms_data})

def reservation_success(request):
    return render(request, 'main/reservation_success.html')

def edit_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)

    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            return redirect('reception:reservation_management')
    else:
        form = ReservationForm(instance=reservation)

    context = {'form': form, 'reservation': reservation}
    return render(request, 'reception/edit_reservation.html', context)

def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id)

    if request.method  == 'POST':
        reservation.status = 'cancelled'  # Assuming you have a status field in your Reservation model
        reservation.save()
        return redirect('reception:reservation_cancelled', reservation_id=reservation.id)

    context = {'reservation': reservation}
    return render(request, 'reception/cancel_reservation.html', context)
def delete_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id)
    if request.method == 'POST':
        reservation.delete()
        return redirect('manager:reservation_management')
    return render(request, 'manager/delete_reservation.html', {'reservation': reservation})

def edit_staff(request, staff_id):
    staff = get_object_or_404(Staff, pk=staff_id)
    if request.method == 'POST':
        form = StaffForm(request.POST, instance=staff)
        if form.is_valid():
            form.save()
            return redirect('manager:reservation_management')
    else:
        form = StaffForm(instance=staff)
    return render(request, 'manager/edit_staff.html', {'form': form, 'staff': staff})


def delete_staff(request, staff_id):
    staff = get_object_or_404(Staff, pk=staff_id)
    if request.method == 'POST':
        staff.delete()
        return redirect('manager:reservation_management')
    return render(request, 'manager/delete_staff.html', {'staff': staff})

def manager_dashboard(request):
    # Get the total number of reservations
    total_reservations = Reservation.objects.count()

    # Get the total number of guests
    total_guests = Guest.objects.count()

    # Calculate total revenue (replace with your actual revenue calculation logic)
    total_revenue = Payment.objects.aggregate(Sum('amount'))['amount__sum']

    # Get the total number of rooms
    total_rooms = Room.objects.count()

    # Get the number of available rooms
    available_rooms = Room.objects.filter(availability=True).count()

    # Calculate the occupancy rate
    occupancy_rate = (
        (total_rooms - available_rooms) / total_rooms * 100
        if total_rooms > 0
        else 0
    )

    # Geting the total number of staff members
    staff_count = Staff.objects.count()

    # Geting the latest reservations (e.g., the last 5)
    latest_reservations = Reservation.objects.all().order_by('-check_in_date')[:5]

    context = {
        'total_reservations': total_reservations,
        'total_guests': total_guests,
        'total_revenue': total_revenue,
        'occupancy_rate': occupancy_rate,
        'staff_count': staff_count,
        'latest_reservations': latest_reservations,
    }
    return render(request, 'manager/dashboard.html', context)

def checkin_checkout(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id)
    context = {'reservation': reservation}
    return render(request, 'reception/checkin_checkout.html', context)

def add_guest(request):
    if request.method == 'POST':
        form = GuestForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('guest_list')  # Redirect to the guest list page
    else:
        form = GuestForm()
    return render(request, 'add_guest.html', {'form': form})
def index(request):
    return render(request, 'index.html')


# Home page view
def home(request):
    return render(request, 'home.html')

def dashboard(request):
    # Get the total number of reservations
    total_reservations = Reservation.objects.count()

    # Get the total number of guests
    total_guests = Guest.objects.count()

    # Get the total number of rooms
    total_rooms = Room.objects.count()

    # Get the number of available rooms
    available_rooms = Room.objects.filter(availability=True).count()

    # Calculate the occupancy rate (percentage of occupied rooms)
    occupancy_rate = (
        (total_rooms - available_rooms) / total_rooms * 100
        if total_rooms > 0
        else 0
    )

    # Get the latest reservations (e.g., the last 5)
    latest_reservations = Reservation.objects.all().order_by('-check_in_date')[:5]

    context = {
        'total_reservations': total_reservations,
        'total_guests': total_guests,
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupancy_rate': occupancy_rate,
        'latest_reservations': latest_reservations,
    }
    return render(request, 'reception/dashboard.html', context)

def order_management(request):
    orders = Order.objects.all()
    return render(request, 'reception/order_management.html', {'orders': orders})

def send_to_kitchen(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'in progress'  # Change to the new intermediate status
    order.save()
    return redirect('reception:order_management')

def mark_as_complete(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'completed'
    order.payment_status = 'pending'
    order.save()
    return redirect('reception:order_management')

def reservation_management(request):
    reservations = Reservation.objects.all()

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('reception:reservation_management')  # Redirect to the same page
    else:
        form = ReservationForm()

    context = {
        'reservations': reservations,
        'form': form,
    }
    return render(request, 'reception/reservation_management.html', context)

def reservation_cancelled(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id)
    context = {'reservation': reservation}
    return render(request, 'reception/reservation_cancelled.html', context)

def guest_check_in(request, reservation_id):
    # Fetch the reservation by ID
    reservation = get_object_or_404(Reservation, id=reservation_id)

    if reservation.status == 'Pending':
        # Update reservation status to 'Checked-in'
        reservation.status = 'Checked-in'
        reservation.save()
        return render(request, 'reception/check_in_success.html', {'reservation': reservation})
    else:
        # Handle other status cases
        return render(request, 'reception/check_in_error.html', {'reservation': reservation})


def guest_cancel(request, reservation_id):
    # Fetch the reservation by ID
    reservation = get_object_or_404(Reservation, id=reservation_id)

    # Update reservation status to 'Cancelled'
    reservation.status = 'Cancelled'
    reservation.save()
    return render(request, 'reception/reservation_cancelled.html', {'reservation': reservation})

def status_management(request):
    # Fetch reservations based on their statuses
    pending_reservations = Reservation.objects.filter(status='pending')
    checked_in_reservations = Reservation.objects.filter(status='checked-in')
    cancelled_reservations = Reservation.objects.filter(status='cancelled')

    # Fetching the orders based on their statuses
    pending_orders = Order.objects.filter(status='pending')
    in_progress_orders = Order.objects.filter(status='in progress')
    completed_orders = Order.objects.filter(status='completed')

    # Prepare context for rendering
    context = {
        'pending_reservations': pending_reservations,
        'checked_in_reservations': checked_in_reservations,
        'cancelled_reservations': cancelled_reservations,
        'pending_orders': pending_orders,
        'in_progress_orders': in_progress_orders,
        'completed_orders': completed_orders,
    }

    return render(request, 'reception/status_management.html', context)

def room_management(request):
    rooms = Room.objects.all()

    if request.method == 'POST':
        if 'add_room' in request.POST:
            form = RoomForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('manager:room_management')
        elif 'edit_room' in request.POST:
            room_id = request.POST.get('room_id')
            room = get_object_or_404(Room, room_number=room_id)
            form = RoomForm(request.POST, instance=room)
            if form.is_valid():
                form.save()
                return redirect('manager:room_management')
    else:
        form = RoomForm()

    context = {
        'rooms': rooms,
        'form': form,
    }
    return render(request, 'manager/room_management.html', context)


def delete_room(request, room_id):
    room = get_object_or_404(Room, room_number=room_id)
    if request.method == 'POST':
        room.delete()
        return redirect('manager:room_management')
    context = {'room': room}
    return render(request, 'manager/delete_room.html', context)

def room_list(request):
    rooms = Room.objects.all()
    return render(request, 'main/room_list.html', {'rooms': rooms})

def payment_billing(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.reservation = reservation
            payment.save()
            return redirect('payment_success', reservation_id=reservation_id)  # Redirect to a success page
    else:
        form = PaymentForm()

    # Calculate total amount due (replace with your actual logic)
    total_amount_due = reservation.room.price * (reservation.check_out_date - reservation.check_in_date).days

    context = {
        'reservation': reservation,
        'form': form,
        'total_amount_due': total_amount_due,
    }
    return render(request, 'main/payment_billing.html', context)



def payment_billing_summary(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)  # Don't save yet
            payment.reservation = reservation  # Link payment to reservation
            payment.save()
            return redirect('reception:payment_success')  # Redirect to success page
    else:
        form = PaymentForm()

    # Calculate total amount due (you might need to fetch this from the Reservation or Order model)
    total_amount_due = reservation.room.price * (reservation.check_out_date - reservation.check_in_date).days

    context = {
        'reservation': reservation,
        'form': form,
        'total_amount_due': total_amount_due,
    }
    return render(request, 'reception/payment_billing_summary.html', context)

def check_in_success(request):
    return render(request, 'reception/check_in_success.html')

def check_in_error(request, error_message=None):
    context = {'error_message': error_message}
    return render(request, 'reception/check_in_error.html', context)


def contact(request):
    return render(request, 'main/contact.html')