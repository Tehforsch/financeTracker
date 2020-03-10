import datetime
from decimal import Decimal

class Transaction:
    def __init__(self, amount, sourceAccount, targetAccount, originator, date, usage):
        self.amount = amount
        self.sourceAccount = sourceAccount
        self.targetAccount = targetAccount
        self.originator = originator
        self.usage = usage
        self.date = date

    def __str__(self):
        # return "{}\n{}\n{}\n{}".format(self.date, self.originator, self.usage, self.amount)
        return "{}:{}->{}->{}".format(self.date, self.sourceAccount.name, self.amount, self.targetAccount.name)

    def serialize(self):
        return ";".join([str(self.date), self.sourceAccount.name, str(self.amount), self.targetAccount.name, self.originator, self.usage])

    @staticmethod
    def deserialize(line, accounts):
        dateIso, sourceAccountName, amount, targetAccountName, originator, usage = line.replace("\n", "").split(";")
        sourceAccount = next(account for account in accounts if account.name == sourceAccountName)
        targetAccount = next(account for account in accounts if account.name == targetAccountName)
        date = datetime.date.fromisoformat(dateIso)
        return Transaction(Decimal(amount), sourceAccount, targetAccount, originator, date, usage)
