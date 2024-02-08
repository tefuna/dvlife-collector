from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from domain.model.position_by_bank import PositionByBank


@dataclass(frozen=True)
class Position:
    position_id: str = field(init=False)
    ticker: str
    base_date: date
    quantity: int
    acquisition_price: Decimal
    current_price: Decimal
    book_value: Decimal = field(init=False)
    market_value: Decimal = field(init=False)
    valuation_value: Decimal = field(init=False)
    valuation_ratio: Decimal = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "position_id", f"{self.ticker}_{self.base_date:%Y%m%d}")
        # 新株予約等、取得価額が 0 のケースの対応。
        acquisition_price = self.acquisition_price
        if self.acquisition_price == 0:
            acquisition_price = self.current_price
        object.__setattr__(self, "book_value", acquisition_price * self.quantity)
        object.__setattr__(self, "market_value", self.current_price * self.quantity)
        object.__setattr__(self, "valuation_value", self.market_value - self.book_value)
        object.__setattr__(self, "valuation_ratio", self.valuation_value / self.book_value)

    def add(self, position_by_bank: PositionByBank) -> Position:
        quantity = self.quantity + position_by_bank.quantity
        acquisition_price = (
            (self.acquisition_price * self.quantity) + (position_by_bank.acquisition_price * position_by_bank.quantity)
        ) / quantity
        return Position(self.ticker, self.base_date, quantity, acquisition_price, self.current_price)
