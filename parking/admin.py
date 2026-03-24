from django.contrib import admin
from .models import Floor, VehicleCategory, ParkingSlot, Booking

admin.site.register(Floor)
admin.site.register(VehicleCategory)
admin.site.register(ParkingSlot)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'owner_name',
        'vehicle_number',
        'mobile',
        'email',
        'category',
        'floor',
        'slot',
        'start_time',
        'end_time',
        'created_at',
        'updated_at'
    ]
