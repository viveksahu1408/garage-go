from django.urls import path
from . import views

urlpatterns = [

    path('about-us/', views.about_us, name='about_us'),
    path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('contact-us/', views.contact_us, name='contact_us'),

    # Auth
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Public pages
    path('', views.home_view, name='home'),
    path('marketplace/', views.marketplace_view, name='marketplace'),
    path('parts/', views.parts_view, name='parts'),
    
    # City selector
    path('set-city/', views.set_city, name='set_city'),
    
    # Bookings
    path('booking/create/', views.create_booking, name='create_booking'),
    
    # Dashboards
    path('dashboard/user/', views.user_dashboard, name='user_dashboard'),
    path('dashboard/mechanic/', views.mechanic_dashboard, name='mechanic_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    
    # Actions
    path('booking/<int:booking_id>/status/', views.update_booking_status, name='update_booking_status'),
    path('mechanic/<int:mechanic_id>/approve/', views.approve_mechanic, name='approve_mechanic'),
    path('car/<int:car_id>/approve/', views.approve_car, name='approve_car'),
    path('booking/<int:booking_id>/assign/', views.assign_booking, name='assign_booking'),
    path('order/<int:order_id>/status/', views.update_order_status, name='update_order_status'),
    path('part/add/', views.add_part, name='add_part'),
    
    # Marketplace
    path('car/sell/', views.sell_car, name='sell_car'),
    path('car/<int:car_id>/inquiry/', views.car_inquiry, name='car_inquiry'),
    path('car/<int:car_id>/', views.car_detail_view, name='car_detail'),

    # Parts
    path('part/<int:part_id>/order/', views.order_part, name='order_part'),
    path('car/status/<int:car_id>/', views.toggle_car_status, name='toggle_car_status'),
    path('part-request/status/<int:req_id>/', views.update_part_request_status, name='update_part_request_status'),

    path('booking/<int:booking_id>/accept-instant/', views.accept_booking_instant, name='accept_booking_instant'),
    path('booking/<int:booking_id>/feedback/', views.submit_booking_feedback, name='submit_booking_feedback'),

]