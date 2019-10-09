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
