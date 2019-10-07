from pathlib import Path

financeDataPath = "/home/toni/resource/finances/data/"

currency = "€"

automaticAccountsFile = Path(financeDataPath, "automaticAccounts")
automaticAccountsFile = Path(financeDataPath, "automaticAccounts")

validBaseAccounts = ["reimbursement", "assets", "income", "liabilities", "expenses", "equity"]
cashAccount = "expenses:cash"

addAutomaticAccountString = "automatic"

checkingAccount = "assets:bankDiba"

accountSeparator = ":"

# budget files
periodIdentifier = "period"
accountsIdentifier = "accounts"

defaultDateFormat = "%Y-%m-%d"

backupFolder = Path(financeDataPath, "backup")
backupFormat = "%Y-%m-%d-%H-%M-%S"

day = "day"
week = "week"
month = "month"
year = "year"
periods = [day, week, month, year]
