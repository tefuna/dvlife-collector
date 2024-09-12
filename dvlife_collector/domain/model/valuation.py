from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from domain.model.valuation_in import ValuationIn


@dataclass(frozen=True)
class Valuation:
    valuation_in: ValuationIn
    last_updated: datetime
    current_price: Decimal
    price_changed_rate_the_day_before: Decimal
    forward_EPS: Decimal
    forward_PER: Decimal
    actual_PBR: Decimal
    dividend_per_share: Decimal
    dividend_yield: Decimal
    equity_ratio: Decimal = Decimal(0)
    actual_ROE: Decimal  = Decimal(0)
    forward_ROE: Decimal = Decimal(0)
    actual_ROA: Decimal = Decimal(0)
    forward_ROA: Decimal  = Decimal(0)
    actual_EPS: Decimal  = Decimal(0)


    def __post_init__(self) -> None:
        pass

    def to_list4gs_all(self) -> list[str]:
        return [
            str(self.last_updated),
            str(self.current_price),
            str(self.price_changed_rate_the_day_before),
            str(self.forward_EPS),
            str(self.forward_PER),
            str(self.actual_PBR),
            str(self.dividend_per_share),
            str(self.dividend_yield),
            str(self.equity_ratio),
            str(self.actual_ROE),
            str(self.forward_ROE),
            str(self.actual_ROA),
            str(self.forward_ROA),
            str(self.actual_EPS),
        ]

    def to_list4gs_price(self) -> list[str]:
        return [
            str(self.last_updated),
            str(self.current_price),
            str(self.price_changed_rate_the_day_before),
            str(self.forward_EPS),
            str(self.forward_PER),
            str(self.actual_PBR),
            str(self.dividend_per_share),
            str(self.dividend_yield),
        ]
