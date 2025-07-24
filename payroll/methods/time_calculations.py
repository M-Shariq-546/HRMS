from datetime import time

def generate_am_pm_time_choices():
    choices = []
    for hour in range(0, 24):
        for minute in range(0, 60):
            t = time(hour, minute)
            display = t.strftime("%I:%M %p") # this is for UI Display
            value = t.strftime("%H:%M:%S") # This is for db value storing
            choices.append((value, display))
    return choices