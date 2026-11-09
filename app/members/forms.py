from django.contrib.auth.models import User
from django import forms

from .models import Profile, Race, RacePresence


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
        fields = ['title', 'date', 'end_date', 'category_type', 'is_dn_race', 'riders', 'staff_members', 'type', 'num_stages']

    def clean(self):
        cleaned_data = super().clean()
        race_type = cleaned_data.get('type')
        start_date = cleaned_data.get('date')
        end_date = cleaned_data.get('end_date')
        num_stages = cleaned_data.get('num_stages')

        if (race_type != 'one_day'):

            if (not end_date):
                self.add_error('end_date', "Ce champ est obligatoire.")

            if (start_date and end_date and end_date <= start_date):
                self.add_error('end_date', "La date de fin ne peut pas être antérieure à la date de début.")

            if (not num_stages):
                self.add_error('num_stages', "Le nombre d'étape est obligatoire pour une course par étape.")

            if (num_stages < 2 or num_stages > 21):
                self.add_error('num_stages', "Minimum 2 étapes - maximum 21 étapes.")


        return cleaned_data

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            return title

        minor_words = {'le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'et', 'à', 'en', 'au', 'aux', 'pour', 'par', 'sur', 'dans'}
        words = title.split()
        formatted_words = []

        for i, word in enumerate(words):
            lower_word = word.lower()

            if i == 0 or lower_word not in minor_words:
                formatted_words.append(word.capitalize())
            else:
                formatted_words.append(lower_word)

        return " ".join(formatted_words)

class ResultForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.statuses = ['DNF', 'DNS', 'OTL', 'DSQ']
        self.race = kwargs.pop('race', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = RacePresence
        fields = ['positions_dict']

    def clean(self):
        self.cleaned_data = super().clean()
        positions = self.cleaned_data.get('positions_dict')

        if self.race and positions:

            if self.race.type == "one_day":
                self.check_one_day(positions)
            elif self.race.type == "stage":
                self.check_stage(positions)
            else:
               self.check_challenge(positions)

    def check_challenge(self, positions):
        for stage, position in positions.items():
            self.check_one_day({stage:position})

    def check_stage(self, positions):

        for stage, position in positions.items():
            self.check_one_day({stage:position})

        self.check_dup(positions)

    def check_dup(self, positions):

        count_status = 0
        for position in positions.values():

           for status in self.statuses:

              if status == position:
                 count_status += 1

        if (count_status > 1):
           self.add_error('positions_dict', "Sur une course par étape, un statut d'abandon (DNS, DSQ, DNF, OTL) ne peut apparaitre qu'une seule fois par coureur")


    def check_one_day(self, positions):

        position = next(iter(positions.values()))

        if not position:
            return

        if len(positions) > 1:
            self.add_error('positions_dict', "Un seul et unique résultat peut être entré pour une course d'un jour")
        elif not position.isdigit():
            self.check_status(position)
        else:
            position = int(position)
            self.check_position(position)


    def check_status(self, position):

        for status in self.statuses:
           if (position == status):
              return

        self.add_error('positions_dict', "Le status doit être un statut valide (DNS, DNF, OTL ou DSQ)")


    def check_position(self, position):

       if (position < 1 or position > 250):
          self.add_error('positions_dict', "La position du coureur doit être comprise entre 1 et 250")
