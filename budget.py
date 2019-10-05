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
    # args.balance = [account for account in budgetDict[config.accountsIdentifier]]
    budgetDict = getBudgetDict(args.budget)
            # for (account, amount) in budgetDict[config.accountsIdentifier].items():
                # transaction = Transaction(amount, config.checkingAccount, account, "Budget", period[0], "Budget")
                # periodLedger.addTransaction(transaction)
