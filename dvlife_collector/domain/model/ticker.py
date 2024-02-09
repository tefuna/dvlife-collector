import re
from dataclasses import dataclass

REG = re.compile(r"aaa")


@dataclass(frozen=True)
class Ticker:
    ticker: str

    def __post_init__(self) -> None:
        pass
