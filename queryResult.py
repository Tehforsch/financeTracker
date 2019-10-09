import config

class TransactionQueryResult(list):
    def toStr(self):
        return "\n".join(str(x) for x in self)

class AccountQueryResult():
    def __init__(self, topAccount, accountPredicate):
        self.topAccount = topAccount.clone()
        self.accountPredicate = accountPredicate

    def toStr(self, printEmptyAccounts=False, sumAllAccounts=False):
        if sumAllAccounts:
            summed = sum(acc.amount for acc in self.topAccount.getAllAccounts() if self.accountPredicate(acc))
            return "{}: {}".format(self.topAccount.name, summed)
        else:
            predicate = lambda account: self.accountPredicate(account) and (printEmptyAccounts or not account.isEmpty())
            return self.accountToStr(predicate)

    def accountToStr(self, predicate):
        s = ""
        accountPadding = max(len(acc.name) for acc in self.topAccount.getAllAccounts())
        amountPadding = max(len(str(acc.total)) for acc in self.topAccount.getAllAccounts())
        for account in self.topAccount.getAllAccounts():
            if not predicate(account):
                continue
            numSpaces = account.level * 4
            indentation = numSpaces * " "
            s = s + "{:<{accountPadding}} \t {:>{amountPadding}}{currency}".format(indentation + account.rawName, str(account.total), accountPadding=accountPadding, amountPadding=amountPadding, currency=config.currency) + "\n"
        return s

    def __str__(self):
        return self.toStr()

    def getAccount(self, accountName):
        return self.topAccount.getAccount(accountName)
