from decimal import Decimal
import config
from collections import defaultdict
import yaml
import re
import budget
import logging
import util

def toList(func):
    def wrapper(*args, **kwargs):
        return list(func(*args, **kwargs))
    return wrapper

def matchesAny(string, regexList, exactMatch=False):
    if exactMatch:
        return any(pattern == string for pattern in regexList)
    else:
        return any(re.search(pattern, string) for pattern in regexList)

def isDirectSubAccount(potentialSubAccount, account):
    return potentialSubAccount.startswith(account) and potentialSubAccount.replace(account, "").startswith(config.accountSeparator) and potentialSubAccount.replace(account, "").count(config.accountSeparator) == 1

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
    def getAllAccounts(self):
        """Get all account names of this account list. This is non-trivial because there are also super-accounts that might have never been added to the list explicitly but should still be listed"""
        allAccounts = set()
        for account in self:
            levels = account.split(config.accountSeparator)
            for i in range(1, len(levels)):
                allAccounts.add(config.accountSeparator.join(levels[:i]))
            allAccounts.add(account)
        return allAccounts

    def __str__(self):
        return util.accountsStr(self)

    def filter(self, predicate):
        newAccounts = Accounts(Decimal)
        for key in self:
            if predicate(key, self[key]):
                newAccounts[key] = self[key]
        return newAccounts

    def __getitem__(self, key):
        realValue = self.realValue(key)
        subAccounts = [account for account in self if isDirectSubAccount(account, key)]
        return realValue + sum(self[account] for account in subAccounts)


    def realValue(self, accountName):
        return super().__getitem__(accountName)

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
        
    def clone(self):
        return Ledger(self.transactions)

    def __str__(self):
        return str(self.accounts)

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
        queryResult = self.balanceQuery(args.balance, args.start, args.end, args.exact)
        util.printAccounts(queryResult, printEmptyAccounts=args.empty, printSuperAccounts=not args.exact)

    def printRegister(self, accountPatterns, start, end, period, printEmptyAccounts=False, exactMatch=False):
        for (period, periodBalance) in self.registerQuery(accountPatterns, start, end, period, exactMatch=exactMatch):
            util.printPeriod(period)
            util.printAccounts(periodBalance, printEmptyAccounts=printEmptyAccounts, printSuperAccounts=not exactMatch)

    @toList
    def registerQuery(self, accountPatterns, start, end, period, exactMatch=False, totals=False):
        periods = util.subdivideTime(start, end, period)
        for period in periods:
            if totals:
                queryStart = start
            else:
                queryStart = period[0]
            yield period, self.balanceQuery(accountPatterns, queryStart, period[1], exactMatch=exactMatch)

    def filterTransactionsByTime(self, start, end):
        transactionsInThatTimeFrame = [transaction for transaction in self.transactions if (start <= transaction.date) and (transaction.date <= end)]
        return Ledger(transactionsInThatTimeFrame)

    def balanceQuery(self, accountPatterns, start, end, exactMatch=False):
        timeLedger = self.filterTransactionsByTime(start, end)
        relevantAccounts = timeLedger.getRelevantAccounts(accountPatterns, exactMatch=exactMatch)
        return relevantAccounts

    def getRelevantAccounts(self, patterns, exactMatch=False):
        if patterns is None or patterns == []:
            return self.accounts.copy()
        else:
            relevantAccounts = self.accounts.filter(lambda name, _: matchesAny(name, patterns, exactMatch=exactMatch))
            return relevantAccounts

    def getAllSubAccounts(self, superAccount):
        return self.accounts.filter(lambda name, amount: name.startswith(superAccount))

    def getFirstTransactionDate(self):
        return min(transaction.date for transaction in self.transactions)

    def getLastTransactionDate(self):
        return max(transaction.date for transaction in self.transactions)
