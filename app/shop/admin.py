from django.contrib import admin
from .models import Article, OrderItem, Order, Campaign

# Register your models here.
admin.site.register(Article)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Campaign)
