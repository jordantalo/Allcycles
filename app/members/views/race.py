from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404

from ..utils import is_active_staff_or_admin
from ..models import Race, Rider, Staff, RacePresence

@user_passes_test(is_active_staff_or_admin, login_url='members:home_redirect')
@login_required
def create_race(request):

    if request.method == "POST":
        title = request.POST.get("title")
        category_type = request.POST.get("category_type")
        date = request.POST.get("date")
        is_dn_race = "dn_race" in request.POST

        selected_rider_ids = request.POST.getlist("riders")
        selected_staff_ids = request.POST.getlist("staff")

        race = Race.objects.create(
            title=title,
            date=date,
            location="",
            category_type=category_type,
            is_dn_race=is_dn_race,
        )

        race.riders.set(selected_rider_ids)
        race.staff_members.set(selected_staff_ids)

        return redirect("members:calendar")

    riders = Rider.objects.filter(is_active=True)
    staff = Staff.objects.all()

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
    }
    return (render(request, "members/save_results.html", context))

@user_passes_test(is_active_staff_or_admin, login_url='members:home_redirect')
@login_required
def edit_race(request, race_id):
    race = get_object_or_404(Race, id=race_id)
    riders = Rider.objects.filter(is_active=True)
    staff = Staff.objects.all()

    if request.method == "POST":
        selected_rider_ids = request.POST.getlist("riders")
        selected_staff_ids = request.POST.getlist("staff")
        race.riders.set(selected_rider_ids)
        race.staff_members.set(selected_staff_ids)
        race.title = request.POST.get('title')
        race.category_type = request.POST.get("category_type")
        race.is_dn_race = "dn_race" in request.POST
        race.date = request.POST.get("date")
        race.save()
        return redirect('members:calendar')

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
