from ledger import Ledger, Transaction
import budget
import readIn
from pathlib import Path
import argparse
import datetime
import config
import shutil

def isoFormat(string):
    return datetime.datetime.strptime(string, config.defaultDateFormat).date()

def setupArgs():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('journal', 
                        type=Path,
                        help='name of the journal file(s) to read')
    parser.add_argument('--balance', 
                        default=None,
                        nargs="*",
                        help='Show the balance of the accounts matching the query (default: all accounts)')
    parser.add_argument('--register', 
                        default=None,
                        nargs="*",
                        help='Show individual transactions of the accounts matching the query (default: all accounts)')
    parser.add_argument('--budget', 
                        type=Path,
                        help='Read the budget file and compare accounts to it')
    parser.add_argument('--read', 
                        default=None,
                        nargs="+",
                        type=Path,
                        help='Read the specified csv files and add them to the journal')
    parser.add_argument('--empty', default=False, action="store_true")
    parser.add_argument('--start', default=None, type=isoFormat)
    parser.add_argument('--end', default=None, type=isoFormat)
    parser.add_argument('--period', default=config.month, type=str, choices=config.periods)

    args = parser.parse_args()
    return args

def setDefaultArgs(args, ledger):
    """Set some default args that can only be determined once the ledger file has been read"""
    if args.start is None:
        args.start = ledger.getFirstTransactionDate()
    if args.end is None:
        args.end = ledger.getLastTransactionDate()

def backupLedger():
    source = args.journal
    target = Path(config.backupFolder, datetime.datetime.today().strftime(config.backupFormat))
    shutil.copy(str(source), str(target))

if __name__ == "__main__":
    args = setupArgs()
    ledger = Ledger.read(args.journal)
    setDefaultArgs(args, ledger)
    if args.read is not None:
        # Create backup ledger
        backupLedger()
        readIn.read(ledger, args)
        ledger.write(args.journal)
    else:
        if args.budget is not None:
            budget.compareToBudget(ledger, args)
        if args.balance is not None:
            ledger.printBalance(args)
        if args.register is not None:
            ledger.printRegister(args)

