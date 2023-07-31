from dataclasses import dataclass

from constant.site_kind import SiteKind


@dataclass(frozen=True)
class DivunitTarget:
    ticker: str
    site_kind: SiteKind
    url: str
