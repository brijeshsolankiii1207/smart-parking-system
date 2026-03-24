"""
URL configuration for pms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from parking import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index,name='index'),
    path('signin.html',views.signin,name='signin'),
    path('signup.html',views.signup,name='signup'),
    path('signout.html',views.signout,name='signout'),
    path('charge-chart.html',views.chargeChart,name='charge_chart'),
    path('create.html',views.create,name='create'),
    path('cancel.html', views.cancel_view, name='cancel_view'),
    path('cancel-booking/', views.cancel_booking, name='cancel_booking'),
    path('booking/confirm/<int:booking_id>/', views.booking_confirm, name='booking_confirm'),

    path("mybooking.html/", views.my_bookings, name="my_booking"),
    path("basement.html/", views.basement, name="basement"),
    path("ground.html/", views.groundfloor, name="groundfloor"),
    path("first_floor.html/", views.firstfloor, name="firstfloor"),
    path("Second_floor.html/", views.secondfloor, name="secondfloor"),
    path('pay/<int:id>/',views.pay,name='pay'),
    path('success_pay/',views.paymentSuccess,name='payment_success'),
]
