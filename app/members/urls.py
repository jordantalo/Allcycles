# members/urls.py
from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    path('', views.home_redirect, name='home_redirect'),
    path('dashboard/rider/', views.rider_dashboard, name='rider_dashboard'),
    path('dashboard/staff/', views.staff_dashboard, name='staff_dashboard'),
    path('calendar/', views.calendar, name='calendar'),
    path('race/create', views.create_race, name='create_race'),
    path('race/<int:race_id>/edit/', views.edit_race, name='edit_race'),
    path('race/<int:race_id>/delete/', views.delete_race, name='delete_race'),
    path('race/presence/<int:race_id>/update', views.update_presence, name="update_presence"),
    path('race/results/<int:race_id>/save', views.save_results, name="save_results"),
    path('profile/', views.profile, name='profile'),
]
