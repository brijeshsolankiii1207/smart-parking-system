from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Booking, ParkingSlot, VehicleCategory, Floor
from django.views.decorators.http import require_POST
from datetime import datetime
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

User = get_user_model()

# Create your views here.
def index(request):
    username = request.user.username if request.user.is_authenticated else "Guest"
    context = {
        "username": username
    }
    return render(request, 'index.html', context)


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('signin')
    else:
        form = CustomUserCreationForm()
    context = {
        'form': form
    }
    return render(request, 'signup.html', context)


def signin(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    context = {
        'form': form
    }
    return render(request, 'signin.html', context)

def signout(request):
    logout(request)
    return redirect('index')


def chargeChart(request):
    return render(request,'charge-chart.html')

@login_required
def create(request):
    slot_id = request.GET.get('slot')
    slot_obj = None
    selected_category = None
    selected_floor = None

    if slot_id:
        slot_obj = get_object_or_404(ParkingSlot, id=slot_id)
        selected_category = slot_obj.vehicle_category
        selected_floor = slot_obj.floor

    if request.method == "POST":
        # Store form data in session instead of saving booking
        request.session['booking_data'] = {
            'owner_name': request.POST.get('owner_name'),
            'vehicle_number': request.POST.get('vehicle_number'),
            'mobile': request.POST.get('mobile'),
            'email': request.POST.get('email'),
            'start_time': request.POST.get('start_time'),
            'end_time': request.POST.get('end_time'),
            'slot_id': request.POST.get('slot'),
        }
        return redirect('pay', id=slot_id)  # Pass slot id to pay()

    context = {
        "categories": VehicleCategory.objects.all(),
        "floors": Floor.objects.all(),
        "selected_slot": slot_obj,
        "selected_category": selected_category,
        "selected_floor": selected_floor
    }

    return render(request, "create.html", context)

@login_required
def my_bookings(request):
    bookings = Booking.objects.all()
    context = {
        "bookings": bookings
    }
    return render(request, "mybookings.html", context)


@require_POST
def cancel_booking(request):
    release_expired_slots()
    booking_id = request.POST.get('booking_id')
    booking = get_object_or_404(Booking, id=booking_id)

    # Mark slot as available again
    slot = booking.slot
    slot.status = 'available'
    slot.save()

    # Delete the booking
    booking.delete()

    return redirect('my_booking')  # Or redirect to 'cancel.html' if desired

@login_required
def cancel_view(request):
    release_expired_slots()
    now = timezone.now()
    bookings = Booking.objects.filter(end_time__gte=now, slot__status='occupied')
    return render(request, 'cancel.html', {"bookings": bookings})


def basement(request):
    release_expired_slots()
    basement_floor = Floor.objects.filter(name__iexact="Basement").first()
    slots = []

    if basement_floor:
        slots = ParkingSlot.objects.filter(floor=basement_floor).order_by('slot_number')

    return render(request, 'basement.html', {"slots": slots})

def groundfloor(request):
    release_expired_slots()
    ground_floor = Floor.objects.filter(name__iexact="Ground").first()
    slots = []

    if ground_floor:

        slots = ParkingSlot.objects.filter(floor=ground_floor).order_by('slot_number')

    return render(request, "ground.html", {"slots": slots})

def firstfloor(request):
    release_expired_slots()
    first_floor = Floor.objects.filter(name__iexact="First").first()
    slots = []

    if first_floor:
        slots = ParkingSlot.objects.filter(floor=first_floor).order_by('slot_number')

    return render(request, "first_floor.html", {"slots": slots})

def secondfloor(request):
    release_expired_slots()
    second_floor = Floor.objects.filter(name__iexact="Second").first()
    slots = []

    if second_floor:
        slots = ParkingSlot.objects.filter(floor=second_floor).order_by('slot_number')

    return render(request, "second_floor.html", {"slots": slots})

@login_required
def booking_confirm(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # Calculate parking duration in hours (fractional)
    if booking.end_time and booking.start_time:
        duration = booking.end_time - booking.start_time
        duration_hours = duration.total_seconds() / 3600
        duration_hours = max(duration_hours, 0)  # avoid negative
    else:
        duration_hours = 0

    # Pricing rules based on floor name
    price_chart = {
        "Basement": {"min_2_hrs": 25, "max_24_hrs": 180},
        "Ground": {"min_2_hrs": 60, "max_24_hrs": 600},
        "First": {"min_2_hrs": 70, "max_24_hrs": 650},
        "Second": {"min_2_hrs": 110, "max_24_hrs": 950},
    }

    floor_name = booking.floor.name
    rates = None

    # find matching floor key ignoring case
    for key in price_chart.keys():
        if key.lower() in floor_name.lower():
            rates = price_chart[key]
            break

    # Default fallback if no match
    if not rates:
        rates = {"min_2_hrs": 0, "max_24_hrs": 0}

    cost = 0
    if duration_hours <= 2:
        cost = rates["min_2_hrs"]
    else:
        # charge min 2 hrs + pro-rate for remaining hours
        extra_hours = duration_hours - 2
        hourly_rate = (rates["max_24_hrs"] - rates["min_2_hrs"]) / 22  # 24 - 2 hrs
        cost = rates["min_2_hrs"] + extra_hours * hourly_rate
        if cost > rates["max_24_hrs"]:
            cost = rates["max_24_hrs"]

    cost = round(cost, 2)

    context = {
        "booking": booking,
        "duration_hours": round(duration_hours, 2),
        "cost": cost,
    }

    return render(request, "booking_confirm.html", context)

@login_required
def pay(request, id):
    booking_data = request.session.get('booking_data')

    if not booking_data:
        messages.error(request, "Booking data missing. Please try again.")
        return redirect('create')  # or back to index

    # Get the slot and validate it
    slot = get_object_or_404(ParkingSlot, id=booking_data['slot_id'])

    # Check if slot is already occupied (optional safety check)
    if slot.status == 'occupied':
        messages.error(request, "Selected slot is no longer available.")
        return redirect('create')

    try:
        start_time = datetime.strptime(booking_data['start_time'], '%Y-%m-%dT%H:%M')
        end_time = datetime.strptime(booking_data['end_time'], '%Y-%m-%dT%H:%M')
    except ValueError:
        messages.error(request, "Invalid time format.")
        return redirect('create')

    # Calculate duration and cost
    duration_hours = max((end_time - start_time).total_seconds() / 3600, 0)

    price_chart = {
        "Basement": {"min_2_hrs": 25, "max_24_hrs": 180},
        "Ground": {"min_2_hrs": 60, "max_24_hrs": 600},
        "First": {"min_2_hrs": 70, "max_24_hrs": 650},
        "Second": {"min_2_hrs": 110, "max_24_hrs": 950},
    }

    floor = slot.floor
    floor_name = floor.name
    rates = next((v for k, v in price_chart.items() if k.lower() in floor_name.lower()), {"min_2_hrs": 0, "max_24_hrs": 0})

    if duration_hours <= 2:
        cost = rates["min_2_hrs"]
    else:
        extra_hours = duration_hours - 2
        hourly_rate = (rates["max_24_hrs"] - rates["min_2_hrs"]) / 22
        cost = min(rates["min_2_hrs"] + extra_hours * hourly_rate, rates["max_24_hrs"])

    cost = round(cost, 2)

    # Create booking but don't mark slot as occupied yet
    booking = Booking.objects.create(
        owner_name=booking_data['owner_name'],
        vehicle_number=booking_data['vehicle_number'],
        mobile=booking_data['mobile'],
        email=booking_data['email'],
        category=slot.vehicle_category,
        floor=slot.floor,
        slot=slot,
        start_time=start_time,
        end_time=end_time,
        payment_status="pending"
    )

    # Create Razorpay order
    client = razorpay.Client(auth=("rzp_test_n0lhpmrEfeIhGJ", "UOrbXQGnsEc2dhB1IFg0zNWZ"))
    razorpay_order = client.order.create({
        "amount": int(cost * 100),
        "currency": "INR",
        "receipt": f"booking_{booking.id}",
        "payment_capture": 1
    })

    booking.razorpay_order_id = razorpay_order['id']
    booking.save()

    # Clean up session data
    del request.session['booking_data']

    context = {
        'booking': booking,
        'payment': razorpay_order,
        'amount': cost,
        'razorpay_key': "rzp_test_n0lhpmrEfeIhGJ"
    }

    return render(request, 'pay.html', context)

from django.core.mail import send_mail
from django.conf import settings

@csrf_exempt
def paymentSuccess(request):
    if request.method == "POST":
        payment_id = request.POST.get("razorpay_payment_id")
        order_id = request.POST.get("razorpay_order_id")

        booking = Booking.objects.filter(razorpay_order_id=order_id).first()

        if booking:
            booking.payment_status = "paid"
            booking.slot.status = "occupied"
            booking.slot.save()
            booking.save()

            # ✅ Send email confirmation
            try:
                send_mail(
                    subject='Booking Confirmation - Parking Slot',
                    message=(
                        f"Dear {booking.owner_name},\n\n"
                        f"Your booking has been confirmed.\n"
                        f"Details:\n"
                        f"Slot: {booking.slot.slot_number}\n"
                        f"Floor: {booking.floor.name}\n"
                        f"Start Time: {booking.start_time.strftime('%Y-%m-%d %H:%M')}\n"
                        f"End Time: {booking.end_time.strftime('%Y-%m-%d %H:%M')}\n"
                        f"Payment ID: {payment_id}\n\n"
                        f"Thank you for using our parking service!"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[booking.email],
                    fail_silently=False
                )
            except Exception as e:
                print("Email sending failed:", str(e))  # You can log this if needed

            context = {
                'payment_id': payment_id,
                'booking': booking,
            }

            return render(request, "success_pay.html", context)
        else:
            messages.error(request, "Invalid payment or booking not found.")
            return redirect('index')

    return redirect('index')

from django.utils import timezone
from .models import Booking, ParkingSlot

def release_expired_slots():
    now = timezone.now()

    # Find expired bookings (end_time < now) and slot still marked as 'occupied'
    expired_bookings = Booking.objects.filter(end_time__lt=now, slot__status='occupied')

    for booking in expired_bookings:
        slot = booking.slot
        slot.status = 'available'
        slot.save()
