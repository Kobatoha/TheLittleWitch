"""
ЛУННЫЙ КАЛЕНДАРЬ
Вычисляет фазу луны по дате.
Формула адаптирована из астрономических алгоритмов.
"""

from datetime import date, datetime

# Известное новолуние (любое эталонное)
KNOWN_NEW_MOON = date(2000, 1, 6)  # 6 января 2000 — новолуние
LUNAR_CYCLE_DAYS = 29.53058867     # синодический месяц в днях

MOON_PHASES = [
    (0, "Новолуние", "🌑", 0),
    (1, "Молодая луна", "🌒", 3),
    (2, "Первая четверть", "🌓", 7),
    (3, "Прибывающая", "🌔", 12),
    (4, "Полнолуние", "🌕", 18),
    (5, "Убывающая", "🌖", 12),
    (6, "Последняя четверть", "🌗", 7),
    (7, "Старая луна", "🌘", 3),
]


def get_moon_phase(d: date = None) -> dict:
    """
    Возвращает фазу луны для указанной даты.
    Если дата не указана — на сегодня.
    """
    if d is None:
        d = datetime.utcnow().date()

    # Сколько дней прошло с эталонного новолуния
    days_since = (d - KNOWN_NEW_MOON).days
    # Текущая позиция в цикле (0.0 — новолуние, 0.5 — полнолуние)
    cycle_position = (days_since % LUNAR_CYCLE_DAYS) / LUNAR_CYCLE_DAYS

    # Определяем фазу (8 фаз)
    phase_index = int(cycle_position * 8) % 8
    phase = MOON_PHASES[phase_index]

    return {
        "index": phase_index,
        "name": phase[1],
        "emoji": phase[2],
        "essence_bonus": phase[3],
        "cycle_position": round(cycle_position, 3),
        "days_to_full_moon": _days_to_full_moon(cycle_position),
    }


def _days_to_full_moon(cycle_position: float) -> int:
    """Сколько дней осталось до полнолуния (фаза 4)."""
    full_moon_pos = 0.5  # полнолуние на 50% цикла
    if cycle_position <= full_moon_pos:
        diff = full_moon_pos - cycle_position
    else:
        diff = 1.0 - cycle_position + full_moon_pos
    return round(diff * LUNAR_CYCLE_DAYS)


def get_essence_bonus_for_night(d: date = None) -> int:
    """Сколько эссенции добавляется за ночь в зависимости от луны."""
    return get_moon_phase(d)["essence_bonus"]
    