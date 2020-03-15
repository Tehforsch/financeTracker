import itertools
import numpy as np
import matplotlib.pyplot as plt
import util
import config


def datePlot(dates, dataSets, title="", xlabel="", ylabel="", labels=[""]):
    fig, ax = plt.subplots()
    # ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    for (dataSet, label) in itertools.zip_longest(dataSets, labels):
        ax.plot_date(dates, dataSet, label=label, linestyle="-")
    ax.grid()
    ax.legend()
    plt.show()

def getQuery(ledger, accounts, start, end, period, invert=False, totals=False):
    if totals:
        raise NotImplementedError
        queryResult = ledger.periodicAccountQuery(accounts, start, end, period)
    else:
        queryResult = ledger.periodicAccountQuery(accounts, start, end, period)
    return [(-1 if invert else 1) * float(sum(getAccountTotal(query, account) for account in accounts)) for (period, query) in queryResult]

def getAccountTotal(query, accountName):
    try:
        return query.getAccount(accountName).total
    except StopIteration:
        return 0

def getAccountListDifference(accountList1, accountList2):
    return [account1 for account1 in accountList1 if not any(account1 == account2 or account1.startswith(account2) for account2 in accountList2)]

def smoothData(data, N=12):
    return np.convolve(data, np.ones((N,))/N, mode='valid')

def smoothDates(dates, N=12):
    return dates[N//2-1:len(dates)-N//2]

def plotAccounts(ledger, accountLists, start, end, xlabel, ylabel, labels, smooth=False, invert=None, totals=False):
    print(accountLists)
    if invert is None:
        invert = [False for _ in accountLists]
    dates = [d[0] for d in util.subdivideTime(start, end, config.month)]
    data = [getQuery(ledger, accountList, start, end, config.month, invert=invert, totals=totals) for (accountList, invert) in zip(accountLists, invert)]
    if smooth:
        dates = smoothDates(dates, N=smooth)
        data = [smoothData(d, N=smooth) for d in data]
    datePlot(dates, data, xlabel=xlabel, ylabel=ylabel, labels=labels)

def plotNetworth(ledger, start, end, smooth=False):
    start = ledger.getFirstTransactionDate()
    plotAccounts(ledger, [["assets", "liabilities"], ["assets"], ["liabilities"]], start, end, "Month", "Amount [€]", ["Net worth", "Assets", "Liabilities"], smooth=smooth, invert=[False, False, True], totals=True)

def plotExpensesIncome(ledger, start, end, smooth=False):
    plotAccounts(ledger, [["expenses"], ["income"]], start, end, "Month", "Monthly expenses [€]", ["Expenses", "Income"], smooth=smooth, invert=[False, True])

def plotLivingLuxury(ledger, start, end, smooth=False):
    allExpenses = [acc.name for acc in ledger.getAccount("expenses").getAllAccounts()]
    allExpenses.remove("expenses")
    listOfLivingExpenses = ["expenses:{}".format(account) for account in ["bhw", "food", "hausgeld", "insurance", "internet", "medical", "rent", "publicTransport", "strom", "uni", "wohnung"]]
    listOfLuxuryExpenses = getAccountListDifference(allExpenses, listOfLivingExpenses)
    print("Assuming the following expenses are luxuries:")
    print("\n".join(sorted(listOfLuxuryExpenses)))
    plotAccounts(ledger, [listOfLivingExpenses, listOfLuxuryExpenses], start, end, "Month", "Monthly expenses [€]", ["Living", "Luxury"], smooth=smooth)

def plotLivingExpenses(ledger, start, end, smooth=False):
    expenses = ["food", "wohnung", "strom", "publicTransport", "internet", "insurance", "bhw", "medical"]
    listOfLivingExpenses = ["expenses:{}".format(account) for account in expenses]
    plotAccounts(ledger, [[expense] for expense in listOfLivingExpenses], start, end, "Month", "Monthly expenses [€]", expenses, smooth=smooth)

def plotLuxuryExpenses(ledger, start, end, smooth=False):
    expenses = ["vacation", "misc"]
    listOfLivingExpenses = ["expenses:{}".format(account) for account in expenses]
    plotAccounts(ledger, [[expense] for expense in listOfLivingExpenses], start, end, "Month", "Monthly expenses [€]", expenses, smooth=smooth)

def doPlots(ledger, args):
    for plotName in args.plot:
        plotFunction, smoothPeriod = plots[plotName]
        plotFunction(ledger, args.start, args.end, smooth=smoothPeriod)

plots = {
        "networth": (plotNetworth, 0),
        "expensesIncome": (plotExpensesIncome, 12),
        "livingLuxury": (plotLivingLuxury, 12),
        "living": (plotLivingExpenses, 0),
        "luxury": (plotLuxuryExpenses, 0),
        }

