from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.utils import timezone
from decimal import Decimal
from django.db.models import Avg, Count, Prefetch
from .models import Mechanic

from .models import (
    User, Mechanic, Booking, MarketplaceCar, 
    AutoPart, PartOrder, Inquiry, ServiceCategory, City,
    CarPhoto, CarVideo, AutoPartPhoto, PartRequest
)


# ============================================================
# HELPERS
# ============================================================

def about_us(request):
    return render(request, 'main/about_us.html')

def terms_and_conditions(request):
    return render(request, 'main/terms.html')

def privacy_policy(request):
    return render(request, 'main/privacy.html')

def contact_us(request):
    if request.method == 'POST':
        messages.success(request, "Aapka message mil gaya hai! Hum jald hi aapse sampark karenge.")
    return render(request, 'main/contact_us.html')

def get_active_city(request):
    return request.session.get('garagego_city', 'Jabalpur')

def set_active_city(request, city):
    request.session['garagego_city'] = city


def role_required(allowed_roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Pehle login karein!')
                return redirect('login')
            if request.user.role not in allowed_roles:
                messages.error(request, 'Permission nahi hai!')
                return redirect('home')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ============================================================
# AUTH
# ============================================================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        contact = request.POST.get('contact')
        password = request.POST.get('password')
        
        user = authenticate(request, contact=contact, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Swagat hai, {user.first_name}!')
            
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'mechanic':
                return redirect('mechanic_dashboard')
            else:
                return redirect('user_dashboard')
        else:
            messages.error(request, 'Galat Mobile ya Password!')
    
    return render(request, 'main/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        password = request.POST.get('password')
        role = request.POST.get('role', 'user')
        
        if User.objects.filter(contact=contact).exists():
            messages.error(request, 'Ye number pehle se registered hai!')
            return render(request, 'main/register.html')
        
        name_parts = name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        user = User.objects.create_user(
            username=contact,
            contact=contact,
            first_name=first_name,
            last_name=last_name,
            password=password,
            role=role
        )
        
        if role == 'mechanic':
            shop_name = request.POST.get('shop_name')
            city = request.POST.get('city', 'Jabalpur')
            id_card = request.POST.get('id_card')
            certifications = request.POST.get('certifications', '')
            
            if not shop_name or not city or not id_card:
                messages.error(request, 'Mechanic ke liye Shop, City, ID Card jaruri hain!')
                user.delete()
                return render(request, 'main/register.html')
            
            Mechanic.objects.create(
                user=user,
                name=name,
                contact=contact,
                shop_name=shop_name,
                city=city,
                id_card=id_card,
                certifications=[certifications] if certifications else ['ITI Certificate'],
                status='Pending'
            )
            user.mechanic_status = 'Pending'
            user.save()
        
        messages.success(request, 'Registration successful! Ab login karein.')
        return redirect('login')
    
    return render(request, 'main/register.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Logout ho gaye!')
    return redirect('home')


# ============================================================
# PUBLIC PAGES
# ============================================================

def home_view(request):
    active_city = get_active_city(request)
    db_cities = City.objects.filter(is_active=True).order_by('name')
    all_categories = ServiceCategory.objects.prefetch_related('packages').all()
    
    return render(request, 'main/home.html', {
        'categories': all_categories,
        'cities': db_cities,
        'active_city': active_city,
    })


def marketplace_view(request):
    brand_filter = request.GET.get('brand', '')
    city_filter = request.GET.get('city', '')
    max_price = request.GET.get('max_price', '')
    
    cars = MarketplaceCar.objects.filter(status='Approved').prefetch_related('photos', 'videos')
    
    if brand_filter:
        cars = cars.filter(make__icontains=brand_filter)
    if city_filter:
        cars = cars.filter(seller_city__iexact=city_filter)
    if max_price:
        try:
            cars = cars.filter(price__lte=float(max_price))
        except ValueError:
            pass
            
    db_cities = City.objects.filter(is_active=True).order_by('name')
    
    return render(request, 'main/marketplace.html', {
        'cars': cars,
        'brand_filter': brand_filter,
        'city_filter': city_filter,
        'max_price': max_price,
        'cities': db_cities,
    })


def parts_view(request):
    search_query = request.GET.get('q', '')
    part_type = request.GET.get('type', '')
    
    parts = AutoPart.objects.all()

    if search_query:
        parts = parts.filter(
            Q(name__icontains=search_query) | 
            Q(compatibility__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    if part_type:
        parts = parts.filter(type=part_type)

    if request.method == 'POST' and 'request_part_submit' in request.POST:
        customer_name = request.POST.get('customer_name')
        customer_contact = request.POST.get('customer_contact')
        car_make_model = request.POST.get('car_make_model')
        part_name = request.POST.get('part_name')
        part_type_req = request.POST.get('part_type', 'Any')
        description = request.POST.get('description', '')
        sample_photo = request.FILES.get('sample_photo')

        PartRequest.objects.create(
            user=request.user if request.user.is_authenticated else None,
            customer_name=customer_name,
            customer_contact=customer_contact,
            car_make_model=car_make_model,
            part_name=part_name,
            part_type=part_type_req,
            description=description,
            sample_photo=sample_photo
        )
        messages.success(request, "Aapki Part Request submit ho gayi hai! Humari team aapse contact karegi.")
        return redirect('parts')

    return render(request, 'main/parts.html', {
        'parts': parts,
        'search_query': search_query,
        'part_type': part_type
    })


# ============================================================
# BOOKINGS (OLA/UBER DISPATCH & FEEDBACK FLOW)
# ============================================================

@login_required
def create_booking(request):
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        customer_contact = request.POST.get('customer_contact')
        car_details = request.POST.get('car_details')
        service_category = request.POST.get('service_category')
        service_subtype = request.POST.get('service_subtype')
        price = request.POST.get('price', 'Quote basis')
        city = request.POST.get('city')
        booking_time = request.POST.get('booking_time')
        
        Booking.objects.create(
            customer_name=customer_name,
            customer_contact=customer_contact,
            car_details=car_details,
            service_category=service_category,
            service_subtype=service_subtype or service_category,
            price=price,
            city=city,
            booking_time=booking_time,
            status='Broadcasting' # ⚡ Ola/Uber style direct broadcast to city mechanics
        )
        
        messages.success(request, 'Service booking request broadcast ho gayi hai! City ke mechanics alert receive kar rahe hain.')
        return redirect('user_dashboard')
    
    return redirect('home')


# ⚡ OLA/UBER STYLE: MECHANIC INSTANT ACCEPT JOB
@login_required
@role_required(['mechanic'])
def accept_booking_instant(request, booking_id):
    mechanic = get_object_or_404(Mechanic, user=request.user)
    
    if mechanic.status != 'Active':
        messages.error(request, 'Aapka mechanic account active nahi hai!')
        return redirect('mechanic_dashboard')
        
    booking = get_object_or_404(Booking, id=booking_id)
    
    if booking.city.lower() != mechanic.city.lower():
        messages.error(request, f'Ye booking {booking.city} ki hai, aap {mechanic.city} me hain!')
        return redirect('mechanic_dashboard')

    # Lock logic: Jo pehle click kare execution lock
    if booking.status != 'Broadcasting' or booking.assigned_mechanic is not None:
        messages.error(request, 'Ye job pehle hi kisi dusre mechanic dwara accept ki ja chuki hai!')
        return redirect('mechanic_dashboard')

    booking.assigned_mechanic = mechanic
    booking.status = 'Assigned'
    booking.save()

    messages.success(request, f'Badhai ho! Booking #{booking.id} aapko assign ho gayi hai.')
    return redirect('mechanic_dashboard')


# ⭐ CUSTOMER FEEDBACK & STAR RATING SUBMIT
@login_required
def submit_booking_feedback(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer_contact=request.user.contact)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        feedback = request.POST.get('feedback')
        
        if booking.status == 'Completed':
            booking.rating = int(rating)
            booking.feedback = feedback
            booking.feedback_date = timezone.now()
            booking.save()
            messages.success(request, 'Thank you! Aapka feedback aur rating record kar liya gaya hai.')
        else:
            messages.error(request, 'Service complete hone ke baad hi feedback de sakte hain!')
            
    return redirect('user_dashboard')


# ============================================================
# DASHBOARDS
# ============================================================

@login_required
def user_dashboard(request):
    # Customer dashboard me assigned mechanic details optimize karke load karein
    bookings = Booking.objects.filter(customer_contact=request.user.contact).select_related('assigned_mechanic')
    
    my_cars = MarketplaceCar.objects.filter(listed_by=request.user).prefetch_related('photos')
    user_orders = PartOrder.objects.filter(buyer_contact=request.user.contact).order_by('-order_date')

    context = {
        'bookings': bookings,
        'my_cars': my_cars,
        'active_orders': [o for o in user_orders if o.status in ['Processing', 'Shipped']],
        'past_orders': [o for o in user_orders if o.status == 'Delivered'],
        'all_orders_count': len(user_orders)
    }
    return render(request, 'main/user_dashboard.html', context)


@login_required
@role_required(['mechanic'])
def mechanic_dashboard(request):
    try:
        mechanic = Mechanic.objects.get(user=request.user)
    except Mechanic.DoesNotExist:
        messages.error(request, 'Mechanic profile not found!')
        return redirect('home')
    
    if mechanic.status != 'Active':
        return render(request, 'main/mechanic_dashboard.html', {
            'mechanic': mechanic,
            'pending': True
        })
    
    # 🚨 Mechanic ki City ke saare OPEN / BROADCASTING Jobs (Ola/Uber Radar Alert)
    broadcast_bookings = Booking.objects.filter(
        city__iexact=mechanic.city, 
        status='Broadcasting'
    ).order_by('-created_at')

    # Already assigned bookings to this mechanic
    assigned_bookings = Booking.objects.filter(assigned_mechanic=mechanic)
    
    my_cars = MarketplaceCar.objects.filter(listed_by=request.user).prefetch_related('photos')
    mechanic_orders = PartOrder.objects.filter(buyer_contact=request.user.contact).order_by('-order_date')

    context = {
        'mechanic': mechanic,
        'broadcast_bookings': broadcast_bookings, # Live Job Radar alerts
        'bookings': assigned_bookings,
        'my_cars': my_cars,
        'active_city': get_active_city(request),
        'active_orders': [o for o in mechanic_orders if o.status in ['Processing', 'Shipped']],
        'past_orders': [o for o in mechanic_orders if o.status == 'Delivered'],
        'all_orders_count': len(mechanic_orders)
    }
    return render(request, 'main/mechanic_dashboard.html', context)


@login_required
@role_required(['admin'])
def admin_dashboard(request):
    total_commission = MarketplaceCar.objects.filter(status='Sold').aggregate(
        total=Sum('commission_earned')
    )['total'] or 0
    
    pending_mechanics = Mechanic.objects.filter(status='Pending').count()
    pending_cars = MarketplaceCar.objects.filter(status='Pending').count()
    active_bookings = Booking.objects.exclude(status__in=['Completed', 'Rejected', 'Cancelled']).count()
    total_orders = PartOrder.objects.count()
    
    cars_with_details = MarketplaceCar.objects.select_related('listed_by').prefetch_related('photos', 'videos').all()

    # FIX: reviews ki jagah bookings field use kiya gaya hai
    mechanics = Mechanic.objects.annotate(
        avg_rating=Avg('bookings__rating'),
        total_reviews=Count('bookings__rating')
    ).prefetch_related('bookings')
    
    context = {
        'stats': {
            'total_commission': total_commission,
            'pending_mechanics': pending_mechanics,
            'pending_cars': pending_cars,
            'active_bookings': active_bookings,
            'total_orders': total_orders,
        },
        'bookings': Booking.objects.select_related('assigned_mechanic').all(),
        'cars': cars_with_details,
        'orders': PartOrder.objects.all(),
        'inquiries': Inquiry.objects.all(),
        'parts': AutoPart.objects.all(),
        'part_requests': PartRequest.objects.all(),
        'mechanics': mechanics,
    }
    return render(request, 'main/admin_dashboard.html', context)


# ============================================================
# ACTIONS (UPDATED FOR ADMIN OVERRIDE & RE-ASSIGNMENT)
# ============================================================

@login_required
def update_booking_status(request, booking_id):
    if request.user.role != 'mechanic':
        messages.error(request, 'Access Denied!')
        return redirect('home')
    
    booking = get_object_or_404(Booking, id=booking_id)
    mechanic = get_object_or_404(Mechanic, user=request.user)
    
    if booking.assigned_mechanic != mechanic:
        messages.error(request, 'Sirf apne assigned kaam ka status badal sakte hain!')
        return redirect('mechanic_dashboard')
    
    status = request.POST.get('status')
    if status in ['Assigned', 'Work in Progress', 'Completed', 'Cancelled']:
        booking.status = status
        booking.save()
        messages.success(request, f'Booking status changed to {status}!')
    
    return redirect('mechanic_dashboard')


@login_required
@role_required(['admin'])
def assign_booking(request, booking_id):
    """Admin Override: Forcefully assign or re-assign a mechanic to any booking"""
    booking = get_object_or_404(Booking, id=booking_id)
    mechanic_id = request.POST.get('mechanic_id')
    
    # Unassign Option
    if not mechanic_id or mechanic_id == 'none':
        booking.assigned_mechanic = None
        booking.status = 'Broadcasting'
        booking.save()
        messages.success(request, 'Booking unassigned & broadcasted back to city mechanics!')
        return redirect('admin_dashboard')

    mechanic = get_object_or_404(Mechanic, id=mechanic_id)
    
    if mechanic.status != 'Active':
        messages.error(request, 'Inactive mechanic ko assign nahi kar sakte!')
        return redirect('admin_dashboard')
    
    if booking.city.lower() != mechanic.city.lower():
        messages.error(request, f'Mechanic {mechanic.city} me hai, booking {booking.city} ki hai!')
        return redirect('admin_dashboard')
    
    booking.assigned_mechanic = mechanic
    booking.status = 'Assigned'
    booking.save()
    messages.success(request, f'Booking #{booking.id} successfully mechanic "{mechanic.name}" ko override/assign ho gayi!')
    return redirect('admin_dashboard')


@login_required
@role_required(['admin'])
def approve_mechanic(request, mechanic_id):
    mechanic = get_object_or_404(Mechanic, id=mechanic_id)
    status = request.POST.get('status')
    
    if status in ['Active', 'Rejected']:
        mechanic.status = status
        mechanic.save()
        mechanic.user.mechanic_status = status
        mechanic.user.save()
        messages.success(request, f'Mechanic status changed to {status}!')
    
    return redirect('admin_dashboard')


@login_required
@role_required(['admin'])
def approve_car(request, car_id):
    car = get_object_or_404(MarketplaceCar, id=car_id)
    status = request.POST.get('status')
    
    if status in ['Approved', 'Rejected', 'Sold']:
        car.status = status
        if status == 'Sold':
            car.commission_earned = car.price * Decimal('0.02')
        car.save()
        messages.success(request, f'Car status changed to {status}!')
    
    return redirect('admin_dashboard')


@login_required
@role_required(['admin'])
def update_order_status(request, order_id):
    order = get_object_or_404(PartOrder, id=order_id)
    status = request.POST.get('status')
    
    if status in ['Processing', 'Shipped', 'Delivered']:
        order.status = status
        order.save()
        messages.success(request, f'Order status: {status}')
    
    return redirect('admin_dashboard')


@login_required
@role_required(['admin'])
def add_part(request):
    if request.method == 'POST':
        part = AutoPart.objects.create(
            name=request.POST.get('name'),
            description=request.POST.get('description', ''),
            type=request.POST.get('type', 'New'),
            compatibility=request.POST.get('compatibility', 'Universal'),
            price=request.POST.get('price'),
            quantity=request.POST.get('quantity'),
        )
        
        images = request.FILES.getlist('part_photos')
        for img in images[:4]: 
            AutoPartPhoto.objects.create(part=part, image=img)
            
        messages.success(request, 'Naya part and images add ho gayi hain!')
    
    return redirect('admin_dashboard')


@login_required
@role_required(['admin'])
def update_part_request_status(request, req_id):
    part_req = get_object_or_404(PartRequest, id=req_id)
    status = request.POST.get('status')
    if status in ['Pending', 'Arranged', 'Unavailable']:
        part_req.status = status
        part_req.save()
        messages.success(request, f"Request status changed to {status}")
    return redirect('admin_dashboard')


# ============================================================
# MARKETPLACE & PARTS
# ============================================================

@login_required
def sell_car(request):
    if request.method == 'POST':
        photos = request.FILES.getlist('photos')
        videos = request.FILES.getlist('videos')

        if len(photos) > 10:
            messages.error(request, '10 se zyada photos upload nahi kar sakte!')
            return redirect('marketplace')
        if len(videos) > 4:
            messages.error(request, '4 se zyada videos upload nahi kar sakte!')
            return redirect('marketplace')

        car = MarketplaceCar.objects.create(
            seller_name=request.POST.get('seller_name', request.user.first_name),
            seller_contact=request.POST.get('seller_contact', request.user.contact),
            seller_alt_contact=request.POST.get('seller_alt_contact', ''),
            seller_city=request.POST.get('seller_city', ''),
            seller_address=request.POST.get('seller_address', ''),
            make=request.POST.get('make'),
            model=request.POST.get('model'),
            variant=request.POST.get('variant', ''),
            year=request.POST.get('year', 2018),
            reg_year=request.POST.get('reg_year') or None,
            kms=request.POST.get('kms', 0),
            price=request.POST.get('price', 0),
            fuel_type=request.POST.get('fuel_type', 'Petrol'),
            transmission=request.POST.get('transmission', 'Manual'),
            owners_count=request.POST.get('owners_count', 1),
            reg_state_rto=request.POST.get('reg_state_rto', ''),
            description=request.POST.get('description', ''),
            insurance_status=request.POST.get('insurance_status', 'Expired'),
            insurance_type=request.POST.get('insurance_type', ''),
            insurance_expiry=request.POST.get('insurance_expiry') or None,
            noc_status=request.POST.get('noc_status', 'Yes'),
            fitness_validity=request.POST.get('fitness_validity', ''),
            accidental_history=request.POST.get('accidental_history', 'No'),
            accidental_details=request.POST.get('accidental_details', ''),
            listed_by=request.user,
            status='Pending'
        )

        for img in photos:
            CarPhoto.objects.create(car=car, image=img)

        for vid in videos:
            CarVideo.objects.create(car=car, video=vid)

        messages.success(request, 'Car listing submit ho gayi! Verification ke baad live hogi.')
        return redirect('marketplace')
    
    return redirect('marketplace')


@login_required
def car_inquiry(request, car_id):
    car = get_object_or_404(MarketplaceCar, id=car_id)
    
    if request.method == 'POST':
        Inquiry.objects.create(
            car=car,
            car_title=f"{car.make} {car.model} ({car.year})",
            buyer_name=request.POST.get('buyer_name', request.user.first_name),
            buyer_contact=request.POST.get('buyer_contact', request.user.contact),
            buyer_message=request.POST.get('buyer_message', 'Interested in buying.')
        )
        messages.success(request, 'Inquiry bhej di gayi!')
    
    return redirect('marketplace')


@login_required
def order_part(request, part_id):
    part = get_object_or_404(AutoPart, id=part_id)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        buyer_address = request.POST.get('buyer_address')
        transaction_id = request.POST.get('transaction_id')
        
        if part.quantity < quantity:
            messages.error(request, f'Sirf {part.quantity} pieces stock me hain!')
            return redirect('parts')
        
        part.quantity -= quantity
        part.save()
        
        PartOrder.objects.create(
            buyer_name=request.user.first_name if request.user.first_name else request.user.username,
            buyer_contact=getattr(request.user, 'contact', 'N/A'), 
            buyer_address=buyer_address,
            part=part,
            part_name=part.name,
            quantity=quantity,
            total_price=part.price * quantity,
            transaction_id=transaction_id,
            payment_status='Pending_Verification'
        )
        
        messages.success(request, 'Order request received! Payment verify hote hi process shuru ho jayega.')
    
    return redirect('parts')


def set_city(request):
    city = request.POST.get('city', 'Jabalpur')
    set_active_city(request, city)
    messages.success(request, f'City updated to {city}!')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def car_detail_view(request, car_id):
    car = get_object_or_404(MarketplaceCar.objects.prefetch_related('photos', 'videos'), id=car_id)
    db_cities = City.objects.filter(is_active=True).order_by('name')
    
    return render(request, 'main/car_detail.html', {
        'car': car,
        'cities': db_cities
    })


@login_required
def toggle_car_status(request, car_id):
    car = get_object_or_404(MarketplaceCar, id=car_id, listed_by=request.user)
    action = request.POST.get('action')
    
    if action == 'sold':
        car.status = 'Sold'
        car.commission_earned = car.price * Decimal('0.02') 
        car.save()
        messages.success(request, 'Car status "Sold" mark ho gayi hai.')
    elif action == 'cancel':
        car.status = 'Rejected'
        car.save()
        messages.success(request, 'Car listing cancel kar di gayi hai!')
        
    if request.user.role == 'mechanic':
        return redirect('mechanic_dashboard')
    return redirect('user_dashboard')