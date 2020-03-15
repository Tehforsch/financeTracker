from typing import List, Optional, Callable, Any
import config
from amount import Amount


class Account:
    def __init__(self, rawName: str) -> None:
        self.rawName = rawName
        self.superAccount: Optional[Account] = None
        self.amount = Amount(0)
        self.subAccounts: List[Account] = []

    def addAccount(self, account: "Account") -> None:
        self.subAccounts.append(account)
        account.superAccount = self

    @property
    def name(self) -> str:
        if self.superAccount is None:
            return ""
        if self.superAccount.name == "":
            return self.rawName
        return self.superAccount.name + config.accountSeparator + self.rawName

    def isEmpty(self) -> bool:
        return self.total == 0 and all(sub.total == 0 for sub in self.subAccounts)

    def getAllAccounts(self) -> List["Account"]:
        return [self] + [subAcc for acc in self.subAccounts for subAcc in acc.getAllAccounts()]

    def gather(self, accountPredicate: Callable) -> List["Account"]:
        return [acc for acc in self.getAllAccounts() if accountPredicate(acc)]

    @property
    def total(self) -> Amount:
        return self.amount + Amount(sum(acc.total for acc in self.subAccounts))

    def reset(self) -> None:
        self.amount = Amount(0)
        for acc in self.subAccounts:
            acc.reset()

    @property
    def level(self) -> int:
        if self.superAccount is None:
            return 0
        return 1 + self.superAccount.level

    def getAccount(self, accountName: str) -> "Account":
        try:
            acc = next(acc for acc in self.getAllAccounts() if acc.name == accountName)
            return acc
        except StopIteration:
            raise StopIteration("No such account: {}".format(accountName))

    def clone(self, superAccount: Optional["Account"] = None) -> "Account":
        newAcc = Account(self.rawName)
        newAcc.amount = self.amount
        newAcc.superAccount = superAccount
        newAcc.subAccounts = [acc.clone(self) for acc in self.subAccounts]
        return newAcc

    def __str__(self) -> str:
        return self.name

    def __eq__(self, account: Any) -> bool:
        return self.name == account.name

    def __hash__(self) -> int:
        return self.name.__hash__()
