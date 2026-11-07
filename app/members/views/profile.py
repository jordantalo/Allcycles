from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import redirect, render
from django.contrib import messages

from ..forms import AvatarForm, UserBioForm, UserEmailForm, ProfilePhoneForm, ProfilePrefForm

@login_required
def profile(request):

    password_form = PasswordChangeForm(user=request.user)

    if (request.method == 'POST'):

        form_type = request.POST.get("form_type")

        if (form_type == "bio_form"):
            form = UserBioForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, "Bio mise a jour avec succès")
                return (redirect('members:profile'))

        elif (form_type == "personal_info_form"):
            user_email_form = UserEmailForm(request.POST, request.FILES, instance=request.user)
            profile_phone_form = ProfilePhoneForm(request.POST, request.FILES, instance=request.user.profile)
            if (user_email_form.is_valid() and profile_phone_form.is_valid()):
                user_email_form.save()
                profile_phone_form.save()
                messages.success(request, "Vos informations personnelles ont été mises à jour avec succès.")
                return (redirect('members:profile'))

        elif (form_type == "avatar_form"):
            form = AvatarForm(request.POST, request.FILES, instance=request.user.profile)
            if form.is_valid():
                form.save()
                messages.success(request, "Votre avatar a été mise à jour avec succès.")
                return (redirect('members:profile'))

        elif (form_type == "pref_form"):
            pref_form = ProfilePrefForm(request.POST, request.FILES, instance=request.user.profile)
            if (pref_form.is_valid()):
                pref_form.save()
                messages.success(request, "Vos préférences personnelles ont été mises à jour avec succès.")
                return (redirect('members:profile'))

        elif (form_type == "password_change"):
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
