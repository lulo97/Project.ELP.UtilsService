import datetime
import random

def getRandomId():
    now = datetime.datetime.now()
    date_str = now.strftime("%Y%m%d%H%M%S")  # YYYYMMDDHHMMSS
    random_digits = "".join(str(random.randint(0, 9)) for _ in range(10))
    return date_str + random_digits
