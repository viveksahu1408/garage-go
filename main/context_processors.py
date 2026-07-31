from .models import City

def global_cities(request):
    """
    Yeh function database se saari active cities fetch karke
    poore app/templates me global 'cities' variable available karata hai.
    """
    db_cities = City.objects.filter(is_active=True).order_by('name')
    return {
        'cities': db_cities,
    }