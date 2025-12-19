from datetime import datetime

def get_system_time():
    from time import time
    return time()

def get_current_time(style="%Y%m%d_%H%M%S"):
    return datetime.now().strftime(style)


def sleep(seconds):
    from time import sleep
    sleep(seconds)
