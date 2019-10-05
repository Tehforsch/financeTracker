from pathlib import Path

currency = "€"

automaticAccountsFile = Path("scripts/automaticAccounts")
automaticAccountsFile = Path("scripts/automaticAccounts")

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

