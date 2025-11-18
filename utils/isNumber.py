def isNumber(value):
    try:
        float(value)  # try converting to float
        return True
    except (ValueError, TypeError):
        return False