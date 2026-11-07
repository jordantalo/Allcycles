from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404

from ..utils import is_active_staff_or_admin
from ..models import Race, Rider, Staff, RacePresence
from ..forms import RaceForm

@user_passes_test(is_active_staff_or_admin, login_url='members:home_redirect')
@login_required
def create_race(request):

    if request.method == "POST":
        race_form = RaceForm(request.POST, request.FILES)
        if race_form.is_valid():
            race_form.save()
            return redirect("members:calendar")

    riders = Rider.objects.filter(is_active=True)
    staff = Staff.objects.filter(is_active=True)

    context = {
        "user": request.user,
        "riders": riders,
        "staff": staff,
    }

    return render(request, "members/create_race.html", context)

@user_passes_test(is_active_staff_or_admin, login_url='members:home_redirect')
@login_required
def save_results(request, race_id):
    race = get_object_or_404(Race, id=race_id)

    if request.method == 'POST':
        race.results_entered = True
        race.save()

        for rider in race.riders.all():

            finisher_status = request.POST.get(f'finisher_status_{ rider.id }')
            position = request.POST.get(f'position_{ rider.id }')

            if position != '':
                defaults = {
                    'finisher_status': finisher_status,
                    'position': int(position),
                }
            else:
                defaults = {
                    'finisher_status': finisher_status,
                }

            RacePresence.objects.update_or_create(
                race=race,
                rider=rider,
                defaults=defaults
            )

        return (redirect('members:calendar'))

    rider_presences = { p.rider_id:p for p in race.presences.all() }
    race.rider_presences = []
    for rider in race.riders.all():
        race.rider_presences.append((rider, rider_presences.get(rider.id)))

    context = {
        'race':race,
        'stages_range': range(1, race.num_stages + 1)
    }
    return (render(request, "members/save_results.html", context))

@user_passes_test(is_active_staff_or_admin, login_url='members:home_redirect')
@login_required
def edit_race(request, race_id):
    race = get_object_or_404(Race, id=race_id)
    riders = Rider.objects.filter(is_active=True)
    staff = Staff.objects.filter(is_active=True)

    if request.method == "POST":
        race_form = RaceForm(request.POST, request.FILES, instance=race)
        if race_form.is_valid():
            race_form.save()
            return redirect("members:calendar")

    context = {
        "race": race,
        "riders": riders,
        "staff": staff,
    }
    return (render(request, 'members/edit_race.html', context))

@user_passes_test(is_active_staff_or_admin, login_url='members:home_redirect')
@login_required
def delete_race(request, race_id):
    race = get_object_or_404(Race, id=race_id)

    if (request.method == 'POST'):
        race.delete()

    return (redirect('members:calendar'))
