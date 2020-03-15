from typing import Union
from decimal import Decimal
import config

class Amount(Decimal):
    def __repr__(self) -> str:
        return "{}{}".format(self, config.currency)

    def __add__(self, other: Union[int, Decimal, float, "Amount"]) -> "Amount":
        return Amount(Decimal(self) + Decimal(other))

    def __sub__(self, other: Union[int, Decimal, float, "Amount"]) -> "Amount":
        return Amount(Decimal(self) - Decimal(other))

    def __mul__(self, other: Union[int, Decimal, float, "Amount"]) -> "Amount":
        return Amount(Decimal(self) * Decimal(other))
