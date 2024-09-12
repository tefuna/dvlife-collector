from dataclasses import dataclass


@dataclass(frozen=True)
class ValuationIn:
    ticker: str
    scope: str
    row_number: int

    def __post_init__(self) -> None:
        pass
