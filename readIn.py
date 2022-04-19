from pathlib import Path
import datetime
import csv
import logging
import inputHandler
import config
from amount import Amount

class Entry:
    def __init__(self, line, keys, quantityNames):
        assert len(line) == len(keys), "Too few entries in line. Probably not enough lines skipped for this file? Line for reference: {}".format(line)
        self.date = Entry.getDate(line[keys.index(quantityNames["date"])])
        self.originator = Entry.getOriginator(line[keys.index(quantityNames["originator"])])
        self.name = line[keys.index(quantityNames["name"])]
        self.usage = line[keys.index(quantityNames["usage"])]
        self.amount = -Entry.readGermanAmountString(line[keys.index(quantityNames["amount"])])

    @staticmethod
    def getOriginator(string):
        return " ".join(string.split())

    @staticmethod
    def getDate(dateStr):
        return datetime.datetime.strptime(dateStr, '%d.%m.%Y').date()

    @staticmethod
    def readGermanAmountString(string):
        return Amount(string.replace(".", "").replace(",", "."))

    def isSameTransaction(self, transaction):
        assert type(self.amount) == Amount and type(transaction.amount) == Amount, f"Wrong types: {type(self.amount)} {type(transaction.amount)}"
        return [self.date, self.originator, self.amount] == [transaction.date, transaction.originator, transaction.amount]

    def __str__(self):
        return "{}:\n\t{}\n\t{}\n\t{}\n\t{}{}".format(self.date, self.name, self.originator, self.usage, self.amount, config.currency)

def readDefaultCsv(fileHandle, keys, quantityNames, delimiter=",", skip=0):
    reader = csv.reader(fileHandle, delimiter=delimiter)
    lines = [line for line in reader][skip:]
    for line in lines:
        print(line)
    lines = [Entry(line, keys, quantityNames) for line in lines]
    return lines

def getDibaCsv(dibaFile):
    keys = ["Buchung", "Valuta", "Auftraggeber/Empfänger", "Buchungstext", "Verwendungszweck", "Saldo", "Währung", "Betrag", "Währung"]
    quantityNames = {
            "date": "Buchung",
            "originator": "Auftraggeber/Empfänger",
            "name": "Buchungstext",
            "usage": "Verwendungszweck",
            "amount": "Betrag"
            }
    with dibaFile.open("r", encoding="latin1") as f:
        return readDefaultCsv(f, keys, quantityNames, delimiter=";", skip=14)

def readEntriesFromCsvFile(args, csvFile):
    # For now only implemented for DiBa specific csv files.
    # To extend this add input args that control the origin bank (or simply the format)
    # of the input file
    return getDibaCsv(csvFile)

def getNewEntries(ledger, entries):
    oldEntries = [entry for entry in entries if any(entry.isSameTransaction(transaction) for transaction in ledger.transactions)]
    print("THESE ENTRIES ARE ALREADY IN THE BOOK:")
    for entry in oldEntries:
        print(entry)
    return [entry for entry in entries if not any(entry.isSameTransaction(transaction) for transaction in ledger.transactions)]

def getNewTransactions(ledger, entries):
    newEntries = getNewEntries(ledger, entries)
    newTransactions = inputHandler.getTransactionsFromCsvEntries(ledger, newEntries)
    for transaction in newTransactions:
        ledger.addTransaction(transaction)

def read(ledger, args):
    for csvFile in args.read:
        entries = readEntriesFromCsvFile(args, csvFile)
        entries.sort(key=lambda entry: entry.date)
        newTransactions = getNewTransactions(ledger, entries)
