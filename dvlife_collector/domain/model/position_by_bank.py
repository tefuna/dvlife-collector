from dataclasses import dataclass
from decimal import Decimal

from constant.bank import Bank
from domain.model.ticker import Ticker


@dataclass(frozen=True)
class PositionByBank:
    ticker: Ticker
    bank: Bank
    quantity: int
    acquisition_price: Decimal
    current_price: Decimal
