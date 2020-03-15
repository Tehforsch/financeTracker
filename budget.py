from typing import Dict
from pathlib import Path
import yaml
from yaml import FullLoader
import config
import util
from queryResult import BudgetResult
from amount import Amount
from period import Period
from util import QueryInput, FormatOptions
from ledger import Ledger

def getBudgetDict(budgetFilename: Path) -> Dict:
    with budgetFilename.open("r") as f:
        budgetDict = yaml.load(f, Loader=FullLoader)
        assert config.periodIdentifier in budgetDict
        budgetDict[config.periodIdentifier] = Period(budgetDict[config.periodIdentifier])
        assert config.accountsIdentifier in budgetDict
    for (k, v) in budgetDict[config.accountsIdentifier].items():
        budgetDict[config.accountsIdentifier][k] = Amount(v.replace(config.currency, ""))
    return budgetDict

def compareToBudget(ledger_: Ledger, budgetFilename: Path, queryInput: QueryInput, formatOptions: FormatOptions) -> None:
    budgetDict = getBudgetDict(budgetFilename)
    budgetDict = extrapolate(budgetDict, queryInput.period)
    # WHY are namedtuples immutable? This code is awful but I am so tired
    queryInput = QueryInput(budgetDict[config.accountsIdentifier], queryInput.timeframe, queryInput.period, queryInput.exactMatch)
    queryResult = ledger_.periodicAccountQuery(queryInput)
    for (timeframe, result) in queryResult:
        result = BudgetResult(result, budgetDict)
        print(timeframe)
        print(result.toStr(formatOptions, factor=1))

def extrapolate(budgetDict: Dict, period: Period) -> Dict:
    numPeriodsPerPrint = util.dividePeriods(period, budgetDict[config.periodIdentifier])
    budgetDict[config.accountsIdentifier] = dict_multiply(budgetDict[config.accountsIdentifier], numPeriodsPerPrint)
    return budgetDict

def dict_multiply(d: Dict, factor: float) -> Dict:
    return dict((k, v * factor) for (k, v) in d.items())
