from dateutil.relativedelta import relativedelta
from datetime import timedelta

def subdivideTime(start, end, period):
    """Subdivide the time between startTime and endTime given into 
    periods of length period and return tuples containing the start
    and end time of the respective period"""
    delta = getPeriodDelta(period)
    periods = []
    today = start
    while today <= end:
        afterOnePeriod = today + delta
        periods.append((today, afterOnePeriod))
        today = afterOnePeriod
    return periods

def getPeriodDelta(periodString):
    return {
            "day": timedelta(1),
            "week": timedelta(7),
            "month": relativedelta(months=+1),
            "year": relativedelta(years=+1)
            }[periodString]
