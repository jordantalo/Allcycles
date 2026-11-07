from django.contrib import admin
from .models import Race, Rider, Staff, Profile, RacePresence

# Register your models here.
admin.site.register(Race)
admin.site.register(Rider)
admin.site.register(Staff)
admin.site.register(Profile)
admin.site.register(RacePresence)
