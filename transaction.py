from typing import List
import datetime
from amount import Amount
from account import Account

class Transaction:
    def __init__(self, amount: Amount, sourceAccount: Account, targetAccount: Account, originator: str, date: datetime.date, usage: str) -> None:
        self.amount = amount
        self.sourceAccount = sourceAccount
        self.targetAccount = targetAccount
        self.originator = originator
        self.usage = usage
        self.date = date

    def __str__(self) -> str:
        # return "{}\n{}\n{}\n{}".format(self.date, self.originator, self.usage, self.amount)
        return "{}:{}->{}->{}".format(self.date, self.sourceAccount.name, self.amount, self.targetAccount.name)

    def serialize(self) -> str:
        return ";".join([str(self.date), self.sourceAccount.name, str(self.amount), self.targetAccount.name, self.originator, self.usage])

    @staticmethod
    def deserialize(line: str, accounts: List[Account]) -> "Transaction":
        dateIso, sourceAccountName, amount, targetAccountName, originator, usage = line.replace("\n", "").split(";")
        sourceAccount = next(account for account in accounts if account.name == sourceAccountName)
        targetAccount = next(account for account in accounts if account.name == targetAccountName)
        date = datetime.date.fromisoformat(dateIso)
        return Transaction(Amount(amount), sourceAccount, targetAccount, originator, date, usage)

    def apply(self) -> None:
        self.sourceAccount.amount -= self.amount
        self.targetAccount.amount += self.amount
