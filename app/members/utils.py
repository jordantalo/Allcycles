from .models import RacePresence, Rider, Race

def is_active_staff_or_admin(user):
    """Renvoie True si le user est admin Django ou un staff actif"""
    if user.is_staff:
        return True
    if hasattr(user, 'staff') and user.staff.is_active:
        return True
    return False

def is_rider(user):
    """Renvoie True si le user est un rider"""
    if hasattr(user, 'rider'):
            return True
    return False

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

def get_stats_info(season_res: list[RacePresence]) -> dict[str, int]:
    stats_info = {
        'race_days': get_race_days(season_res),
        'finisher': get_finished_races(season_res),
        'dns': count_status(season_res, 'DNS'),
        'dnf': count_status(season_res, ['DNF', 'OTL', 'DSQ']),
        'podium': count_top(season_res, 3),
        'first': count_position(season_res, 1),
        'second': count_position(season_res, 2),
        'third': count_position(season_res, 3),
        'top_5': count_top(season_res, 5),
        'top_10': count_top(season_res, 10),
        'top_20': count_top(season_res, 20),
    }
    return stats_info

def get_race_days(season: list[RacePresence]):
    race_days = 0
    for presence in season:
        for stage, position in presence.positions_dict.items():
            if (position != "DNS" and stage != "G"):
                race_days += 1
    return (race_days)

def get_finished_races(season: list[RacePresence]):
    finished = 0

    for presence in season:
        for stage, position in presence.positions_dict.items():

            if stage == 'G':
                continue
            elif isinstance(position, int):
                finished += 1
            elif isinstance(position, str) and position.isdigit():
                finished += 1

    return finished

def count_status(season: list[RacePresence], statuses: list[str]):
    count_status = 0
    for presence in season:
        for position in presence.positions_dict.values():
            for status in statuses:
                if (position == status):
                    count_status += 1
    return (count_status)

def count_top(season: list[RacePresence], top: int):
    top_perf = 0
    for presence in season:
        for stage, position in presence.positions_dict.items():
            if (isinstance(position, int) and position > 0 and position <= top):
                top_perf += 1

    return (top_perf)

def count_position(season: list[RacePresence], target: int):
    count = 0
    for presence in season:
        for stage, position in presence.positions_dict.items():
            if (position == target):
                count += 1
    return (count)
