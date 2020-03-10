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
    period = budgetDict.get(config.periodIdentifier, config.defaultPeriod)
    # periods = util.subdivideTime(args.start, args.end, budgetDict[config.periodIdentifier])
    # for period in periods:
    #     for (account, amount) in budgetDict[config.accountsIdentifier].items():
    #         transaction = ledger.Transaction(amount, config.checkingAccount, account, "Budget", period[0], "Budget")
    #         budgetLedger.addTransaction(transaction)
    # for account in budgetDict[config.accountsIdentifier]:
    accounts = budgetDict[config.accountsIdentifier]
    queryResult = ledger_.periodicAccountQuery(accounts, args.start, args.end, period)
    for (period, result) in queryResult:
        print(period)
        print(result)
        print("WRITE A QUERYRESULT CLASS HERE THAT EXTENDS THIS OUTPUT. This is all thats left to do.")
