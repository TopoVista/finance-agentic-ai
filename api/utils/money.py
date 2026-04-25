def clamp_percentage(value: float) -> float:
    return round(max(min(value, 100), -100), 2)
