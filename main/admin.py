from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Mechanic, Booking, MarketplaceCar, AutoPart, PartOrder, Inquiry
from .models import ServiceCategory, ServicePackage,City



@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['contact', 'username', 'first_name', 'last_name', 'role', 'mechanic_status', 'is_active']
    list_filter = ['role', 'mechanic_status', 'is_active']
    search_fields = ['contact', 'username', 'first_name', 'last_name']
    
    fieldsets = UserAdmin.fieldsets + (
        ('GarageGo Info', {'fields': ('contact', 'role', 'mechanic_status')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('GarageGo Info', {'fields': ('contact', 'role', 'mechanic_status')}),
    )


@admin.register(Mechanic)
class MechanicAdmin(admin.ModelAdmin):
    list_display = ['name', 'shop_name', 'city', 'status', 'created_at']
    list_filter = ['status', 'city']
    search_fields = ['name', 'shop_name', 'contact']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'service_category', 'city', 'status', 'booking_time', 'assigned_mechanic']
    list_filter = ['status', 'city', 'service_category']
    search_fields = ['customer_name', 'customer_contact', 'car_details']
    date_hierarchy = 'booking_time'


@admin.register(MarketplaceCar)
class MarketplaceCarAdmin(admin.ModelAdmin):
    list_display = ['make', 'model', 'year', 'price', 'status', 'seller_city', 'created_at']
    list_filter = ['status', 'fuel_type', 'transmission', 'seller_city']
    search_fields = ['make', 'model', 'seller_name', 'seller_contact']


@admin.register(AutoPart)
class AutoPartAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'price', 'quantity', 'compatibility']
    list_filter = ['type']
    search_fields = ['name', 'compatibility']


@admin.register(PartOrder)
class PartOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer_name', 'part_name', 'quantity', 'total_price', 'status', 'order_date']
    list_filter = ['status']
    search_fields = ['buyer_name', 'buyer_contact', 'part_name']


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ['car_title', 'buyer_name', 'buyer_contact', 'date']
    search_fields = ['buyer_name', 'buyer_contact', 'car_title']

class ServicePackageInline(admin.TabularInline):
    model = ServicePackage
    extra = 1

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ServicePackageInline]

@admin.register(ServicePackage)
class ServicePackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'time_duration', 'is_custom_quote')
    list_filter = ('category', 'is_custom_quote')
    search_fields = ('name', 'description')    

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)    