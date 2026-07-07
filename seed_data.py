import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'creative_hub.settings')
django.setup()

from core.models import MarketPrice, GovernmentScheme

# Clear existing
MarketPrice.objects.all().delete()
GovernmentScheme.objects.all().delete()

# Seed Market Price
MarketPrice.objects.create(crop_name_en='Paddy', crop_name_ta='நெல்', price_per_quintal=2200, trend='+₹50', is_up=True)
MarketPrice.objects.create(crop_name_en='Tomato', crop_name_ta='தக்காளி', price_per_quintal=1500, trend='-₹200', is_up=False)
MarketPrice.objects.create(crop_name_en='Cotton', crop_name_ta='பருத்தி', price_per_quintal=7100, trend='+₹100', is_up=True)

# Seed Schemes
GovernmentScheme.objects.create(
    name='PM-KISAN Samman Nidhi', 
    description='₹6,000 per year minimum income support.',
    link_text='Apply Here',
    link_url='#'
)
GovernmentScheme.objects.create(
    name='Uzhavar Sandhai Connect', 
    description='Direct market selling for farmers in Tamil Nadu without middlemen.',
    link_text='',
    link_url=''
)
GovernmentScheme.objects.create(
    name='Sub-Mission on Agricultural Mechanization (SMAM)', 
    description='Subsidies for buying tractors and farming machinery.',
    link_text='',
    link_url=''
)

print("Database successfully seeded.")
