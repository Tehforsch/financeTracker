from typing import List, Callable, Any, Dict, Iterable, Tuple
import re
import datetime
import util
from queryResult import TransactionQueryResult, AccountQueryResult
from account import Account
import config
from transaction import Transaction
from timeframe import Timeframe
from util import FormatOptions, QueryInput

def toList(func: Callable) -> Callable:
    def wrapper(*args: List[Any], **kwargs: Dict[str, Any]) -> List:
        return list(func(*args, **kwargs))
    return wrapper

def matchesAny(string: str, regexList: List[str], exactMatch: bool = False) -> bool:
    if exactMatch:
        return any(pattern == string for pattern in regexList)
    return any(re.search(pattern, string) for pattern in regexList)

def isDirectSubAccount(potentialSubAccount: str, account: str) -> bool:
    return potentialSubAccount.startswith(account) and potentialSubAccount.replace(account, "").startswith(config.accountSeparator) and potentialSubAccount.replace(account, "").count(config.accountSeparator) == 1

@toList
def periodicQuery(queryFunction: Callable, queryInput: QueryInput) -> Iterable[Tuple[Timeframe, Any]]:
    timeframes = util.subdivideTime(queryInput.timeframe, queryInput.period)
    for timeframe_ in timeframes:
        yield timeframe_, queryFunction(queryInput.changeTimeframe(timeframe_))

def printPeriodicQuery(queryFunction: Callable, queryInput: QueryInput, formatOptions: FormatOptions) -> None:
    result = periodicQuery(queryFunction, queryInput)
    for (timeframe_, out) in result:
        print(timeframe_)
        print(out.toStr(formatOptions))

def patternQuery(queryFunction: Callable, queryInput: QueryInput) -> Any:
    def accountPredicate(account: Account) -> bool:
        if queryInput.accountPatterns is None or queryInput.accountPatterns == []:
            return True
        return matchesAny(account.name, queryInput.accountPatterns, exactMatch=queryInput.exactMatch)
    return queryFunction(transactionPredicate=queryInput.timeframe.containsTransaction, accountPredicate=accountPredicate)

class Ledger:
    def __init__(self) -> None:
        self.topAccount = Account("all")
        self.transactions: List[Transaction] = []

    def addTransaction(self, transaction: Transaction) -> None:
        self.transactions.append(transaction)
        transaction.apply()

    def getFirstTransactionDate(self) -> datetime.date:
        return min(transaction.date for transaction in self.transactions)

    def getLastTransactionDate(self) -> datetime.date:
        return max(transaction.date for transaction in self.transactions)

    def printAverages(self, queryInput: QueryInput, formatOptions: FormatOptions) -> None:
        result = self.patternAccountQuery(queryInput)
        factor = 1.0 / util.countPeriods(queryInput.timeframe, queryInput.period)
        print(result.toStr(formatOptions, factor=factor))

    def printAccounts(self, queryInput: QueryInput, formatOptions: FormatOptions) -> None:
        printPeriodicQuery(self.patternAccountQuery, queryInput, formatOptions)

    def printTransactions(self, queryInput: QueryInput, formatOptions: FormatOptions) -> None:
        printPeriodicQuery(self.patternTransactionQuery, queryInput, formatOptions)

    def periodicAccountQuery(self, queryInput: QueryInput) -> List[Tuple[Timeframe, AccountQueryResult]]:
        return periodicQuery(self.patternAccountQuery, queryInput)

    def patternAccountQuery(self, queryInput: QueryInput) -> AccountQueryResult:
        return patternQuery(self.accountQuery, queryInput)
    
    def patternTransactionQuery(self, queryInput: QueryInput) -> AccountQueryResult:
        return patternQuery(self.transactionQuery, queryInput)
    
    def accountQuery(self, transactionPredicate: Callable[[Transaction], bool] = lambda _:True, accountPredicate: Callable[[Account], bool] = lambda _:True) -> AccountQueryResult:
        self.topAccount.reset()
        for transaction in self.transactions:
            if transactionPredicate(transaction):
                transaction.apply()
        return AccountQueryResult(self.topAccount, accountPredicate)

    def transactionQuery(self, transactionPredicate: Callable[[Transaction], bool] = lambda _:True, accountPredicate: Callable[[Account], bool] = lambda _:True) -> TransactionQueryResult:
        transactions = [transaction for transaction in self.transactions if transactionPredicate(transaction) and (accountPredicate(transaction.sourceAccount) or accountPredicate(transaction.targetAccount))]
        return TransactionQueryResult(sorted(transactions, key=lambda transaction: transaction.date))

    def getAccountFromStr(self, fullName: str, account: Account = None) -> Account:
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

    def getAccount(self, accountName: str) -> Account:
        return self.topAccount.getAccount(accountName)
