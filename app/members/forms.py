from django.contrib.auth.models import User
from django import forms

from .models import Profile, Race


class AvatarForm(forms.ModelForm):

  class Meta:
    model = Profile
    fields = ['avatar']

class UserBioForm(forms.ModelForm):

  class Meta:
    model = User
    fields = ['first_name', 'last_name']

class UserEmailForm(forms.ModelForm):

  class Meta:
    model = User
    fields = ['email']

class ProfilePhoneForm(forms.ModelForm):

  class Meta:
    model = Profile
    fields = ['phone']

class ProfilePrefForm(forms.ModelForm):

  class Meta:
    model = Profile
    fields = ['theme']

class RaceForm(forms.ModelForm):

    class Meta:
        model = Race
        fields = ['title', 'date', 'end_date', 'category_type', 'is_dn_race', 'riders', 'staff_members', 'is_stage_race', 'num_stages']

    def clean(self):
        cleaned_data = super().clean()
        is_stage_race = cleaned_data.get('is_stage_race')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        num_stages = cleaned_data.get('num_stages')

        if (is_stage_race):

            if (not end_date):
                self.add_error('end_date', "Une date de fin est obligatoire pour une course par étape.")

            if (start_date and end_date and end_date <= start_date):
                self.add_error('end_date', "La date de fin ne peut pas être antérieure à la date de début.")

            if (not num_stages):
                self.add_error('num_stages', "Le nombre d'étape est obligatoire pour une course par étape.")

        return cleaned_data




