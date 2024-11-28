from django import forms
from .models import Room, Staff, Guest, Reservation, Order, Payment, MenuItem
from django import forms
from .models import Order, MenuItem, Room

class OrderForm(forms.ModelForm):
    customer_id = forms.ModelChoiceField(
        queryset=Room.objects.all(),
        empty_label="Select Room",
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,  #general optional field
    )
    guest_id = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
    )
    items = forms.ModelMultipleChoiceField(
        queryset=MenuItem.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Order
        fields = ['customer_name', 'customer_id', 'guest_id', 'order_items']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'order_items': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order_items'].required = False
        initial_items = kwargs.get('initial', {}).get('items', {})
        self.fields['items'].initial = [int(item_id) for item_id in initial_items]

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_number', 'room_type', 'price', 'availability', 'description', 'name']

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['name', 'role', 'contact_info']


class GuestForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
        }

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['name', 'email', 'check_in_date', 'check_out_date', 'room_type', 'room', 'num_guests',
                  'special_requests']

        widgets = {
            'check_in_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'check_out_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'special_requests': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'room': forms.Select(attrs={'class': 'form-select'}),
            'room_type': forms.Select(attrs={'class': 'form-select'}),
        }

    room_type = forms.ChoiceField(
        choices=Room.ROOM_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )

    room = forms.ModelChoiceField(
        queryset=Room.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set initial values and attributes for form fields
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['room_type'].widget.attrs.update({'class': 'form-select'})
        self.fields['num_guests'].widget.attrs.update({'class': 'form-control', 'min': 1})

        if 'room_type' in self.data:
            try:
                room_type = self.data.get('room_type')
                self.fields['room'].queryset = Room.objects.filter(room_type=room_type, availability=True)
            except (ValueError, TypeError):
                pass  # Invalid room_type value, ignore
        else:
            self.fields['room'].queryset = Room.objects.none()


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method']

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['name',  'description', 'category',  'price', 'image']