from decimal import Decimal
import config
from collections import defaultdict
import yaml
import re
import budget
import logging
import util

def matchesAny(string, regexList):
    return any(re.search(pattern, string) for pattern in regexList)

def isSubAccount(potentialSubAccount, account):
    return potentialSubAccount.startswith(account) and potentialSubAccount.replace(account, "").startswith(config.accountSeparator)

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
        subAccounts = [account for account in self if isSubAccount(account, key)]
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
        queryResult = self.balanceQuery(args.balance, args.start, args.end, args.empty)
        util.printAccounts(queryResult)

    def printRegister(self, args):
        for (period, periodBalance) in self.registerQuery(args.register, args.start, args.end, args.period, args.empty):
            util.printPeriod(period)
            util.printAccounts(periodBalance)

    def registerQuery(self, accountPatterns, start, end, period, printEmptyAccounts=False):
        periods = util.subdivideTime(start, end, period)
        for period in periods:
            yield period, self.balanceQuery(accountPatterns, period[0], period[1], printEmptyAccounts=printEmptyAccounts)

    def filterTransactionsByTime(self, start, end):
        transactionsInThatTimeFrame = [transaction for transaction in self.transactions if (start <= transaction.date) and (transaction.date < end)]
        return Ledger(transactionsInThatTimeFrame)

    def balanceQuery(self, accountPatterns, start, end, printEmptyAccounts=False):
        timeLedger = self.filterTransactionsByTime(start, end)
        relevantAccounts = timeLedger.getRelevantAccounts(accountPatterns)
        if not printEmptyAccounts:
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
