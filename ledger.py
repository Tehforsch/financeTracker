from decimal import Decimal
import config
from collections import defaultdict
import yaml
import re
import budget
import logging
import util
from queryResult import TransactionQueryResult, AccountQueryResult
from account import Account
from transaction import Transaction

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

class Ledger:
    def __init__(self):
        self.topAccount = Account("all")
        self.transactions = []

    def addTransaction(self, transaction):
        self.transactions.append(transaction)
        self.handleTransaction(transaction)

    def handleTransaction(self, transaction):
        transaction.sourceAccount.amount -= transaction.amount
        transaction.targetAccount.amount += transaction.amount

    def getFirstTransactionDate(self):
        return min(transaction.date for transaction in self.transactions)

    def getLastTransactionDate(self):
        return max(transaction.date for transaction in self.transactions)

    # def filter(self, predicate):
    #     newAccounts = Accounts(Decimal)
    #     for key in self:
    #         if predicate(key, self[key]):
    #             newAccounts[key] = self[key]
    #     return newAccounts

    def printAccounts(self, accountPatterns, start, end, period, printEmptyAccounts=False, exactMatch=False, sumAllAccounts=False):
        self.printPeriodicQuery(self.patternAccountQuery, accountPatterns, start, end, period, printEmptyAccounts=printEmptyAccounts, exactMatch=exactMatch, sumAllAccounts=sumAllAccounts)

    def printTransactions(self, accountPatterns, start, end, period, exactMatch=False):
        self.printPeriodicQuery(self.patternTransactionQuery, accountPatterns, start, end, period, exactMatch=exactMatch)

    def printPeriodicQuery(self, queryFunction, accountPatterns, start, end, period, exactMatch=False, **kwargs):
        result = self.periodicQuery(queryFunction, accountPatterns, start, end, period, exactMatch=False)
        for (period_, out) in result:
            if period == config.infinite:
                print(period_)
            print(out.toStr(**kwargs))

    def periodicTransactionQuery(self, accountPatterns, start, end, period, exactMatch=False, **kwargs):
        return self.periodicQuery(self.patternTransactionQuery, accountPatterns, start, end, period, exactMatch=False)

    def periodicAccountQuery(self, accountPatterns, start, end, period, exactMatch=False, **kwargs):
        return self.periodicQuery(self.patternAccountQuery, accountPatterns, start, end, period, exactMatch=False)

    @toList
    def periodicQuery(self, queryFunction, accountPatterns, start, end, period, exactMatch=False):
        periods = util.subdivideTime(start, end, period)
        for period_ in periods:
            yield period_, queryFunction(accountPatterns, period_[0], period_[1], exactMatch=exactMatch)

    def patternAccountQuery(self, accountPatterns, start, end, exactMatch=False):
        return self.patternQuery(self.accountQuery, accountPatterns, start, end, exactMatch=exactMatch)
    
    def patternTransactionQuery(self, accountPatterns, start, end, exactMatch=False):
        return self.patternQuery(self.transactionQuery, accountPatterns, start, end, exactMatch=exactMatch)
    
    def patternQuery(self, function, accountPatterns, start, end, exactMatch=False):
        isInThatTimeFrame = lambda transaction: (start <= transaction.date) and (transaction.date <= end)
        # accountPredicate = lambda _:True if accountPatterns is None or accountPatterns == [] else lambda account: matchesAny(account.name, accountPatterns, exactMatch=exactMatch)
        if accountPatterns is None or accountPatterns == []:
            accountPredicate = lambda _: True
        else:
            accountPredicate = lambda account: matchesAny(account.name, accountPatterns, exactMatch=exactMatch)
        return function(transactionPredicate=isInThatTimeFrame, accountPredicate=accountPredicate)
    
    def accountQuery(self, transactionPredicate=lambda _:True, accountPredicate=lambda _:True):
        self.topAccount.reset()
        for transaction in self.transactions:
            if transactionPredicate(transaction):
                self.handleTransaction(transaction)
        return AccountQueryResult(self.topAccount, accountPredicate)

    def transactionQuery(self, transactionPredicate=lambda _:True, accountPredicate=lambda _:True):
        return TransactionQueryResult([transaction for transaction in self.transactions if transactionPredicate(transaction) and (accountPredicate(transaction.sourceAccount) or accountPredicate(transaction.targetAccount))])

    def getAccountFromStr(self, fullName, account=None):
        split = fullName.split(":")
        topName = split[0]
        subName = ":".join(split[1:])
        if account is None:
            return self.getAccountFromStr(fullName, self.topAccount)
        else:
            if topName in [acc.rawName for acc in account.subAccounts]:
                nextAccount = next(acc for acc in account.subAccounts if acc.rawName == topName)
            else:
                nextAccount = Account(topName)
                account.addAccount(nextAccount)
            if fullName == topName:
                return nextAccount
            else:
                return self.getAccountFromStr(subName, nextAccount)

    def getAccount(self, accountName):
        return self.topAccount.getAccount(accountName)
