import decimal
from dataclasses import dataclass, field

from domain.model.divunit import Divunit


@dataclass(frozen=True)
class AnnualDividend:
    ticker: str
    amount: decimal = field(init=False)
    divunits: list[Divunit]

    def __post_init__(self):
        object.__setattr__(self, "amount", sum([x.amount for x in self.divunits]))
