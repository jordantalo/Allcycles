from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404

from ..utils import is_active_staff_or_admin
from ..models import Race, Rider, Staff, RacePresence
from ..forms import RaceForm, ResultForm
from django.contrib import messages

@user_passes_test(is_active_staff_or_admin, login_url='members:home_redirect')
@login_required
def create_race(request):

    race_form = RaceForm(initial={'is_dn_race': True})
    if request.method == "POST":
        print ('post: ', request.POST)
        race_form = RaceForm(request.POST, request.FILES)
        if race_form.is_valid():
            race_form.save()
            messages.success(request, "La course a été créée avec succès.")
            return redirect("members:calendar")

    riders = Rider.objects.filter(is_active=True)
    staff = Staff.objects.filter(is_active=True)

    context = {
        "user": request.user,
        "riders": riders,
        "staff": staff,
        "form": race_form,
    }

    return render(request, "members/create_race.html", context)

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
            messages.success(request, "La course a été modifiée avec succès.")
            return redirect("members:calendar")
    else:
        race_form = RaceForm(instance=race)

    context = {
        "form": race_form,
        "riders": riders,
        "staff": staff,
        "race": race,
    }
    return (render(request, 'members/edit_race.html', context))

@user_passes_test(is_active_staff_or_admin, login_url='members:home_redirect')
@login_required
def delete_race(request, race_id):
    race = get_object_or_404(Race, id=race_id)

    if (request.method == 'POST'):
        race.delete()
        messages.success(request, "La course a été supprimée avec succès.")

    return (redirect('members:calendar'))

@user_passes_test(is_active_staff_or_admin, login_url='members:home_redirect')
@login_required
def save_results(request, race_id):
    race = get_object_or_404(Race, id=race_id)

    if request.method == 'POST':

        race.results_entered = True
        race.save()
        error = False

        for rider in race.riders.all():

            positions_dict = {}
            positions = request.POST.getlist(f'position_{rider.id}')

            for index, position in enumerate(positions):

                if len(positions) == 0:
                    continue

                elif index == len(positions) - 1 and len(positions) != 1:
                    positions_dict['G'] = position.upper()

                else:
                    positions_dict[index + 1] = position.upper()

            if not positions_dict:
                continue

            presence, created = RacePresence.objects.get_or_create(
                rider=rider,
                race=race
            )

            form = ResultForm(
                data={'positions_dict': positions_dict},
                instance=presence,
                race=race,
            )

            if form.is_valid():
                form.save()
            else:
                error = True
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{rider.user.first_name} {rider.user.last_name} - {error}")

        if (not error):
            messages.success(request, "Enregistrement des resultats réussi !")
            return redirect("members:calendar")


    rider_presences = { p.rider_id:p for p in race.presences.all() }
    stages = [str(i) for i in range(1, race.num_stages + 1)]
    if race.type != "one_day":
        stages.append('G')
    global_res = []
    for stage in stages:
        riders_res = []
        for rider in race.riders.all():
            rider_presence = rider_presences.get(rider.id)
            res = None
            if rider_presence:
                res = rider_presence.positions_dict.get(stage)
            riders_res.append((rider, res))
        global_res.append((stage, riders_res))

    context = {
        'race':race,
        'results': global_res,
    }
    return (render(request, "members/save_results.html", context))


