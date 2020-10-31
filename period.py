from dateutil.relativedelta import relativedelta
from datetime import timedelta
import config


class Period:
    def __init__(self, name: str) -> None:
        self.name = name
        if name == "infinite":
            return
        self.delta = {
            config.day: relativedelta(days=1),
            config.week: relativedelta(days=7),
            config.fourweeks: relativedelta(weeks=4),
            config.month: relativedelta(months=+1),
            config.year: relativedelta(years=+1),
        }[name]
        self.days = {config.day: 1, config.week: 7, config.fourweeks: 28, config.month: 365 / 12, config.year: 365}[name]

    def __str__(self) -> str:
        return "Period({})".format(self.name)

    def isInfinite(self) -> bool:
        return self.name == "infinite"
