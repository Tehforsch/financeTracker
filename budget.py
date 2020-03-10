import ledger
import yaml
import config
import util
from queryResult import BudgetResult
from decimal import Decimal
from yaml import UnsafeLoader

def getBudgetForTime(budgetFilename, startDate, endDate):
    budgetDict = getBudgetDict(budgetFilename)

def getBudgetDict(budgetFilename):
    with budgetFilename.open("r") as f:
        budgetDict = yaml.load(f, Loader=UnsafeLoader)
        assert config.periodIdentifier in budgetDict
        assert config.accountsIdentifier in budgetDict
    for (k, v) in budgetDict[config.accountsIdentifier].items():
        budgetDict[config.accountsIdentifier][k] = Decimal(v.replace(config.currency, ""))
    return budgetDict

def compareToBudget(ledger_, args):
    budgetDict = getBudgetDict(args.budget)
    accounts = budgetDict[config.accountsIdentifier]
    if args.sum:
        queryResult = ledger_.patternAccountQuery(accounts, args.start, args.end)
        result = BudgetResult(queryResult, budgetDict)
        budgetDict = extrapolate(budgetDict, args)
        print(result)
    else:
        queryResult = ledger_.periodicAccountQuery(accounts, args.start, args.end, args.period, exactMatch=True)
        for (period, result) in queryResult:
            print(period)
            result = BudgetResult(result, budgetDict)
            print(result)

def showRemainingMoney(ledger_, args):
    budgetDict = getBudgetDict(args.budget)
    accounts = budgetDict[config.accountsIdentifier]
    queryResult = ledger_.patternAccountQuery(accounts, args.start, args.end)
    totalUsed = Decimal(0.0)
    for acc in queryResult.topAccount.getAllAccounts():
        if acc.name in accounts:
            if args.invert is None:
                factor = 1
            else:
                factor = -1 if acc.name in args.invert else 1
            totalUsed += factor * acc.total
    budgetDict = extrapolate(budgetDict, args)
    totalAvailable = sum(budgetDict[config.accountsIdentifier].values())
    print("Used: {}/{}{currency}".format(totalUsed, totalAvailable, currency=config.currency))
    print("Left: {}{currency}".format(totalAvailable - totalUsed, currency=config.currency))

def extrapolate(budgetDict, args):
    delta = args.end - args.start
    numPeriods = Decimal(util.countPeriods(args.start, args.end, args.period)).to_integral_exact()
    budgetDict[config.accountsIdentifier] = dict_multiply(budgetDict[config.accountsIdentifier], numPeriods)
    return budgetDict

def dict_multiply(d, factor):
    return dict((k, v * factor) for (k, v) in d.items())
