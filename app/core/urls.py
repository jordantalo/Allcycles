from django.urls import path
from . import views

urlpatterns = [
	path("", views.home, name="home"),
	path("dn3/", views.dn3, name="dn3"),
	path("jeunes/", views.young, name="young"),
	path("organisations/", views.events, name="events"),
	path("club/", views.club, name="club"),
	path("partenaires/", views.partner, name="partner"),
	
]
