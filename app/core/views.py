from django.shortcuts import render, redirect
from django.db import transaction
from django.conf import settings
import traceback
from django.utils import timezone
from .models import Article, Order, OrderItem
from .forms import OrderItemForm, OrderForm
from django.contrib import messages
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

    order_form = OrderForm()

    articles = Article.objects.all()
    shop_group = request.session["shop_group"]

    if request.method == "POST":

        print(request.POST)

        order_form = OrderForm(request.POST)
        is_valid_shop = order_form.is_valid()
        is_valid_shop = check_shop_validity(request, articles, is_valid_shop)

        if is_valid_shop:
            order = order_form.save(commit=False)

            try:
                create_order(request, order, articles, shop_group)
                messages.success(request, "Votre pre-commande a bien ete enregistree")
                return redirect("recap")
            except Exception as e:
                print(f"erreur: {e}")
                traceback.print_exc()
                messages.error(request, "Votre pre-commande n'a pas pu etre enregistree suite a une erreur technique !")
        else:
            messages.error(request, "Votre pre-commande n'a pas pu etre enregistree en raison d'une erreur de saisie !")

    for article in articles:
        if shop_group in article.package_config and article.package_config[shop_group] != 0:
            article.is_package_included = True
            article.quantity = article.package_config[shop_group]

    context = {
        "articles": articles,
        "order_form": order_form,
    }

    return render(request, "core/shop.html", context)

def check_shop_validity(request, articles:list[Article], is_valid_shop):

    for article in articles:
        form = OrderItemForm(request.POST, prefix=f'article_{article.id}')
        article.form = form

        if (not form.is_valid()):
            is_valid_shop = False

    return is_valid_shop

def create_order(request, order:Order, articles:list[Article], shop_group):

    with transaction.atomic():
        order.date = timezone.now()
        order.club_cost = 0
        order.rider_cost = 0
        order.total_cost = 0
        order.save()

        club_cost = 0
        rider_cost = 0

        for article in articles:
            form = OrderItemForm(request.POST, prefix=f'article_{article.id}')
            order_item:OrderItem = form.save(commit=False)
            order_item.order = order
            order_item.article = article
            order_item.save()

            package_qty = None
            package_qty = article.package_config.get(shop_group, 0)

            qty = form.cleaned_data['quantity']
            price = article.price
            club_cost += min(qty, package_qty) * price
            rider_cost += max(0, qty - package_qty) * price

        order.rider_cost = rider_cost
        order.club_cost = club_cost
        order.total_cost = rider_cost + club_cost
        order.save()

def recap(request):
    if not request.session["has_shop_access"]:
        return redirect("shop_login")

    request.session["has_shop_access"] = False
    return render(request, "core/recap.html")

def shop_logout(request):

    request.session["has_shop_access"] = False
    return redirect("shop_login")


