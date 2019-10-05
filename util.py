from dateutil.relativedelta import relativedelta
from datetime import timedelta
import config

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
            config.day: timedelta(1),
            config.week: timedelta(7),
            config.month: relativedelta(months=+1),
            config.year: relativedelta(years=+1)
            }[periodString]

def printPeriod(period):
    print("{} - {}".format(*period))

def printAccounts(accounts):
    print(accountsStr(accounts))

def accountsStr(accounts):
    sortedAccounts = sorted([account for account in accounts.getAllAccounts()])
    accountPadding = max(len(account) for account in sortedAccounts)
    amountPadding = max(len(str(accounts[account])) for account in sortedAccounts)
    return "\n".join("{:<{accountPadding}} \t {:>{amountPadding}}{currency}".format(account, accounts[account], accountPadding=accountPadding, amountPadding=amountPadding, currency=config.currency) for account in sortedAccounts)

