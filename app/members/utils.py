from .models import RacePresence

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


def get_stats_info(season_res: list[RacePresence]) -> dict[str, int]:
    stats_info = {
        'race_days': len(season_res),
        'finisher': count_status(season_res, 'finisher'),
        'dns': count_status(season_res, 'DNS'),
        'dnf': count_status(season_res, 'DNF'),
        'podium': count_top(season_res, 3),
        'first': count_position(season_res, 1),
        'second': count_position(season_res, 2),
        'third': count_position(season_res, 3),
        'top_5': count_top(season_res, 5),
        'top_10': count_top(season_res, 10),
        'top_20': count_top(season_res, 20),
    }
    return stats_info

def count_status(season: list[RacePresence], status: str):
    count_status = 0
    for presence in season:
        if (presence.finisher_status == status):
            count_status += 1
    return (count_status)

def count_top(season: list[RacePresence], top: int):
    podium = 0
    for presence in season:
        if (presence.finisher_status == 'finisher' and presence.position is not None):
            if (presence.position > 0 and presence.position <= top):
                podium += 1
    return (podium)

def count_position(season: list[RacePresence], target: int):
    position = 0
    for presence in season:
        if (presence.finisher_status == 'finisher' and presence.position is not None):
            if (presence.position == target):
                position += 1
    return (position)
