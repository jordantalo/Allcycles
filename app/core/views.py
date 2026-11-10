from django.shortcuts import render, redirect
from django.conf import settings
from .data import RIDERS_DN3, STAFF_DN3, CLUB_BOARD, PASSWORDS, PACKAGE_DN3

# Create your views here.
def home(request):
	context = {
		'club_email': settings.CLUB_CONTACT_EMAIL
	}
	return render(request, "core/home.html", context)

def dn3(request):
	context = {
		'team_members': RIDERS_DN3,
		'team_staff': STAFF_DN3
	}
	return render(request, "core/dn3.html", context)

def young(request):
	return render(request, "core/young.html")

def events(request):
	return render(request, "core/events.html")

def club(request):
	context = {
		'board_members': CLUB_BOARD,
	}
	return render(request, "core/club.html", context)

def partner(request):
	return render(request, "core/partner.html")

def legal(request):
	context = {
		'club_email': settings.CLUB_CONTACT_EMAIL
	}
	return render(request, "core/legal.html", context)

def shop_login(request):

    error = None

    if request.method == 'POST':
        password = request.POST.get("password")

        if password in PASSWORDS.keys():
            request.session["has_shop_access"] = True
            request.session["shop_group"] = PASSWORDS[password]
            return redirect("shop")
        else:
            error = "Le mot de passe d'accès à la boutique est incorrect"

    context = {
		'error': error,
    }

    return render(request, "core/shop_login.html", context)

def shop(request):
	return render(request, "core/shop.html")
