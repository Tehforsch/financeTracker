import datetime
from transaction import Transaction

class Timeframe:
    def __init__(self, start: datetime.date, end: datetime.date) -> None:
        self.start = start
        self.end = end

    def __repr__(self) -> str:
        return "{} - {}".format(self.start, self.end)

    def containsTransaction(self, transaction: Transaction) -> bool:
        return (self.start <= transaction.date) and (transaction.date <= self.end)
