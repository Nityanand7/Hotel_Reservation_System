from django.db import models


from django.contrib.auth.models import AbstractUser
from django.db import models

# Custom User model that extends AbstractUser
class User(AbstractUser):
   first_name = models.CharField(max_length=60,null=True)
   last_name = models.CharField(max_length=60,null=True)
   email = models.CharField(max_length=60,null=True)

# Room
class Room(models.Model):
    ROOM_TYPES = (
        ('SIN', 'Single'),
        ('DBL', 'Double'),
        ('SUI', 'Suite'),
    )
    room_number = models.CharField(max_length=5, unique=True)
    room_type = models.CharField(max_length=3, choices=ROOM_TYPES)
    capacity = models.IntegerField(null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='room_images/', null=True,
                              blank=True)  # Assume you have a media directory set up
    description = models.TextField(null=True, blank=True)


# Service
class Service(models.Model):
    service_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.service_name} - ${self.price}"


# Booking
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)
    check_in = models.DateField()
    check_out = models.DateField()
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)



# BookingService (Intermediate model for Many-to-Many relationship between Booking and Service)
class BookingService(models.Model):
    booking = models.ForeignKey(Booking, related_name='booking_services', on_delete=models.CASCADE,null=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE,null=True)
    quantity = models.IntegerField(default=1)



# CreditCard (Dummy model for educational purposes only)
class CreditCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cardholder_name = models.CharField(max_length=100)
    card_type = models.CharField(max_length=50)
    last_four_digits = models.CharField(max_length=4)
    expiration_month = models.IntegerField()
    expiration_year = models.IntegerField()
    billing_address = models.TextField()



# Payment
class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    credit_card = models.ForeignKey(CreditCard, on_delete=models.SET_NULL, null=True)
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    payment_method = models.CharField(max_length=50)  # e.g., 'credit_card', 'paypal'
    status = models.CharField(max_length=50)  # e.g., 'pending', 'completed', 'refunded'



