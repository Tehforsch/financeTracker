import config
import yaml
from ledger import Transaction

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

def createManualEntry():
    localtime = time.localtime()
    date = str(localtime.tm_year) + "." + str(localtime.tm_mon) + "." + str(localtime.tm_mday)
    account = formatAccountInput(input("Account: "))
    payor = input("Payor: ")
    amount = float(input("Amount you were given (negative if you spent): "))
    amount = ("%.2f" % round(amount,2))
    st = date + "\t" + payor + "\n\t{}    ".format(cashAccount) + amount + "€\n\t" + account + "\n"
    return st

def checkAccountExists(ledger, account):
    return account in ledger.accounts

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

def getAccountInput(ledger, entry):
    print("Please enter account for this transaction (or '{}' to create automatic account):".format(config.addAutomaticAccountString))
    print(entry)
    accountInput = input()
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
        sourceAccount = getAccount(ledger, entry)
        targetAccount = config.checkingAccount
        yield Transaction(entry.amount, sourceAccount, targetAccount, entry.originator, entry.date, entry.usage)
    writeAutomaticAccounts()

automaticAccounts = readAutomaticAccounts()
