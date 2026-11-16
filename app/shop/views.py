from django.shortcuts import render, redirect
from django.db import transaction
from django.utils import timezone
from django.contrib import messages

from .models import Article, Order, OrderItem, Campaign
from .forms import OrderItemForm, OrderForm
from .data import PASSWORDS
from .decorators import shop_manager_required

from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm

# Create your views here.
def shop_login(request):

    today = timezone.now().date()
    password_error = None
    identification_error = None
    order_id = None
    email = None
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

            order_id = request.POST.get("order_id")
            email = request.POST.get("email")

            order = get_order(order_id, email)

            if order:
                request.session["order_id"] = order.id
                return redirect("shop:recap")
            elif order_id and email:
                identification_error = "Le numéro de commande ou l'adresse e-mail est incorrect."
            else:
                return redirect("shop:shop")
        else:
            password_error = "Le mot de passe d'accès à la boutique est incorrect"

    context = {
        'password_error': password_error,
        'identification_error': identification_error,
        'is_shop_open': is_shop_open,
        'order_id': order_id,
        'email': email,
    }

    return render(request, "shop/shop_login.html", context)

def get_order(order_id, email):

    if not order_id.isdigit():
        return None

    order_id = int(order_id)

    email = email.lower()
    order = Order.objects.filter(pk=order_id).first()

    if order and order.email == email:
        return order
    else:
        return None

def shop(request):
    if not request.session.get("has_shop_access", False):
        return redirect("shop:shop_login")

    order = None
    order_id = request.session.get("order_id")
    if order_id:
        order = Order.objects.filter(pk=order_id).first()
        order_form = OrderForm(instance=order)
    else:
        order_form = OrderForm()

    articles = Article.objects.all().order_by('name')
    shop_group = request.session["shop_group"]

    if request.method == "POST":

        order_form = OrderForm(request.POST, instance=order)
        is_valid_shop = order_form.is_valid()
        is_valid_shop = check_shop_validity(request, articles, is_valid_shop, order)

        active_campaign = Campaign.objects.filter(is_active=True).first()
        if not active_campaign:
            return redirect('shop:shop_logout')

        if is_valid_shop:
            order = order_form.save(commit=False)
            order.campaign = active_campaign

            try:
                create_order(order, articles, shop_group)
                messages.success(request, "Votre pre-commande a bien ete enregistree")
                request.session["order_id"] = order.id
                return redirect("shop:recap")
            except Exception as e:
                messages.error(request, "Votre pre-commande n'a pas pu etre enregistree suite a une erreur technique !")
        else:
            messages.error(request, "Votre pre-commande n'a pas pu etre enregistree en raison d'une erreur de saisie !")
    elif order:
        for article in articles:
            order_item = None
            order_item = OrderItem.objects.filter(order=order, article=article).first()
            article.form = OrderItemForm(instance=order_item)

    for article in articles:
        if shop_group in article.package_config and article.package_config[shop_group] != 0:
            article.is_package_included = True
            article.quantity = article.package_config[shop_group]

    context = {
        "articles": articles,
        "order_form": order_form,
    }

    return render(request, "shop/shop.html", context)

def check_shop_validity(request, articles:list[Article], is_valid_shop, order):

    for article in articles:
        order_item = OrderItem.objects.filter(order=order, article=article).first()
        form = OrderItemForm(request.POST, instance=order_item, prefix=f'article_{article.id}')
        article.form = form

        if (not form.is_valid()):
            is_valid_shop = False

    return is_valid_shop

def create_order(order:Order, articles:list[Article], shop_group):

    with transaction.atomic():
        order.date = timezone.now()
        order.club_cost = 0
        order.rider_cost = 0
        order.total_cost = 0
        order.save()

        club_cost = 0
        rider_cost = 0

        for article in articles:
            form = article.form
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
    if not request.session.get("has_shop_access", False):
        return redirect("shop:shop_login")

    if not request.session["order_id"]:
        return redirect("shop:shop")

    order = Order.objects.get(pk=request.session["order_id"])
    print(order)

    context = {
         'order': order,
    }

    return render(request, "shop/recap.html", context)

def shop_logout(request):

    request.session["has_shop_access"] = False
    request.session["order_id"] = False
    return redirect("shop:shop_login")

def admin_login(request):

    form = AuthenticationForm()
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

            if user.groups.filter(name='shop_admin').exists() or user.is_superuser:
                login(request, user)
                return redirect('shop:admin_dashboard')
            else:
                form.add_error(None, "Ce compte n'a pas les droits pour gerer la boutique du club.")

    context = {
        'form': form,
    }

    return render(request, 'shop/admin_login.html', context)

@shop_manager_required
def admin_dashboard(request):
    return render(request, "shop/admin_dashboard.html")
