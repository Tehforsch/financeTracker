import yaml
import config
import util

def getBudgetForTime(budgetFilename, startDate, endDate):
    budgetDict = getBudgetDict(budgetFilename)

def getBudgetDict(budgetFilename):
    with budgetFilename.open("r") as f:
        budgetDict = yaml.unsafe_load(f)
        assert config.periodIdentifier in budgetDict
        assert config.accountsIdentifier in budgetDict
    return budgetDict

def compareToBudget(ledger, args):
    budgetDict = getBudgetDict(args.budget)
    periods = util.subdivideTime(args.start, args.end, budgetDict[config.periodIdentifier])
    for period in periods:
        periodLedger = ledger.filterTransactionsByTime(*period)
        print(period)
        print(periodLedger.accounts)
        periodLedger.printBalance(args)
