from django.contrib import admin
from .models import Race, Rider, Staff

# Register your models here.
admin.site.register(Race)
admin.site.register(Rider)
admin.site.register(Staff)