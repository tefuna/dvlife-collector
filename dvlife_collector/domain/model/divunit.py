import decimal
from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class Divunit:
    divunit_id: str = field(init=False)
    ticker: str
    div_date: date
    amount: decimal
    paid: bool

    def __post_init__(self):
        object.__setattr__(self, "divunit_id", f"{self.ticker}_{self.div_date:%Y%m%d}")
