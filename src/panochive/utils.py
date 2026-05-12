from math import floor


def format_duration(seconds: float) -> str:
    minutes: float = seconds / 60.0
    if minutes < 1.0:
        return f"{seconds:.2f}s"
    elif minutes < 60.0:
        return f"{minutes:.2f}m"
    else:
        hours: int = floor(minutes / 60.0)
        remainder_minutes: float = minutes % 60.0
        return f"{hours}h {remainder_minutes:.2f}m"
