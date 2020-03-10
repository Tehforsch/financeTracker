import config
from decimal import Decimal

class Account:
    def __init__(self, rawName):
        self.rawName = rawName
        self.superAccount = None
        self.amount = Decimal(0)
        self.subAccounts = []

    def addAccount(self, account):
        self.subAccounts.append(account)
        account.superAccount = self

    @property
    def name(self):
        if self.superAccount is None:
            return ""
        else:
            if self.superAccount.name == "":
                return self.rawName
            else:
                return self.superAccount.name + config.accountSeparator + self.rawName

    def isEmpty(self):
        return self.total == 0 and all(sub.total == 0 for sub in self.subAccounts)

    def getAllAccounts(self):
        return [self] + [subAcc for acc in self.subAccounts for subAcc in acc.getAllAccounts()]

    def gather(self, accountPredicate):
        return [acc for acc in self.getAllAccounts() if accountPredicate(acc)]

    @property
    def total(self):
        return self.amount + sum(acc.total for acc in self.subAccounts)
    
    def reset(self):
        self.amount = 0
        for acc in self.subAccounts:
            acc.reset()

    @property
    def level(self):
        if self.superAccount is None:
            return 0
        else:
            return 1+self.superAccount.level

    def getAccount(self, accountName):
        try:
            acc = next(acc for acc in self.getAllAccounts() if acc.name == accountName)
            return acc
        except StopIteration:
            raise StopIteration("No such account: {}".format(accountName))

    def clone(self, superAccount=None):
        newAcc = Account(self.rawName)
        newAcc.amount = self.amount
        newAcc.superAccount=superAccount
        newAcc.subAccounts = [acc.clone(self) for acc in self.subAccounts]
        return newAcc

    def __str__(self):
        return self.name

    def __eq__(self, account):
        return self.name == account.name

    def __hash__(self):
        return self.name.__hash__()
