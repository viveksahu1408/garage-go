from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom User with phone-based login"""
    
    ROLE_CHOICES = [
        ('admin', 'Supreme Admin'),
        ('mechanic', 'Mechanic'),
        ('user', 'Customer'),
    ]
    
    contact = models.CharField(max_length=15, unique=True, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    mechanic_status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Active', 'Active'), ('Rejected', 'Rejected')],
        default='Pending',
        blank=True
    )
    
    USERNAME_FIELD = 'contact'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.contact})"
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_mechanic(self):
        return self.role == 'mechanic'


class Mechanic(models.Model):
    """Mechanic/Workshop profile"""
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Active', 'Active'),
        ('Rejected', 'Rejected'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mechanic_profile')
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=15)
    shop_name = models.CharField(max_length=200)
    shop_photo = models.URLField(max_length=500, blank=True)
    certifications = models.JSONField(default=list, blank=True)
    id_card = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.shop_name} ({self.city})"
    
    class Meta:
        ordering = ['-created_at']


class Booking(models.Model):
    """Service booking"""
    
    STATUS_CHOICES = [
        ('Pending Assignment', 'Pending Assignment'),
        ('Assigned', 'Assigned'),
        ('Accepted', 'Accepted'),
        ('Work in Progress', 'Work in Progress'),
        ('Completed', 'Completed'),
        ('Rejected', 'Rejected'),
    ]
    
    customer_name = models.CharField(max_length=100)
    customer_contact = models.CharField(max_length=15)
    car_details = models.CharField(max_length=200)
    service_category = models.CharField(max_length=100)
    service_subtype = models.CharField(max_length=300)
    price = models.CharField(max_length=100, default='Quote basis')
    city = models.CharField(max_length=50)
    booking_time = models.DateTimeField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending Assignment')
    assigned_mechanic = models.ForeignKey(
        Mechanic, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"#{self.id} - {self.service_category} for {self.customer_name}"
    
    class Meta:
        ordering = ['-created_at']


class MarketplaceCar(models.Model):
    """Used car listing"""
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Sold', 'Sold'),
    ]
    
    FUEL_CHOICES = [
        ('Petrol', 'Petrol'),
        ('Diesel', 'Diesel'),
        ('CNG', 'CNG'),
        ('EV', 'EV'),
    ]
    
    TRANSMISSION_CHOICES = [
        ('Manual', 'Manual'),
        ('Automatic', 'Automatic'),
    ]
    
    # Seller info
    seller_name = models.CharField(max_length=100)
    seller_contact = models.CharField(max_length=15)
    seller_alt_contact = models.CharField(max_length=15, blank=True)
    seller_city = models.CharField(max_length=50, blank=True)
    seller_address = models.TextField(blank=True)
    
    # Car details
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    variant = models.CharField(max_length=100, blank=True)
    year = models.PositiveIntegerField()
    reg_year = models.PositiveIntegerField(null=True, blank=True)
    kms = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, default='Petrol')
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES, default='Manual')
    owners_count = models.PositiveIntegerField(default=1)
    reg_state_rto = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    
    # Insurance & Legal
    insurance_status = models.CharField(max_length=20, choices=[('Active', 'Active'), ('Expired', 'Expired')], default='Expired')
    insurance_type = models.CharField(max_length=100, blank=True)
    insurance_expiry = models.DateField(null=True, blank=True)
    noc_status = models.CharField(max_length=20, choices=[('Yes', 'Yes'), ('No', 'No')], default='Yes')
    fitness_validity = models.CharField(max_length=100, blank=True)
    accidental_history = models.CharField(max_length=20, choices=[('Yes', 'Yes'), ('No', 'No')], default='No')
    accidental_details = models.TextField(blank=True)
    
    # --- MEDIA FIELDS MODIFIED FOR FILE UPLOADS ---
    # Har car ke liye multiple photos aur videos save karne ke liye hum related child models banayenge
    # Isse data clean rahega aur filter/looping me dikkat nahi aayegi.
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    commission_earned = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    listed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listed_cars', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.make} {self.model} ({self.year}) - ₹{self.price}"
    
    class Meta:
        ordering = ['-created_at']


# 📸 MULTIPLE PHOTOS KE LIYE NEW TABLE
class CarPhoto(models.Model):
    car = models.ForeignKey(MarketplaceCar, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='cars/photos/')

    def __str__(self):
        return f"Photo for {self.car.make} {self.car.model}"


# 🎥 MULTIPLE VIDEOS KE LIYE NEW TABLE
class CarVideo(models.Model):
    car = models.ForeignKey(MarketplaceCar, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='cars/videos/')

    def __str__(self):
        return f"Video for {self.car.make} {self.car.model}"


class AutoPart(models.Model):
    """Auto spare parts - Pure Dynamic Image Support ke sath"""
    
    TYPE_CHOICES = [
        ('New', 'New'),
        ('Used', 'Used'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True) # Description optional kar diya
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='New')
    compatibility = models.CharField(max_length=200, default='Universal')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    # photo_url ko humne YAHA SE HATA DIYA HAI (Kyoki ab files direct upload hongi)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - ₹{self.price}"
    
    class Meta:
        ordering = ['-created_at']


class AutoPartPhoto(models.Model):
    """AutoPart ke liye multiple images upload karne ke liye (Max 4 handle views me hoga)"""
    part = models.ForeignKey(AutoPart, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='parts/')


class PartOrder(models.Model):
    """Spare parts UPI payment orders tracking"""
    
    STATUS_CHOICES = [
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
    ]
    
    buyer_name = models.CharField(max_length=100)
    buyer_contact = models.CharField(max_length=15)
    buyer_address = models.TextField()
    part = models.ForeignKey(AutoPart, on_delete=models.CASCADE, related_name='orders')
    part_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # NEW FIELDS: For UPI / QR Tracking instead of COD
    transaction_id = models.CharField(
        max_length=100, 
        default='', 
        help_text="UPI Transaction ID / UTR"
    )    
    payment_status = models.CharField(max_length=20, default='Pending_Verification') # Admin verifies UPI transaction

    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Processing')
    
    def __str__(self):
        return f"Order #{self.id} - {self.part_name} x{self.quantity}"
    
    class Meta:
        ordering = ['-order_date']



class Inquiry(models.Model):
    """Car buyer inquiry/lead"""
    
    car = models.ForeignKey(MarketplaceCar, on_delete=models.CASCADE, related_name='inquiries')
    car_title = models.CharField(max_length=200)
    buyer_name = models.CharField(max_length=100)
    buyer_contact = models.CharField(max_length=15)
    buyer_message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Inquiry for {self.car_title} by {self.buyer_name}"
    
    class Meta:
        ordering = ['-date']


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="E.g., Car Wash, Car Services, Breakdown Services")
    slug = models.SlugField(max_length=100, unique=True, help_text="E.g., car_wash, car_services (Lowercase without spaces)")
    description = models.TextField(blank=True, null=True, help_text="Optional overall category description")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Service Categories"


class ServicePackage(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='packages')
    name = models.CharField(max_length=150, help_text="E.g., Top Wash, General Checkup")
    price = models.IntegerField(default=0, help_text="Put 0 if it is a custom quote base")
    time_duration = models.CharField(max_length=50, blank=True, null=True, help_text="E.g., 30 mins, 4 hours")
    description = models.TextField(help_text="Detailed description of what is included")
    is_custom_quote = models.BooleanField(default=False, help_text="Check this for Dent/Paint or Towing where price varies work-to-work")

    def __str__(self):
        return f"{self.category.name} - {self.name}"     

    
class City(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Shahar ya kasbe ka naam (e.g., Katni, Jabalpur)")
    is_active = models.BooleanField(default=True, help_text="Kya is shahar me service live rakhni hai?")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Cities"

