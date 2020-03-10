from ledger import Ledger
from transaction import Transaction
import budget
import readIn
from pathlib import Path
import argparse
import datetime
import config
import shutil
import inputHandler
import util
import plots
import csvIo
import decimal

def setupArgs():
    parser = argparse.ArgumentParser(description='Track finances and calculate queries')
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
    parser.add_argument('--empty', default=False, action="store_true", help="Print empty accounts?")
    parser.add_argument('--start', default=None, type=util.dateFromIsoformat, help="Start date")
    parser.add_argument('--end', default=None, type=util.dateFromIsoformat, help="End date")
    parser.add_argument('--period', default=config.infinite, type=str, choices=config.periods, help="Smallest period for which to aggregate entries in the register/budget commands")
    parser.add_argument('--cash', default=False, action="store_true", help="Add a cash transaction")
    parser.add_argument('--plot', 
                        default=None,
                        nargs="+",
                        type=str,
                        choices=list(plots.plots.keys()) + ["all"],
                        help='Show a plot showing the data.')
    parser.add_argument('--exact', default=False, action="store_true", help="Only accept exact pattern matches when specifying accounts (instead of any regex match)")
    parser.add_argument('--sum', default=False, action="store_true", help="Calculate the sum of the values of all the matching accounts for register/balance queries")
    parser.add_argument('--average', default=False, action="store_true", help="Show the average change per period of the account.")
    parser.add_argument('--invert', default=None, nargs="*", help="When calculating totals invert the passed accounts")


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
    ledger = csvIo.read(args.journal)
    setDefaultArgs(args, ledger)
    # Create backup ledger
    backupLedger()
    if args.read is not None:
        readIn.read(ledger, args)
        csvIo.write(ledger, args.journal)
    if args.cash:
        inputHandler.addManualTransaction(ledger)
        csvIo.write(ledger, args.journal)
    if args.budget is not None:
        if args.sum:
            budget.showRemainingMoney(ledger, args)
        else:
            budget.compareToBudget(ledger, args)
    if args.balance is not None:
        if args.average:
            ledger.printAverages(args.balance, args.start, args.end, args.period, printEmptyAccounts=args.empty, exactMatch=args.exact)
        else:
            ledger.printAccounts(args.balance, args.start, args.end, args.period, args.empty, exactMatch=args.exact, sumAllAccounts=args.sum)
    if args.register is not None:
        ledger.printTransactions(args.register, args.start, args.end, args.period, exactMatch=args.exact)
    if args.plot is not None:
        if "all" in args.plot:
            args.plot = sorted(list(plots.plots.keys()))
        plots.doPlots(ledger, args)

