from django.contrib.auth.decorators import user_passes_test

def shop_manager_required(view_func):
    """
    Vérifie que l'utilisateur est connecté et appartient au groupe 'shop_admin'
    (ou est superutilisateur). Sinon, redirige vers le login du back-office boutique.
    """
    def check_user(user):
        if not user.is_authenticated:
            return False
        return user.groups.filter(name='shop_admin').exists() or user.is_superuser

    return user_passes_test(check_user, login_url='shop:admin_login')(view_func)
