import config
import yaml
from transaction import Transaction
import datetime
from decimal import Decimal
import util

def readAutomaticAccounts():
    with config.automaticAccountsFile.open("r") as f:
        return yaml.unsafe_load(f)

def writeAutomaticAccounts():
    yaml.dump(automaticAccounts, config.automaticAccountsFile.open("w"))

def formatAccountInput(inp):
    split = inp.split(":")
    if not split[0] in config.validBaseAccounts:
        account = ":".join(["expenses"] + split)
        print("Converting this account to {}".format(account))
        return account
    elif split[0] == "reimbursement":
        return ":".join(["assets"] + split)
    else:
        return ":".join(split)

def getManualTransaction(ledger):
    print("Adding a new cash entry.")
    print("Date? YYYY-MM-DD (leave empty for today)")
    date = inputDefault(datetime.datetime.today().date())
    if type(date) == str:
        date = util.dateFromIsoformat(date)
    print("Source account? (Leave empty for cash)")
    source = ledger.getAccountFromStr(getAccountInput(ledger, None, defaultAccount="expenses:cash"))
    print("Target account?")
    target = ledger.getAccountFromStr(getAccountInput(ledger, None))
    amount = Decimal(input("Amount you spent (negative if you were given): "))
    return Transaction(amount, source, target, config.defaultOriginator, date, "")

def addManualTransaction(ledger):
    ledger.addTransaction(getManualTransaction(ledger))

def checkAccountExists(ledger, account):
    return account in (acc.name for acc in ledger.topAccount.getAllAccounts())

def createAutomaticAccount(entry):
    decision = input("Create automatic account by originator, by usage or both?\n")
    if decision == "originator":
        print("Originator for automatic account? (leave empty if you want to keep '{}')".format(entry.originator))
        automaticOriginator = inputDefault(entry.originator)
        automaticUsage = ""
    elif decision == "usage":
        print("Usage for automatic account? (leave empty if you want to keep '{}')".format(entry.usage))
        automaticUsage = inputDefault(entry.usage)
        automaticOriginator = ""
    else:
        print("Originator for automatic account? (leave empty if you want to keep '{}')".format(entry.originator))
        automaticOriginator = inputDefault(entry.originator)
        print("Usage for automatic account? (leave empty if you want to keep '{}')".format(entry.usage))
        automaticUsage = inputDefault(entry.usage)
    automaticAccount = formatAccountInput(input("Target account?\n"))
    automaticAccounts.append({
        "usage": automaticUsage,
        "originator": automaticOriginator,
        "account": automaticAccount
        })
    return automaticAccount

def inputDefault(defaultString):
    inp = input()
    if inp == "":
        return defaultString
    else:
        return inp

def getAccountInput(ledger, entry, canAddAutomatic=True, defaultAccount=None):
    print("Please enter account for this transaction (or '{}' to create automatic account):".format(config.addAutomaticAccountString))
    if entry is not None:
        print(entry)
    accountInput = input()
    if accountInput == "" and defaultAccount is not None:
        accountInput = defaultAccount
    if accountInput == config.addAutomaticAccountString:
        accountInput = createAutomaticAccount(entry)
    else:
        accountInput = formatAccountInput(accountInput)
    if not checkAccountExists(ledger, accountInput):
        print(accountInput)
        print("This account does not exist yet. Do you want to create it? y/N")
        inp = input()
        if inp == "y":
            return accountInput
        else:
            return getAccountInput(ledger, entry)
    else:
        return accountInput

def automaticAccountMatches(automaticAccount, entry):
    return (automaticAccount["originator"] == "" or automaticAccount["originator"] in entry.originator) and (automaticAccount["usage"] == "" or automaticAccount["usage"] in entry.usage)


def getAccount(ledger, entry):
    for automaticAccount in automaticAccounts:
        if automaticAccountMatches(automaticAccount, entry):
            account = automaticAccount["account"]
            print("Found automatically assignable account: {}\n".format(account))
            break
    else:
        account = getAccountInput(ledger, entry)
    return formatAccountInput(account)

def getTransactionsFromCsvEntries(ledger, entries):
    for entry in entries:
        targetAccount = ledger.getAccountFromStr(getAccount(ledger, entry))
        sourceAccount = ledger.getAccountFromStr(config.checkingAccount)
        yield Transaction(entry.amount, sourceAccount, targetAccount, entry.originator, entry.date, entry.usage)
    writeAutomaticAccounts()

automaticAccounts = readAutomaticAccounts()
