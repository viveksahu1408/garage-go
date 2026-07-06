from django.core.management.base import BaseCommand
from main.models import User, Mechanic, Booking, MarketplaceCar, AutoPart, PartOrder, Inquiry


class Command(BaseCommand):
    help = 'Seed database with demo data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')

        # Create Users
        admin_user, _ = User.objects.get_or_create(
            contact='9999999999',
            defaults={
                'username': '9999999999',
                'first_name': 'Supreme',
                'last_name': 'Admin',
                'role': 'admin',
                'mechanic_status': 'Active'
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()

        mech_user1, _ = User.objects.get_or_create(
            contact='9876543210',
            defaults={
                'username': '9876543210',
                'first_name': 'Rajesh',
                'last_name': 'Kumar',
                'role': 'mechanic',
                'mechanic_status': 'Active'
            }
        )
        mech_user1.set_password('123')
        mech_user1.save()

        mech_user2, _ = User.objects.get_or_create(
            contact='8765432109',
            defaults={
                'username': '8765432109',
                'first_name': 'Sunil',
                'last_name': 'Sharma',
                'role': 'mechanic',
                'mechanic_status': 'Pending'
            }
        )
        mech_user2.set_password('123')
        mech_user2.save()

        cust_user, _ = User.objects.get_or_create(
            contact='9001122334',
            defaults={
                'username': '9001122334',
                'first_name': 'Ramesh',
                'last_name': 'Verma',
                'role': 'user'
            }
        )
        cust_user.set_password('123')
        cust_user.save()

        # Create Mechanics
        mech1, _ = Mechanic.objects.get_or_create(
            contact='9876543210',
            defaults={
                'user': mech_user1,
                'name': 'Rajesh Kumar',
                'shop_name': 'Rajesh Car Care',
                'shop_photo': 'https://images.unsplash.com/photo-1517524206127-48bbd363f3d7?auto=format&fit=crop&q=80&w=600',
                'certifications': ['ITI Motor Mechanic Certificate', 'GST Registration Copy'],
                'id_card': 'Aadhaar Card: 1234-5678-9012',
                'city': 'Jabalpur',
                'status': 'Active'
            }
        )

        mech2, _ = Mechanic.objects.get_or_create(
            contact='8765432109',
            defaults={
                'user': mech_user2,
                'name': 'Sunil Sharma',
                'shop_name': 'Sharma Auto Repairs',
                'shop_photo': 'https://images.unsplash.com/photo-1486006920555-c77dce18193b?auto=format&fit=crop&q=80&w=600',
                'certifications': ['Experience Letter 5 years'],
                'id_card': 'Driving License: MP-20-Y-2018',
                'city': 'Katni',
                'status': 'Pending'
            }
        )

        # Create Bookings
        Booking.objects.get_or_create(
            id=1,
            defaults={
                'customer_name': 'Ramesh Verma',
                'customer_contact': '9001122334',
                'car_details': 'Maruti Suzuki Swift (Petrol, 2018)',
                'service_category': 'Car Wash',
                'service_subtype': 'Full Wash (₹300)',
                'price': '300',
                'city': 'Jabalpur',
                'booking_time': '2026-07-10T10:00',
                'status': 'Completed',
                'assigned_mechanic': mech1
            }
        )

        Booking.objects.get_or_create(
            id=2,
            defaults={
                'customer_name': 'Amit Patel',
                'customer_contact': '9112233445',
                'car_details': 'Hyundai i20 (Diesel, 2019)',
                'service_category': 'Break Down Services',
                'service_subtype': 'Battery Tochan (₹500)',
                'price': '500',
                'city': 'Jabalpur',
                'booking_time': '2026-07-12T14:30',
                'status': 'Pending Assignment',
                'assigned_mechanic': None
            }
        )

        # Create Cars
        MarketplaceCar.objects.get_or_create(
            id=1,
            defaults={
                'seller_name': 'Vijay Tiwari',
                'seller_contact': '9334455667',
                'seller_city': 'Jabalpur',
                'make': 'Maruti Suzuki',
                'model': 'Swift LXI',
                'year': 2017,
                'kms': 65000,
                'price': 380000,
                'description': 'Badiya condition mein hai, family car, accha mileage deti hai. All original paint, local Jabalpur registration.',
                'photo_url': 'https://images.unsplash.com/photo-1549399542-7e3f8b79c341?auto=format&fit=crop&q=80&w=600',
                'video_link': 'https://youtube.com/watch?v=example1',
                'status': 'Approved',
                'listed_by': cust_user
            }
        )

        MarketplaceCar.objects.get_or_create(
            id=2,
            defaults={
                'seller_name': 'Suresh Gupta',
                'seller_contact': '9445566778',
                'seller_city': 'Jabalpur',
                'make': 'Hyundai',
                'model': 'Creta SX',
                'year': 2019,
                'kms': 42000,
                'price': 920000,
                'description': 'Single owner, automatic gearbox, bilkul fresh condition. Full service history available.',
                'photo_url': 'https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&q=80&w=600',
                'video_link': 'https://youtube.com/watch?v=example2',
                'status': 'Approved',
                'listed_by': cust_user
            }
        )

        MarketplaceCar.objects.get_or_create(
            id=3,
            defaults={
                'seller_name': 'Kuldeep Singh',
                'seller_contact': '9556677889',
                'seller_city': 'Katni',
                'make': 'Honda',
                'model': 'Amaze S Petrol',
                'year': 2018,
                'kms': 51000,
                'price': 460000,
                'description': 'Kuch scratches hain bumper pe, par engine aur suspension mast hai.',
                'photo_url': 'https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?auto=format&fit=crop&q=80&w=600',
                'status': 'Pending',
                'listed_by': cust_user
            }
        )

        # Create Parts
        AutoPart.objects.get_or_create(
            id=1,
            defaults={
                'name': 'Maruti Swift Headlight Assembly',
                'description': 'Original headlight assembly, genuine spare part for Swift 2018-2022 models.',
                'type': 'New',
                'compatibility': 'Maruti Suzuki Swift (2018-2022)',
                'price': 1850,
                'quantity': 10,
                'photo_url': 'https://images.unsplash.com/photo-1508962914676-134849a727f0?auto=format&fit=crop&q=80&w=600'
            }
        )

        AutoPart.objects.get_or_create(
            id=2,
            defaults={
                'name': 'Creta Left Side Mirror (ORVM)',
                'description': 'Slightly used side mirror, original paint, electrically adjustable.',
                'type': 'Used',
                'compatibility': 'Hyundai Creta (2015-2019)',
                'price': 800,
                'quantity': 3,
                'photo_url': 'https://images.unsplash.com/photo-1617814076367-b759c7d7e738?auto=format&fit=crop&q=80&w=600'
            }
        )

        AutoPart.objects.get_or_create(
            id=3,
            defaults={
                'name': 'Exide Car Battery - 44AH',
                'description': 'Exide Mileage brand battery, 44AH power rating. 36 months warranty.',
                'type': 'New',
                'compatibility': 'Swift, Dzire, i20, Amaze, WagonR',
                'price': 4500,
                'quantity': 8,
                'photo_url': 'https://images.unsplash.com/photo-1620843105151-51833f443b7f?auto=format&fit=crop&q=80&w=600'
            }
        )

        AutoPart.objects.get_or_create(
            id=4,
            defaults={
                'name': 'Castrol Magnatec Engine Oil 4L',
                'description': 'Castrol Magnatec 5W-30 full synthetic engine oil.',
                'type': 'New',
                'compatibility': 'Universal (All Petrol & Diesel Cars)',
                'price': 2200,
                'quantity': 15,
                'photo_url': 'https://images.unsplash.com/photo-1611244419377-b0a72189986d?auto=format&fit=crop&q=80&w=600'
            }
        )

        AutoPart.objects.get_or_create(
            id=5,
            defaults={
                'name': 'Alloy Wheels Set R15 (4 pieces)',
                'description': 'Gently used alloy wheel set of 4, five-spoke gunmetal finish.',
                'type': 'Used',
                'compatibility': 'Swift, i20, Dzire, Baleno, Amaze',
                'price': 12000,
                'quantity': 1,
                'photo_url': 'https://images.unsplash.com/photo-1580273916550-e323be2ae537?auto=format&fit=crop&q=80&w=600'
            }
        )

        # Create Orders
        PartOrder.objects.get_or_create(
            id=1,
            defaults={
                'buyer_name': 'Vijay Patel',
                'buyer_contact': '9000111222',
                'buyer_address': '12, Civil Lines, Katni',
                'part_id': 1,
                'part_name': 'Maruti Swift Headlight Assembly',
                'quantity': 2,
                'total_price': 3700,
                'status': 'Processing'
            }
        )

        # Create Inquiry
        Inquiry.objects.get_or_create(
            id=1,
            defaults={
                'car_id': 1,
                'car_title': 'Maruti Suzuki Swift LXI (2017)',
                'buyer_name': 'Subhash Sen',
                'buyer_contact': '9888777666',
                'buyer_message': 'Gadi test drive karna hai, Jabalpur mein kahan dekh sakte hain? Please call back.'
            }
        )

        self.stdout.write(self.style.SUCCESS('✅ Seed data loaded successfully!'))