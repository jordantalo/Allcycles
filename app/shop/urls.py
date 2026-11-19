from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'shop'

urlpatterns = [
    path("", views.shop, name="shop"),
    path("login/", views.shop_login, name="shop_login"),
    path("logout/", views.shop_logout, name="shop_logout"),
    path("recap/", views.recap, name="recap"),
    path("admin/login", views.admin_login, name="admin_login"),
    path("admin/logout", LogoutView.as_view(next_page='shop:admin_login'), name="admin_logout"),
    path("admin/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/campaign/create", views.create_campaign, name="create_campaign"),
    path("admin/<int:campaign_id>/export-adherents", views.export_adherents, name="export_adherents"),
    path("admin/<int:campaign_id>/export-articles", views.export_articles, name="export_articles"),
    path("admin/manage", views.manage, name="manage"),
    path("admin/manage/groups/<int:group_id>/update", views.update_group, name="update_group"),
]
