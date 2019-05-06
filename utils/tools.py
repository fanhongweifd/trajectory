import datetime
import time


def timestamp_to_string(sp):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(sp))