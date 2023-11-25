from django.contrib.auth import login
from django.http import HttpResponseForbidden
from django.shortcuts import render,get_object_or_404

# Create your views here.

def landing_view(request):
    return render(request,'landing_page.html')

from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import UserSignUpForm

from django.contrib import messages

def signup(request):
    if request.method == 'POST':
        print(request.path)
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.mobile_number = user.username
            print("form is valid and user is created")
            # You can also log the user in and then redirect
            if "admin" in request.path:
                user.is_superuser = True
                user.is_staff = True
                user.save()
                login(request,user)
                messages.add_message(request,messages.SUCCESS,'Admin account created successfully.')
                return redirect('admin_user_home')
            user.save()
            login(request, user)
            messages.add_message(request,messages.SUCCESS,'Your user account created successfully.')
            return redirect(reverse('user_home'))
    else:
        form = UserSignUpForm()
    return render(request, 'user_signup.html', {'form': form})

from .forms import UserLoginForm

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()  # Get the authenticated user from the form
            login(request, user)    # Pass both the request and user to the login function
            # Redirect to a success page.
            if "admin" in request.path:
                return redirect('admin_user_home')
            return redirect(reverse('user_home'))
    else:
        form = UserLoginForm()

    return render(request, 'login.html', {'form': form})


def administraion_user_home(request):
    print("coming here")
    return render(request,'administraion_user_home.html')

def user_home(request):
    return render(request,'user_home.html')

from .models import Room
def room_list(request):
    # Get query parameters for search, filter, and price range
    query = request.GET.get('q', '')
    room_type = request.GET.get('type', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    rooms = Room.objects.all()

    if query:
        rooms = rooms.filter(room_number__icontains=query)
    if room_type:
        rooms = rooms.filter(room_type=room_type)
    if min_price:
        rooms = rooms.filter(price__gte=min_price)
    if max_price:
        rooms = rooms.filter(price__lte=max_price)

    context = {
        'rooms': rooms,
        'min_price': min_price,
        'max_price': max_price
    }
    return render(request, 'room_list.html', context)


from .forms import BookingForm


def book_room(request, room_id):
    room = get_object_or_404(Room, pk=room_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.room = room
            booking.user = request.user
            booking.total_price = room.price  # You might want to calculate this based on days
            booking.save()
            #room.is_available = False
            room.save()
            messages.success(request, 'Room Added successfully.')
            return redirect('select_services', booking_id=booking.id)
    else:
        form = BookingForm()

    return render(request, 'book_room.html', {'form': form, 'room': room})

from .forms import ServiceForm

from .models import Booking,BookingService

def select_services(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            selected_services = form.cleaned_data['services']
            for service in selected_services:
                BookingService.objects.create(
                    booking=booking,
                    service=service,
                    quantity=form.cleaned_data['quantity']
                )
            messages.success(request, 'Services added to your booking.')
            return redirect('booking_confirmation', booking_id=booking.id)  # Redirect to a confirmation page or similar
    else:
        form = ServiceForm()

    return render(request, 'select_services.html', {'form': form, 'booking': booking})


def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking_services = BookingService.objects.filter(booking=booking)

    # Calculate the total price for the booking including services
    additional_services_cost = sum(service.service.price * service.quantity for service in booking_services)
    total_cost = booking.total_price + additional_services_cost

    context = {
        'booking': booking,
        'booking_services': booking_services,
        'total_cost': total_cost,
    }
    return render(request, 'booking_confirmation.html', context)



from django.utils import timezone
from .forms import CreditCardForm
from .models import Booking, BookingService, Room, CreditCard,Payment

def credit_card_info(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if not booking.is_active:  # Check if the booking hasn't been processed already
        messages.error(request, "This booking has already been processed.")
        return redirect('booking_detail', booking_id=booking_id)

        # Calculate the total price including any additional services
    additional_services_cost = sum(
            bs.service.price * bs.quantity for bs in BookingService.objects.filter(booking=booking))
    total_cost = booking.total_price + additional_services_cost
    if request.method == 'POST':
        form = CreditCardForm(request.POST)
        if form.is_valid():
            credit_card = form.save(commit=False)
            credit_card.user = request.user
            credit_card.save()

            # Update booking status and room availability
            booking.is_active = True
            booking.room.is_available = False
            booking.save()
            try:

                # If you have a payment model, you can also create a payment record
                Payment.objects.create(booking=booking, amount_paid=total_cost, credit_card=credit_card,
                                       payment_method='credit-card',payment_date=timezone.now(),status='completed')
            except Exception as e:
                print("Exception in creating the payment:", str(e))
                pass
            try:
                send_booking_receipt_email(booking)
            except Exception as e:
                print("Error in sending mail:", str(e))
                pass
            # Redirect to a confirmation page or the user's booking list
            return redirect('user_bookings')
    else:
        form = CreditCardForm()



    context = {
        'form': form,
        'booking': booking,
        'total_cost': total_cost,
    }
    return render(request, 'credit_card_info.html', context)


def user_bookings(request):
    user = request.user
    bookings = Payment.objects.filter(booking__user=user)
    print("bookings",bookings)
    return render(request, 'user_bookings.html', {'bookings': bookings})


# views.py

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_booking_receipt_email(booking):
    subject = 'Your Hotel Booking Receipt'
    html_message = render_to_string('email_receipt.html', {'booking': booking})
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    to = booking.user.email

    send_mail(subject, plain_message, from_email, [to], html_message=html_message)

def print_receipt(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    # Make sure the user requesting the receipt is the one who made the booking
    if request.user != booking.user:
        return HttpResponseForbidden()
    return render(request, 'print_receipt.html', {'booking': booking})


from .forms import RoomForm

def add_room(request):
    if not request.user.is_staff:
        messages.error(request, "You are not authorized to view this page.")
        return redirect('administration_user_signup')

    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "New room added successfully!")
            return redirect('available_rooms')  # Redirect to the room list or wherever appropriate
    else:
        form = RoomForm()

    return render(request, 'add_room.html', {'form': form})

from .forms import AddServiceForm

def add_service(request):
    if not request.user.is_superuser:  # Assuming only superusers can add services
        messages.error(request, "You are not authorized to perform this action.")
        return redirect('administration_user_signup')

    if request.method == 'POST':
        form = AddServiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New service added successfully!")
            return redirect('service_list')  # Redirect to the service list view
    else:
        form = AddServiceForm()

    return render(request, 'add_service.html', {'form': form})

from .models import Service
def service_list(request):
    services = Service.objects.all()  # Fetch all services
    return render(request, 'service_list.html', {'services': services})

from .models import User
def users_list(request):
    users = User.objects.filter(is_superuser=False)
    return render(request,'users_list.html',{'users':users})

def user_profile(request):
    return render(request, 'user_profile.html')
def bookins_list(request):
    bookings = Booking.objects.all()
    return render(request, 'bookings_list.html', {'bookings': bookings})

def user_bookings_list(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'user_bookings_list.html', {'bookings': bookings})