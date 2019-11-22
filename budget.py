import ledger
import yaml
import config
import util
from queryResult import BudgetResult
from decimal import Decimal

def getBudgetForTime(budgetFilename, startDate, endDate):
    budgetDict = getBudgetDict(budgetFilename)

def getBudgetDict(budgetFilename):
    with budgetFilename.open("r") as f:
        budgetDict = yaml.load(f)
        assert config.periodIdentifier in budgetDict
        assert config.accountsIdentifier in budgetDict
    for (k, v) in budgetDict[config.accountsIdentifier].items():
        budgetDict[config.accountsIdentifier][k] = Decimal(v.replace(config.currency, ""))
    return budgetDict

def getPeriod(budgetDict):
    return budgetDict.get(config.periodIdentifier, config.defaultPeriod)

def compareToBudget(ledger_, args):
    budgetDict = getBudgetDict(args.budget)
    period = getPeriod(budgetDict)
    accounts = budgetDict[config.accountsIdentifier]
    if args.sum:
        queryResult = ledger_.patternAccountQuery(accounts, args.start, args.end, exactMatch=True)
        result = BudgetResult(queryResult, budgetDict)
        budgetDict = extrapolate(budgetDict, args)
        print(result)
    else:
        queryResult = ledger_.periodicAccountQuery(accounts, args.start, args.end, period, exactMatch=True)
        for (period, result) in queryResult:
            print(period)
            result = BudgetResult(result, budgetDict)
            print(result)

def extrapolate(budgetDict, args):
    delta = args.end - args.start
    period = getPeriod(budgetDict)
    numPeriods = Decimal(util.countPeriods(args.start, args.end, period)).to_integral_exact()
    budgetDict[config.accountsIdentifier] = dict_multiply(budgetDict[config.accountsIdentifier], numPeriods)

def dict_multiply(d, factor):
    return dict((k, v * factor) for (k, v) in d.items())
