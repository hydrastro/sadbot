"""Here are some functions used used by more files"""

import time

def safe_cast(val, to_type, default=None):
    """Safely casts to a type, mostly used for int casting"""
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default

def convert_time(conv_time: int, ago: bool=False) -> str:
    periods = ["second", "minute", "hour", "day", "week", "month", "year", "decade", "century", "millennium"]
    lengths = [60, 60, 24, 7, 4.35, 12, 10, 10, 10]
    if ago:
        now = time.time();
        difference = now - conv_time
    else:
        difference = conv_time
    j = 0
    while difference >= lengths[j] and j < len(lengths) - 1:
        j += 1
        difference /= lengths[j]
    difference = round(difference)
    if difference != 1:
        periods[j] += "s"
    output = f"{difference} {periods[j]}"
    if ago:
        output = "now" if (difference == 0) else f"{difference} {periods[j]} ago"
    return output
