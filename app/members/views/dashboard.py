from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.utils import timezone

from ..utils import is_rider, get_stats_info, get_team_res, get_team_stats, is_active_staff_or_admin
from ..models import RacePresence, Race, Rider

@login_required
def home_redirect(request):

    if hasattr(request.user, 'rider') and request.user.rider:
        return redirect("members:rider_dashboard")

    return redirect("members:staff_dashboard")

@user_passes_test(is_rider, login_url='members:home_redirect')
@login_required
def rider_dashboard(request):

    presences = RacePresence.objects.filter(rider=request.user.rider).exclude(positions={}).order_by('race__date')
    stats_info = []
    res_by_season = []
    seasons = []

    if presences:
        prev_year = presences.first().race.date.year
        season_res = []

        for presence in presences:
            current_year = presence.race.date.year

            if (current_year != prev_year):
                res_by_season.append((prev_year, season_res))

                stats_info.append((prev_year, get_stats_info(season_res)))
                season_res = []
                seasons.append(prev_year)
                prev_year = current_year

            season_res.append(presence)

        res_by_season.append((current_year, season_res))
        stats_info.append((current_year, get_stats_info(season_res)))
        seasons.append(current_year)
        seasons.sort(reverse=True)

    next_race = None
    today = timezone.now().date()
    next_race = Race.objects.filter(
        riders=request.user.rider,
        date__gte=today,
    ).order_by('date').first()

    presence = None

    if next_race and next_race.presences:
        presence = next_race.presences.filter(rider=request.user.rider).first()
        print('presence:', presence)
        next_race.curr_rider_presence = presence

    context = {
        'next_race': next_race,
        'res_by_season': res_by_season,
        'seasons': seasons,
        'stats_info': stats_info,
    }

    return render(request, 'members/rider_dashboard.html', context)


@user_passes_test(is_active_staff_or_admin, login_url='members:home_redirect')
@login_required
def staff_dashboard(request):
    today = timezone.now().date()

    races = Race.objects.all().filter(date__lt=today).order_by('-date')
    prev_year = races.first().date.year
    team_res_by_season = []
    seasons = []
    stats_info =[]
    season_res = {}

    for race in races:
        curr_year = race.date.year

        if prev_year != curr_year:
            count_races = races.filter(date__year=prev_year).count()
            team_res_by_season.append((prev_year, get_team_res(season_res)))
            stats_info.append((prev_year, get_team_stats(season_res, count_races)))
            seasons.append(prev_year)
            prev_year = curr_year
            season_res = {}

        for presence in race.presences.all():

            if (presence.rider_id not in season_res):
                season_res[presence.rider_id] = []
            season_res[presence.rider_id].append(presence)

    team_res_by_season.append((curr_year, get_team_res(season_res)))
    print ('test pour voir si ca calcul')
    print (get_team_stats(season_res, count_races))
    count_races = races.filter(date__year=curr_year).count()
    stats_info.append((curr_year, get_team_stats(season_res, count_races)))
    seasons.append(curr_year)

    next_race = None
    last_race = None


    next_race = Race.objects.filter(
        date__gte=today,
    ).order_by('date').first()

    last_race = Race.objects.filter(
        date__lt=today,
    ).order_by('-date').first()

    context = {
        'next_race': next_race,
        'last_race': last_race,
        'team_res_by_season': team_res_by_season,
        'stats_info': stats_info,
        'seasons': seasons,
    }

    return render(request, 'members/staff_dashboard.html', context)
