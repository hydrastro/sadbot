"""Here are some functions used used by more files"""

import os
import random
import subprocess
import time
from typing import Optional


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


def convert_to_seconds(time_string: str) -> int:
    """Converts a time string format to seconds"""
    seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604_800}
    if time_string[-1] not in seconds_per_unit:
        return safe_cast(time_string, int, 0)
    return safe_cast(time_string[:-1], int, 0) * seconds_per_unit.get(
        time_string[-1], 0
    )


def convert_to_days(time_string: str) -> int:
    """Converts a time string format to days"""
    days_per_unit = {"d": 1, "w": 7, "m": 30}
    if time_string[-1] not in days_per_unit:
        return safe_cast(time_string, int, 0)
    return safe_cast(time_string[:-1], int, 0) * days_per_unit.get(time_string[-1], 0)


def webm_to_mp4_convert(file_bytes: bytes) -> Optional[bytes]:
    """Converts the input bytes representing a webm into mp4 bytes using ffmpeg"""
    name = str(random.randint(0, 10000000000))
    with open(name, "wb") as file:
        file.write(file_bytes)
    output = name + ".mp4"
    retcode = subprocess.call(
        ["ffmpeg", "-i", name, "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", output],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if retcode != 0:
        try:
            os.remove(name)
            os.remove(output)
        except os.error:
            return None
    with open(output, "rb") as file:
        output_bytes = file.read()
    os.remove(name)
    os.remove(output)
    return output_bytes
