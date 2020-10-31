from typing import List, Callable
import config
from account import Account
from transaction import Transaction
from util import FormatOptions


class TransactionQueryResult(list):
    def __init__(self, values: List[Transaction]) -> None:
        super().__init__(values)
        self.sort(key=lambda transaction: transaction.date)

    def toStr(self, formatOptions: FormatOptions, factor=None) -> str:
        return "\n".join(str(x) for x in self)


class AccountQueryResult:
    def __init__(self, topAccount: Account, accountPredicate: Callable[[Account], bool]) -> None:
        self.topAccount = topAccount.clone()
        self.accountPredicate = accountPredicate

    def toStr(self, formatOptions: FormatOptions, factor: float) -> str:
        if formatOptions.sumAllAccounts:
            summed = sum(acc.amount * factor for acc in self.topAccount.getAllAccounts() if self.accountPredicate(acc))
            return "{}: {}".format(self.topAccount.name, summed)

        def predicate(account: Account) -> bool:
            return self.accountPredicate(account) and (formatOptions.printEmptyAccounts or not account.isEmpty())

        return self.accountsToStr(predicate, factor=factor)

    def accountsToStr(self, predicate: Callable[[Account], bool], factor: float = 1) -> str:
        s = ""
        accountPadding = max(len(acc.name) for acc in self.topAccount.getAllAccounts())
        amountPadding = max(len(str(acc.total * factor)) for acc in self.topAccount.getAllAccounts())
        for account in sorted(self.topAccount.getAllAccounts(), key=lambda acc: acc.name):
            if not predicate(account):
                continue
            numSpaces = account.level * 4
            indentation = numSpaces * " "
            s = (
                s
                + "{:<{accountPadding}} \t {:>{amountPadding}}{currency}".format(
                    indentation + account.rawName, account.total * factor, accountPadding=accountPadding, amountPadding=amountPadding, currency=config.currency
                )
                + "\n"
            )
        return s

    def getAccount(self, accountName: str) -> Account:
        return self.topAccount.getAccount(accountName)


class BudgetResult(AccountQueryResult):
    def __init__(self, accountQueryResult: AccountQueryResult, budget: dict) -> None:
        super().__init__(accountQueryResult.topAccount, accountQueryResult.accountPredicate)
        self.budget = budget

    def accountsToStr(self, predicate: Callable[[Account], bool], factor: float = 1) -> str:
        s = ""
        accountPadding = max(len(acc.name) for acc in self.topAccount.getAllAccounts())
        amountPadding = max(len(str(acc.total)) for acc in self.topAccount.getAllAccounts())
        for account in sorted(self.topAccount.getAllAccounts(), key=lambda acc: acc.name):
            if (not predicate(account)) or (account.name not in self.budget[config.accountsIdentifier]):
                continue
            budgetAmount = self.budget[config.accountsIdentifier][account.name]
            if budgetAmount == 0:
                percentage = 0
            else:
                percentage = account.total / budgetAmount * 100
            amount = account.total * factor
            s = (
                s
                + "{:<{accountPadding}} \t {difference}{currency} \t {:>{amountPadding}}{currency} / {budgetAmount}{currency} ({percentage:.0f}%)".format(
                    account.name,
                    amount,
                    difference=str(budgetAmount - amount),
                    accountPadding=accountPadding,
                    amountPadding=amountPadding,
                    currency=config.currency,
                    budgetAmount=str(budgetAmount),
                    percentage=percentage,
                )
                + "\n"
            )
        return s
