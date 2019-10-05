from decimal import Decimal
import config
from collections import defaultdict
import yaml
import re
import budget
import logging

def matchesAny(string, regexList):
    return any(re.search(pattern, string) for pattern in regexList)

class Transaction:
    def __init__(self, amount, sourceAccount, targetAccount, originator, date, usage):
        self.amount = amount
        self.sourceAccount = sourceAccount
        self.targetAccount = targetAccount
        self.originator = originator
        self.usage = usage
        self.date = date

    def __str__(self):
        return "{}\n{}\n{}\n{}".format(self.date, self.originator, self.usage, self.amount)

class Accounts(defaultdict):
    def __str__(self):
        sortedKeys = sorted([key for key in self])
        return "\n".join("{}: \t {}".format(key, self[key]) for key in sortedKeys)

    def filter(self, predicate):
        newAccounts = Accounts(Decimal)
        for key in self:
            if predicate(key, self[key]):
                newAccounts[key] = self[key]
        return newAccounts

class Ledger:
    def __init__(self, transactions=[]):
        self.accounts = Accounts(Decimal)
        self.transactions = []
        for transaction in transactions:
            self.addTransaction(transaction)

    def addTransaction(self, transaction):
        self.transactions.append(transaction)
        self.accounts[transaction.sourceAccount] -= transaction.amount
        self.accounts[transaction.targetAccount] += transaction.amount
        
    def __str__(self):
        sortedAccounts = sorted(self.accounts.keys())
        return "\n".join(self.accountToStr(acc) for acc in sortedAccounts)

    def accountToStr(self, acc):
        return "{}:\t{}".format(acc, self.accounts[acc])

    def write(self, outFile):
        with outFile.open("w") as f:
            yaml.dump(self.transactions, f)

    @staticmethod
    def read(inFile):
        with inFile.open("r") as f:
            transactions = yaml.unsafe_load(f)
            ledger = Ledger()
            for transaction in transactions:
                ledger.addTransaction(transaction)
        return ledger

    def printBalance(self, args):
        queryResult = self.balanceQuery(args)
        print(queryResult)

    # def printRegister(self, args):
    #     queryResult = self.registerQuery(args)
    #     print(queryResult)

    def filterTransactionsByTime(self, start, end):
        for transaction in self.transactions:
            if (start <= transaction.date) and (transaction.date < end):
                print(start, transaction.date, end)
        transactionsInThatTimeFrame = [transaction for transaction in self.transactions if (start <= transaction.date) and (transaction.date < end)]
        # for t in transactionsInThatTimeFrame:
            # print(t)
        return Ledger(transactionsInThatTimeFrame)

    def balanceQuery(self, args):
        relevantAccounts = self.getRelevantAccounts(args.balance)
        if not args.empty:
            relevantAccounts = relevantAccounts.filter(lambda _, value: value != 0)
        return relevantAccounts

    def getRelevantAccounts(self, patterns):
        if patterns is None or patterns == []:
            return self.accounts.copy()
        else:
            relevantAccounts = self.accounts.filter(lambda name, _: matchesAny(name, patterns))
            return relevantAccounts

    def getFirstTransactionDate(self):
        return min(transaction.date for transaction in self.transactions)

    def getLastTransactionDate(self):
        return max(transaction.date for transaction in self.transactions)

# def amount_representer(dumper, data):
#     return dumper.represent_scalar('!decimal', str(data))

# yaml.add_representer(Decimal, amount_representer)
