from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class Divunit:
    divunit_id: str = field(init=False)
    ticker: str
    div_date: date
    amount: Decimal
    paid: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "divunit_id", f"{self.ticker}_{self.div_date:%Y%m%d}")
