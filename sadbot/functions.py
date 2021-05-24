"""Here are some functions used used by more files"""


def safe_cast(val, to_type, default=None):
    """Safely casts to a type, mostly used for int casting"""
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default
