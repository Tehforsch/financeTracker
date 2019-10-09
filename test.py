import ledger
import yamlIo
from ledger import Ledger
from transaction import Transaction
from account import Account
import unittest
from decimal import Decimal
from pathlib import Path
import datetime

class TestLedger(unittest.TestCase):
    def testSubTransactions(self):
        ledger = oneSymmetricTransactionSetup()
        self.assertEqual(ledger.topAccount.total, 0)
        self.assertEqual(ledger.topAccount.subAccounts[0].total, -ledger.topAccount.subAccounts[1].total)

    def testTotalTransactions(self):
        ledger = oneAsymmetricTransactionSetup()
        self.assertEqual(ledger.topAccount.total, 0)
        self.assertEqual(ledger.topAccount.amount, -ledger.topAccount.subAccounts[1].total)
        self.assertEqual(ledger.topAccount.subAccounts[0].total, 0)

    def testWriting(self):
        ledger = oneSymmetricTransactionSetup()
        out = Path("test/out")
        yamlIo.write(ledger, out)

    def testQueries(self):
        ledger = someTransactionsSetup()
        self.assertEqual(ledger.topAccount.total, 0)
        result = ledger.patternAccountQuery(None, datetime.date(2000,1,2), datetime.date(2000,1,4))
        self.assertEqual(ledger.topAccount.total, 0)
        self.assertEqual(result[1].amount, Decimal("3.3"))
        result = ledger.patternAccountQuery(None, datetime.date(2000,1,1), datetime.date(2000,1,5))
        self.assertEqual(ledger.topAccount.total, 0)
        self.assertEqual(result[1].amount, Decimal("5.5"))
        result = ledger.patternTransactionQuery(None, datetime.date(2000,1,2), datetime.date(2000,1,4))
        self.assertEqual(len(result), 6)


def basicLedgerSetup():
    ledger = Ledger()
    top = ledger.topAccount
    top.addAccount(Account("sub1"))
    top.addAccount(Account("sub2"))
    return ledger

def oneSymmetricTransactionSetup():
    ledger = basicLedgerSetup()
    top = ledger.topAccount
    amount = Decimal("1.1")
    t = Transaction(amount, top.subAccounts[0], top.subAccounts[1], None, None, None)
    ledger.addTransaction(t)
    return ledger

def oneAsymmetricTransactionSetup():
    ledger = basicLedgerSetup()
    top = ledger.topAccount
    amount = Decimal("1.1")
    t = Transaction(amount, top, top.subAccounts[1], None, None, None)
    ledger.addTransaction(t)
    return ledger

def someTransactionsSetup():
    ledger = basicLedgerSetup()
    top = ledger.topAccount
    amount = Decimal("1.1")
    t1 = Transaction(amount, top, top.subAccounts[0], None, datetime.date(2000, 1, 1), None)
    t2 = Transaction(amount, top, top.subAccounts[0], None, datetime.date(2000, 1, 2), None)
    t3 = Transaction(amount, top, top.subAccounts[0], None, datetime.date(2000, 1, 3), None)
    t4 = Transaction(amount, top, top.subAccounts[0], None, datetime.date(2000, 1, 4), None)
    t5 = Transaction(amount, top, top.subAccounts[0], None, datetime.date(2000, 1, 5), None)
    ledger.addTransaction(t1)
    ledger.addTransaction(t2)
    ledger.addTransaction(t3)
    ledger.addTransaction(t4)
    ledger.addTransaction(t5)
    t1 = Transaction(amount, top, top.subAccounts[1], None, datetime.date(2000, 1, 1), None)
    t2 = Transaction(amount, top, top.subAccounts[1], None, datetime.date(2000, 1, 2), None)
    t3 = Transaction(amount, top, top.subAccounts[1], None, datetime.date(2000, 1, 3), None)
    t4 = Transaction(amount, top, top.subAccounts[1], None, datetime.date(2000, 1, 4), None)
    t5 = Transaction(amount, top, top.subAccounts[1], None, datetime.date(2000, 1, 5), None)
    ledger.addTransaction(t1)
    ledger.addTransaction(t2)
    ledger.addTransaction(t3)
    ledger.addTransaction(t4)
    ledger.addTransaction(t5)
    return ledger

if __name__ == '__main__':
    unittest.main()

