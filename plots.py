import itertools
import numpy as np
import matplotlib.pyplot as plt
import util
import config
from timeframe import Timeframe
from period import Period
from util import QueryInput


def datePlot(dates, dataSets, title="", xlabel="", ylabel="", labels=[""]):
    fig, ax = plt.subplots()
    # ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    for (dataSet, label) in itertools.zip_longest(dataSets, labels):
        ax.plot_date(dates, dataSet, label=label, linestyle="-")
    ax.grid()
    ax.legend()
    plt.show()


def getQuery(ledger, accounts, timeframe, period, invert=False, totals=False):
    if totals:
        raise NotImplementedError
        queryResult = ledger.periodicAccountQuery(QueryInput(accounts, timeframe, period, exactMatch=False))
    else:
        queryResult = ledger.periodicAccountQuery(QueryInput(accounts, timeframe, period, exactMatch=False))
    return [(-1 if invert else 1) * float(sum(getAccountTotal(query, account) for account in accounts)) for (period, query) in queryResult]


def getAccountTotal(query, accountName):
    try:
        return query.getAccount(accountName).total
    except StopIteration:
        return 0


def getAccountListDifference(accountList1, accountList2):
    return [account1 for account1 in accountList1 if not any(account1 == account2 or account1.startswith(account2) for account2 in accountList2)]


def smoothData(data, N=12):
    return np.convolve(data, np.ones((N,)) / N, mode="valid")


def smoothDates(dates, N=12):
    return dates[N // 2 - 1 : len(dates) - N // 2]


def plotAccounts(ledger, accountLists, timeframe, xlabel, ylabel, labels, smooth=False, invert=None, totals=False):
    print(accountLists)
    if invert is None:
        invert = [False for _ in accountLists]
    dates = [d.start for d in util.subdivideTime(timeframe, Period(config.month))]
    data = [getQuery(ledger, accountList, timeframe, Period(config.month), invert=invert, totals=totals) for (accountList, invert) in zip(accountLists, invert)]
    if smooth:
        dates = smoothDates(dates, N=smooth)
        data = [smoothData(d, N=smooth) for d in data]
    datePlot(dates, data, xlabel=xlabel, ylabel=ylabel, labels=labels)


def plotNetworth(ledger, timeframe, smooth=False):
    start = ledger.getFirstTransactionDate()
    plotAccounts(
        ledger,
        [["assets", "liabilities"], ["assets"], ["liabilities"]],
        Timeframe(start, timeframe.end),
        "Month",
        "Amount [€]",
        ["Net worth", "Assets", "Liabilities"],
        smooth=smooth,
        invert=[False, False, True],
        totals=True,
    )


def plotExpensesIncome(ledger, timeframe, smooth=False):
    plotAccounts(ledger, [["expenses"], ["income"]], timeframe, "Month", "Monthly expenses [€]", ["Expenses", "Income"], smooth=smooth, invert=[False, True])


def plotLivingLuxury(ledger, timeframe, smooth=False):
    allExpenses = [acc.name for acc in ledger.getAccount("expenses").getAllAccounts()]
    allExpenses.remove("expenses")
    listOfLivingExpenses = [
        "expenses:{}".format(account)
        for account in ["bhw", "food", "hausgeld", "insurance", "internet", "medical", "rent", "publicTransport", "strom", "uni", "wohnung"]
    ]
    listOfLuxuryExpenses = getAccountListDifference(allExpenses, listOfLivingExpenses)
    print("Assuming the following expenses are luxuries:")
    print("\n".join(sorted(listOfLuxuryExpenses)))
    plotAccounts(ledger, [listOfLivingExpenses, listOfLuxuryExpenses], timeframe, "Month", "Monthly expenses [€]", ["Living", "Luxury"], smooth=smooth)


def plotLivingExpenses(ledger, timeframe, smooth=False):
    expenses = ["food", "wohnung", "strom", "publicTransport", "internet", "insurance", "bhw", "medical"]
    listOfLivingExpenses = ["expenses:{}".format(account) for account in expenses]
    plotAccounts(ledger, [[expense] for expense in listOfLivingExpenses], timeframe, "Month", "Monthly expenses [€]", expenses, smooth=smooth)


def plotLuxuryExpenses(ledger, timeframe, smooth=False):
    expenses = ["vacation", "misc"]
    listOfLivingExpenses = ["expenses:{}".format(account) for account in expenses]
    plotAccounts(ledger, [[expense] for expense in listOfLivingExpenses], timeframe, "Month", "Monthly expenses [€]", expenses, smooth=smooth)


def doPlots(ledger, args):
    for plotName in args.plot:
        plotFunction, smoothPeriod = plots[plotName]
        plotFunction(ledger, args.timeframe, smooth=smoothPeriod)


plots = {
    "networth": (plotNetworth, 0),
    "expensesIncome": (plotExpensesIncome, 12),
    "livingLuxury": (plotLivingLuxury, 12),
    "living": (plotLivingExpenses, 0),
    "luxury": (plotLuxuryExpenses, 0),
}
