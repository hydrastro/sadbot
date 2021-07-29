"""Here are some functions used used by more files"""

import time


def safe_cast(val, to_type, default=None):
    """Safely casts to a type, mostly used for int casting"""
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default


def convert_time(conv_time: int, ago: bool = False) -> str:
    """Returns time ago/stuff lol"""
    periods = [
        "second",
        "minute",
        "hour",
        "day",
        "week",
        "month",
        "year",
        "decade",
        "century",
        "millennium",
    ]
    lengths = [60, 60, 24, 7, 4.35, 12, 10, 10, 10]
    if ago:
        now = time.time()
        difference = now - conv_time
    else:
        difference = conv_time
    j = 0
    while difference >= lengths[j] and j < len(lengths) - 1:
        difference /= lengths[j]
        j += 1
    difference = round(difference)
    if difference != 1:
        periods[j] += "s"
    output = f"{difference} {periods[j]}"
    if ago:
        output = "now" if (difference == 0) else f"{difference} {periods[j]} ago"
    return output


def convert_to_seconds(s: str) -> int:
    seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604_800}
    if s[-1] not in seconds_per_unit:
        return safe_cast(s, int, 0)
    return int(s[:-1]) * seconds_per_unit[s[-1]]
