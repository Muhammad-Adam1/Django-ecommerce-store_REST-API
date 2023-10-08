from django.contrib import admin

# Register your models here.
from . models import Order, OrderItem

admin.site.register(Order)
