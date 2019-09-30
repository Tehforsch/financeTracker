from ledger import Ledger, Transaction
import readIn
from pathlib import Path
import argparse

def setupArgs():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('journal', 
                        type=Path,
                        help='name of the journal file(s) to read')
    parser.add_argument('--balance', 
                        default=None,
                        nargs="*",
                        help='Show the balance of the accounts matching the query (default: all accounts)')
    # parser.add_argument('--register', 
                        # default=None,
                        # nargs="*",
                        # help='Show individual transactions of the accounts matching the query (default: all accounts)')
    parser.add_argument('--read', 
                        default=None,
                        nargs="+",
                        type=Path,
                        help='Read the specified csv files and add them to the journal')
    parser.add_argument('--empty', default=False)

    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = setupArgs()
    ledger = Ledger.read(args.journal)
    if args.balance is not None:
        ledger.printBalance(args)
    # if args.register is not None:
        # ledger.printRegister(args)
    if args.read is not None:
        readIn.read(ledger, args)
    ledger.write(args.journal)
