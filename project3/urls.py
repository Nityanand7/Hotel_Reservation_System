"""
URL configuration for project3 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from hotel import views

urlpatterns = [
    path('hotel/admin/', admin.site.urls),
    path('',views.landing_view,name='landing_page'),
    path('signup/', views.signup, name='signup'),
    path('login/',views.user_login,name='login'),
    path('administration/user/signup/', views.signup,name='administration_user_signup'),
    path('administration/user/login/', views.user_login,name='administration_user_signup'),
    path('user/home/',views.user_home,name='user_home'),
    path('administration/user/home/',views.administraion_user_home,name='admin_user_home'),
    path('available/rooms/',views.room_list,name='available_rooms'),
    path('book-room/<int:room_id>/', views.book_room, name='book_room'),
    path('select-services/<int:booking_id>/', views.select_services, name='select_services'),
    path('credit-card-info/<int:booking_id>/', views.credit_card_info, name='credit_card_info'),
    path('print-receipt/<int:booking_id>/', views.print_receipt, name='print_receipt'),
    path('booking-confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('add-room/', views.add_room, name='add_room'),
    path('add-service/', views.add_service, name='add_service'),
    path('services/', views.service_list, name='service_list'),
    path('users/',views.users_list,name='users_list'),
    path('bookings/',views.bookins_list,name='users_list'),
    path('user/bookings/',views.user_bookings_list,name='user_bookings'),
    path('user/profile/',views.user_profile,name='user_profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
