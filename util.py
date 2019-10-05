from dateutil.relativedelta import relativedelta
from datetime import timedelta
import config
import itertools
import datetime

def dateFromIsoformat(string):
    return datetime.datetime.strptime(string, config.defaultDateFormat).date()

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

def getSharedSuperAccounts(string1, string2):
    accounts1 = string1.split(config.accountSeparator)
    accounts2 = string2.split(config.accountSeparator)
    sharedAccounts = (x[0] for x in itertools.takewhile(lambda x: x[0] == x[1], zip(accounts1, accounts2)))
    return config.accountSeparator.join(sharedAccounts)

def printAccounts(accounts):
    print(accountsStr(accounts))

def accountsStr(accounts):
    if len(accounts) == 0:
        return ""
    sortedAccounts = sorted([account for account in accounts.getAllAccounts()])
    accountPadding = max(len(account) for account in sortedAccounts)
    amountPadding = max(len(str(accounts[account])) for account in sortedAccounts)
    accountLines = []
    for (account, previousAccount) in zip(sortedAccounts, [""] + sortedAccounts):
        shared = getSharedSuperAccounts(account, previousAccount)
        accountDisplay = account.replace(shared+config.accountSeparator, " " * len(shared))
        amount = accounts[account]
        accountLines.append("{:<{accountPadding}} \t {:>{amountPadding}}{currency}".format(accountDisplay, amount, accountPadding=accountPadding, amountPadding=amountPadding, currency=config.currency))
    return "\n".join(accountLines)

