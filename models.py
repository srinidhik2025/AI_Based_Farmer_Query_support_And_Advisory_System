from django.db import models

class MarketPrice(models.Model):
    crop_name_en = models.CharField(max_length=100)
    crop_name_ta = models.CharField(max_length=100)
    price_per_quintal = models.IntegerField()
    trend = models.CharField(max_length=20) # e.g. "▲ +₹50" or "▼ -₹200"
    is_up = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.crop_name_en} / {self.crop_name_ta} - ₹{self.price_per_quintal}"

class GovernmentScheme(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    link_text = models.CharField(max_length=100, blank=True, null=True)
    link_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
