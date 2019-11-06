import ledger
from ledger import Account, Transaction
import yaml

def write(ledger_, outFile):
    with outFile.open("w") as f:
        yaml.dump(ledger_, f)

def readOld(inFile):
    with inFile.open("r") as f:
        transactions = yaml.unsafe_load(f)
        ledger_ = ledger.Ledger()
        for str_transaction in transactions:
            transaction = getTransaction(ledger_, str_transaction)
            ledger_.addTransaction(transaction)
    return ledger_


def read(inFile):
    with inFile.open("r") as f:
        ledger_ = yaml.unsafe_load(f)
        x = ledger_.topAccount.reset()
        return ledger_

def getTransaction(ledger_, str_transaction):
    sourceAccount = ledger.getAccountFromStr(str_transaction.sourceAccount)
    targetAccount = ledger.getAccountFromStr(str_transaction.targetAccount)
    return Transaction(str_transaction.amount, sourceAccount, targetAccount, str_transaction.originator, str_transaction.date, str_transaction.usage)
