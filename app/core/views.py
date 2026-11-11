from django.shortcuts import render, redirect
from django.conf import settings
from django.utils import timezone
from .models import Article
from .data import RIDERS_DN3, STAFF_DN3, CLUB_BOARD, PASSWORDS, PACKAGES

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

    today = timezone.now().date()
    error = None
    is_shop_open = True

    today_tuple = (today.month, today.day)
    opening_date = (11, 1)
    ending_date = (12, 15)

    if opening_date > today_tuple or ending_date < today_tuple:
          is_shop_open = False

    elif request.method == 'POST':
        password = request.POST.get("password")

        if password in PASSWORDS.keys():
            request.session["has_shop_access"] = True
            request.session["shop_group"] = PASSWORDS[password]
            return redirect("shop")
        else:
            error = "Le mot de passe d'accès à la boutique est incorrect"

    context = {
        'error': error,
        'is_shop_open': is_shop_open,
    }

    return render(request, "core/shop_login.html", context)

def shop(request):
    if not request.session["has_shop_access"]:
        return redirect("shop_login")

    articles = Article.objects.all()
    shop_group = request.session["shop_group"]
    for article in articles:
        if shop_group in article.package_config and article.package_config[shop_group] != 0:
            article.is_package_included = True
            article.quantity = article.package_config[shop_group]

    context = {
        'articles': articles,
    }

    return render(request, "core/shop.html", context)

def shop_logout(request):

    request.session["has_shop_access"] = False
    return redirect("shop_login")
