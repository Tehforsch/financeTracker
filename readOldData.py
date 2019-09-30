import itertools
from ledger import Ledger, Transaction
import config
from pathlib import Path
import yaml
from decimal import Decimal
import datetime

def getDecimal(amountStr):
    assert config.currency in amountStr
    return Decimal(amountStr.replace(config.currency, ""))

def readLedger():
    ledger = Ledger()

    with open("scripts/onlyEntries", "r") as f:
        lines = [l.rstrip("\n") for l in f.readlines()]
        entries = (list(lines) for (isEmpty, lines) in itertools.groupby(lines, lambda line: line.rstrip("\n").strip() == "") if not isEmpty)
        for e in entries:
            dateStr, *originator = e[0].split()
            date = datetime.datetime.strptime(dateStr, '%Y.%m.%d').date()
            originator = " ".join(originator)
            account1, amount = e[1].split()
            amount = getDecimal(amount)
            if len(e) == 3:
                account2 = e[2].split()[0]
                ledger.addTransaction(Transaction(-amount, account1, account2, originator, date=date, usage=""))
            else:
                assert len(e) == 4
                account2, amount2 = e[2].split()
                account3 = e[3].split()[0]
                amount2 = getDecimal(amount2)
                ledger.addTransaction(Transaction(amount2, account1, account2, originator, date=date, usage=""))
                ledger.addTransaction(Transaction(-amount - amount2, account1, account3, originator, date=date, usage=""))
    return ledger

# ledger = Ledger.read(Path("data/finances"))
ledger = readLedger()
ledger.write(Path("data/finances"))
