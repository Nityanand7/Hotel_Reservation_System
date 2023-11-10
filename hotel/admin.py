from django.contrib import admin

from hotel.models import *

admin.site.register(Room)
admin.site.register(Service)
admin.site.register(Payment)
admin.site.register(Booking)