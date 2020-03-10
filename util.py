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
    if period == config.infinite:
        return [(start, end)]
    delta = getPeriodDelta(period)
    periods = []
    today = start
    oneDay = timedelta(1)
    while today <= end:
        afterOnePeriod = today + delta
        periods.append((today, afterOnePeriod - oneDay)) # Shift the last date backward one day so we dont have overlapping dates.
        today = afterOnePeriod
    return periods

def getPeriodDelta(periodString):
    return {
            config.day: timedelta(1),
            config.week: timedelta(7),
            config.month: relativedelta(months=+1),
            config.year: relativedelta(years=+1)
            }[periodString]

def getPeriodDays(periodString):
    return {
            config.day: 1,
            config.week: 7,
            config.month: 30,
            config.year: 365
            }[periodString]

def printPeriod(period):
    print("{} - {}".format(*period))

def getSharedSuperAccounts(string1, string2):
    accounts1 = string1.split(config.accountSeparator)
    accounts2 = string2.split(config.accountSeparator)
    sharedAccounts = [x[0] for x in itertools.takewhile(lambda x: x[0] == x[1], zip(accounts1, accounts2))]
    return sharedAccounts

def printAccounts(accounts, printEmptyAccounts=False, printSuperAccounts=True):
    if not printEmptyAccounts:
        accounts = accounts.filter(lambda _, value: value != 0)
    print(accountsStr(accounts, printSuperAccounts=printSuperAccounts))

def accountsStr(accounts, printSuperAccounts=True):
    if len(accounts) == 0:
        return ""
    numSpacesToIndent = 4
    if printSuperAccounts:
        allAccounts = accounts.getAllAccounts()
    else:
        allAccounts = accounts
    sortedAccounts = sorted(list(allAccounts))
    accountPadding = max(len(account) for account in sortedAccounts)
    amountPadding = max(len(str(accounts[account])) for account in sortedAccounts)
    accountLines = []
    for (account, previousAccount) in zip(sortedAccounts, [""] + sortedAccounts):
        if printSuperAccounts:
            shared = getSharedSuperAccounts(account, previousAccount)
            indentationLevel = len(shared)
            accountDisplay = account.replace(config.accountSeparator.join(shared)+config.accountSeparator, " " * indentationLevel * numSpacesToIndent)
        else:
            accountDisplay = account
        amount = accounts[account]
        accountLines.append("{:<{accountPadding}} \t {:>{amountPadding}}{currency}".format(accountDisplay, amount, accountPadding=accountPadding, amountPadding=amountPadding, currency=config.currency))
    return "\n".join(accountLines)

def countPeriods(start, end, period):
    return (end-start).days / getPeriodDays(period)
        
