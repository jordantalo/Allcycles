from django.shortcuts import render
from .data import RIDERS_DN3, STAFF_DN3

# Create your views here.
def home(request):
	return render(request, "core/home.html")

def dn3(request):
	context = {
		'team_members': RIDERS_DN3,
		'team_staff': STAFF_DN3
	}
	return render(request, "core/dn3.html", context)

def young(request):
	return render(request, "core/young.html")
