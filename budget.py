import ledger
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

def compareToBudget(ledger_, args):
    budgetDict = getBudgetDict(args.budget)
    patterns = ["^"+account for account in budgetDict[config.accountsIdentifier]]
    budgetLedger = ledger_.clone()
    periods = util.subdivideTime(args.start, args.end, budgetDict[config.periodIdentifier])
    for period in periods:
        for (account, amount) in budgetDict[config.accountsIdentifier].items():
            transaction = ledger.Transaction(amount, config.checkingAccount, account, "Budget", period[0], "Budget")
            budgetLedger.addTransaction(transaction)
    budgetLedger.printRegister(patterns, args.start, args.end, budgetDict[config.periodIdentifier])
