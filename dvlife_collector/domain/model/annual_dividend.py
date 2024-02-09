from dataclasses import dataclass, field
from decimal import Decimal

from domain.model.divunit import Divunit


@dataclass(frozen=True)
class AnnualDividend:
    ticker: str
    amount: Decimal = field(init=False)
    divunits: list[Divunit]

    def __post_init__(self) -> None:
        object.__setattr__(self, "amount", sum([x.amount for x in self.divunits]))
