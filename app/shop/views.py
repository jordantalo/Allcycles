from django.shortcuts import render, redirect
from django.db import transaction
from django.utils import timezone
from django.contrib import messages
from django.db.models import F, Sum

from .models import Article, Order, OrderItem, Campaign, PackageGroup, GroupeArticleConfig
from .forms import OrderItemForm, OrderForm, CampaignForm, PackageGroupForm, GroupArticleConfigForm
from .data import PASSWORDS
from .decorators import shop_manager_required

from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm

import csv
from django.http import HttpResponse

# Create your views here.
def shop_login(request):

    today = timezone.now().date()
    password_error = None
    identification_error = None
    order_id = None
    email = None
    is_shop_open = False

    active_campaign = Campaign.objects.filter(is_active=True).first()
    if (active_campaign):
        today_tuple = (today.month, today.day)
        opening_date = (active_campaign.start_date.month, active_campaign.start_date.day)
        ending_date = (active_campaign.end_date.month, active_campaign.end_date.day)

        if opening_date <= today_tuple and ending_date >= today_tuple:
            is_shop_open = True

    if request.method == 'POST':
        password = request.POST.get("password")

        if password in PASSWORDS.keys():
            print("bien entree")
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
            if form.cleaned_data.get('quantity') == 0:
                continue
            order_item:OrderItem = form.save(commit=False)
            order_item.order = order
            order_item.article = article
            order_item.article_name = article.name
            order_item.unit_price = article.price
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
    campaigns = Campaign.objects.all().order_by('start_date')
    selected_campaign = campaigns.filter(is_active=True).first()

    if request.method == 'POST':
        campaign_id = request.POST.get("selected_campaign")
        request.session['selected_campaign_id'] = campaign_id
        return (redirect('shop:admin_dashboard'))


    campaign_id = request.session.get('selected_campaign_id')
    if campaign_id:
        selected_campaign = Campaign.objects.filter(pk=campaign_id).first()
        request.session['selected_campaign_id'] = False

    if selected_campaign:
        add_campaign_context(selected_campaign)

    context = {
        'campaigns': campaigns,
        'selected_campaign': selected_campaign,

    }
    return render(request, "shop/admin_dashboard.html", context)

def add_campaign_context(selected_campaign):
    total = 0
    total_club = 0
    num_orders = 0
    for order in selected_campaign.orders.all():
        total += order.total_cost
        total_club += order.club_cost
        num_orders += 1

    selected_campaign.total_cost = total
    selected_campaign.num_orders = num_orders
    selected_campaign.club_cost = total_club

    inventory_stats = OrderItem.objects.filter(order__campaign=selected_campaign) \
    .values('article_name', 'size', 'unit_price') \
    .annotate(
        total_quantity=Sum('quantity'),
        total_price=Sum(F('quantity') * F('unit_price'))
    )

    ARTICLE_LABELS = dict(Article.ARTICLE_CHOICES)

    for row in inventory_stats:
        tech_name = row['article_name']
        pretty_name = ARTICLE_LABELS.get(tech_name, tech_name)
        row['article_name'] = pretty_name
        row['size'] = row['size'].upper()

    selected_campaign.articles = inventory_stats


@shop_manager_required
def create_campaign(request):
    form = CampaignForm()

    if request.method == 'POST':
        form = CampaignForm(request.POST)

        if form.is_valid():
            new_campaign = form.save(commit=False)
            new_campaign.is_active = True
            new_campaign.save()
            return redirect("shop:admin_dashboard")


    context = {
        'form': form,
    }
    return render(request, "shop/create_campaign.html", context)

@shop_manager_required
def export_adherents(request, campaign_id):

    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="export-adherents.csv"'},
    )

    writer = csv.writer(response)

    orders = Order.objects.filter(campaign=campaign_id) \
        .values('id', 'email', 'last_name', 'first_name', 'total_cost', 'club_cost', 'rider_cost')

    articles = OrderItem.objects.filter(order__campaign=campaign_id).distinct() \
        .values('article_name', 'article_id')

    titles = ['Email', 'Nom', 'Prenom', 'Cout_total', 'Cout_club', 'Cout_adherent']
    articles_titles = []

    for article in articles:
        articles_titles.append(f"Taille_{article.get('article_name')}")
        articles_titles.append(f"Quantite_{article.get('article_name')}")

    titles.extend(articles_titles)
    writer.writerow(titles)

    for order in orders:
        row = [order.get('email'), order.get('last_name'), order.get('first_name'), order.get('total_cost'), order.get('club_cost'), order.get('rider_cost')]

        order_id = order.get('id')
        order_items = OrderItem.objects.filter(order=order_id)

        for article in articles:
            article_id = article.get('article_id')
            item = order_items.filter(article=article_id).first()

            if item:
                row.append(item.size)
                row.append(item.quantity)
            else:
                row.extend(['', ''])

        writer.writerow(row)
        row = []

    return response

@shop_manager_required
def export_articles(request, campaign_id):

    response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="export-articles.csv"'},
        )

    writer = csv.writer(response)
    inventory_stats = get_inventory_stats(campaign_id)

    writer.writerow(["Nom de l'article", "Taille", "Quantite", "Prix unitaire", "Total"])

    total = 0
    for inventory_row in inventory_stats:
        row = []
        row.append(inventory_row.get('article_name'))
        row.append(inventory_row.get('size'))
        row.append(inventory_row.get('total_quantity'))
        row.append(inventory_row.get('unit_price'))
        total_price = inventory_row.get('total_price')
        total += total_price
        row.append(total_price)
        writer.writerow(row)

    writer.writerow(["Total", '', '', '', total])

    return response

def get_inventory_stats(campaign_id):
    inventory_stats = OrderItem.objects.filter(order__campaign=campaign_id) \
        .values('article_name', 'size', 'unit_price') \
        .annotate(
            total_quantity=Sum('quantity'),
            total_price=Sum(F('quantity') * F('unit_price'))
    )

    return inventory_stats

def manage(request):

    articles = Article.objects.all()
    groups = PackageGroup.objects.all()


    context = {
        'articles': articles,
        'groups': groups,
    }

    return render(request, "shop/manage.html", context)

def update_group(request, group_id):

    group = PackageGroup.objects.filter(pk=group_id).first()
    articles = Article.objects.all()
    group_form = PackageGroupForm(instance=group)

    if request.method == 'POST':
        print(request.POST)
        group_form = PackageGroupForm(request.POST, instance=group)
        is_valid_group = group_form.is_valid()
        is_valid_group = check_package_validity(request, articles, group, is_valid_group)

        if is_valid_group:
            save_group(articles, group_form)
            return redirect('shop:manage')

    else:
        prepare_context(group, articles)

    context = {
        'form': group_form,
        'articles': articles,
    }

    return render(request, "shop/update_group.html", context)

def check_package_validity(request, articles, group, is_valid):

    for article in articles:
        item = GroupeArticleConfig.objects.filter(article=article, group=group).first()
        article.form = GroupArticleConfigForm(request.POST, instance=item, prefix=f"{article.id}")
        if not article.form.is_valid():
            is_valid = False

    return is_valid

def save_group(articles, form_group):

    group = form_group.save()

    for article in articles:
        if article.form.cleaned_data.get('quantity') == 0:
            continue
        item = article.form.save(commit=False)
        item.article = article
        item.group = group
        item.save()

def prepare_context(group, articles):

    for article in articles:
        article.form = GroupArticleConfigForm()
        for item in group.package_items.all():
            if item.article.id == article.id:
                article.form = GroupArticleConfigForm(instance=item)
                continue
