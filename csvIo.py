import ledger
from ledger import Account, Transaction
import itertools

def write(ledger_, outFile):
    s = "\n".join(transaction.serialize() for transaction in ledger_.transactions)
    with outFile.open("w") as f:
        f.write(s)
        
def read(inFile):
    with inFile.open("r") as f:
        lines = f.readlines()
        topAccount, accounts = getAccountsFromLines(lines)
        transactions = [Transaction.deserialize(line, accounts) for line in lines]
        ledger_ = ledger.Ledger()
        ledger_.topAccount = topAccount
        for transaction in transactions:
            ledger_.addTransaction(transaction)
        x = ledger_.topAccount.reset()
        return ledger_

def getAccountsFromLines(lines):
    accountNames = set()
    for line in lines:
        _, source, _, target, _, _ = line.replace("\n", "").split(";")
        accountNames.add(source)
        accountNames.add(target)
    accountNames = sorted(list(accountNames), key=lambda x:len(x))
    accounts = set()
    allAccount = Account("all")
    for accountName in accountNames:
        getAccountAndTopAccounts(accounts, accountName, allAccount)
    return allAccount, accounts

def getAccountAndTopAccounts(accounts, accountName, allAccount):
    if not ":" in accountName:
        topAccount = allAccount
        rawName = accountName
    else:
        split = accountName.split(":")
        top = ":".join(split[:-1])
        rawName = split[-1]
        assert not accountName in (account.name for account in accounts)
        if not top in (account.name for account in accounts):
            topAccount = getAccountAndTopAccounts(accounts, top, allAccount)
        else:
            topAccount = next(account for account in accounts if account.name == top)
    account = Account(rawName)
    accounts.add(account)
    topAccount.addAccount(account)
    return account
        
