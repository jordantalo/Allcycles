from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from ..utils import is_rider
from ..models import Race, RacePresence

@login_required
def calendar(request):
    today = timezone.now().date()
    curr_rider = getattr(request.user, 'rider', None)

     # Courses à venir (aujourd'hui ou dans le futur), triées de la plus proche à la plus lointaine
    next_races = list(Race.objects.filter(date__gte=today).order_by("date"))

    # Courses passées (avant aujourd'hui), triées de la plus récente à la plus ancienne
    past_races = list(Race.objects.filter(date__lt=today).order_by("-date"))

    if curr_rider:
        curr_rider_presences = {p.race_id: p.status for p in curr_rider.race_presences.all()}

    for race in next_races + past_races:
        rider_presences = { p.rider_id: p for p in race.presences.all() }
        race.rider_statuses = []

        if curr_rider:
            race.curr_rider_presence = curr_rider_presences.get(race.id)

        for rider in race.riders.all():
            presence_obj = rider_presences.get(rider.id)
            race.rider_statuses.append((rider, presence_obj))

    context = {
        "next_races": next_races,
        "past_races": past_races,
        "user": request.user,
    }

    return render(request, "members/calendar.html", context)

@user_passes_test(is_rider, login_url='members:home_redirect')
@login_required
def update_presence(request, race_id):

    if (request.method == 'POST'):
        race = get_object_or_404(Race, id=race_id)
        rider = request.user.rider
        status = request.POST.get('status')

        if (not rider):
            return (redirect('members:calendar'))

        RacePresence.objects.update_or_create(
            race=race,
            rider=rider,
            defaults={
                'status': status
            }
        )

    return (redirect('members:calendar'))
