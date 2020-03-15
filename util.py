from typing import List, Callable
import itertools
import datetime
from datetime import timedelta
from collections import namedtuple
import config
from timeframe import Timeframe
from period import Period

class QueryInput:
    def __init__(self, accountPatterns: List[str], timeframe: Timeframe, period: Period, exactMatch: bool) -> None:
        self.accountPatterns = accountPatterns
        self.timeframe = timeframe
        self.period = period
        self.exactMatch = exactMatch

    def changeTimeframe(self, timeFrame: Timeframe) -> "QueryInput":
        return QueryInput(self.accountPatterns, timeFrame, self.period, self.exactMatch)
        
FormatOptions = namedtuple("FormatOptions", ["sumAllAccounts", "printEmptyAccounts"])

def dateFromIsoformat(string: str) -> datetime.date:
    return datetime.datetime.strptime(string, config.defaultDateFormat).date()

def subdivideTime(timeframe: Timeframe, period: Period) -> List[Timeframe]:
    """Subdivide the time between startTime and endTime given into
    periods of length period and return tuples containing the start
    and end time of the respective period"""
    if period.isInfinite():
        return [timeframe]
    delta = period.delta
    periods = []
    today = timeframe.start
    oneDay = timedelta(1)
    while today <= timeframe.end:
        afterOnePeriod = today + delta
        periods.append(Timeframe(today, afterOnePeriod - oneDay))  # Shift the last date backward one day so we dont have overlapping dates.
        today = afterOnePeriod
    return periods

def getSharedSuperAccounts(string1: str, string2: str) -> List[str]:
    accounts1 = string1.split(config.accountSeparator)
    accounts2 = string2.split(config.accountSeparator)
    sharedAccounts = [x[0] for x in itertools.takewhile(lambda x: x[0] == x[1], zip(accounts1, accounts2))]
    return sharedAccounts

def countPeriods(timeframe: Timeframe, period: Period) -> float:
    return (timeframe.end - timeframe.start).days / period.days

def dividePeriods(period1: Period, period2: Period) -> float:
    return period1.days / period2.days
