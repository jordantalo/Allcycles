from django.contrib import admin
from .models import Article, OrderItem, Order

# Register your models here.
admin.site.register(Article)
admin.site.register(Order)
admin.site.register(OrderItem)
