from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Race, Rider, Staff, RacePresence
from .utils import *
from .forms import AvatarForm

# Create your views here.
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

@login_required
def home_redirect(request):

    if hasattr(request.user, 'rider') and request.user.rider:
        return redirect("members:rider_dashboard")

    return redirect("members:staff_dashboard")

@user_passes_test(is_rider, login_url='members:home_redirect')
@login_required
def rider_dashboard(request):

    presences = RacePresence.objects.filter(rider=request.user.rider, finisher_status__isnull=False).order_by('race__date')
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
        next_race.curr_rider_presence = presence

    context = {
        'next_race': next_race,
        'res_by_season': res_by_season,
        'seasons': seasons,
        'stats_info': stats_info,
    }

    return render(request, 'members/rider_dashboard.html', context)

def get_team_res(season_res) -> list[tuple[Rider, dict[str, int]]]:

    res = []
    for key, presences in season_res.items():
        res.append((presences[0].rider, get_stats_info(presences)))

    return res

def get_team_stats(season_res, race_days):

    stats = {
        'race_days': race_days,
        'podium': 0,
        'first': 0,
        'second': 0,
        'third': 0,
        'top_5': 0,
        'top_10': 0,
        'top_20': 0,
    }

    for key, presences in season_res.items():
        stats['podium'] += count_top(presences, 3)
        stats['top_5'] += count_top(presences, 5)
        stats['top_10'] += count_top(presences, 10)
        stats['top_20'] += count_top(presences, 20)
        stats['first'] += count_position(presences, 1)
        stats['second'] += count_position(presences, 2)
        stats['third'] += count_position(presences, 3)

    return stats


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

@login_required
def profile(request):

    if (request.method == 'POST'):

        if ("first_name" in request.POST):
            request.user.first_name = request.POST.get("first_name").lower()
            request.user.last_name = request.POST.get("last_name").lower()
            request.user.save()

        if ("user_email" in request.POST):
            request.user.email = request.POST.get("user_email")
            request.user.profile.phone = request.POST.get("user_phone")
            request.user.save()
            request.user.profile.save()

        if ("avatar" in request.FILES):
            form = AvatarForm(request.POST, request.FILES, instance=request.user.profile)

            if form.is_valid():
                form.save()

        if ("theme_pref" in request.POST):
            request.user.profile.theme = request.POST.get("theme_pref")
            request.user.profile.save()

        return (redirect('members:profile'))


    return render(request, "members/profile.html")
