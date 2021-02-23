import argparse
from typing import Dict
from pathlib import Path
import yaml
import config
import util
from queryResult import BudgetResult
from amount import Amount
from period import Period
from timeframe import Timeframe
from util import QueryInput, FormatOptions
from ledger import Ledger
from amount import Amount


def getBudgetDict(budgetFilename: Path) -> Dict:
    with budgetFilename.open("r") as f:
        budgetDict = yaml.load(f, Loader=SafeLoader)
        assert config.periodIdentifier in budgetDict
        budgetDict[config.periodIdentifier] = Period(budgetDict[config.periodIdentifier])
        assert config.accountsIdentifier in budgetDict
    for (k, v) in budgetDict[config.accountsIdentifier].items():
        budgetDict[config.accountsIdentifier][k] = Amount(v.replace(config.currency, ""))
    return budgetDict


def compareToBudget(ledger_: Ledger, budgetFilename: Path, queryInput: QueryInput, formatOptions: FormatOptions) -> None:
    budgetDict = getBudgetDict(budgetFilename)
    periodBudgetDict = extrapolate(budgetDict, queryInput.period)
    # WHY are namedtuples immutable? This code is awful but I am so tired
    queryInput = QueryInput(periodBudgetDict[config.accountsIdentifier], queryInput.timeframe, queryInput.period, queryInput.exactMatch)
    queryResult = ledger_.periodicAccountQuery(queryInput)
    for (timeframe, result) in queryResult:
        result = BudgetResult(result, periodBudgetDict)
        print(timeframe)
        print(result.toStr(formatOptions, factor=1))
    # Show total
    totalBudgetDict = extrapolateToTimeframe(budgetDict, queryInput.timeframe)
    queryInput = QueryInput(totalBudgetDict[config.accountsIdentifier], queryInput.timeframe, Period("infinite"), queryInput.exactMatch)
    result = BudgetResult(ledger_.patternAccountQuery(queryInput), totalBudgetDict)
    print("TOTAL")
    print(result.toStr(formatOptions, factor=1))


def extrapolate(budgetDict: Dict, period: Period) -> Dict:
    numPeriodsPerPrint = util.dividePeriods(period, budgetDict[config.periodIdentifier])
    budgetDict[config.accountsIdentifier] = dict_multiply(budgetDict[config.accountsIdentifier], numPeriodsPerPrint)
    return budgetDict


def extrapolateToTimeframe(budgetDict: Dict, timeframe: Timeframe) -> Dict:
    numPeriodsPerPrint = timeframe.days / budgetDict[config.periodIdentifier].days
    budgetDict[config.accountsIdentifier] = dict_multiply(budgetDict[config.accountsIdentifier], numPeriodsPerPrint)
    return budgetDict


def dict_multiply(d: Dict, factor: float) -> Dict:
    return dict((k, Amount(v * factor)) for (k, v) in d.items())
