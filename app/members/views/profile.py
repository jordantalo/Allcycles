from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import redirect, render
from django.contrib import messages

from ..forms import AvatarForm

@login_required
def profile(request):

    password_form = PasswordChangeForm(user=request.user)

    if (request.method == 'POST'):

        if ("first_name" in request.POST):
            request.user.first_name = request.POST.get("first_name").lower()
            request.user.last_name = request.POST.get("last_name").lower()
            request.user.save()
            return (redirect('members:profile'))

        elif ("user_email" in request.POST):
            request.user.email = request.POST.get("user_email")
            request.user.profile.phone = request.POST.get("user_phone")
            request.user.save()
            request.user.profile.save()
            return (redirect('members:profile'))

        elif ("avatar" in request.FILES):
            form = AvatarForm(request.POST, request.FILES, instance=request.user.profile)

            if form.is_valid():
                form.save()
                return (redirect('members:profile'))

        elif ("theme_pref" in request.POST):
            request.user.profile.theme = request.POST.get("theme_pref")
            request.user.profile.save()
            return (redirect('members:profile'))

        elif ("update_password" in request.POST):
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Votre mot de passe a été modifié avec succès !")
                return (redirect('members:profile'))

    context = {
        'password_form': password_form,
    }

    return render(request, "members/profile.html", context)
