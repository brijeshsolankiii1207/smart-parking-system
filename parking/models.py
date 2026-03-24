from django.db import models

# Floor model
class Floor(models.Model):
    name = models.CharField(max_length=50)  # Example: Basement, Ground, 1st Floor
    total_slots = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


# Vehicle Category (Bike, Small Car, Big Car, etc.)
class VehicleCategory(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


# Parking Slots
class ParkingSlot(models.Model):
    STATUS_CHOICES = (
        ("available", "Available"),
        ("occupied", "Occupied"),
    )

    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name="slots")
    vehicle_category = models.ForeignKey(VehicleCategory, on_delete=models.CASCADE)
    slot_number = models.CharField(max_length=20)  # Example: B1-01, G-05
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")

    def __str__(self):
        return f"{self.slot_number} ({self.vehicle_category.name})"

# Booking
class Booking(models.Model):
    
    owner_name = models.CharField(max_length=251)
    vehicle_number = models.CharField(max_length=251)
    mobile = models.CharField(max_length=251)
    email = models.EmailField(max_length=200)
    category = models.ForeignKey(VehicleCategory, on_delete=models.CASCADE)
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE)
    slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_status = models.CharField(max_length=20, default='pending')  # 'pending', 'paid'
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Booking {self.id} - {self.owner_name}"

