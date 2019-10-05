from pathlib import Path

financeTrackerPath = "/home/toni/projects/financeTracker/"

currency = "€"

automaticAccountsFile = Path(financeTrackerPath, "data/automaticAccounts")
automaticAccountsFile = Path(financeTrackerPath, "data/automaticAccounts")

validBaseAccounts = ["reimbursement", "assets", "income", "liabilities", "expenses", "equity"]
cashAccount = "expenses:cash"

addAutomaticAccountString = "automatic"

checkingAccount = "assets:bankDiba"

accountSeparator = ":"

# budget files
periodIdentifier = "period"
accountsIdentifier = "accounts"

defaultDateFormat = "%Y-%m-%d"

backupFolder = "backup"
backupFormat = "%Y-%m-%d-%H-%M-%S"

day = "day"
week = "week"
month = "month"
year = "year"
periods = [day, week, month, year]

