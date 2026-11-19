from django.contrib import admin
from .models import Article, OrderItem, Order, Campaign, PackageGroup, GroupeArticleConfig

# Register your models here.
admin.site.register(Article)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Campaign)
admin.site.register(PackageGroup)
admin.site.register(GroupeArticleConfig)

